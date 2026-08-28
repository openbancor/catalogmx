"""Tests for Comercio Exterior Python consumers backed by shared CFDI datasets."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from catalogmx.catalogs.sat.comercio_exterior import MonedaCatalog


def _create_cfdi_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            "CREATE TABLE cfdi_40_monedas ("
            "id TEXT PRIMARY KEY, texto TEXT NOT NULL, decimales INTEGER, "
            "porcentaje_variacion TEXT, vigencia_desde TEXT, vigencia_hasta TEXT)"
        )
        connection.executemany(
            "INSERT INTO cfdi_40_monedas VALUES (?, ?, ?, ?, ?, ?)",
            [
                ("EUR", "Euro", 2, "0.01", "2022-01-01", ""),
                ("MXN", "Peso Mexicano", 2, "0.01", "2022-01-01", ""),
                ("USD", "Dolar americano", 2, "0.01", "2022-01-01", ""),
                ("XAU", "Oro", 0, "0.01", "2022-01-01", ""),
            ],
        )
        connection.commit()
    finally:
        connection.close()


@pytest.fixture(autouse=True)
def cfdi_shared_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    shared = tmp_path / "shared"
    database = shared / "sat" / "cfdi_4.0" / "sat_cfdi_40.sqlite3"
    _create_cfdi_database(database)
    monkeypatch.setenv("CATALOGMX_SHARED_DATA", str(shared))
    MonedaCatalog._data = None
    MonedaCatalog._moneda_by_code = None
    try:
        yield database
    finally:
        MonedaCatalog._data = None
        MonedaCatalog._moneda_by_code = None


def test_moneda_catalog_uses_shared_cfdi_authority_rows() -> None:
    mxn = MonedaCatalog.get_moneda("mxn")
    assert mxn == {
        "codigo": "MXN",
        "nombre": "Peso Mexicano",
        "pais": None,
        "decimales": 2,
        "porcentaje_variacion": "0.01",
        "valid_from": "2022-01-01",
        "valid_to": None,
    }
    assert MonedaCatalog.get_moneda("XAU")["decimales"] == 0
    assert MonedaCatalog.is_valid("USD") is True
    assert MonedaCatalog.is_valid("NOPE") is False


def test_currency_search_uses_authority_code_and_name_not_legacy_country() -> None:
    assert [item["codigo"] for item in MonedaCatalog.search("peso")] == ["MXN"]
    assert [item["codigo"] for item in MonedaCatalog.search("EUR")] == ["EUR"]
    assert MonedaCatalog.search("México") == []


def test_validate_conversion_usd_preserves_historical_behavior() -> None:
    assert MonedaCatalog.validate_conversion_usd(
        {"moneda": "USD", "total": 100, "tipo_cambio_usd": 1, "total_usd": 100}
    ) == {"valid": True, "errors": []}

    invalid_usd = MonedaCatalog.validate_conversion_usd(
        {"moneda": "USD", "total": 100, "tipo_cambio_usd": 2, "total_usd": 200}
    )
    assert invalid_usd["valid"] is False
    assert len(invalid_usd["errors"]) == 2

    assert MonedaCatalog.validate_conversion_usd(
        {"moneda": "EUR", "total": 100, "tipo_cambio_usd": 1.2, "total_usd": 120}
    ) == {"valid": True, "errors": []}

    missing_fx = MonedaCatalog.validate_conversion_usd(
        {"moneda": "EUR", "total": 100, "total_usd": 120}
    )
    assert missing_fx["valid"] is False
    assert "TipoCambioUSD es obligatorio" in missing_fx["errors"][0]
