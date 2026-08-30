"""Regression coverage for Banxico dynamic data through DatasetResolver."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError

import pytest

from catalogmx.data.resolver import DatasetResolver

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY_PATH = REPO_ROOT / "packages" / "shared-data" / "catalog-registry.json"
CONTRACT_PATH = REPO_ROOT / "packages" / "python" / "catalogmx" / "data" / "dataset_contract.json"


def test_registry_exposes_dynamic_profile_and_verified_release_contract():
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    assert registry["profiles"]["banxico-dynamic"]["datasets"] == ["banxico.sie_dynamic"]
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
    assert dynamic["bootstrap"] == {
        "kind": "file",
        "package_path": "data/mexico_dynamic.sqlite3",
        "role": "offline-fallback",
    }
    assert dynamic["implementation"]["bootstrap_is_canonical"] is False

    assert contract["profiles"]["banxico-dynamic"]["datasets"] == ["banxico.sie_dynamic"]
    assert contract["datasets"]["banxico.sie_dynamic"]["artifact"] == dynamic["artifact"]
    assert contract["datasets"]["banxico.sie_dynamic"]["bootstrap"] == dynamic["bootstrap"]


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
                "bootstrap": {
                    "kind": "file",
                    "package_path": "data/mexico_dynamic.sqlite3",
                    "role": "offline-fallback",
                },
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
        f"{release_base}/{release_tag}/mexico_dynamic.manifest.json": json.dumps(manifest).encode(),
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

    root = resolver.resolve_dataset_root("banxico.sie_dynamic")
    assert (root / "mexico_dynamic.sqlite3").read_bytes() == database
    assert str(root).startswith(str(tmp_path / "cache"))
    assert resolver.verify_profile("banxico-dynamic") == {"banxico.sie_dynamic": True}
    assert resolver.cache_status("banxico.sie_dynamic")["release_tag"] == release_tag


def test_resolver_uses_bootstrap_offline_only_after_cache_and_shared_sources(
    tmp_path: Path, monkeypatch
):
    monkeypatch.delenv("CATALOGMX_SHARED_DATA", raising=False)
    resolver = DatasetResolver(cache_dir=tmp_path / "empty-cache", mode="offline")
    root = resolver.resolve_dataset_root("banxico.sie_dynamic")
    database = root / "mexico_dynamic.sqlite3"
    assert database.is_file()
    assert root == Path(__file__).resolve().parents[1] / "catalogmx" / "data"


def test_fetch_failure_can_fall_back_to_bootstrap_without_marking_it_cached(
    tmp_path: Path, monkeypatch
):
    monkeypatch.delenv("CATALOGMX_SHARED_DATA", raising=False)
    resolver = DatasetResolver(
        cache_dir=tmp_path / "empty-cache",
        mode="fetch-missing",
        downloader=lambda _url: (_ for _ in ()).throw(OSError("offline")),
    )
    root = resolver.resolve_dataset_root("banxico.sie_dynamic")
    assert (root / "mexico_dynamic.sqlite3").is_file()
    assert resolver.cache_status("banxico.sie_dynamic")["cached"] is False


def test_invalid_release_metadata_never_falls_back_to_bootstrap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("CATALOGMX_SHARED_DATA", raising=False)
    resolver = DatasetResolver(
        cache_dir=tmp_path / "empty-cache",
        mode="fetch-missing",
        downloader=lambda _url: b"{not-valid-json",
    )

    with pytest.raises(RuntimeError, match="invalid dataset channel metadata"):
        resolver.resolve_dataset_root("banxico.sie_dynamic")

    assert resolver.cache_status("banxico.sie_dynamic")["cached"] is False


def test_http_release_failure_never_falls_back_to_bootstrap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("CATALOGMX_SHARED_DATA", raising=False)

    def missing(url: str) -> bytes:
        raise HTTPError(url, 404, "Not Found", hdrs=None, fp=None)

    resolver = DatasetResolver(
        cache_dir=tmp_path / "empty-cache",
        mode="fetch-missing",
        downloader=missing,
    )

    with pytest.raises(HTTPError) as exc_info:
        resolver.resolve_dataset_root("banxico.sie_dynamic")
    assert exc_info.value.code == 404
    assert resolver.cache_status("banxico.sie_dynamic")["cached"] is False
