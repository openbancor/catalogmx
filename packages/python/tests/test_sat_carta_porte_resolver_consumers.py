"""Runtime tests for resolver-backed SAT Carta Porte 3.1 public catalogs."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from catalogmx.catalogs.sat.carta_porte import (
    ConfigAutotransporteCatalog,
    MaterialPeligrosoCatalog,
    TipoEmbalajeCatalog,
    TipoPermisoCatalog,
)

CATALOGS = (
    ConfigAutotransporteCatalog,
    MaterialPeligrosoCatalog,
    TipoEmbalajeCatalog,
    TipoPermisoCatalog,
)


def _create_carta_porte_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            "CREATE TABLE ccp_31_configuraciones_autotransporte ("
            "id TEXT PRIMARY KEY, texto TEXT NOT NULL, numero_de_ejes INTEGER, "
            "numero_de_llantas INTEGER, remolque TEXT, vigencia_desde TEXT, "
            "vigencia_hasta TEXT)"
        )
        connection.executemany(
            "INSERT INTO ccp_31_configuraciones_autotransporte VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    "VL",
                    "Vehículo ligero de carga",
                    2,
                    4,
                    "0, 1",
                    "2024-07-17",
                    "",
                ),
                (
                    "C2",
                    "Camión Unitario (2 llantas en el eje delantero y 4 llantas en el eje trasero)",
                    2,
                    6,
                    "0",
                    "2024-07-17",
                    "",
                ),
                (
                    "C2R2",
                    "Camión-Remolque",
                    4,
                    12,
                    "1",
                    "2024-07-17",
                    "",
                ),
            ],
        )

        connection.execute(
            "CREATE TABLE ccp_31_materiales_peligrosos ("
            "id TEXT PRIMARY KEY, texto TEXT NOT NULL, clase_o_div TEXT, "
            "peligro_secundario TEXT, nombre_tecnico TEXT, vigencia_desde TEXT, "
            "vigencia_hasta TEXT)"
        )
        connection.executemany(
            "INSERT INTO ccp_31_materiales_peligrosos VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    "0004",
                    "PICRATO AMÓNICO seco",
                    "1.1D",
                    "",
                    "",
                    "2024-07-17",
                    "",
                ),
                (
                    "1203",
                    "GASOLINA",
                    "3",
                    "",
                    "",
                    "2024-07-17",
                    "",
                ),
            ],
        )

        connection.execute(
            "CREATE TABLE ccp_31_tipos_embalaje ("
            "id TEXT PRIMARY KEY, texto TEXT NOT NULL, vigencia_desde TEXT, "
            "vigencia_hasta TEXT)"
        )
        connection.executemany(
            "INSERT INTO ccp_31_tipos_embalaje VALUES (?, ?, ?, ?)",
            [
                ("1A1", "Bidones (Tambores) de Acero 1 de tapa no desmontable", "2024-07-17", ""),
                ("5M1", "Sacos de Papel de varias hojas", "2024-07-17", ""),
            ],
        )

        connection.execute(
            "CREATE TABLE ccp_31_tipos_permiso ("
            "id TEXT PRIMARY KEY, texto TEXT NOT NULL, clave_transporte TEXT, "
            "vigencia_desde TEXT, vigencia_hasta TEXT)"
        )
        connection.executemany(
            "INSERT INTO ccp_31_tipos_permiso VALUES (?, ?, ?, ?, ?)",
            [
                (
                    "TPAF01",
                    "Autotransporte Federal de carga general.",
                    "01",
                    "2024-07-17",
                    "",
                ),
                (
                    "TPAF99",
                    "Autotransporte Federal de pasaje y turismo.",
                    "01",
                    "2024-07-17",
                    "",
                ),
                (
                    "TPMR01",
                    "Permiso para transporte marítimo.",
                    "02",
                    "2024-07-17",
                    "",
                ),
            ],
        )
        connection.commit()
    finally:
        connection.close()


def _reset_catalogs() -> None:
    for catalog in CATALOGS:
        catalog._data = None
        if hasattr(catalog, "_by_code"):
            catalog._by_code = None
        if hasattr(catalog, "_by_un_number"):
            catalog._by_un_number = None


@pytest.fixture(autouse=True)
def carta_porte_shared_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    shared = tmp_path / "shared"
    database = shared / "sat" / "carta_porte_3.1" / "sat_carta_porte_31.sqlite3"
    _create_carta_porte_database(database)
    monkeypatch.setenv("CATALOGMX_SHARED_DATA", str(shared))
    _reset_catalogs()
    try:
        yield database
    finally:
        _reset_catalogs()


def test_config_autotransporte_uses_current_sat_rows() -> None:
    config = ConfigAutotransporteCatalog.get_config("C2")
    assert config == {
        "code": "C2",
        "name": "Camión Unitario (2 llantas en el eje delantero y 4 llantas en el eje trasero)",
        "type": "Unitario",
        "axes": 2,
        "wheels": 6,
        "trailer": "0",
        "valid_from": "2024-07-17",
        "valid_to": None,
    }
    assert ConfigAutotransporteCatalog.get_axes_count("C2") == 2
    assert [item["code"] for item in ConfigAutotransporteCatalog.get_by_type("Ligero")] == ["VL"]
    assert [item["code"] for item in ConfigAutotransporteCatalog.get_by_type("Articulado")] == [
        "C2R2"
    ]


def test_material_peligroso_preserves_sat_class_without_fabricating_packing_group() -> None:
    material = MaterialPeligrosoCatalog.get_material("0004")
    assert material is not None
    assert material["class"] == "1"
    assert material["clase_riesgo"] == "1"
    assert material["clase_division"] == "1.1D"
    assert material["packing_group"] is None
    assert material["grupo_embalaje"] is None
    assert MaterialPeligrosoCatalog.get_by_packing_group("I") == []
    assert MaterialPeligrosoCatalog.requires_special_handling("0004") is False
    assert [item["code"] for item in MaterialPeligrosoCatalog.get_by_class("1")] == ["0004"]


def test_tipo_embalaje_derives_search_material_from_official_text() -> None:
    steel = TipoEmbalajeCatalog.get_embalaje("1A1")
    assert steel is not None
    assert steel["material"] == "Acero"
    assert steel["categoria_onu"] is None
    assert [item["code"] for item in TipoEmbalajeCatalog.get_by_material("Papel")] == ["5M1"]


def test_tipo_permiso_uses_sat_transport_key_and_derived_legacy_type() -> None:
    cargo = TipoPermisoCatalog.get_permiso("TPAF01")
    assert cargo is not None
    assert cargo["name"] == "Autotransporte Federal de carga general"
    assert cargo["transport"] == "01"
    assert cargo["clave_transporte"] == "01"
    assert cargo["type"] == "Carga"
    assert TipoPermisoCatalog.is_carga_permit("TPAF01") is True

    assert [item["code"] for item in TipoPermisoCatalog.get_by_type("Pasajeros")] == ["TPAF99"]
    assert [item["code"] for item in TipoPermisoCatalog.get_by_transport("02")] == ["TPMR01"]


def test_missing_codes_remain_false_or_none() -> None:
    assert ConfigAutotransporteCatalog.get_config("NOPE") is None
    assert ConfigAutotransporteCatalog.is_valid("NOPE") is False
    assert MaterialPeligrosoCatalog.is_valid("NOPE") is False
    assert TipoEmbalajeCatalog.is_valid("NOPE") is False
    assert TipoPermisoCatalog.is_valid("NOPE") is False
