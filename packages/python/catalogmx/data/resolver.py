"""Dataset-aware resolver for independently versioned CatalogMX data."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tarfile
import tempfile
import uuid
from contextlib import contextmanager
from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Iterator, TypeGuard
from urllib.request import Request, urlopen

DEFAULT_RELEASE_BASE_URL = "https://github.com/openbancor/catalogmx/releases/download"
DEFAULT_RELEASE_METADATA_BASE_URL = (
    "https://api.github.com/repos/openbancor/catalogmx/releases/tags"
)
DEFAULT_DATA_MODE = "fetch-missing"
ALLOWED_DATA_MODES = {"offline", "fetch-missing", "refresh"}
CONTRACT_RESOURCE = "dataset_contract.json"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_RELEASE_TAG_RE = re.compile(r"^[A-Za-z0-9._-]+$")

Downloader = Callable[[str], bytes]


def load_dataset_contract() -> dict[str, Any]:
    """Load the package-local runtime contract generated from the registry."""
    resource = resources.files("catalogmx.data").joinpath(CONTRACT_RESOURCE)
    with resource.open("r", encoding="utf-8") as handle:
        contract = json.load(handle)
    if contract.get("schema_version") != 1:
        raise RuntimeError("unsupported CatalogMX dataset contract schema")
    if not isinstance(contract.get("datasets"), dict):
        raise RuntimeError("dataset contract is missing datasets")
    if not isinstance(contract.get("profiles"), dict):
        raise RuntimeError("dataset contract is missing profiles")
    return contract


def default_cache_root() -> Path:
    configured = os.getenv("CATALOGMX_CACHE_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path.home() / ".cache" / "catalogmx"


def _default_downloader(url: str) -> bytes:
    request = Request(
        url,
        headers={
            "Accept": "application/octet-stream,application/json",
            "User-Agent": "catalogmx-dataset-resolver",
        },
    )
    with urlopen(request, timeout=30) as response:  # noqa: S310
        return response.read()


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _is_sha256(value: object) -> TypeGuard[str]:
    return isinstance(value, str) and _SHA256_RE.fullmatch(value) is not None


def _safe_relative_path(value: str) -> Path:
    """Return a path that is relative and safe on POSIX and Windows."""
    if not value or "\x00" in value or "\\" in value:
        raise RuntimeError(f"unsafe dataset path in manifest: {value!r}")

    raw_parts = value.split("/")
    if any(part in {"", ".", ".."} for part in raw_parts):
        raise RuntimeError(f"unsafe dataset path in manifest: {value!r}")

    posix = PurePosixPath(value)
    windows = PureWindowsPath(value)
    if posix.is_absolute() or windows.is_absolute() or windows.drive:
        raise RuntimeError(f"unsafe dataset path in manifest: {value!r}")
    return Path(*posix.parts)


def _atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temp_path = Path(temp_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)


@contextmanager
def _exclusive_file_lock(path: Path) -> Iterator[None]:
    """Serialize a small cache metadata critical section across processes."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if handle.tell() == 0:
            handle.write(b"\0")
            handle.flush()
        handle.seek(0)

        if os.name == "nt":
            import msvcrt

            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


