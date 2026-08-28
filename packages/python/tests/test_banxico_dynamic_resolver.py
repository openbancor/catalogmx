"""Regression coverage for Banxico dynamic data through DatasetResolver."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from catalogmx.data.resolver import DatasetResolver

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = REPO_ROOT / "packages" / "shared-data" / "catalog-registry.json"
CONTRACT_PATH = REPO_ROOT / "packages" / "python" / "catalogmx" / "data" / "dataset_contract.json"


def test_registry_exposes_dynamic_profile_and_verified_release_contract():
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    assert registry["profiles"]["banxico-dynamic"]["datasets"] == [
        "banxico.sie_dynamic"
    ]
    dynamic = next(
        dataset for dataset in registry["datasets"] if dataset["id"] == "banxico.sie_dynamic"
    )
    assert dynamic["distribution"] == "release"
    assert dynamic["artifact"] == {
        "version": "1",
        "channel": "data-banxico-sie-dynamic-1-latest",
        "file": "mexico_dynamic.sqlite3",
        "manifest": "mexico_dynamic.manifest.json",
        "format": "file",
        "mount_path": "dynamic",
        "discovery": "release-pointer",
    }

    assert contract["profiles"]["banxico-dynamic"]["datasets"] == [
        "banxico.sie_dynamic"
    ]
    assert contract["datasets"]["banxico.sie_dynamic"]["artifact"] == dynamic["artifact"]


def test_resolver_fetches_dynamic_file_from_verified_pointer(tmp_path: Path):
    database = b"SQLite fixture bytes"
    file_sha = hashlib.sha256(database).hexdigest()
    content_sha = hashlib.sha256(b"semantic dynamic fixture").hexdigest()
    release_tag = f"data-banxico-sie-dynamic-1-{content_sha}"
    channel = "data-banxico-sie-dynamic-1-latest"

    contract = {
        "schema_version": 1,
        "profiles": {
            "banxico-dynamic": {"datasets": ["banxico.sie_dynamic"]},
        },
        "datasets": {
            "banxico.sie_dynamic": {
                "artifact": {
                    "version": "1",
                    "channel": channel,
                    "discovery": "release-pointer",
                    "file": "mexico_dynamic.sqlite3",
                    "manifest": "mexico_dynamic.manifest.json",
                    "format": "file",
                    "mount_path": "dynamic",
                },
                "freshness": {"mode": "pipeline", "max_age_days": 2},
            }
        },
    }
    manifest = {
        "schema_version": 1,
        "dataset_id": "banxico.sie_dynamic",
        "dataset_version": "1",
        "data_version": "2026-08-27",
        "dataset": {
            "file": "mexico_dynamic.sqlite3",
            "format": "file",
            "mount_path": "dynamic",
            "file_sha256": file_sha,
            "content_sha256": content_sha,
        },
    }
    pointer = {
        "schema_version": 1,
        "dataset_id": "banxico.sie_dynamic",
        "dataset_version": "1",
        "release_tag": release_tag,
        "content_sha256": content_sha,
        "artifact": "mexico_dynamic.sqlite3",
        "manifest": "mexico_dynamic.manifest.json",
    }

    release_base = "https://example.invalid/releases"
    metadata_base = "https://example.invalid/releases/tags"
    responses = {
        f"{metadata_base}/{channel}": json.dumps(
            {"tag_name": channel, "body": json.dumps(pointer)}
        ).encode(),
        f"{release_base}/{release_tag}/mexico_dynamic.manifest.json": json.dumps(
            manifest
        ).encode(),
        f"{release_base}/{release_tag}/mexico_dynamic.sqlite3": database,
    }

    resolver = DatasetResolver(
        cache_dir=tmp_path / "cache",
        mode="fetch-missing",
        contract=contract,
        downloader=lambda url: responses[url],
        release_base_url=release_base,
        release_metadata_base_url=metadata_base,
    )

    fetched = resolver.fetch_profile("banxico-dynamic")
    root = fetched["banxico.sie_dynamic"]
    assert (root / "mexico_dynamic.sqlite3").read_bytes() == database
    assert resolver.verify_profile("banxico-dynamic") == {"banxico.sie_dynamic": True}
    assert resolver.cache_status("banxico.sie_dynamic")["release_tag"] == release_tag
