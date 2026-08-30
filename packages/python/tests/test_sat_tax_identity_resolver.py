"""Tests for SAT country-scoped tax identity validation."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from catalogmx.catalogs.sat.comercio_exterior import (
    EstadoCatalog,
    RegistroIdentTribCatalog,
)
from catalogmx.catalogs.sat.comercio_exterior.validator import ComercioExteriorValidator


def _create_cfdi_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            "CREATE TABLE cfdi_40_paises ("
            "id TEXT PRIMARY KEY, texto TEXT NOT NULL, patron_codigo_postal TEXT, "
            "patron_identidad_tributaria TEXT, validacion_identidad_tributaria TEXT, "
            "agrupaciones TEXT)"
        )
        connection.executemany(
            "INSERT INTO cfdi_40_paises VALUES (?, ?, ?, ?, ?, ?)",
            [
                (
                    "CAN",
                    "Canadá",
                    "[A-Z][0-9][A-Z] [0-9][A-Z][0-9]",
                    "[0-9]{9}",
                    "",
                    "TLCAN",
                ),
                ("ESP", "España", "", "", "", "Unión Europea"),
                (
                    "MEX",
                    "México",
                    "[0-9]{5}",
                    "[A-Z&Ñ]{3,4}[0-9]{6}[A-Z0-9]{3}",
                    "Lista del SAT",
                    "TLCAN",
                ),
                (
                    "USA",
                    "Estados Unidos (los)",
                    "[0-9]{5}(-[0-9]{4})?",
                    "[0-9]{9}",
                    "",
                    "TLCAN",
                ),
            ],
        )
        connection.commit()
    finally:
        connection.close()


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
                ("ON", "CAN", "Ontario", "2024-01-18", ""),
                ("TX", "USA", "Texas", "2024-01-18", ""),
            ],
        )
        connection.commit()
    finally:
        connection.close()


def _reset() -> None:
    RegistroIdentTribCatalog._data = None
    RegistroIdentTribCatalog._tipo_by_code = None
    RegistroIdentTribCatalog._country_rules = None
    RegistroIdentTribCatalog._country_rule_by_code = None
    EstadoCatalog._estados_usa = None
    EstadoCatalog._provincias_canada = None
    EstadoCatalog._estado_by_code = None


@pytest.fixture(autouse=True)
def tax_identity_shared_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    shared = tmp_path / "shared"
    _create_cfdi_database(shared / "sat" / "cfdi_4.0" / "sat_cfdi_40.sqlite3")
    _create_cce_database(
        shared / "sat" / "comercio_exterior_2.0" / "sat_comercio_exterior_20.sqlite3"
    )
    monkeypatch.setenv("CATALOGMX_SHARED_DATA", str(shared))
    _reset()
    try:
        yield shared
    finally:
        _reset()


def test_country_rules_are_resolver_backed_sat_metadata() -> None:
    usa = RegistroIdentTribCatalog.get_country_rule("usa")
    assert usa == {
        "country": "USA",
        "country_name": "Estados Unidos (los)",
        "format_pattern": "[0-9]{9}",
        "validation_mode": None,
        "postal_code_pattern": "[0-9]{5}(-[0-9]{4})?",
        "groups": "TLCAN",
    }
    assert len(RegistroIdentTribCatalog.get_all_country_rules()) == 4


def test_usa_and_canada_use_sat_nine_digit_pattern() -> None:
    assert RegistroIdentTribCatalog.validate_for_country("USA", "123456789") == {
        "valid": True,
        "errors": [],
        "validation": None,
        "requires_external_validation": False,
    }
    assert RegistroIdentTribCatalog.validate_for_country("CAN", "987654321")["valid"] is True

    usa_invalid = RegistroIdentTribCatalog.validate_for_country("USA", "12345678")
    assert usa_invalid["valid"] is False
    assert usa_invalid["requires_external_validation"] is False
    assert "USA" in usa_invalid["errors"][0]

    canada_invalid = RegistroIdentTribCatalog.validate_for_country("CAN", "123-456-789")
    assert canada_invalid["valid"] is False


def test_countries_without_local_pattern_are_not_given_invented_rules() -> None:
    assert RegistroIdentTribCatalog.validate_for_country("ESP", "NIF-LOCAL-FORMAT") == {
        "valid": True,
        "errors": [],
        "validation": None,
        "requires_external_validation": False,
    }
    assert RegistroIdentTribCatalog.validate_for_country("ESP", "")["valid"] is False


def test_sat_list_validation_is_not_reduced_to_regex() -> None:
    # SAT marks Mexico as "Lista del SAT". A local regex match or mismatch cannot
    # replace that external validation mode, so CatalogMX does not reject locally.
    result = RegistroIdentTribCatalog.validate_for_country("MEX", "NOT-A-MEXICAN-RFC")
    assert result == {
        "valid": True,
        "errors": [],
        "validation": "Lista del SAT",
        "requires_external_validation": True,
    }


def test_legacy_identity_type_aliases_remain_code_owned_compatibility() -> None:
    aliases = RegistroIdentTribCatalog.get_all()
    assert len(aliases) == 15
    assert all(item["source"] == "catalogmx-legacy" for item in aliases)
    assert RegistroIdentTribCatalog.get_tipo("06")["descripcion"].startswith("EIN")
    assert RegistroIdentTribCatalog.validate_tax_id("06", "anything") == {
        "valid": True,
        "errors": [],
    }
    assert RegistroIdentTribCatalog.validate_tax_id("XX", "123456789")["valid"] is False
    assert RegistroIdentTribCatalog.validate_tax_id("USA", "123456789")["valid"] is True


def test_receptor_validation_uses_country_even_without_legacy_type() -> None:
    result = ComercioExteriorValidator._validate_receptor(
        {"pais": "USA", "estado": "TX", "num_reg_id_trib": "12345678"}
    )
    assert result["errors"] == ["Formato de NumRegIdTrib no válido para país USA"]

    valid = ComercioExteriorValidator._validate_receptor(
        {"pais": "USA", "estado": "TX", "num_reg_id_trib": "123456789"}
    )
    assert valid == {"errors": []}


def test_receptor_keeps_optional_legacy_type_validation_separate() -> None:
    result = ComercioExteriorValidator._validate_receptor(
        {
            "pais": "CAN",
            "estado": "ON",
            "tipo_registro_trib": "XX",
            "num_reg_id_trib": "123456789",
        }
    )
    assert result["errors"] == ["Tipo de registro no válido"]
