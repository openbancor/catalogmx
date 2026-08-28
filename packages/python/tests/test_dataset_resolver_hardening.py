"""Hardening coverage for dataset discovery and content-addressed cache publication."""

from __future__ import annotations

import errno
import gzip
import hashlib
import io
import json
import os
import shutil
import sys
import tarfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from catalogmx.data import resolver as resolver_module
from catalogmx.data.resolver import DatasetResolver

CHANNEL = "data-banxico-reference-1-latest"
IMMUTABLE = "data-banxico-reference-1-" + "a" * 64
ARTIFACT = "banxico_reference.tar.gz"
MANIFEST = "banxico_reference.manifest.json"


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def make_tar(payload: bytes) -> bytes:
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w") as archive:
        info = tarfile.TarInfo("banxico/banks.json")
        info.size = len(payload)
        info.mtime = 0
        archive.addfile(info, io.BytesIO(payload))
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as compressed:
        compressed.write(tar_buffer.getvalue())
    return output.getvalue()


def release_fixture() -> tuple[dict, bytes, bytes]:
    member_payload = b'[{"code":"002"}]\n'
    artifact = make_tar(member_payload)
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
                    "path": "banxico/banks.json",
                    "bytes": len(member_payload),
                    "sha256": sha256(member_payload),
                }
            ],
        },
    }
    return manifest, json.dumps(manifest).encode(), artifact


def contract(*, discovery: str = "direct") -> dict:
    return {
        "schema_version": 1,
        "profiles": {"payglobal": {"datasets": ["banxico.reference"]}},
        "datasets": {
            "banxico.reference": {
                "source_subpath": "banxico",
                "freshness": {"mode": "interval", "max_age_days": 31},
                "artifact": {
                    "version": "1",
                    "channel": CHANNEL,
                    "discovery": discovery,
                    "file": ARTIFACT,
                    "manifest": MANIFEST,
                    "format": "tar.gz",
                    "mount_path": "banxico",
                },
            }
        },
    }


def direct_downloader(manifest_payload: bytes, artifact_payload: bytes):
    def download(url: str) -> bytes:
        if url.endswith("/" + MANIFEST):
            return manifest_payload
        if url.endswith("/" + ARTIFACT):
            return artifact_payload
        raise AssertionError(f"unexpected URL: {url}")

    return download


def pointer_downloader(
    manifest_payload: bytes,
    artifact_payload: bytes,
    *,
    pointer_sha: str = "a" * 64,
):
    pointer = {
        "schema_version": 1,
        "dataset_id": "banxico.reference",
        "dataset_version": "1",
        "release_tag": IMMUTABLE,
        "content_sha256": pointer_sha,
        "artifact": ARTIFACT,
        "manifest": MANIFEST,
    }
    metadata = {
        "tag_name": CHANNEL,
        "body": json.dumps(pointer, separators=(",", ":")),
    }
    calls: list[str] = []

    def download(url: str) -> bytes:
        calls.append(url)
        if url.endswith("/" + CHANNEL):
            return json.dumps(metadata).encode()
        if url.endswith(f"/{IMMUTABLE}/{MANIFEST}"):
            return manifest_payload
        if url.endswith(f"/{IMMUTABLE}/{ARTIFACT}"):
            return artifact_payload
        raise AssertionError(f"unexpected URL: {url}")

    return download, calls


def test_release_pointer_resolves_only_immutable_assets(tmp_path: Path):
    _, manifest_payload, artifact_payload = release_fixture()
    download, calls = pointer_downloader(manifest_payload, artifact_payload)
    resolver = DatasetResolver(
        cache_dir=tmp_path / "cache",
        contract=contract(discovery="release-pointer"),
        downloader=download,
        release_base_url="https://example.invalid/releases/download",
        release_metadata_base_url="https://example.invalid/releases/tags",
    )

    root = resolver.fetch_dataset("banxico.reference")

    assert json.loads((root / "banks.json").read_text())[0]["code"] == "002"
    assert calls == [
        f"https://example.invalid/releases/tags/{CHANNEL}",
        f"https://example.invalid/releases/download/{IMMUTABLE}/{MANIFEST}",
        f"https://example.invalid/releases/download/{IMMUTABLE}/{ARTIFACT}",
        f"https://example.invalid/releases/tags/{CHANNEL}",
        f"https://example.invalid/releases/download/{IMMUTABLE}/{MANIFEST}",
    ]
    assert resolver.cache_status("banxico.reference")["release_tag"] == IMMUTABLE


