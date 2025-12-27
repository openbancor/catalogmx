"""
Data Updater - Automatic download of dynamic data from GitHub Releases

This module allows catalogmx to update dynamic data (UDI, exchange rates, TIIE, etc.)
without requiring a new library release. Data is downloaded from GitHub Releases
and cached locally.

Usage:
    from catalogmx.data import DataUpdater

    # Automatic update (recommended)
    updater = DataUpdater()
    db_path = updater.auto_update(max_age_hours=24)

    # Manual update
    updater.download_latest()

    # Check version
    version = updater.get_local_version()
"""

import json
import os
import shutil
import sqlite3
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path


# Configuration
GITHUB_RELEASE_URL = os.getenv(
    "CATALOGMX_DATA_URL",
    "https://github.com/openbancor/catalogmx/releases/download/latest/mexico_dynamic.sqlite3",
)

CACHE_DIR = Path(os.getenv("CATALOGMX_CACHE_DIR", str(Path.home() / ".catalogmx")))
CACHE_DB = CACHE_DIR / "mexico_dynamic.sqlite3"
VERSION_FILE = CACHE_DIR / "version.json"

# Embedded fallback database (included in package)
EMBEDDED_DB = Path(__file__).parent / "mexico_dynamic.sqlite3"

# Auto-update enabled by default
AUTO_UPDATE_ENABLED = os.getenv("CATALOGMX_AUTO_UPDATE", "true").lower() in (
    "true",
    "1",
    "yes",
)


