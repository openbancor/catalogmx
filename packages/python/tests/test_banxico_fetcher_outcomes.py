"""Regression tests for the Banxico fetcher process contract."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = REPO_ROOT / "packages" / "shared-data" / "scripts"
FULL_CHECK = REPO_ROOT / "scripts" / "full_check.sh"


def load_script(filename: str) -> ModuleType:
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))
    path = SCRIPTS_DIR / filename
    module_name = "test_" + filename.removesuffix(".py")
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_shared_exit_code_contract_is_explicit():
    helper = load_script("banxico_sqlite_helper.py")

    assert helper.EXIT_SUCCESS == 0
    assert helper.EXIT_ERROR == 1
    assert helper.EXIT_NO_OBSERVATION == 3


@pytest.mark.parametrize(
    ("filename", "fetch_function"),
    [
        ("fetch_udis_banxico.py", "fetch_udi_data"),
        ("fetch_tipo_cambio_banxico.py", "fetch_data"),
        ("fetch_tipo_cambio_hist_banxico.py", "fetch_data"),
        ("fetch_tiie_banxico.py", "fetch_data"),
        ("fetch_cetes_banxico.py", "fetch_data"),
        ("fetch_inflacion_banxico.py", "fetch_data"),
        ("fetch_salarios_minimos_banxico.py", "fetch_all_series"),
    ],
)
def test_valid_empty_source_window_returns_no_observation(
    filename: str,
    fetch_function: str,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    module = load_script(filename)
    monkeypatch.setattr(module, "ensure_database_exists", lambda _path: None)
    monkeypatch.setattr(module, fetch_function, lambda *_args, **_kwargs: [])
    monkeypatch.setattr(
        sys,
        "argv",
        [
            filename,
            "--token",
            "test-token",
            "--start-date",
            "2026-08-01",
            "--end-date",
            "2026-08-27",
            "--database",
            str(tmp_path / "dynamic.sqlite3"),
        ],
    )

    assert module.main() == 3


def test_salary_fetch_is_fail_closed_across_series(monkeypatch: pytest.MonkeyPatch):
    module = load_script("fetch_salarios_minimos_banxico.py")
    monkeypatch.setattr(
        module,
        "SALARY_SERIES",
        {
            "FIRST": {
                "name": "First",
                "start_date": "2026-01-01",
                "type": "nominal",
                "zone": "general",
            },
            "SECOND": {
                "name": "Second",
                "start_date": "2026-01-01",
                "type": "nominal",
                "zone": "frontera_norte",
            },
        },
    )

    def fake_fetch(_token, series_id, _info, _start, _end):
        if series_id == "FIRST":
            return [
                {
                    "fecha": "2026-01-01",
                    "zona": "general",
                    "salario_diario": 1.0,
                    "anio": 2026,
                    "mes": 1,
                }
            ]
        raise RuntimeError("upstream unavailable")

    monkeypatch.setattr(module, "fetch_series_chunk", fake_fetch)

    with pytest.raises(ValueError, match="SECOND: upstream unavailable"):
        module.fetch_all_series("token", "2026-01-01", "2026-01-31")


def test_local_full_check_understands_no_observation_exit_code():
    text = FULL_CHECK.read_text(encoding="utf-8")

    assert "status=$?" in text
    assert "3)" in text
    assert "valid source window contained no new observations" in text
