"""Registry expectations for the audited SAT Carta Porte 3.1 dataset."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = REPO_ROOT / "packages" / "shared-data" / "catalog-registry.json"


def test_carta_porte_is_current_but_partial_and_not_a_full_embedded_mirror():
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    dataset = next(
        item for item in registry["datasets"] if item["id"] == "sat.carta_porte"
    )

    assert dataset["version"] == "3.1"
    assert dataset["distribution"] == "mixed"
    assert dataset["freshness"]["max_age_days"] == 31
    assert dataset["freshness"]["upstream_checked_at"] == "2026-08-26"

    implementation = dataset["implementation"]
    assert implementation["status"] == "partial"
    assert implementation["official_catalogs"] == 32
    assert implementation["embedded_convenience_json_files"] == 7
    assert implementation["canonical_full_dataset"] is False
    assert implementation["planned_full_distribution"] == "release"

    roles = {source["role"] for source in dataset["upstream"]}
    assert {"authoritative_portal", "authoritative_catalog", "technical_mirror"} <= roles
