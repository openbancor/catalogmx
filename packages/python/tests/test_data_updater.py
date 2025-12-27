"""
Tests for DataUpdater module

Tests the automatic update system for dynamic data from GitHub Releases.
"""

import os
import sqlite3
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from catalogmx.data.updater import DataUpdater, get_database_path, get_version, update_now


class TestDataUpdater:
    """Test DataUpdater class"""

    def test_init_default(self):
        """Test initialization with default config"""
        updater = DataUpdater()
        assert updater is not None

    def test_init_custom_cache_dir(self):
        """Test initialization with custom cache directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            updater = DataUpdater(cache_dir=Path(tmpdir))
            assert updater.cache_dir == Path(tmpdir)

    def test_get_local_version_no_cache(self):
        """Test getting local version when no cache exists"""
        with tempfile.TemporaryDirectory() as tmpdir:
            updater = DataUpdater(cache_dir=Path(tmpdir))
            version = updater.get_local_version()
            assert version is None

    def test_get_local_age_hours_no_cache(self):
        """Test getting age when no cache exists"""
        with tempfile.TemporaryDirectory() as tmpdir:
            updater = DataUpdater(cache_dir=Path(tmpdir))
            age = updater.get_local_age_hours()
            assert age is None

    @mock.patch("catalogmx.data.updater.urllib.request.urlretrieve")
    def test_download_latest_success(self, mock_urlretrieve):
        """Test successful download"""
        with tempfile.TemporaryDirectory() as tmpdir:
            updater = DataUpdater(cache_dir=Path(tmpdir))

            # Create a mock SQLite database
            temp_db = Path(tmpdir) / "test.db"
            db = sqlite3.connect(temp_db)
            db.execute("CREATE TABLE _metadata (key TEXT, value TEXT)")
            db.execute("INSERT INTO _metadata VALUES ('version', '2025-12-04')")
            db.commit()
            db.close()

            # Mock urlretrieve to copy our test db
            def mock_retrieve(url, filename):
                import shutil

                shutil.copy(temp_db, filename)

            mock_urlretrieve.side_effect = mock_retrieve

            # Test download
            result = updater.download_latest(verbose=False)
            assert result is True

            # Verify version was saved
            version = updater.get_local_version()
            assert version == "2025-12-04"

    def test_auto_update_with_embedded_fallback(self):
        """Test auto_update falls back to embedded when download fails"""
        with tempfile.TemporaryDirectory() as tmpdir:
            updater = DataUpdater(cache_dir=Path(tmpdir))

            # Disable auto-update to test fallback
            with mock.patch.dict(os.environ, {"CATALOGMX_AUTO_UPDATE": "false"}):
                db_path = updater.auto_update(verbose=False)

                # Should return embedded path
                assert db_path.exists()
                assert db_path.name == "mexico_dynamic.sqlite3"

    def test_get_database_path_no_auto_update(self):
        """Test getting database path without auto-update"""
        with tempfile.TemporaryDirectory() as tmpdir:
            updater = DataUpdater(cache_dir=Path(tmpdir))

            # Should return embedded path when no cache
            db_path = updater.get_database_path(auto_update=False)
            assert db_path.exists()

    def test_clear_cache(self):
        """Test clearing cache"""
        with tempfile.TemporaryDirectory() as tmpdir:
            updater = DataUpdater(cache_dir=Path(tmpdir))

            # Create fake cache files
            cache_db = updater.cache_db
            version_file = updater.version_file

            cache_db.parent.mkdir(parents=True, exist_ok=True)
            cache_db.touch()
            version_file.touch()

            assert cache_db.exists()
            assert version_file.exists()

            # Clear cache
            result = updater.clearCache()
            assert result is True
            assert not cache_db.exists()
            assert not version_file.exists()

    def test_environment_variables(self):
        """Test configuration via environment variables"""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_vars = {
                "CATALOGMX_CACHE_DIR": tmpdir,
                "CATALOGMX_AUTO_UPDATE": "false",
                "CATALOGMX_DATA_URL": "https://example.com/test.db",
            }

            with mock.patch.dict(os.environ, env_vars):
                # Need to reload module to pick up new env vars
                from catalogmx.data import updater as updater_module
                from importlib import reload

                reload(updater_module)

                assert updater_module.CACHE_DIR == Path(tmpdir)
                assert updater_module.AUTO_UPDATE_ENABLED is False


class TestConvenienceFunctions:
    """Test convenience functions"""

    def test_get_database_path(self):
        """Test get_database_path function"""
        db_path = get_database_path(auto_update=False)
        assert db_path.exists()
        assert db_path.name == "mexico_dynamic.sqlite3"

    def test_get_version_no_cache(self):
        """Test get_version with no cache"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch("catalogmx.data.updater.CACHE_DIR", Path(tmpdir)):
                version = get_version()
                # May return None (no cache) or a version (embedded)
                assert version is None or isinstance(version, str)

    @mock.patch("catalogmx.data.updater.DataUpdater.download_latest")
    def test_update_now(self, mock_download):
        """Test update_now function"""
        mock_download.return_value = True

        result = update_now(force=True, verbose=False)
        assert result is True
        mock_download.assert_called_once()


class TestDatabaseIntegrity:
    """Test database integrity and structure"""

    def test_embedded_database_exists(self):
        """Test that embedded database exists and is valid"""
        from catalogmx.data.updater import EMBEDDED_DB

        assert EMBEDDED_DB.exists()

        # Verify it's a valid SQLite database
        db = sqlite3.connect(EMBEDDED_DB)
        cursor = db.execute("SELECT value FROM _metadata WHERE key = 'version'")
        version = cursor.fetchone()
        db.close()

        assert version is not None
        assert isinstance(version[0], str)

    def test_embedded_database_has_required_tables(self):
        """Test that embedded database has all required tables"""
        from catalogmx.data.updater import EMBEDDED_DB

        db = sqlite3.connect(EMBEDDED_DB)

        # Check for required tables
        cursor = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = {row[0] for row in cursor.fetchall()}

        required_tables = {
            "_metadata",
            "udis",
            "tipo_cambio",
            "tiie",
            "cetes",
            "inflacion",
            "salarios_minimos",
        }

        assert required_tables.issubset(tables), f"Missing tables: {required_tables - tables}"

        db.close()

    def test_embedded_database_has_data(self):
        """Test that embedded database has actual data"""
        from catalogmx.data.updater import EMBEDDED_DB

        db = sqlite3.connect(EMBEDDED_DB)

        # Check UDIs count
        cursor = db.execute("SELECT COUNT(*) FROM udis")
        udi_count = cursor.fetchone()[0]
        assert udi_count > 10000, "UDIs table should have 10,000+ records"

        # Check tipo_cambio count
        cursor = db.execute("SELECT COUNT(*) FROM tipo_cambio")
        tc_count = cursor.fetchone()[0]
        assert tc_count > 20000, "tipo_cambio table should have 20,000+ records"

        db.close()

    def test_database_has_indexes(self):
        """Test that database has proper indexes"""
        from catalogmx.data.updater import EMBEDDED_DB

        db = sqlite3.connect(EMBEDDED_DB)

        # Check for indexes
        cursor = db.execute(
            "SELECT name FROM sqlite_master WHERE type='index' ORDER BY name"
        )
        indexes = {row[0] for row in cursor.fetchall()}

        # Should have at least some indexes
        assert "idx_udis_anio_mes" in indexes
        assert "idx_tipo_cambio_fuente" in indexes

        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
