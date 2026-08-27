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
    *,
    member_path: str = "banxico/banks.json",
    member_payload: bytes = b'[{"code":"002"}]\n',
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


def test_manifest_rejects_non_hex_content_hash_before_cache_path_use(tmp_path: Path):
    manifest, _, artifact_payload = release_fixture()
    manifest["dataset"]["content_sha256"] = "../" * 21 + "x"
    download, _ = mapped_downloader(json.dumps(manifest).encode(), artifact_payload)
    resolver = DatasetResolver(
        cache_dir=tmp_path / "cache",
        contract=contract(),
        downloader=download,
    )

    with pytest.raises(RuntimeError, match="semantic SHA-256"):
        resolver.fetch_dataset("banxico.reference")
    assert not (tmp_path / "x").exists()


def test_offline_missing_dataset_fails_without_network(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    def no_network(url: str) -> bytes:
        raise AssertionError(f"offline resolver attempted network: {url}")

    resolver = DatasetResolver(
        cache_dir=tmp_path / "cache",
        contract=contract(),
        downloader=no_network,
        mode="offline",
    )
    monkeypatch.setattr(resolver, "_package_root", lambda dataset: None)
    monkeypatch.setattr(resolver, "_repo_root", lambda dataset: None)

    with pytest.raises(FileNotFoundError, match="offline mode"):
        resolver.resolve_dataset_root("banxico.reference")


@pytest.mark.parametrize(
    "member_path",
    [
        "../escape.json",
        r"..\escape.json",
        r"C:\escape.json",
        r"banxico\..\escape.json",
    ],
)
def test_archive_rejects_unsafe_member_path(tmp_path: Path, member_path: str):
    _, manifest_payload, artifact_payload = release_fixture(member_path=member_path)
    download, _ = mapped_downloader(manifest_payload, artifact_payload)
    resolver = DatasetResolver(
        cache_dir=tmp_path / "cache",
        contract=contract(),
        downloader=download,
    )
    with pytest.raises(RuntimeError, match="unsafe dataset path"):
        resolver.fetch_dataset("banxico.reference")
    assert not (tmp_path / "escape.json").exists()


def test_archive_rejects_duplicate_manifest_members_and_size_drift(tmp_path: Path):
    manifest, _, artifact_payload = release_fixture()
    manifest["dataset"]["files"].append(dict(manifest["dataset"]["files"][0]))
    download, _ = mapped_downloader(json.dumps(manifest).encode(), artifact_payload)
    resolver = DatasetResolver(
        cache_dir=tmp_path / "cache-a",
        contract=contract(),
        downloader=download,
    )
    with pytest.raises(RuntimeError, match="duplicate file"):
        resolver.fetch_dataset("banxico.reference")

    manifest, _, artifact_payload = release_fixture()
    manifest["dataset"]["files"][0]["bytes"] += 1
    download, _ = mapped_downloader(json.dumps(manifest).encode(), artifact_payload)
    resolver = DatasetResolver(
        cache_dir=tmp_path / "cache-b",
        contract=contract(),
        downloader=download,
    )
    with pytest.raises(RuntimeError, match="size mismatch"):
        resolver.fetch_dataset("banxico.reference")


def test_dataset_path_rejects_caller_traversal(tmp_path: Path):
    resolver = DatasetResolver(cache_dir=tmp_path / "cache", contract=contract())
    with pytest.raises(RuntimeError, match="unsafe dataset path"):
        resolver.get_dataset_path("banxico.reference", "..", "catalog-registry.json")


def test_verify_detects_cached_file_and_manifest_tampering(tmp_path: Path):
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

    root = resolver.fetch_dataset("banxico.reference")
    object_dir = root.parent
    manifest_path = object_dir / ".manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["dataset"]["files"][0].pop("sha256")
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
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
