"""Registry expectations for the audited SAT Carta Porte 3.1 dataset."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = REPO_ROOT / "packages" / "shared-data" / "catalog-registry.json"


def test_carta_porte_has_complete_release_and_legacy_embedded_projection():
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    dataset = next(
        item for item in registry["datasets"] if item["id"] == "sat.carta_porte"
    )

    assert dataset["version"] == "3.1"
    assert dataset["distribution"] == "mixed"
    assert dataset["freshness"]["max_age_days"] == 31
    assert dataset["freshness"]["upstream_checked_at"] == "2026-08-26"

    implementation = dataset["implementation"]
    assert implementation["status"] == "resolver_ready"
    assert implementation["official_catalogs"] == 32
    assert implementation["embedded_convenience_json_files"] == 7
    assert implementation["canonical_distribution"] == "release"
    assert implementation["release_artifact"] == "sat_carta_porte_31.sqlite3"
    assert implementation["legacy_view_path"] == "packages/shared-data/sat/carta_porte_3"
    assert implementation["consumer_migration_required_before_removal"] is True

    artifact = dataset["artifact"]
    assert artifact == {
        "version": "3.1",
        "channel": "data-sat-carta-porte-3-1-latest",
        "file": "sat_carta_porte_31.sqlite3",
        "manifest": "sat_carta_porte_31.manifest.json",
        "format": "file",
        "mount_path": "sat/carta_porte_3.1",
        "discovery": "release-pointer",
    }

    roles = {source["role"] for source in dataset["upstream"]}
    assert {"authoritative_portal", "authoritative_catalog", "technical_mirror"} <= roles
