"""Dataset-aware resolver for independently versioned CatalogMX data."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tarfile
import tempfile
from collections.abc import Callable, Mapping
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any
from urllib.request import Request, urlopen

DEFAULT_RELEASE_BASE_URL = "https://github.com/openbancor/catalogmx/releases/download"
DEFAULT_DATA_MODE = "fetch-missing"
ALLOWED_DATA_MODES = {"offline", "fetch-missing", "refresh"}
CONTRACT_RESOURCE = "dataset_contract.json"

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


class DatasetResolver:
    """Resolve, fetch, verify and materialize versioned data artifacts."""

    def __init__(
        self,
        *,
        cache_dir: str | Path | None = None,
        mode: str | None = None,
        release_base_url: str | None = None,
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
        if not state:
            return None
        content_sha = state.get("content_sha256")
        if not isinstance(content_sha, str) or len(content_sha) != 64:
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
            if self.mode in {"offline", "fetch-missing"}:
                return root
            if not self._cache_is_stale(dataset, state):
                return root

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
            if cached is not None:
                return cached[0]
            raise

    def get_dataset_path(self, dataset_id: str, *parts: str) -> Path:
        path = self.resolve_dataset_root(dataset_id).joinpath(*parts)
        if not path.exists():
            raise FileNotFoundError(f"dataset path does not exist: {dataset_id}:{'/'.join(parts)}")
        return path

    def _release_url(self, channel: str, filename: str) -> str:
        return f"{self.release_base_url}/{channel}/{filename}"

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
        _safe_relative_path(str(manifest_dataset["mount_path"]))
        file_sha = manifest_dataset.get("file_sha256")
        content_sha = manifest_dataset.get("content_sha256")
        if not isinstance(file_sha, str) or len(file_sha) != 64:
            raise RuntimeError("dataset manifest is missing artifact SHA-256")
        if not isinstance(content_sha, str) or len(content_sha) != 64:
            raise RuntimeError("dataset manifest is missing semantic SHA-256")
        return manifest_dataset, content_sha

    def _extract_tar_bundle(
        self,
        payload: bytes,
        stage: Path,
        manifest_dataset: Mapping[str, Any],
    ) -> None:
        expected_files = manifest_dataset.get("files")
        if not isinstance(expected_files, list) or not expected_files:
            raise RuntimeError("tar dataset manifest must list extracted files")
        expected: dict[str, str] = {}
        for item in expected_files:
            if not isinstance(item, dict):
                raise RuntimeError("invalid file metadata in dataset manifest")
            path = item.get("path")
            sha = item.get("sha256")
            if not isinstance(path, str) or not isinstance(sha, str) or len(sha) != 64:
                raise RuntimeError("invalid file metadata in dataset manifest")
            _safe_relative_path(path)
            expected[path] = sha

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
                    if _sha256(data) != expected[name]:
                        raise RuntimeError(f"dataset member checksum mismatch: {member.name}")
                    destination = stage / relative
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(data)
                    observed.add(name)
        if observed != set(expected):
            missing = sorted(set(expected) - observed)
            raise RuntimeError("dataset archive is missing manifest files: " + ", ".join(missing))

    def fetch_dataset(self, dataset_id: str) -> Path:
        dataset = self._dataset(dataset_id)
        artifact = dataset["artifact"]
        channel = artifact["channel"]
        manifest_name = artifact["manifest"]
        artifact_name = artifact["file"]

        manifest_payload = self.downloader(self._release_url(channel, manifest_name))
        try:
            manifest = json.loads(manifest_payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("invalid dataset release manifest") from exc
        if not isinstance(manifest, dict):
            raise RuntimeError("dataset release manifest must be an object")
        manifest_dataset, content_sha = self._validate_manifest(dataset_id, dataset, manifest)

        artifact_payload = self.downloader(self._release_url(channel, artifact_name))
        if _sha256(artifact_payload) != manifest_dataset["file_sha256"]:
            raise RuntimeError("dataset release artifact checksum mismatch")

        dataset_cache = self._dataset_cache_dir(dataset_id)
        objects_dir = dataset_cache / "objects"
        objects_dir.mkdir(parents=True, exist_ok=True)
        object_dir = objects_dir / content_sha

        if not object_dir.exists():
            stage = Path(tempfile.mkdtemp(prefix=".stage-", dir=dataset_cache))
            try:
                artifact_format = artifact["format"]
                mount_path = _safe_relative_path(artifact["mount_path"])
                if artifact_format == "tar.gz":
                    self._extract_tar_bundle(artifact_payload, stage, manifest_dataset)
                elif artifact_format == "file":
                    destination_dir = stage / mount_path
                    destination_dir.mkdir(parents=True, exist_ok=True)
                    (destination_dir / artifact_name).write_bytes(artifact_payload)
                else:
                    raise RuntimeError(f"unsupported dataset artifact format: {artifact_format}")
                (stage / ".manifest.json").write_bytes(manifest_payload)
                os.replace(stage, object_dir)
            finally:
                if stage.exists():
                    shutil.rmtree(stage)

        state = {
            "dataset_id": dataset_id,
            "content_sha256": content_sha,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
        _atomic_write(
            self._state_path(dataset_id),
            (json.dumps(state, sort_keys=True, indent=2) + "\n").encode("utf-8"),
        )
        root = object_dir / _safe_relative_path(artifact["mount_path"])
        if not root.exists():
            raise RuntimeError("cached dataset does not contain its mount path")
        return root

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
        if not manifest_path.exists():
            return False
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest_dataset, content_sha = self._validate_manifest(dataset_id, dataset, manifest)
            if content_sha != state.get("content_sha256"):
                return False

            if dataset["artifact"]["format"] == "tar.gz":
                files = manifest_dataset.get("files")
                if not isinstance(files, list):
                    return False
                for item in files:
                    if not isinstance(item, dict):
                        return False
                    path_value = item.get("path")
                    sha_value = item.get("sha256")
                    if not isinstance(path_value, str) or not isinstance(sha_value, str):
                        return False
                    path = object_dir / _safe_relative_path(path_value)
                    if not path.exists() or _sha256(path.read_bytes()) != sha_value:
                        return False
                return True

            artifact_path = root / dataset["artifact"]["file"]
            return (
                artifact_path.exists()
                and _sha256(artifact_path.read_bytes()) == manifest_dataset["file_sha256"]
            )
        except (KeyError, OSError, TypeError, ValueError, json.JSONDecodeError, RuntimeError):
            return False

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
