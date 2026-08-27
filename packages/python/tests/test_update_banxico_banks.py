"""Tests for fail-closed Banxico CEP reference maintenance."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "update_banxico_banks.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("banxico_reference_updater", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_parser_extracts_live_table_and_ignores_header(monkeypatch: pytest.MonkeyPatch):
    module = load_module()
    monkeypatch.setattr(module, "MIN_EXPECTED_INSTITUTIONS", 2)
    html = """
    <table>
      <tr><th>Clave de la institución</th><th>Nombre de la institución</th></tr>
      <tr><td>40002</td><td>BANAMEX</td></tr>
      <tr><td>2001</td><td> BANXICO </td></tr>
    </table>
    """

    assert module.parse_institutions_html(html) == [
        ("40002", "BANAMEX"),
        ("2001", "BANXICO"),
    ]
    assert module.normalize_institution_key("40002") == "002"
    assert module.normalize_institution_key("2001") == "001"


def test_parser_fails_closed_on_partial_or_ambiguous_source(
    monkeypatch: pytest.MonkeyPatch,
):
    module = load_module()
    with pytest.raises(RuntimeError, match="looks incomplete"):
        module.parse_institutions_html("<tr><td>40002</td><td>BANAMEX</td></tr>")

    monkeypatch.setattr(module, "MIN_EXPECTED_INSTITUTIONS", 2)
    with pytest.raises(RuntimeError, match="collapse"):
        module.validate_institutions(
            [("40001", "FIRST"), ("90001", "SECOND")]
        )
    with pytest.raises(ValueError, match="invalid Banxico institution key"):
        module.normalize_institution_key("ABC")


def test_sync_preserves_enrichments_and_historical_rows(
    monkeypatch: pytest.MonkeyPatch,
):
    module = load_module()
    monkeypatch.setattr(module, "MIN_EXPECTED_INSTITUTIONS", 2)
    existing = [
        {
            "code": "002",
            "name": "OLD BANAMEX",
            "full_name": "Banco Nacional de México, S.A.",
            "rfc": "BNM840515VB1",
            "spei": True,
            "tipo_institucion": "banca_multiple",
        },
        {
            "code": "143",
            "name": "CIBanco",
            "full_name": "CIBanco, S.A.",
            "rfc": None,
            "spei": False,
        },
    ]

    merged, summary = module.sync_banks(
        existing,
        [("40002", "BANAMEX"), ("90721", "albo")],
    )
    by_code = {item["code"]: item for item in merged}

    assert by_code["002"]["name"] == "BANAMEX"
    assert by_code["002"]["full_name"] == "Banco Nacional de México, S.A."
    assert by_code["002"]["rfc"] == "BNM840515VB1"
    assert by_code["002"]["tipo_institucion"] == "banca_multiple"
    assert by_code["002"]["banxico_key"] == "40002"
    assert by_code["002"]["cep_current"] is True

    assert by_code["143"]["cep_current"] is False
    assert by_code["143"]["spei"] is False

    assert by_code["721"] == {
        "code": "721",
        "name": "albo",
        "full_name": "albo",
        "rfc": None,
        "spei": True,
        "banxico_key": "90721",
        "cep_current": True,
    }
    assert summary == module.SyncSummary(current=2, added=1, renamed=1, historical=1)


def test_snapshot_is_source_faithful_and_deterministic(
    monkeypatch: pytest.MonkeyPatch,
):
    module = load_module()
    monkeypatch.setattr(module, "MIN_EXPECTED_INSTITUTIONS", 2)
    institutions = module.validate_institutions(
        [("90721", "albo"), ("40002", "BANAMEX")]
    )

    assert module.render_current_snapshot(institutions) == [
        {"banxico_key": "40002", "code": "002", "name": "BANAMEX"},
        {"banxico_key": "90721", "code": "721", "name": "albo"},
    ]


def test_main_does_not_write_when_source_validation_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
):
    module = load_module()
    banks_path = tmp_path / "banks.json"
    snapshot_path = tmp_path / "spei_institutions.json"
    banks_path.write_text(
        json.dumps(
            [
                {
                    "code": "002",
                    "name": "BANAMEX",
                    "full_name": "Banco Nacional de México, S.A.",
                    "rfc": None,
                    "spei": True,
                }
            ]
        ),
        encoding="utf-8",
    )
    original = banks_path.read_text(encoding="utf-8")
    monkeypatch.setattr(module, "fetch_institutions", lambda url: [])

    result = module.main(
        [
            "--banks-path",
            str(banks_path),
            "--snapshot-path",
            str(snapshot_path),
        ]
    )

    assert result == 1
    assert banks_path.read_text(encoding="utf-8") == original
    assert not snapshot_path.exists()
