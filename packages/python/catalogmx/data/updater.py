"""Backward-compatible facade for the ``banxico.sie_dynamic`` dataset.

``DatasetResolver`` owns runtime discovery, integrity verification, caching and
refresh.  This module intentionally preserves the historical ``DataUpdater``
API so existing callers do not need to migrate in lock-step with the data
lifecycle architecture.
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from catalogmx.data.resolver import DatasetResolver, default_cache_root

DATASET_ID = "banxico.sie_dynamic"
DATABASE_NAME = "mexico_dynamic.sqlite3"

# Deprecated compatibility names.  They no longer define a second downloader or
# cache protocol; all authoritative runtime state lives under DatasetResolver.
GITHUB_RELEASE_URL = os.getenv(
    "CATALOGMX_DATA_URL",
    "https://github.com/openbancor/catalogmx/releases",
)
CACHE_DIR = default_cache_root()
CACHE_DB = CACHE_DIR / DATABASE_NAME
VERSION_FILE = CACHE_DIR / "version.json"
EMBEDDED_DB = Path(__file__).parent / DATABASE_NAME
AUTO_UPDATE_ENABLED = os.getenv("CATALOGMX_AUTO_UPDATE", "true").lower() in {
    "true",
    "1",
    "yes",
}


class DataUpdater:
    """Compatibility wrapper over :class:`catalogmx.data.DatasetResolver`.

    The old updater downloaded a mutable ``latest`` asset, maintained its own
    ``version.json`` and could fall back to a database embedded in the wheel.
    Those responsibilities now belong to the common dataset contract.  A
    verified cache or ``CATALOGMX_SHARED_DATA`` is the only offline source.
    """

    def __init__(self, cache_dir: str | Path | None = None):
        self.cache_dir = Path(cache_dir) if cache_dir is not None else CACHE_DIR
        # Keep these attributes for callers that introspect the legacy object.
        # They are migration/cleanup locations, not authoritative resolver state.
        self.cache_db = self.cache_dir / DATABASE_NAME
        self.version_file = self.cache_dir / "version.json"

    def _resolver(
        self,
        *,
        mode: str,
        max_age_hours: int | float | None = None,
    ) -> DatasetResolver:
        ttl_seconds = None
        if max_age_hours is not None:
            ttl_seconds = max(1, int(float(max_age_hours) * 3600))
        return DatasetResolver(
            cache_dir=self.cache_dir,
            mode=mode,
            cache_ttl_seconds=ttl_seconds,
        )

    @staticmethod
    def _database_from_root(root: Path) -> Path:
        path = root / DATABASE_NAME
        if not path.is_file():
            raise FileNotFoundError(f"resolved {DATASET_ID} artifact is missing {DATABASE_NAME}")
        return path

    def _cached_database_path(self) -> Path | None:
        resolver = self._resolver(mode="offline")
        status = resolver.cache_status(DATASET_ID)
        if not status.get("cached") or not resolver.verify_cached_dataset(DATASET_ID):
            return None
        root_value = status.get("root")
        if not isinstance(root_value, str):
            return None
        path = Path(root_value) / DATABASE_NAME
        return path if path.is_file() else None

    def get_local_version(self) -> str | None:
        """Return the version stored in the verified resolver cache, if any."""
        path = self._cached_database_path()
        return self._verify_database(path) if path is not None else None

    def get_local_age_hours(self) -> float | None:
        """Return the age of the verified resolver cache metadata."""
        status = self._resolver(mode="offline").cache_status(DATASET_ID)
        fetched_at = status.get("fetched_at")
        if not isinstance(fetched_at, str):
            return None
        try:
            fetched = datetime.fromisoformat(fetched_at.replace("Z", "+00:00"))
        except ValueError:
            return None
        if fetched.tzinfo is None:
            fetched = fetched.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - fetched.astimezone(timezone.utc)).total_seconds() / 3600

    def _verify_database(self, db_path: Path | None) -> str | None:
        """Verify SQLite readability and return its declared data version."""
        if db_path is None or not db_path.is_file():
            return None
        try:
            with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as db:
                row = db.execute("SELECT value FROM _metadata WHERE key = 'version'").fetchone()
            return str(row[0]) if row else None
        except (sqlite3.Error, OSError):
            return None

    def download_latest(self, force: bool = False, verbose: bool = True) -> bool:
        """Synchronize the verified immutable release selected by its stable pointer."""
        del force  # The explicit operation always resolves the current pointer.
        try:
            root = self._resolver(mode="refresh").fetch_dataset(DATASET_ID)
            path = self._database_from_root(root)
            version = self._verify_database(path)
            if version is None:
                raise RuntimeError("resolved dynamic database failed SQLite metadata verification")
            if verbose:
                print(f"Data synchronized to version {version}")
            return True
        except Exception as exc:
            if verbose:
                print(f"Error synchronizing data: {exc}")
            return False

    def auto_update(self, max_age_hours: int = 24, verbose: bool = False) -> Path:
        """Resolve dynamic data and refresh verified cache entries older than the TTL.

        ``max_age_hours`` is retained for API compatibility and is translated to
        the resolver TTL.  Network failures may fall back only to a previously
        verified resolver object; unverified legacy caches and wheel snapshots
        are deliberately excluded.
        """
        mode = "refresh" if AUTO_UPDATE_ENABLED else "offline"
        resolver = self._resolver(mode=mode, max_age_hours=max_age_hours)
        try:
            return self._database_from_root(resolver.resolve_dataset_root(DATASET_ID))
        except Exception as exc:
            if verbose:
                print(f"Error resolving data: {exc}")
            raise

    def get_database_path(self, auto_update: bool = True, max_age_hours: int = 24) -> Path:
        """Return the resolved SQLite artifact path."""
        if auto_update:
            return self.auto_update(max_age_hours=max_age_hours)
        resolver = self._resolver(mode="offline", max_age_hours=max_age_hours)
        return self._database_from_root(resolver.resolve_dataset_root(DATASET_ID))

    def get_version_info(self) -> dict[str, str]:
        """Return compatibility metadata derived from resolver state."""
        status = self._resolver(mode="offline").cache_status(DATASET_ID)
        version = self.get_local_version()
        age = self.get_local_age_hours()
        if not status.get("cached"):
            return {
                "version": "unknown",
                "source": "none",
                "age_hours": "N/A",
                "updated_at": "N/A",
            }
        return {
            "version": version or "unknown",
            "source": "dataset_resolver",
            "age_hours": f"{age:.1f}" if age is not None else "N/A",
            "updated_at": str(status.get("fetched_at") or "N/A"),
            "content_sha256": str(status.get("content_sha256") or "N/A"),
            "release_tag": str(status.get("release_tag") or "N/A"),
        }

    def clear_cache(self) -> bool:
        """Clear resolver state plus obsolete legacy cache metadata."""
        try:
            self._resolver(mode="offline").clear_cache(DATASET_ID)
            self.cache_db.unlink(missing_ok=True)
            self.version_file.unlink(missing_ok=True)
            return True
        except OSError:
            return False

    def clearCache(self) -> bool:
        """Deprecated camelCase alias for :meth:`clear_cache`."""
        return self.clear_cache()


_default_updater = DataUpdater()


def get_database_path(auto_update: bool = True, max_age_hours: int = 24) -> Path:
    return _default_updater.get_database_path(auto_update, max_age_hours)


def get_version() -> str | None:
    return _default_updater.get_local_version()


def update_now(force: bool = False, verbose: bool = True) -> bool:
    return _default_updater.download_latest(force=force, verbose=verbose)


__all__ = [
    "AUTO_UPDATE_ENABLED",
    "CACHE_DB",
    "CACHE_DIR",
    "DATABASE_NAME",
    "DATASET_ID",
    "DataUpdater",
    "EMBEDDED_DB",
    "GITHUB_RELEASE_URL",
    "VERSION_FILE",
    "get_database_path",
    "get_version",
    "update_now",
]
