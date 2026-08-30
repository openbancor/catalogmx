"""Registry expectations for SEPOMEX postal-code distribution."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = REPO_ROOT / "packages" / "shared-data" / "catalog-registry.json"


def test_sepomex_uses_resolver_ready_release_with_legacy_embedded_snapshot():
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    dataset = next(
        item for item in registry["datasets"] if item["id"] == "sepomex.codigos_postales"
    )

    assert dataset["distribution"] == "mixed"
    assert dataset["freshness"]["max_age_days"] == 31
    assert dataset["freshness"]["upstream_checked_at"] == "2026-08-26"
    assert dataset["freshness"]["source_reported_updated_at"] == "2026-08-25"

    implementation = dataset["implementation"]
    assert implementation["status"] == "resolver_ready"
    assert implementation["canonical_distribution"] == "release"
    assert implementation["release_artifact"] == "sepomex_codigos_postales.sqlite3"
    assert implementation["consumer_migration_required_before_removal"] is True
    assert implementation["legacy_full_json_bytes"] > 40_000_000
    assert implementation["legacy_sqlite_bytes"] > 10_000_000

    artifact = dataset["artifact"]
    assert artifact == {
        "version": "1",
        "channel": "data-sepomex-codigos-postales-1-latest",
        "file": "sepomex_codigos_postales.sqlite3",
        "manifest": "sepomex_codigos_postales.manifest.json",
        "format": "file",
        "mount_path": "sepomex",
        "discovery": "release-pointer",
    }

    roles = {source["role"] for source in dataset["upstream"]}
    assert {"authoritative_portal", "authoritative_export"} <= roles

    rights = dataset["rights"]
    assert rights["source_terms_checked_at"] == "2026-08-26"
    assert rights["project_relicenses_source_data"] is False
