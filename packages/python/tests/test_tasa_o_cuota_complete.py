"""Behavioral tests for the resolver-backed CFDI TasaOCuota catalog."""

from __future__ import annotations

import sqlite3
from decimal import Decimal
from pathlib import Path

import pytest

from catalogmx.catalogs.sat.cfdi_4.tasa_o_cuota import TasaOCuota


def _create_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            "CREATE TABLE cfdi_40_reglas_tasa_cuota ("
            "tipo TEXT NOT NULL, minimo TEXT, valor TEXT, impuesto TEXT NOT NULL, "
            "factor TEXT NOT NULL, traslado INTEGER, retencion INTEGER, "
            "vigencia_desde TEXT, vigencia_hasta TEXT)"
        )
        connection.executemany(
            "INSERT INTO cfdi_40_reglas_tasa_cuota VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                ("Fijo", "", "0.000000", "IVA", "Tasa", 1, 0, "2022-01-01", ""),
                ("Fijo", "", "0.160000", "IVA", "Tasa", 1, 0, "2022-01-01", ""),
                (
                    "Rango",
                    "0.000000",
                    "0.160000",
                    "IVA",
                    "Tasa",
                    0,
                    1,
                    "2022-01-01",
                    "",
                ),
                (
                    "Rango",
                    "0.000000",
                    "0.350000",
                    "ISR",
                    "Tasa",
                    0,
                    1,
                    "2022-01-01",
                    "",
                ),
                ("Fijo", "", "0.530000", "IEPS", "Tasa", 1, 1, "2022-01-01", ""),
            ],
        )
        connection.commit()
    finally:
        connection.close()


@pytest.fixture(autouse=True)
def tasa_shared_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    shared = tmp_path / "shared"
    database = shared / "sat" / "cfdi_4.0" / "sat_cfdi_40.sqlite3"
    _create_database(database)
    monkeypatch.setenv("CATALOGMX_SHARED_DATA", str(shared))
    TasaOCuota._data = None
    try:
        yield database
    finally:
        TasaOCuota._data = None


def test_get_data_normalizes_fixed_and_range_rows() -> None:
    data = TasaOCuota.get_data()
    assert len(data) == 5
    assert data[0] == {
        "tipo": "Fijo",
        "valor_mínimo": None,
        "valor_máximo": "0.000000",
        "impuesto": "IVA",
        "factor": "Tasa",
        "trasladado": True,
        "retenido": False,
        "vigencia_desde": "2022-01-01",
        "vigencia_hasta": "",
    }
    range_row = next(
        item
        for item in data
        if item["tipo"] == "Rango" and item["impuesto"] == "IVA"
    )
    assert range_row["valor_mínimo"] == "0.000000"
    assert range_row["valor_máximo"] == "0.160000"


def test_get_data_is_cached() -> None:
    assert TasaOCuota.get_data() is TasaOCuota.get_data()


def test_filters_fixed_rate_with_tax_code_alias_and_flags() -> None:
    results = TasaOCuota.get_by_range_and_tax(
        valor_min=None,
        valor_max=Decimal("0.16"),
        impuesto="002",
        factor="tasa",
        trasladado=True,
        retenido=False,
    )
    assert len(results) == 1
    assert results[0]["tipo"] == "Fijo"
    assert results[0]["impuesto"] == "IVA"
    assert results[0]["valor_máximo"] == "0.160000"


def test_filters_range_and_uses_transfer_retention_criteria() -> None:
    retained = TasaOCuota.get_by_range_and_tax(
        valor_min=0,
        valor_max=0.16,
        impuesto="IVA",
        factor="Tasa",
        trasladado=False,
        retenido=True,
    )
    assert len(retained) == 1
    assert retained[0]["tipo"] == "Rango"

    transferred = TasaOCuota.get_by_range_and_tax(
        valor_min=0,
        valor_max=0.16,
        impuesto="IVA",
        factor="Tasa",
        trasladado=True,
        retenido=False,
    )
    assert transferred == []


def test_none_criteria_are_wildcards() -> None:
    assert TasaOCuota.get_by_range_and_tax(None, None, None, None, None, None) == (
        TasaOCuota.get_data()
    )


def test_decimal_criteria_are_representation_independent() -> None:
    from_string = TasaOCuota.get_by_range_and_tax(None, "0.530000", "003", "Tasa", True, True)
    from_float = TasaOCuota.get_by_range_and_tax(None, 0.53, "IEPS", "tasa", True, True)
    assert from_string == from_float
    assert len(from_float) == 1


def test_nonexistent_criteria_return_empty_list() -> None:
    assert (
        TasaOCuota.get_by_range_and_tax(
            "NONEXISTENT",
            "NONEXISTENT",
            "NONEXISTENT",
            "NONEXISTENT",
            None,
            None,
        )
        == []
    )
