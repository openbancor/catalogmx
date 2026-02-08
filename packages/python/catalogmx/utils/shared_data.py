"""Shared-data path helpers."""

from __future__ import annotations

import os
from pathlib import Path


def get_shared_data_root() -> Path:
    """Return the shared-data root path.

    Resolution order:
    1) $CATALOGMX_SHARED_DATA
    2) catalogmx package-local shared-data
    3) repo layout: packages/shared-data
    4) sibling shared-data (fallback)
    """
    env_path = os.getenv("CATALOGMX_SHARED_DATA")
    if env_path:
        candidate = Path(env_path).expanduser().resolve()
        if candidate.exists():
            return candidate

    pkg_root = Path(__file__).resolve().parents[1]  # catalogmx/
    candidate = pkg_root / "shared-data"
    if candidate.exists():
        return candidate

    for parent in Path(__file__).resolve().parents:
        repo_candidate = parent / "packages" / "shared-data"
        if repo_candidate.exists():
            return repo_candidate

    for parent in Path(__file__).resolve().parents:
        sibling_candidate = parent / "shared-data"
        if sibling_candidate.exists():
            return sibling_candidate

    raise FileNotFoundError("shared-data not found. Set CATALOGMX_SHARED_DATA to a valid path.")


def get_shared_data_path(*parts: str) -> Path:
    """Return a path inside shared-data."""
    return get_shared_data_root().joinpath(*parts)
