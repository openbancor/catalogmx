import json
from pathlib import Path

import pytest

from catalogmx.utils import shared_data as sd


def test_shared_data_env_override(tmp_path, monkeypatch):
    target = tmp_path / "custom_shared"
    target.mkdir()
    monkeypatch.setenv("CATALOGMX_SHARED_DATA", str(target))
    assert sd.get_shared_data_root() == target.resolve()


def test_shared_data_default_package_location(monkeypatch):
    monkeypatch.delenv("CATALOGMX_SHARED_DATA", raising=False)
    root = sd.get_shared_data_root()
    expected = Path(sd.__file__).resolve().parents[1] / "shared-data"
    if not expected.exists():
        for parent in Path(sd.__file__).resolve().parents:
            repo_candidate = parent / "packages" / "shared-data"
            if repo_candidate.exists():
                expected = repo_candidate
                break
    assert root == expected
    assert root.exists()


def test_shared_data_missing_raises(monkeypatch):
    monkeypatch.delenv("CATALOGMX_SHARED_DATA", raising=False)

    def _always_false(self):
        return False

    monkeypatch.setattr(sd.Path, "exists", _always_false, raising=True)
    with pytest.raises(FileNotFoundError):
        sd.get_shared_data_root()


def test_banxico_catalogs_use_shared_data_env_override(tmp_path, monkeypatch):
    from catalogmx.catalogs.banxico.banks import BankCatalog
    from catalogmx.catalogs.banxico.codigos_plaza import CodigosPlazaCatalog

    root = tmp_path / "shared-data"
    banxico = root / "banxico"
    banxico.mkdir(parents=True)

    (banxico / "banks.json").write_text(
        json.dumps(
            [
                {
                    "code": "999",
                    "name": "BANCO TEST",
                    "full_name": "Banco Test",
                    "rfc": None,
                    "spei": True,
                }
            ]
        ),
        encoding="utf-8",
    )
    (banxico / "codigos_plaza.json").write_text(
        json.dumps(
            {
                "plazas": [
                    {
                        "codigo": "999",
                        "plaza": "Plaza Test",
                        "estado": "Estado Test",
                        "cve_entidad": "99",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("CATALOGMX_SHARED_DATA", str(root))

    monkeypatch.setattr(BankCatalog, "_data", None)
    monkeypatch.setattr(BankCatalog, "_bank_by_code", None)
    monkeypatch.setattr(BankCatalog, "_bank_by_name", None)
    monkeypatch.setattr(BankCatalog, "_bank_by_name_normalized", None)

    monkeypatch.setattr(CodigosPlazaCatalog, "_data", None)
    monkeypatch.setattr(CodigosPlazaCatalog, "_by_codigo", None)
    monkeypatch.setattr(CodigosPlazaCatalog, "_by_estado", None)
    monkeypatch.setattr(CodigosPlazaCatalog, "_by_plaza", None)
    monkeypatch.setattr(CodigosPlazaCatalog, "_by_plaza_normalized", None)

    assert BankCatalog.get_bank_by_code("999")["name"] == "BANCO TEST"
    plazas = CodigosPlazaCatalog.buscar_por_codigo("999")
    assert len(plazas) == 1
    assert plazas[0]["plaza"] == "Plaza Test"
