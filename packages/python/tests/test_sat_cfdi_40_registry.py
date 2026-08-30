"""Registry expectations for the canonical SAT CFDI 4.0 dataset."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = REPO_ROOT / "packages" / "shared-data" / "catalog-registry.json"


def test_cfdi_40_uses_resolver_ready_release_with_legacy_embedded_views():
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    dataset = next(
        item for item in registry["datasets"] if item["id"] == "sat.cfdi_4"
    )

    assert dataset["version"] == "4.0"
    assert dataset["effective_from"] == "2022-01-01"
    assert dataset["mandatory_from"] == "2023-04-01"
    assert dataset["distribution"] == "mixed"
    assert dataset["freshness"]["max_age_days"] == 31
    assert dataset["freshness"]["upstream_checked_at"] == "2026-08-26"

    implementation = dataset["implementation"]
    assert implementation["status"] == "resolver_ready"
    assert implementation["official_catalogs"] == 25
    assert implementation["embedded_convenience_json_files"] == 14
    assert implementation["canonical_distribution"] == "release"
    assert implementation["release_artifact"] == "sat_cfdi_40.sqlite3"
    assert implementation["consumer_migration_required_before_removal"] is True

    artifact = dataset["artifact"]
    assert artifact == {
        "version": "4.0",
        "channel": "data-sat-cfdi-4-4-0-latest",
        "file": "sat_cfdi_40.sqlite3",
        "manifest": "sat_cfdi_40.manifest.json",
        "format": "file",
        "mount_path": "sat/cfdi_4.0",
        "discovery": "release-pointer",
    }

    roles = {source["role"] for source in dataset["upstream"]}
    assert {"authoritative_portal", "authoritative_catalog", "technical_mirror"} <= roles
