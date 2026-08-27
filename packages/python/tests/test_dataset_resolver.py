"""Tests for dataset-aware release resolution and caching."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path

import pytest

from catalogmx.data.resolver import DatasetResolver

CHANNEL = "data-banxico-reference-1-latest"
ARTIFACT = "banxico_reference.tar.gz"
MANIFEST = "banxico_reference.manifest.json"


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def make_tar(path: str, payload: bytes) -> bytes:
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w") as archive:
        info = tarfile.TarInfo(path)
        info.size = len(payload)
        info.mtime = 0
        archive.addfile(info, io.BytesIO(payload))
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as compressed:
        compressed.write(tar_buffer.getvalue())
    return output.getvalue()


def release_fixture(
    *, member_path: str = "banxico/banks.json", member_payload: bytes = b'[{"code":"002"}]\n'
) -> tuple[dict, bytes, bytes]:
    artifact = make_tar(member_path, member_payload)
    manifest = {
        "schema_version": 1,
        "dataset_id": "banxico.reference",
        "dataset_version": "1",
        "dataset": {
            "file": ARTIFACT,
            "file_sha256": sha256(artifact),
            "content_sha256": "a" * 64,
            "format": "tar.gz",
            "mount_path": "banxico",
            "files": [
                {
                    "path": member_path,
                    "bytes": len(member_payload),
                    "sha256": sha256(member_payload),
                }
            ],
        },
    }
    return manifest, json.dumps(manifest).encode(), artifact


def contract() -> dict:
    return {
        "schema_version": 1,
        "profiles": {
            "core": {"datasets": []},
            "payglobal": {"datasets": ["banxico.reference"]},
        },
        "datasets": {
            "banxico.reference": {
                "source_subpath": "banxico",
                "freshness": {"mode": "interval", "max_age_days": 31},
                "artifact": {
                    "version": "1",
                    "channel": CHANNEL,
                    "file": ARTIFACT,
                    "manifest": MANIFEST,
                    "format": "tar.gz",
                    "mount_path": "banxico",
                },
            }
        },
    }


def mapped_downloader(manifest_payload: bytes, artifact_payload: bytes):
    calls: list[str] = []

    def download(url: str) -> bytes:
        calls.append(url)
        if url.endswith("/" + MANIFEST):
            return manifest_payload
        if url.endswith("/" + ARTIFACT):
            return artifact_payload
        raise AssertionError(f"unexpected URL: {url}")

    return download, calls


def test_configured_shared_data_is_strict_and_wins(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    shared = tmp_path / "shared"
    (shared / "banxico").mkdir(parents=True)
    (shared / "banxico" / "banks.json").write_text("[]\n", encoding="utf-8")
    monkeypatch.setenv("CATALOGMX_SHARED_DATA", str(shared))

    def no_network(url: str) -> bytes:
        raise AssertionError(f"network should not be used: {url}")

    resolver = DatasetResolver(
        cache_dir=tmp_path / "cache",
        contract=contract(),
        downloader=no_network,
    )
    assert resolver.get_dataset_path("banxico.reference", "banks.json") == (
        shared / "banxico" / "banks.json"
    )

    monkeypatch.setenv("CATALOGMX_SHARED_DATA", str(tmp_path / "missing"))
    with pytest.raises(FileNotFoundError, match="CATALOGMX_SHARED_DATA"):
        resolver.resolve_dataset_root("banxico.reference")


def test_fetch_missing_verifies_release_and_reuses_content_addressed_cache(tmp_path: Path):
    _, manifest_payload, artifact_payload = release_fixture()
    download, calls = mapped_downloader(manifest_payload, artifact_payload)
    resolver = DatasetResolver(
        cache_dir=tmp_path / "cache",
        contract=contract(),
        downloader=download,
        release_base_url="https://example.invalid/releases/download",
    )

    root = resolver.fetch_dataset("banxico.reference")
    assert json.loads((root / "banks.json").read_text())[0]["code"] == "002"
    assert len(calls) == 2
    assert resolver.verify_cached_dataset("banxico.reference") is True

    def fail_network(url: str) -> bytes:
        raise AssertionError(f"cached lookup should not fetch: {url}")

    cached = DatasetResolver(
        cache_dir=tmp_path / "cache",
        contract=contract(),
        downloader=fail_network,
        release_base_url="https://example.invalid/releases/download",
    )
    assert cached.resolve_dataset_root("banxico.reference") == root


def test_checksum_failure_does_not_publish_current_cache(tmp_path: Path):
    _, manifest_payload, artifact_payload = release_fixture()
    broken = artifact_payload + b"corrupt"
    download, _ = mapped_downloader(manifest_payload, broken)
    resolver = DatasetResolver(
        cache_dir=tmp_path / "cache",
        contract=contract(),
        downloader=download,
    )

    with pytest.raises(RuntimeError, match="artifact checksum mismatch"):
        resolver.fetch_dataset("banxico.reference")
    assert resolver.cache_status("banxico.reference")["cached"] is False


def test_offline_missing_dataset_fails_without_network(tmp_path: Path):
    def no_network(url: str) -> bytes:
        raise AssertionError(f"offline resolver attempted network: {url}")

    resolver = DatasetResolver(
        cache_dir=tmp_path / "cache",
        contract=contract(),
        downloader=no_network,
        mode="offline",
    )
    with pytest.raises(FileNotFoundError, match="offline mode"):
        resolver.resolve_dataset_root("banxico.reference")


def test_archive_rejects_unsafe_member_path(tmp_path: Path):
    _, manifest_payload, artifact_payload = release_fixture(member_path="../escape.json")
    download, _ = mapped_downloader(manifest_payload, artifact_payload)
    resolver = DatasetResolver(
        cache_dir=tmp_path / "cache",
        contract=contract(),
        downloader=download,
    )
    with pytest.raises(RuntimeError, match="unsafe dataset path"):
        resolver.fetch_dataset("banxico.reference")
    assert not (tmp_path / "escape.json").exists()


def test_verify_detects_cached_file_tampering(tmp_path: Path):
    _, manifest_payload, artifact_payload = release_fixture()
    download, _ = mapped_downloader(manifest_payload, artifact_payload)
    resolver = DatasetResolver(
        cache_dir=tmp_path / "cache",
        contract=contract(),
        downloader=download,
    )
    root = resolver.fetch_dataset("banxico.reference")
    assert resolver.verify_cached_dataset("banxico.reference") is True
    (root / "banks.json").write_text("[]\n", encoding="utf-8")
    assert resolver.verify_cached_dataset("banxico.reference") is False


def test_profile_materialization_creates_shared_root_and_manifest(tmp_path: Path):
    _, manifest_payload, artifact_payload = release_fixture()
    download, _ = mapped_downloader(manifest_payload, artifact_payload)
    resolver = DatasetResolver(
        cache_dir=tmp_path / "cache",
        contract=contract(),
        downloader=download,
    )
    destination = resolver.materialize_profile("payglobal", tmp_path / "shared")
    assert (destination / "banxico" / "banks.json").exists()
    assert (
        destination / ".catalogmx" / "manifests" / "banxico.reference.json"
    ).exists()
    assert resolver.verify_profile("payglobal") == {"banxico.reference": True}
    assert resolver.dataset_ids_for_profile("core") == []
