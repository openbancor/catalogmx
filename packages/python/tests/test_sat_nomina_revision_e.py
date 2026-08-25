"""Regression tests for SAT Nómina 1.2 revision E resources."""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SHARED_XSD = (
    REPO_ROOT
    / "packages"
    / "shared-data"
    / "sat"
    / "xsd"
    / "resources"
    / "www.sat.gob.mx"
    / "sitio_internet"
    / "cfd"
    / "catalogos"
    / "Nomina"
    / "catNomina.xsd"
)
WEB_XSD = (
    REPO_ROOT
    / "packages"
    / "webapp-svelte"
    / "static"
    / "data"
    / "sat"
    / "xsd"
    / "resources"
    / "www.sat.gob.mx"
    / "sitio_internet"
    / "cfd"
    / "catalogos"
    / "Nomina"
    / "catNomina.xsd"
)
REGISTRY = REPO_ROOT / "packages" / "shared-data" / "catalog-registry.json"
XS = {"xs": "http://www.w3.org/2001/XMLSchema"}


def _enumerations(type_name: str) -> set[str]:
    root = ET.parse(SHARED_XSD).getroot()
    simple_type = root.find(f"xs:simpleType[@name='{type_name}']", XS)
    assert simple_type is not None, f"missing XSD simple type {type_name}"
    return {
        item.attrib["value"]
        for item in simple_type.findall("xs:restriction/xs:enumeration", XS)
    }


def test_revision_e_perception_and_deduction_codes_are_present():
    """Guard the catalog additions published for Nómina 1.2 revision E."""
    perceptions = _enumerations("c_TipoPercepcion")
    deductions = _enumerations("c_TipoDeduccion")

    assert {"054", "055", "057"} <= perceptions
    assert {"108", "109", "110", "111", "114", "115"} <= deductions


def test_web_and_shared_nomina_xsd_are_identical():
    """The browser asset must not drift from the shared SAT resource."""
    assert WEB_XSD.read_bytes() == SHARED_XSD.read_bytes()


def test_registry_records_revision_e_and_partial_normalized_coverage():
    """Freshness and implementation completeness are distinct registry facts."""
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    dataset = next(item for item in registry["datasets"] if item["id"] == "sat.nomina_1_2")

    assert dataset["version"] == "1.2"
    assert dataset["revision"] == "E"
    assert dataset["effective_from"] == "2026-01-01"
    assert dataset["freshness"]["upstream_checked_at"] == "2026-08-25"
    assert dataset["implementation"]["status"] == "partial"
    assert dataset["implementation"]["normalized_catalogs"] == 7
    assert dataset["implementation"]["xsd_catalog_types"] == 13
    assert set(dataset["implementation"]["missing_normalized_catalogs"]) == {
        "c_OrigenRecurso",
        "c_TipoDeduccion",
        "c_TipoHoras",
        "c_TipoIncapacidad",
        "c_TipoOtroPago",
        "c_TipoPercepcion",
    }
