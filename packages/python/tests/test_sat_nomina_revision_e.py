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


def test_registry_records_revision_e_canonical_distribution_and_api_gap():
    """Canonical data completeness and language API completeness are distinct."""
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    dataset = next(item for item in registry["datasets"] if item["id"] == "sat.nomina_1_2")

    assert dataset["version"] == "1.2"
    assert dataset["revision"] == "E"
    assert dataset["effective_from"] == "2026-01-01"
    assert dataset["distribution"] == "mixed"
    assert dataset["freshness"]["max_age_days"] == 31
    assert dataset["freshness"]["upstream_checked_at"] == "2026-08-26"

    implementation = dataset["implementation"]
    assert implementation["status"] == "partial"
    assert implementation["xsd_catalog_types"] == 13
    assert implementation["canonical_catalog_tables"] == 13
    assert implementation["canonical_distribution"] == "release"
    assert implementation["release_artifact"] == "sat_nomina_12.sqlite3"
    assert implementation["excluded_auxiliary_tables"] == ["nomina_estados"]
    assert implementation["embedded_convenience_json_files"] == 7
    assert implementation["normalized_catalogs"] == 7
    assert implementation["consumer_migration_required_before_removal"] is True
    assert set(implementation["missing_normalized_catalogs"]) == {
        "c_OrigenRecurso",
        "c_TipoDeduccion",
        "c_TipoHoras",
        "c_TipoIncapacidad",
        "c_TipoOtroPago",
        "c_TipoPercepcion",
    }

    roles = {source["role"] for source in dataset["upstream"]}
    assert {
        "authoritative_notice",
        "authoritative_catalog",
        "authoritative_resource",
        "technical_mirror",
    } <= roles