class DatasetResolver:
    """Resolve, fetch, verify and materialize versioned data artifacts."""

    def __init__(
        self,
        *,
        cache_dir: str | Path | None = None,
        mode: str | None = None,
        release_base_url: str | None = None,
        release_metadata_base_url: str | None = None,
        contract: Mapping[str, Any] | None = None,
        downloader: Downloader | None = None,
    ) -> None:
        self.contract = dict(contract or load_dataset_contract())
        self.cache_root = (
            Path(cache_dir).expanduser().resolve()
            if cache_dir is not None
            else default_cache_root()
        )
        self.mode = mode or os.getenv("CATALOGMX_DATA_MODE", DEFAULT_DATA_MODE)
        if self.mode not in ALLOWED_DATA_MODES:
            raise ValueError(f"CATALOGMX_DATA_MODE must be one of {sorted(ALLOWED_DATA_MODES)}")
        self.release_base_url = (
            release_base_url or os.getenv("CATALOGMX_RELEASE_BASE_URL") or DEFAULT_RELEASE_BASE_URL
        ).rstrip("/")
        self.release_metadata_base_url = (
            release_metadata_base_url
            or os.getenv("CATALOGMX_RELEASE_METADATA_BASE_URL")
            or DEFAULT_RELEASE_METADATA_BASE_URL
        ).rstrip("/")
        self.downloader = downloader or _default_downloader

    def dataset_ids_for_profile(self, profile: str) -> list[str]:
        profiles = self.contract["profiles"]
        if profile not in profiles:
            raise KeyError(f"unknown CatalogMX data profile: {profile}")
        value = profiles[profile]
        datasets = value.get("datasets") if isinstance(value, dict) else value
        if not isinstance(datasets, list) or not all(isinstance(item, str) for item in datasets):
            raise RuntimeError(f"invalid dataset profile contract: {profile}")
        return list(datasets)

    def _dataset(self, dataset_id: str) -> dict[str, Any]:
        datasets = self.contract["datasets"]
        dataset = datasets.get(dataset_id)
        if not isinstance(dataset, dict):
            raise KeyError(f"unknown CatalogMX dataset: {dataset_id}")
        artifact = dataset.get("artifact")
        if not isinstance(artifact, dict):
            raise RuntimeError(f"dataset has no runtime artifact contract: {dataset_id}")
        return dataset

    def _dataset_cache_dir(self, dataset_id: str) -> Path:
        return self.cache_root / "datasets" / dataset_id

    def _state_path(self, dataset_id: str) -> Path:
        return self._dataset_cache_dir(dataset_id) / "current.json"

    def _state_lock_path(self, dataset_id: str) -> Path:
        return self.cache_root / ".locks" / f"{dataset_id}.lock"

    def _read_state(self, dataset_id: str) -> dict[str, Any] | None:
        path = self._state_path(dataset_id)
        if not path.exists():
            return None
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        return value if isinstance(value, dict) else None

    def _cached_root(self, dataset_id: str) -> tuple[Path, dict[str, Any]] | None:
        state = self._read_state(dataset_id)
        if not state or state.get("dataset_id") != dataset_id:
            return None
        content_sha = state.get("content_sha256")
        if not _is_sha256(content_sha):
            return None
        dataset = self._dataset(dataset_id)
        mount_path = _safe_relative_path(dataset["artifact"]["mount_path"])
        object_dir = self._dataset_cache_dir(dataset_id) / "objects" / content_sha
        root = object_dir / mount_path
        if not root.exists():
            return None
        return root, state

    def _cache_is_stale(self, dataset: Mapping[str, Any], state: Mapping[str, Any]) -> bool:
        max_age_days = dataset.get("freshness", {}).get("max_age_days")
        if not isinstance(max_age_days, int) or max_age_days <= 0:
            return False
        fetched_at = state.get("fetched_at")
        if not isinstance(fetched_at, str):
            return True
        try:
            fetched = datetime.fromisoformat(fetched_at.replace("Z", "+00:00"))
        except ValueError:
            return True
        if fetched.tzinfo is None:
            fetched = fetched.replace(tzinfo=timezone.utc)
        age = datetime.now(timezone.utc) - fetched.astimezone(timezone.utc)
        return age.total_seconds() > max_age_days * 86400

    def _configured_root(self, dataset: Mapping[str, Any]) -> Path | None:
        configured = os.getenv("CATALOGMX_SHARED_DATA")
        if not configured:
            return None
        base = Path(configured).expanduser().resolve()
        if not base.exists():
            raise FileNotFoundError(f"CATALOGMX_SHARED_DATA does not exist: {base}")
        candidate = base / _safe_relative_path(dataset["artifact"]["mount_path"])
        if not candidate.exists():
            raise FileNotFoundError(f"dataset is missing from CATALOGMX_SHARED_DATA: {candidate}")
        return candidate

    def _package_root(self, dataset: Mapping[str, Any]) -> Path | None:
        source_subpath = dataset.get("source_subpath")
        if not isinstance(source_subpath, str):
            return None
        package_root = Path(__file__).resolve().parents[1] / "shared-data"
        candidate = package_root / _safe_relative_path(source_subpath)
        return candidate if candidate.exists() else None

    def _repo_root(self, dataset: Mapping[str, Any]) -> Path | None:
        source_subpath = dataset.get("source_subpath")
        if not isinstance(source_subpath, str):
            return None
        relative = _safe_relative_path(source_subpath)
        for parent in Path(__file__).resolve().parents:
            candidate = parent / "packages" / "shared-data" / relative
            if candidate.exists():
                return candidate
        return None

    def resolve_dataset_root(self, dataset_id: str) -> Path:
        dataset = self._dataset(dataset_id)

        configured = self._configured_root(dataset)
        if configured is not None:
            return configured

        cached = self._cached_root(dataset_id)
        if cached is not None:
            root, state = cached
            if self.verify_cached_dataset(dataset_id):
                if self.mode in {"offline", "fetch-missing"}:
                    return root
                if not self._cache_is_stale(dataset, state):
                    return root
            else:
                cached = None

        package = self._package_root(dataset)
        if package is not None:
            return package

        repository = self._repo_root(dataset)
        if repository is not None:
            return repository

        if self.mode == "offline":
            if cached is not None:
                return cached[0]
            raise FileNotFoundError(f"dataset {dataset_id} is unavailable in offline mode")

        try:
            return self.fetch_dataset(dataset_id)
        except Exception:
            if cached is not None and self.verify_cached_dataset(dataset_id):
                return cached[0]
            raise

    def get_dataset_path(self, dataset_id: str, *parts: str) -> Path:
        root = self.resolve_dataset_root(dataset_id)
        if not parts:
            return root
        relative = _safe_relative_path("/".join(parts))
        path = root / relative
        if not path.exists():
            raise FileNotFoundError(f"dataset path does not exist: {dataset_id}:{'/'.join(parts)}")
        return path

    def _release_url(self, release_tag: str, filename: str) -> str:
        if not _RELEASE_TAG_RE.fullmatch(release_tag):
            raise RuntimeError(f"unsafe dataset release tag: {release_tag!r}")
        return f"{self.release_base_url}/{release_tag}/{filename}"

    def _release_metadata_url(self, channel: str) -> str:
        if not _RELEASE_TAG_RE.fullmatch(channel):
            raise RuntimeError(f"unsafe dataset channel: {channel!r}")
        return f"{self.release_metadata_base_url}/{channel}"

    def _validate_manifest(
        self,
        dataset_id: str,
        dataset: Mapping[str, Any],
        manifest: Mapping[str, Any],
    ) -> tuple[dict[str, Any], str]:
        artifact = dataset["artifact"]
        if manifest.get("schema_version") != 1:
            raise RuntimeError("unsupported dataset manifest schema")
        if manifest.get("dataset_id") != dataset_id:
            raise RuntimeError("dataset manifest id mismatch")
        if str(manifest.get("dataset_version")) != str(artifact["version"]):
            raise RuntimeError("dataset manifest version mismatch")
        manifest_dataset = manifest.get("dataset")
        if not isinstance(manifest_dataset, dict):
            raise RuntimeError("dataset manifest is missing dataset metadata")
        if manifest_dataset.get("file") != artifact["file"]:
            raise RuntimeError("dataset manifest artifact filename mismatch")
        if manifest_dataset.get("format") != artifact["format"]:
            raise RuntimeError("dataset manifest artifact format mismatch")
        if manifest_dataset.get("mount_path") != artifact["mount_path"]:
            raise RuntimeError("dataset manifest mount path mismatch")
        mount_value = manifest_dataset.get("mount_path")
        if not isinstance(mount_value, str):
            raise RuntimeError("dataset manifest mount path must be a string")
        _safe_relative_path(mount_value)
        file_sha = manifest_dataset.get("file_sha256")
        content_sha = manifest_dataset.get("content_sha256")
        if not _is_sha256(file_sha):
            raise RuntimeError("dataset manifest is missing artifact SHA-256")
        if not _is_sha256(content_sha):
            raise RuntimeError("dataset manifest is missing semantic SHA-256")
        return manifest_dataset, content_sha

    def _parse_manifest(
        self, dataset_id: str, dataset: Mapping[str, Any], payload: bytes
    ) -> tuple[dict[str, Any], dict[str, Any], str]:
        try:
            manifest = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("invalid dataset release manifest") from exc
        if not isinstance(manifest, dict):
            raise RuntimeError("dataset release manifest must be an object")
        manifest_dataset, content_sha = self._validate_manifest(dataset_id, dataset, manifest)
        return manifest, manifest_dataset, content_sha

    def _resolve_release(
        self, dataset_id: str, dataset: Mapping[str, Any]
    ) -> tuple[str, bytes, dict[str, Any], dict[str, Any], str]:
        artifact = dataset["artifact"]
        channel = artifact["channel"]
        release_tag = channel
        expected_pointer_sha: str | None = None

        discovery = artifact.get("discovery", "direct")
        if discovery == "release-pointer":
            metadata_payload = self.downloader(self._release_metadata_url(channel))
            try:
                metadata = json.loads(metadata_payload.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise RuntimeError("invalid dataset channel metadata") from exc
            if not isinstance(metadata, dict):
                raise RuntimeError("dataset channel metadata must be an object")
            if metadata.get("tag_name") not in {None, channel}:
                raise RuntimeError("dataset channel tag mismatch")
            body = metadata.get("body")
            if not isinstance(body, str):
                raise RuntimeError("dataset channel metadata is missing pointer body")
            try:
                pointer = json.loads(body)
            except json.JSONDecodeError as exc:
                raise RuntimeError("invalid dataset release pointer") from exc
            if not isinstance(pointer, dict) or pointer.get("schema_version") != 1:
                raise RuntimeError("unsupported dataset release pointer schema")
            if pointer.get("dataset_id") != dataset_id:
                raise RuntimeError("dataset release pointer id mismatch")
            if str(pointer.get("dataset_version")) != str(artifact["version"]):
                raise RuntimeError("dataset release pointer version mismatch")
            if pointer.get("artifact") != artifact["file"]:
                raise RuntimeError("dataset release pointer artifact mismatch")
            if pointer.get("manifest") != artifact["manifest"]:
                raise RuntimeError("dataset release pointer manifest mismatch")
            release_tag_value = pointer.get("release_tag")
            if not isinstance(release_tag_value, str) or not _RELEASE_TAG_RE.fullmatch(
                release_tag_value
            ):
                raise RuntimeError("dataset release pointer has unsafe release tag")
            pointer_sha = pointer.get("content_sha256")
            if not _is_sha256(pointer_sha):
                raise RuntimeError("dataset release pointer is missing content SHA-256")
            release_tag = release_tag_value
            expected_pointer_sha = pointer_sha
        elif discovery != "direct":
            raise RuntimeError(f"unsupported dataset discovery mode: {discovery}")

        manifest_payload = self.downloader(self._release_url(release_tag, artifact["manifest"]))
        manifest, manifest_dataset, content_sha = self._parse_manifest(
            dataset_id, dataset, manifest_payload
        )
        if expected_pointer_sha is not None and content_sha != expected_pointer_sha:
            raise RuntimeError("dataset release pointer content SHA-256 mismatch")
        return (
            release_tag,
            manifest_payload,
            manifest,
            manifest_dataset,
            content_sha,
        )

    def _expected_tar_files(
        self, manifest_dataset: Mapping[str, Any]
    ) -> dict[str, tuple[str, int]]:
        expected_files = manifest_dataset.get("files")
        if not isinstance(expected_files, list) or not expected_files:
            raise RuntimeError("tar dataset manifest must list extracted files")

        mount_value = manifest_dataset.get("mount_path")
        if not isinstance(mount_value, str):
            raise RuntimeError("dataset manifest mount path must be a string")
        mount_parts = PurePosixPath(mount_value).parts

        expected: dict[str, tuple[str, int]] = {}
        for item in expected_files:
            if not isinstance(item, dict):
                raise RuntimeError("invalid file metadata in dataset manifest")
            path = item.get("path")
            sha = item.get("sha256")
            size = item.get("bytes")
            if not isinstance(path, str) or not _is_sha256(sha):
                raise RuntimeError("invalid file metadata in dataset manifest")
            if not isinstance(size, int) or isinstance(size, bool) or size < 0:
                raise RuntimeError("invalid file size in dataset manifest")
            _safe_relative_path(path)
            if PurePosixPath(path).parts[: len(mount_parts)] != mount_parts:
                raise RuntimeError(f"dataset file is outside mount path: {path}")
            if path in expected:
                raise RuntimeError(f"duplicate file in dataset manifest: {path}")
            expected[path] = (sha, size)
        return expected

    def _extract_tar_bundle(
        self,
        payload: bytes,
        stage: Path,
        manifest_dataset: Mapping[str, Any],
    ) -> None:
        expected = self._expected_tar_files(manifest_dataset)
        observed: set[str] = set()
        with tempfile.SpooledTemporaryFile() as archive_file:
            archive_file.write(payload)
            archive_file.seek(0)
            with tarfile.open(fileobj=archive_file, mode="r:gz") as archive:
                for member in archive.getmembers():
                    if not member.isfile():
                        raise RuntimeError(
                            f"dataset archive contains non-regular entry: {member.name}"
                        )
                    relative = _safe_relative_path(member.name)
                    name = PurePosixPath(member.name).as_posix()
                    if name not in expected:
                        raise RuntimeError(
                            f"dataset archive contains unexpected file: {member.name}"
                        )
                    if name in observed:
                        raise RuntimeError(
                            f"dataset archive contains duplicate file: {member.name}"
                        )
                    source = archive.extractfile(member)
                    if source is None:
                        raise RuntimeError(f"cannot read dataset archive member: {member.name}")
                    data = source.read()
                    expected_sha, expected_size = expected[name]
                    if len(data) != expected_size:
                        raise RuntimeError(f"dataset member size mismatch: {member.name}")
                    if _sha256(data) != expected_sha:
                        raise RuntimeError(f"dataset member checksum mismatch: {member.name}")
                    destination = stage / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(data)
                    observed.add(name)
        if observed != set(expected):
            missing = sorted(set(expected) - observed)
            raise RuntimeError("dataset archive is missing manifest files: " + ", ".join(missing))

    def _object_matches_manifest(
        self,
        object_dir: Path,
        dataset: Mapping[str, Any],
        manifest: Mapping[str, Any],
        manifest_dataset: Mapping[str, Any],
    ) -> bool:
        if not object_dir.is_dir() or object_dir.is_symlink():
            return False
        stored_manifest_path = object_dir / ".manifest.json"
        try:
            stored_manifest = json.loads(stored_manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False
        if stored_manifest != manifest:
            return False

        artifact = dataset["artifact"]
        mount_path = _safe_relative_path(artifact["mount_path"])
        root = object_dir / mount_path
        if not root.exists() or root.is_symlink():
            return False

        if artifact["format"] == "tar.gz":
            try:
                expected = self._expected_tar_files(manifest_dataset)
            except RuntimeError:
                return False
            expected_paths = set(expected)
            observed_paths: set[str] = set()
            try:
                for path in object_dir.rglob("*"):
                    if path.is_symlink():
                        return False
                    if not path.is_file():
                        continue
                    relative = path.relative_to(object_dir).as_posix()
                    if relative == ".manifest.json":
                        continue
                    observed_paths.add(relative)
                if observed_paths != expected_paths:
                    return False
                for relative, (expected_sha, expected_size) in expected.items():
                    path = object_dir / _safe_relative_path(relative)
                    payload = path.read_bytes()
                    if len(payload) != expected_size or _sha256(payload) != expected_sha:
                        return False
                return True
            except OSError:
                return False

        if artifact["format"] == "file":
            artifact_path = root / artifact["file"]
            try:
                return (
                    artifact_path.is_file()
                    and not artifact_path.is_symlink()
                    and _sha256(artifact_path.read_bytes()) == manifest_dataset["file_sha256"]
                )
            except OSError:
                return False
        return False

    def _stage_object(
        self,
        dataset_cache: Path,
        dataset: Mapping[str, Any],
        manifest_payload: bytes,
        manifest: Mapping[str, Any],
        manifest_dataset: Mapping[str, Any],
        artifact_payload: bytes,
    ) -> Path:
        stage = Path(tempfile.mkdtemp(prefix=".stage-", dir=dataset_cache))
        try:
            artifact = dataset["artifact"]
            mount_path = _safe_relative_path(artifact["mount_path"])
            if artifact["format"] == "tar.gz":
                self._extract_tar_bundle(artifact_payload, stage, manifest_dataset)
            elif artifact["format"] == "file":
                destination_dir = stage / mount_path
                destination_dir.mkdir(parents=True, exist_ok=True)
                (destination_dir / artifact["file"]).write_bytes(artifact_payload)
            else:
                raise RuntimeError(f"unsupported dataset artifact format: {artifact['format']}")
            (stage / ".manifest.json").write_bytes(manifest_payload)
            if not self._object_matches_manifest(stage, dataset, manifest, manifest_dataset):
                raise RuntimeError("staged dataset object failed verification")
            return stage
        except Exception:
            shutil.rmtree(stage, ignore_errors=True)
            raise

    def _install_object_race_safe(
        self,
        *,
        stage: Path,
        object_dir: Path,
        dataset: Mapping[str, Any],
        manifest: Mapping[str, Any],
        manifest_dataset: Mapping[str, Any],
    ) -> None:
        """Install a verified object without clobbering a valid concurrent winner."""
        quarantine: Path | None = None
        stage_path: Path | None = stage
        try:
            if object_dir.exists():
                if self._object_matches_manifest(object_dir, dataset, manifest, manifest_dataset):
                    return
                quarantine = object_dir.with_name(f".corrupt-{object_dir.name}-{uuid.uuid4().hex}")
                try:
                    os.replace(object_dir, quarantine)
                except FileNotFoundError:
                    quarantine = None
                except OSError:
                    if object_dir.exists() and self._object_matches_manifest(
                        object_dir, dataset, manifest, manifest_dataset
                    ):
                        return
                    raise

            try:
                assert stage_path is not None
                os.replace(stage_path, object_dir)
                stage_path = None
            except OSError:
                if object_dir.exists() and self._object_matches_manifest(
                    object_dir, dataset, manifest, manifest_dataset
                ):
                    return
                if quarantine is not None and quarantine.exists() and not object_dir.exists():
                    os.replace(quarantine, object_dir)
                    quarantine = None
                raise

            if not self._object_matches_manifest(object_dir, dataset, manifest, manifest_dataset):
                raise RuntimeError("installed dataset object failed verification")
        except Exception:
            if quarantine is not None and quarantine.exists() and not object_dir.exists():
                os.replace(quarantine, object_dir)
                quarantine = None
            raise
        finally:
            if stage_path is not None and stage_path.exists():
                shutil.rmtree(stage_path, ignore_errors=True)
            if quarantine is not None and quarantine.exists():
                shutil.rmtree(quarantine, ignore_errors=True)

    def _commit_state_if_current(
        self,
        dataset_id: str,
        dataset: Mapping[str, Any],
        release_tag: str,
        content_sha: str,
    ) -> bool:
        """Commit current.json only while this release is still authoritative."""
        with _exclusive_file_lock(self._state_lock_path(dataset_id)):
            discovery = dataset["artifact"].get("discovery", "direct")
            if discovery == "release-pointer":
                latest_tag, _, _, _, latest_sha = self._resolve_release(dataset_id, dataset)
                if latest_tag != release_tag or latest_sha != content_sha:
                    return False

            state = {
                "dataset_id": dataset_id,
                "content_sha256": content_sha,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "release_tag": release_tag,
            }
            _atomic_write(
                self._state_path(dataset_id),
                (json.dumps(state, sort_keys=True, indent=2) + "\n").encode("utf-8"),
            )
            return True

    def fetch_dataset(self, dataset_id: str) -> Path:
        if self.mode == "offline":
            raise RuntimeError("cannot fetch or update datasets while CATALOGMX_DATA_MODE=offline")

        dataset = self._dataset(dataset_id)
        artifact = dataset["artifact"]

        for _attempt in range(3):
            (
                release_tag,
                manifest_payload,
                manifest,
                manifest_dataset,
                content_sha,
            ) = self._resolve_release(dataset_id, dataset)

            artifact_payload = self.downloader(self._release_url(release_tag, artifact["file"]))
            if _sha256(artifact_payload) != manifest_dataset["file_sha256"]:
                raise RuntimeError("dataset release artifact checksum mismatch")

            dataset_cache = self._dataset_cache_dir(dataset_id)
            objects_dir = dataset_cache / "objects"
            objects_dir.mkdir(parents=True, exist_ok=True)
            object_dir = objects_dir / content_sha

            if not self._object_matches_manifest(object_dir, dataset, manifest, manifest_dataset):
                stage = self._stage_object(
                    dataset_cache,
                    dataset,
                    manifest_payload,
                    manifest,
                    manifest_dataset,
                    artifact_payload,
                )
                self._install_object_race_safe(
                    stage=stage,
                    object_dir=object_dir,
                    dataset=dataset,
                    manifest=manifest,
                    manifest_dataset=manifest_dataset,
                )

            root = object_dir / _safe_relative_path(artifact["mount_path"])
            if not root.exists():
                raise RuntimeError("cached dataset does not contain its mount path")

            if self._commit_state_if_current(dataset_id, dataset, release_tag, content_sha):
                return root

        raise RuntimeError(
            f"dataset release channel changed repeatedly while fetching {dataset_id}"
        )

    def fetch_profile(self, profile: str) -> dict[str, Path]:
        return {
            dataset_id: self.fetch_dataset(dataset_id)
            for dataset_id in self.dataset_ids_for_profile(profile)
        }

    def verify_cached_dataset(self, dataset_id: str) -> bool:
        cached = self._cached_root(dataset_id)
        if cached is None:
            return False
        root, state = cached
        object_dir = root
        dataset = self._dataset(dataset_id)
        mount_path = _safe_relative_path(dataset["artifact"]["mount_path"])
        for _ in mount_path.parts:
            object_dir = object_dir.parent
        manifest_path = object_dir / ".manifest.json"
        try:
            manifest_payload = manifest_path.read_bytes()
            manifest, manifest_dataset, content_sha = self._parse_manifest(
                dataset_id, dataset, manifest_payload
            )
        except (KeyError, OSError, TypeError, ValueError, RuntimeError):
            return False
        if content_sha != state.get("content_sha256"):
            return False
        return self._object_matches_manifest(object_dir, dataset, manifest, manifest_dataset)

    def verify_profile(self, profile: str) -> dict[str, bool]:
        return {
            dataset_id: self.verify_cached_dataset(dataset_id)
            for dataset_id in self.dataset_ids_for_profile(profile)
        }

    def materialize_profile(self, profile: str, destination: str | Path) -> Path:
        destination_root = Path(destination).expanduser().resolve()
        destination_root.mkdir(parents=True, exist_ok=True)
        manifest_dir = destination_root / ".catalogmx" / "manifests"
        manifest_dir.mkdir(parents=True, exist_ok=True)

        for dataset_id in self.dataset_ids_for_profile(profile):
            root = self.fetch_dataset(dataset_id)
            dataset = self._dataset(dataset_id)
            mount_path = _safe_relative_path(dataset["artifact"]["mount_path"])
            target = destination_root / mount_path
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
            target.parent.mkdir(parents=True, exist_ok=True)
            if root.is_dir():
                shutil.copytree(root, target)
            else:
                shutil.copy2(root, target)

            cached = self._cached_root(dataset_id)
            if cached is None:
                raise RuntimeError(f"dataset cache disappeared: {dataset_id}")
            object_dir = cached[0]
            for _ in mount_path.parts:
                object_dir = object_dir.parent
            shutil.copy2(
                object_dir / ".manifest.json",
                manifest_dir / f"{dataset_id}.json",
            )
        return destination_root

    def cache_status(self, dataset_id: str) -> dict[str, Any]:
        cached = self._cached_root(dataset_id)
        dataset = self._dataset(dataset_id)
        if cached is None:
            return {"dataset_id": dataset_id, "cached": False, "stale": None}
        root, state = cached
        return {
            "dataset_id": dataset_id,
            "cached": True,
            "stale": self._cache_is_stale(dataset, state),
            "content_sha256": state.get("content_sha256"),
            "fetched_at": state.get("fetched_at"),
            "release_tag": state.get("release_tag"),
            "root": str(root),
        }

    def clear_cache(self, dataset_id: str | None = None) -> None:
        if dataset_id is None:
            target = self.cache_root / "datasets"
        else:
            self._dataset(dataset_id)
            target = self._dataset_cache_dir(dataset_id)
        if target.exists():
            shutil.rmtree(target)


def get_dataset_root(dataset_id: str) -> Path:
    return DatasetResolver().resolve_dataset_root(dataset_id)


def get_dataset_path(dataset_id: str, *parts: str) -> Path:
    return DatasetResolver().get_dataset_path(dataset_id, *parts)


__all__ = [
    "ALLOWED_DATA_MODES",
    "DatasetResolver",
    "get_dataset_path",
    "get_dataset_root",
    "load_dataset_contract",
]
