"""Shared-data compatibility helpers backed by dataset-aware resolution."""

from __future__ import annotations

import os
from pathlib import Path

_DATASET_PREFIXES = {
    "banxico": "banxico.reference",
}


def _configured_root() -> Path | None:
    configured = os.getenv("CATALOGMX_SHARED_DATA")
    if not configured:
        return None
    root = Path(configured).expanduser().resolve()
    if not root.exists():
        raise FileNotFoundError(f"CATALOGMX_SHARED_DATA does not exist: {root}")
    return root


def _local_roots() -> list[Path]:
    roots: list[Path] = []
    package_root = Path(__file__).resolve().parents[1] / "shared-data"
    if package_root.exists():
        roots.append(package_root)

    for parent in Path(__file__).resolve().parents:
        repo_candidate = parent / "packages" / "shared-data"
        if repo_candidate.exists() and repo_candidate not in roots:
            roots.append(repo_candidate)

    for parent in Path(__file__).resolve().parents:
        sibling_candidate = parent / "shared-data"
        if sibling_candidate.exists() and sibling_candidate not in roots:
            roots.append(sibling_candidate)
    return roots


def get_shared_data_root() -> Path:
    """Return a complete local shared-data root.

    Dataset caches are intentionally not exposed as one synthetic monolithic
    root: profiles may contain only selected datasets. Consumers that know a
    dataset should use :func:`get_shared_data_path` or the dataset resolver.
    """
    configured = _configured_root()
    if configured is not None:
        return configured

    roots = _local_roots()
    if roots:
        return roots[0]
    raise FileNotFoundError(
        "shared-data root not found. Set CATALOGMX_SHARED_DATA or resolve a dataset explicitly."
    )


def get_shared_data_path(*parts: str) -> Path:
    """Resolve a legacy shared-data path without repository-layout assumptions.

    Existing local layouts remain first-class. If the first path component maps
    to an independently distributed dataset, an installed wheel may lazily fetch
    that verified release artifact on first data access according to
    ``CATALOGMX_DATA_MODE``. Importing modules performs no fetch.
    """
    if not parts:
        return get_shared_data_root()

    configured = _configured_root()
    if configured is not None:
        candidate = configured.joinpath(*parts)
        if not candidate.exists():
            raise FileNotFoundError(f"shared-data path does not exist: {candidate}")
        return candidate

    for root in _local_roots():
        candidate = root.joinpath(*parts)
        if candidate.exists():
            return candidate

    dataset_id = _DATASET_PREFIXES.get(parts[0])
    if dataset_id is not None:
        from catalogmx.data.resolver import get_dataset_path

        return get_dataset_path(dataset_id, *parts[1:])

    raise FileNotFoundError(
        "shared-data path not found locally and no dataset resolver is registered for "
        + "/".join(parts)
    )