class DataUpdater:
    """
    Manages automatic updates of dynamic data from GitHub Releases

    This class handles downloading, caching, and version management of the
    dynamic data SQLite database, allowing data updates without library releases.
    """

    def __init__(self, cache_dir: Path | None = None):
        """
        Initialize DataUpdater

        :param cache_dir: Custom cache directory (default: ~/.catalogmx)
        """
        self.cache_dir = cache_dir or CACHE_DIR
        self.cache_db = self.cache_dir / "mexico_dynamic.sqlite3"
        self.version_file = self.cache_dir / "version.json"

        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_local_version(self) -> str | None:
        """
        Get version of local cached data

        :return: Version string (e.g., "2025-12-04") or None if no cache
        """
        if not self.version_file.exists():
            return None

        try:
            with open(self.version_file, encoding="utf-8") as f:
                return json.load(f).get("version")
        except (json.JSONDecodeError, OSError):
            return None

    def get_local_age_hours(self) -> float | None:
        """
        Get age of local cached data in hours

        :return: Age in hours or None if no cache
        """
        if not self.version_file.exists():
            return None

        try:
            with open(self.version_file, encoding="utf-8") as f:
                data = json.load(f)
                updated_str = data.get("updated_at")
                if not updated_str:
                    return None

                updated = datetime.fromisoformat(updated_str)
                return (datetime.now() - updated).total_seconds() / 3600
        except (json.JSONDecodeError, OSError, ValueError):
            return None

    def _verify_database(self, db_path: Path) -> str | None:
        """
        Verify database integrity and get version

        :param db_path: Path to database file
        :return: Version string or None if invalid
        """
        try:
            db = sqlite3.connect(db_path)
            cursor = db.execute("SELECT value FROM _metadata WHERE key = 'version'")
            row = cursor.fetchone()
            db.close()

            if row:
                return row[0]
            return None
        except (sqlite3.Error, OSError):
            return None

    def download_latest(self, force: bool = False, verbose: bool = True) -> bool:
        """
        Download latest version of data from GitHub Releases

        :param force: Force download even if cache is recent
        :param verbose: Print progress messages
        :return: True if download successful, False otherwise
        """
        if verbose:
            print(f"📥 Downloading data from {GITHUB_RELEASE_URL}...")

        try:
            # Download to temporary file
            temp_db = self.cache_dir / "mexico_dynamic.sqlite3.tmp"
            urllib.request.urlretrieve(GITHUB_RELEASE_URL, temp_db)

            # Verify integrity
            version = self._verify_database(temp_db)
            if not version:
                if verbose:
                    print("❌ Downloaded database is invalid or corrupted")
                temp_db.unlink(missing_ok=True)
                return False

            # Move to cache
            shutil.move(str(temp_db), str(self.cache_db))

            # Save metadata
            with open(self.version_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "version": version,
                        "updated_at": datetime.now().isoformat(),
                        "source": "github_releases",
                        "url": GITHUB_RELEASE_URL,
                    },
                    f,
                    indent=2,
                )

            if verbose:
                print(f"✅ Data updated to version {version}")
            return True

        except Exception as e:
            if verbose:
                print(f"❌ Error downloading data: {e}")
            return False

    def auto_update(
        self, max_age_hours: int = 24, verbose: bool = False
    ) -> Path:
        """
        Auto-update with intelligent fallback

        This method:
        1. Checks if local cache exists and is recent
        2. Downloads update if cache is old or missing
        3. Falls back to cache if download fails
        4. Falls back to embedded data if no cache exists

        :param max_age_hours: Maximum age before updating (default 24 hours)
        :param verbose: Print progress messages
        :return: Path to database to use
        """
        if not AUTO_UPDATE_ENABLED:
            # Auto-update disabled, use cache or embedded
            if self.cache_db.exists():
                return self.cache_db
            if EMBEDDED_DB.exists():
                return EMBEDDED_DB
            raise FileNotFoundError("No database available and auto-update is disabled")

        age = self.get_local_age_hours()

        # If no cache or cache is old, try to update
        if age is None or age > max_age_hours:
            if self.download_latest(verbose=verbose):
                return self.cache_db

        # If cache exists (even if update failed), use it
        if self.cache_db.exists():
            if verbose and age is not None:
                print(f"ℹ️  Using cached data (age: {age:.1f} hours)")
            return self.cache_db

        # Fallback: embedded data
        if EMBEDDED_DB.exists():
            if verbose:
                print("⚠️  Using embedded data (may be outdated)")
            return EMBEDDED_DB

        raise FileNotFoundError(
            "No database available. Please check your internet connection or manually download the database."
        )

    def get_database_path(self, auto_update: bool = True, max_age_hours: int = 24) -> Path:
        """
        Get path to database (with or without auto-update)

        :param auto_update: Enable auto-update (default True)
        :param max_age_hours: Maximum age before updating (default 24 hours)
        :return: Path to database file
        """
        if auto_update:
            return self.auto_update(max_age_hours=max_age_hours)

        # No auto-update, use cache or embedded
        if self.cache_db.exists():
            return self.cache_db

        if EMBEDDED_DB.exists():
            return EMBEDDED_DB

        raise FileNotFoundError("No database available")

    def get_version_info(self) -> dict[str, str]:
        """
        Get detailed version information

        :return: Dictionary with version, age, source, etc.
        """
        if not self.version_file.exists():
            return {
                "version": "unknown",
                "source": "embedded" if EMBEDDED_DB.exists() else "none",
                "age_hours": "N/A",
                "updated_at": "N/A",
            }

        try:
            with open(self.version_file, encoding="utf-8") as f:
                data = json.load(f)

            age = self.get_local_age_hours()
            data["age_hours"] = f"{age:.1f}" if age is not None else "N/A"

            return data
        except (json.JSONDecodeError, OSError):
            return {
                "version": "error",
                "source": "error",
                "age_hours": "N/A",
                "updated_at": "N/A",
            }

    def clear_cache(self) -> bool:
        """
        Clear local cache

        :return: True if cache cleared successfully
        """
        try:
            if self.cache_db.exists():
                self.cache_db.unlink()
            if self.version_file.exists():
                self.version_file.unlink()
            return True
        except OSError:
            return False


# Singleton instance for convenience
_default_updater = DataUpdater()


def get_database_path(auto_update: bool = True, max_age_hours: int = 24) -> Path:
    """
    Get path to dynamic data database

    Convenience function using default updater instance.

    :param auto_update: Enable auto-update (default True)
    :param max_age_hours: Maximum age before updating (default 24 hours)
    :return: Path to database file
    """
    return _default_updater.get_database_path(auto_update, max_age_hours)


def get_version() -> str | None:
    """
    Get version of local cached data

    Convenience function using default updater instance.

    :return: Version string or None
    """
    return _default_updater.get_local_version()


def update_now(force: bool = False, verbose: bool = True) -> bool:
    """
    Force update data now

    Convenience function using default updater instance.

    :param force: Force download even if cache is recent
    :param verbose: Print progress messages
    :return: True if successful
    """
    return _default_updater.download_latest(force=force, verbose=verbose)


# Export public API
__all__ = [
    "DataUpdater",
    "get_database_path",
    "get_version",
    "update_now",
    "CACHE_DIR",
    "AUTO_UPDATE_ENABLED",
]