def test_release_pointer_rejects_manifest_content_mismatch(tmp_path: Path):
    _, manifest_payload, artifact_payload = release_fixture()
    download, _ = pointer_downloader(
        manifest_payload,
        artifact_payload,
        pointer_sha="b" * 64,
    )
    resolver = DatasetResolver(
        cache_dir=tmp_path / "cache",
        contract=contract(discovery="release-pointer"),
        downloader=download,
    )

    with pytest.raises(RuntimeError, match="pointer content SHA-256 mismatch"):
        resolver.fetch_dataset("banxico.reference")


def test_explicit_fetch_repairs_corrupt_content_addressed_object(tmp_path: Path):
    _, manifest_payload, artifact_payload = release_fixture()
    resolver = DatasetResolver(
        cache_dir=tmp_path / "cache",
        contract=contract(),
        downloader=direct_downloader(manifest_payload, artifact_payload),
    )

    root = resolver.fetch_dataset("banxico.reference")
    (root / "banks.json").write_text("[]\n", encoding="utf-8")
    assert resolver.verify_cached_dataset("banxico.reference") is False

    repaired = resolver.fetch_dataset("banxico.reference")

    assert repaired == root
    assert json.loads((root / "banks.json").read_text())[0]["code"] == "002"
    assert resolver.verify_cached_dataset("banxico.reference") is True


def test_fetch_missing_repairs_corrupt_cache_before_returning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    _, manifest_payload, artifact_payload = release_fixture()
    resolver = DatasetResolver(
        cache_dir=tmp_path / "cache",
        contract=contract(),
        downloader=direct_downloader(manifest_payload, artifact_payload),
    )
    root = resolver.fetch_dataset("banxico.reference")
    (root / "banks.json").write_text("[]\n", encoding="utf-8")
    monkeypatch.setattr(resolver, "_package_root", lambda dataset: None)
    monkeypatch.setattr(resolver, "_repo_root", lambda dataset: None)

    repaired = resolver.resolve_dataset_root("banxico.reference")

    assert repaired == root
    assert json.loads((root / "banks.json").read_text())[0]["code"] == "002"
    assert resolver.verify_cached_dataset("banxico.reference") is True


def test_offline_resolution_fails_closed_on_corrupt_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    _, manifest_payload, artifact_payload = release_fixture()
    cache_dir = tmp_path / "cache"
    online = DatasetResolver(
        cache_dir=cache_dir,
        contract=contract(),
        downloader=direct_downloader(manifest_payload, artifact_payload),
    )
    root = online.fetch_dataset("banxico.reference")
    (root / "banks.json").write_text("[]\n", encoding="utf-8")

    calls = 0

    def forbidden_download(url: str) -> bytes:
        nonlocal calls
        calls += 1
        raise AssertionError(f"offline resolver attempted network access: {url}")

    offline = DatasetResolver(
        cache_dir=cache_dir,
        mode="offline",
        contract=contract(),
        downloader=forbidden_download,
    )
    monkeypatch.setattr(offline, "_package_root", lambda dataset: None)
    monkeypatch.setattr(offline, "_repo_root", lambda dataset: None)

    with pytest.raises(FileNotFoundError, match="offline mode"):
        offline.resolve_dataset_root("banxico.reference")
    assert calls == 0


def test_offline_fetch_profile_rejects_without_downloading(tmp_path: Path):
    calls = 0

    def forbidden_download(url: str) -> bytes:
        nonlocal calls
        calls += 1
        raise AssertionError(f"offline resolver attempted network access: {url}")

    resolver = DatasetResolver(
        cache_dir=tmp_path / "cache",
        mode="offline",
        contract=contract(),
        downloader=forbidden_download,
    )

    with pytest.raises(RuntimeError, match="offline"):
        resolver.fetch_profile("payglobal")
    assert calls == 0


def _prepared_stage(tmp_path: Path):
    manifest, manifest_payload, artifact_payload = release_fixture()
    resolver = DatasetResolver(
        cache_dir=tmp_path / "cache",
        contract=contract(),
        downloader=direct_downloader(manifest_payload, artifact_payload),
    )
    dataset = resolver._dataset("banxico.reference")
    manifest_dataset, content_sha = resolver._validate_manifest(
        "banxico.reference", dataset, manifest
    )
    dataset_cache = resolver._dataset_cache_dir("banxico.reference")
    dataset_cache.mkdir(parents=True, exist_ok=True)
    stage = resolver._stage_object(
        dataset_cache,
        dataset,
        manifest_payload,
        manifest,
        manifest_dataset,
        artifact_payload,
    )
    object_dir = dataset_cache / "objects" / content_sha
    object_dir.parent.mkdir(parents=True, exist_ok=True)
    return resolver, dataset, manifest, manifest_dataset, stage, object_dir


