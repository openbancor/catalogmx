"""Runtime tests for resolver-backed SAT Comercio Exterior 2.0 consumers."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from catalogmx.catalogs.sat.comercio_exterior import (
    EstadoCatalog,
    IncotermsValidator,
    MotivoTrasladoCatalog,
    UnidadAduanaCatalog,
)


def _create_cce_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            "CREATE TABLE cce_20_estados ("
            "estado TEXT NOT NULL, pais TEXT NOT NULL, texto TEXT NOT NULL, "
            "vigencia_desde TEXT, vigencia_hasta TEXT)"
        )
        connection.executemany(
            "INSERT INTO cce_20_estados VALUES (?, ?, ?, ?, ?)",
            [
                ("AGU", "MEX", "Aguascalientes", "2024-01-18", ""),
                ("ON", "CAN", "Ontario", "2024-01-18", ""),
                ("UN", "CAN", "Nunavut", "2024-01-18", ""),
                ("TX", "USA", "Texas", "2024-01-18", ""),
            ],
        )

        connection.execute(
            "CREATE TABLE cce_20_incoterms ("
            "id TEXT PRIMARY KEY, texto TEXT NOT NULL, vigencia_desde TEXT, "
            "vigencia_hasta TEXT)"
        )
        connection.executemany(
            "INSERT INTO cce_20_incoterms VALUES (?, ?, ?, ?)",
            [
                ("CIF", "COSTE, SEGURO Y FLETE (PUERTO DE DESTINO CONVENIDO).", "2024-01-18", ""),
                ("EXW", "EN FABRICA (LUGAR CONVENIDO).", "2024-01-18", ""),
                ("FCA", "FRANCO TRANSPORTISTA (LUGAR DESIGNADO).", "2024-01-18", ""),
            ],
        )

        connection.execute(
            "CREATE TABLE cce_20_motivos_traslado (id TEXT PRIMARY KEY, texto TEXT NOT NULL)"
        )
        connection.executemany(
            "INSERT INTO cce_20_motivos_traslado VALUES (?, ?)",
            [
                ("01", "Envío de mercancias facturadas con anterioridad"),
                ("05", "Envío de mercancías propiedad de terceros"),
                ("99", "Otros"),
            ],
        )

        connection.execute(
            "CREATE TABLE cce_20_unidades_medida ("
            "id TEXT PRIMARY KEY, texto TEXT NOT NULL, vigencia_desde TEXT, "
            "vigencia_hasta TEXT)"
        )
        connection.executemany(
            "INSERT INTO cce_20_unidades_medida VALUES (?, ?, ?, ?)",
            [
                ("01", "KILO", "2024-01-18", ""),
                ("05", "METRO CUBICO", "2024-01-18", ""),
                ("20", "CAJA", "2024-01-18", ""),
                ("99", "SERVICIO", "2024-01-18", ""),
            ],
        )
        connection.commit()
    finally:
        connection.close()


def _reset_catalogs() -> None:
    EstadoCatalog._estados_usa = None
    EstadoCatalog._provincias_canada = None
    EstadoCatalog._estado_by_code = None
    IncotermsValidator._data = None
    IncotermsValidator._incoterm_by_code = None
    MotivoTrasladoCatalog._data = None
    MotivoTrasladoCatalog._motivo_by_code = None
    UnidadAduanaCatalog._data = None
    UnidadAduanaCatalog._unidad_by_code = None


@pytest.fixture(autouse=True)
def cce_shared_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    shared = tmp_path / "shared"
    database = shared / "sat" / "comercio_exterior_2.0" / "sat_comercio_exterior_20.sqlite3"
    _create_cce_database(database)
    monkeypatch.setenv("CATALOGMX_SHARED_DATA", str(shared))
    _reset_catalogs()
    try:
        yield database
    finally:
        _reset_catalogs()


def test_estado_catalog_uses_current_cce_subdivision_rows() -> None:
    texas = EstadoCatalog.get_estado_usa("tx")
    assert texas == {
        "code": "TX",
        "name": "Texas",
        "country": "USA",
        "valid_from": "2024-01-18",
        "valid_to": None,
    }
    assert EstadoCatalog.get_estado("TX", "CAN") is None
    assert [item["code"] for item in EstadoCatalog.get_all_usa()] == ["TX"]
    assert [item["code"] for item in EstadoCatalog.get_all_canada()] == ["ON", "UN"]
    assert all(item["country"] != "MEX" for item in EstadoCatalog.get_all())
    assert EstadoCatalog.get_provincia_canada("UN")["name"] == "Nunavut"


def test_estado_validation_uses_current_sat_country_membership() -> None:
    assert EstadoCatalog.validate_foreign_address({"pais": "USA", "estado": "TX"}) == {
        "valid": True,
        "errors": [],
    }
    missing = EstadoCatalog.validate_foreign_address({"pais": "CAN", "estado": ""})
    assert missing["valid"] is False
    assert "obligatorio" in missing["errors"][0]
    wrong_country = EstadoCatalog.validate_foreign_address({"pais": "CAN", "estado": "TX"})
    assert wrong_country["valid"] is False


def test_incoterms_use_sat_text_with_explicit_convenience_rules() -> None:
    cif = IncotermsValidator.get_incoterm("cif")
    assert cif is not None
    assert cif["description"] == "COSTE, SEGURO Y FLETE (PUERTO DE DESTINO CONVENIDO)."
    assert cif["name"] == "Cost, Insurance and Freight"
    assert cif["transport_mode"] == "maritime"
    assert cif["seller_pays_freight"] is True
    assert cif["seller_pays_insurance"] is True
    assert cif["valid_from"] == "2024-01-18"
    assert IncotermsValidator.is_valid_for_transport("CIF", "sea") is True
    assert IncotermsValidator.is_valid_for_transport("CIF", "land") is False
    assert IncotermsValidator.is_valid_for_transport("EXW", "air") is True
    assert IncotermsValidator.seller_pays_freight("EXW") is False
    assert IncotermsValidator.seller_pays_insurance("CIF") is True
    assert IncotermsValidator.get_maritime_incoterms() == ["CIF"]
    assert IncotermsValidator.get_multimodal_incoterms() == ["EXW", "FCA"]
    assert [item["code"] for item in IncotermsValidator.search("seguro")] == ["CIF"]


def test_motivo_traslado_uses_current_text_and_propietario_rule() -> None:
    motivo = MotivoTrasladoCatalog.get_motivo("01")
    assert motivo is not None
    assert motivo["descripcion"] == "Envío de mercancias facturadas con anterioridad"
    assert MotivoTrasladoCatalog.requires_propietario("01") is False
    assert MotivoTrasladoCatalog.requires_propietario("05") is True
    assert MotivoTrasladoCatalog.is_valid("99") is True


def test_unidad_aduana_uses_complete_canonical_shape_and_search_classification() -> None:
    kilo = UnidadAduanaCatalog.get_unidad("01")
    assert kilo == {
        "code": "01",
        "descripcion": "KILO",
        "type": "weight",
        "valid_from": "2024-01-18",
        "valid_to": None,
    }
    assert [item["code"] for item in UnidadAduanaCatalog.get_by_type("volume")] == ["05"]
    assert [item["code"] for item in UnidadAduanaCatalog.get_by_type("container")] == ["20"]
    assert [item["code"] for item in UnidadAduanaCatalog.get_by_type("service")] == ["99"]
    assert UnidadAduanaCatalog.is_valid("NOPE") is False
