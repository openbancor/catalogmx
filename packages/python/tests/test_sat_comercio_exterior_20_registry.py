"""Registry expectations for SAT Comercio Exterior 2.0."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = REPO_ROOT / "packages" / "shared-data" / "catalog-registry.json"


def test_comercio_exterior_20_separates_owned_and_shared_catalogs():
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    dataset = next(
        item
        for item in registry["datasets"]
        if item["id"] == "sat.comercio_exterior"
    )

    assert dataset["version"] == "2.0"
    assert dataset["effective_from"] == "2024-01-18"
    assert dataset["distribution"] == "mixed"
    assert dataset["freshness"]["max_age_days"] == 31
    assert dataset["freshness"]["upstream_checked_at"] == "2026-08-26"

    implementation = dataset["implementation"]
    assert implementation["status"] == "resolver_ready"
    assert implementation["official_catalogs_total"] == 14
    assert implementation["canonical_owned_catalogs"] == 10
    assert implementation["shared_cfdi_catalogs"] == 4
    assert implementation["shared_cfdi_dependency"] == "sat.cfdi_4"
    assert implementation["shared_cfdi_tables"] == [
        "cfdi_40_codigos_postales",
        "cfdi_40_monedas",
        "cfdi_40_paises",
        "cfdi_40_regimenes_fiscales",
    ]
    assert implementation["embedded_convenience_json_files"] == 8
    assert implementation["canonical_distribution"] == "release"
    assert implementation["release_artifact"] == "sat_comercio_exterior_20.sqlite3"
    assert implementation["consumer_migration_required_before_removal"] is True

    artifact = dataset["artifact"]
    assert artifact == {
        "version": "2.0",
        "channel": "data-sat-comercio-exterior-2-0-latest",
        "file": "sat_comercio_exterior_20.sqlite3",
        "manifest": "sat_comercio_exterior_20.manifest.json",
        "format": "file",
        "mount_path": "sat/comercio_exterior_2.0",
        "discovery": "release-pointer",
    }

    roles = {source["role"] for source in dataset["upstream"]}
    assert {
        "authoritative_portal",
        "authoritative_technical_page",
        "technical_mirror",
    } <= roles