def test_concurrent_cold_cache_winner_is_accepted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    resolver, dataset, manifest, manifest_dataset, stage, object_dir = _prepared_stage(tmp_path)
    real_replace = os.replace
    injected = False

    def racing_replace(source, destination):
        nonlocal injected
        if Path(source) == stage and Path(destination) == object_dir and not injected:
            injected = True
            shutil.copytree(stage, object_dir)
            raise OSError("simulated concurrent winner")
        return real_replace(source, destination)

    monkeypatch.setattr(resolver_module.os, "replace", racing_replace)

    resolver._install_object_race_safe(
        stage=stage,
        object_dir=object_dir,
        dataset=dataset,
        manifest=manifest,
        manifest_dataset=manifest_dataset,
    )

    assert injected is True
    assert resolver._object_matches_manifest(object_dir, dataset, manifest, manifest_dataset)
    assert not stage.exists()


def test_repair_race_preserves_concurrently_installed_valid_object(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    resolver, dataset, manifest, manifest_dataset, stage, object_dir = _prepared_stage(tmp_path)
    object_dir.mkdir(parents=True)
    (object_dir / ".manifest.json").write_text("{}", encoding="utf-8")
    (object_dir / "banxico").mkdir()
    (object_dir / "banxico" / "banks.json").write_text("corrupt", encoding="utf-8")

    real_replace = os.replace
    injected = False

    def racing_replace(source, destination):
        nonlocal injected
        source_path = Path(source)
        destination_path = Path(destination)
        if source_path == stage and destination_path == object_dir and not injected:
            injected = True
            shutil.copytree(stage, object_dir)
            raise OSError("simulated concurrent repair winner")
        return real_replace(source, destination)

    monkeypatch.setattr(resolver_module.os, "replace", racing_replace)

    resolver._install_object_race_safe(
        stage=stage,
        object_dir=object_dir,
        dataset=dataset,
        manifest=manifest,
        manifest_dataset=manifest_dataset,
    )

    assert injected is True
    assert resolver._object_matches_manifest(object_dir, dataset, manifest, manifest_dataset)
    assert not list(object_dir.parent.glob(".corrupt-*"))


def test_older_candidate_cannot_replace_current_release_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    resolver = DatasetResolver(
        cache_dir=tmp_path / "cache",
        contract=contract(discovery="release-pointer"),
        downloader=lambda url: (_ for _ in ()).throw(AssertionError(url)),
    )
    dataset = resolver._dataset("banxico.reference")
    state_path = resolver._state_path("banxico.reference")
    state_path.parent.mkdir(parents=True, exist_ok=True)
    newer_state = {
        "dataset_id": "banxico.reference",
        "content_sha256": "b" * 64,
        "fetched_at": "2026-08-27T22:00:00+00:00",
        "release_tag": "data-banxico-reference-1-" + "b" * 64,
    }
    state_path.write_text(json.dumps(newer_state), encoding="utf-8")

    monkeypatch.setattr(
        resolver,
        "_resolve_release",
        lambda dataset_id, dataset: (
            newer_state["release_tag"],
            b"{}",
            {},
            {},
            newer_state["content_sha256"],
        ),
    )

    committed = resolver._commit_state_if_current(
        "banxico.reference",
        dataset,
        "data-banxico-reference-1-" + "a" * 64,
        "a" * 64,
    )

    assert committed is False
    assert json.loads(state_path.read_text(encoding="utf-8")) == newer_state


def test_windows_lock_retries_beyond_msvcrt_default_limit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    attempts = 0
    unlocks = 0
    sleeps: list[float] = []
    lk_nblck = 1
    lk_unlck = 2

    def locking(_fd: int, mode: int, nbytes: int) -> None:
        nonlocal attempts, unlocks
        assert nbytes == 1
        if mode == lk_unlck:
            unlocks += 1
            return
        assert mode == lk_nblck
        attempts += 1
        if attempts <= 12:
            raise OSError(errno.EACCES, "simulated lock contention")

    fake_msvcrt = SimpleNamespace(
        LK_NBLCK=lk_nblck,
        LK_UNLCK=lk_unlck,
        locking=locking,
    )
    monkeypatch.setitem(sys.modules, "msvcrt", fake_msvcrt)
    monkeypatch.setattr(resolver_module.os, "name", "nt")
    monkeypatch.setattr(resolver_module.time, "sleep", sleeps.append)

    with resolver_module._exclusive_file_lock(tmp_path / "windows.lock"):
        assert attempts == 13

    assert unlocks == 1
    assert sleeps == [0.05] * 12
