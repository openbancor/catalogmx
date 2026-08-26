"""Registry expectations for INEGI geographic and classification datasets."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = REPO_ROOT / "packages" / "shared-data" / "catalog-registry.json"


def load_datasets() -> dict[str, dict]:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return {dataset["id"]: dataset for dataset in registry["datasets"]}


def test_ageeml_is_monthly_release_data_with_legacy_embedded_views():
    dataset = load_datasets()["inegi.ageeml"]

    assert dataset["distribution"] == "mixed"
    assert dataset["freshness"]["max_age_days"] == 31
    assert dataset["freshness"]["upstream_checked_at"] == "2026-08-26"
    assert dataset["freshness"]["latest_indexed_cut"] == "2026/JUN"

    implementation = dataset["implementation"]
    assert implementation["status"] == "legacy_embedded_views"
    assert implementation["canonical_distribution"] == "release"
    assert implementation["planned_release_artifact"] == "inegi_ageeml.sqlite3"
    assert implementation["synthetic_fallback_forbidden"] is True

    assert all("/scian" not in path for path in dataset["local_paths"])
    roles = {source["role"] for source in dataset["upstream"]}
    assert {"authoritative_portal", "authoritative_predefined_catalog"} <= roles


def test_scian_is_versioned_independently_and_event_driven():
    dataset = load_datasets()["inegi.scian_2023"]

    assert dataset["version"] == "2023"
    assert dataset["freshness"]["mode"] == "event"
    assert dataset["local_paths"] == ["packages/shared-data/inegi/scian"]
    assert dataset["distribution"] == "embedded"
