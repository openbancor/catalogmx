"""Compatibility tests for the legacy DataUpdater facade."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from unittest import mock

import pytest

from catalogmx.data import updater as updater_module
from catalogmx.data.updater import DATASET_ID, DataUpdater


def _database(root: Path, version: str = "2026-08-31") -> Path:
    root.mkdir(parents=True, exist_ok=True)
    path = root / "mexico_dynamic.sqlite3"
    with sqlite3.connect(path) as db:
        db.execute("CREATE TABLE _metadata (key TEXT, value TEXT)")
        db.execute("INSERT INTO _metadata VALUES ('version', ?)", (version,))
    return path


def test_custom_cache_dir_is_retained_for_compatibility(tmp_path: Path) -> None:
    updater = DataUpdater(cache_dir=tmp_path)
    assert updater.cache_dir == tmp_path
    assert updater.cache_db == tmp_path / "mexico_dynamic.sqlite3"
    assert updater.version_file == tmp_path / "version.json"


def test_verify_database_reads_dynamic_metadata(tmp_path: Path) -> None:
    updater = DataUpdater(cache_dir=tmp_path / "cache")
    database = _database(tmp_path / "artifact", "2026-09-01")
    assert updater._verify_database(database) == "2026-09-01"

    invalid = tmp_path / "invalid.sqlite3"
    invalid.write_text("not sqlite", encoding="utf-8")
    assert updater._verify_database(invalid) is None


def test_auto_update_delegates_to_refresh_resolver_with_legacy_24h_ttl(
    tmp_path: Path,
) -> None:
    root = tmp_path / "dynamic"
    database = _database(root)
    resolver = mock.Mock()
    resolver.resolve_dataset_root.return_value = root

    with mock.patch(
        "catalogmx.data.updater.DatasetResolver", return_value=resolver
    ) as resolver_type:
        updater = DataUpdater(cache_dir=tmp_path / "cache")
        assert updater.auto_update(max_age_hours=24) == database

    resolver_type.assert_called_once_with(
        cache_dir=tmp_path / "cache",
        mode="refresh",
        cache_ttl_seconds=86400,
    )
    resolver.resolve_dataset_root.assert_called_once_with(DATASET_ID)


def test_auto_update_disabled_delegates_to_offline_resolver(tmp_path: Path) -> None:
    root = tmp_path / "dynamic"
    database = _database(root)
    resolver = mock.Mock()
    resolver.resolve_dataset_root.return_value = root

    with (
        mock.patch.object(updater_module, "AUTO_UPDATE_ENABLED", False),
        mock.patch(
            "catalogmx.data.updater.DatasetResolver", return_value=resolver
        ) as resolver_type,
    ):
        updater = DataUpdater(cache_dir=tmp_path / "cache")
        assert updater.auto_update() == database

    resolver_type.assert_called_once_with(
        cache_dir=tmp_path / "cache",
        mode="offline",
        cache_ttl_seconds=None,
    )


def test_explicit_download_uses_common_dataset_fetch(tmp_path: Path) -> None:
    root = tmp_path / "dynamic"
    _database(root)
    resolver = mock.Mock()
    resolver.fetch_dataset.return_value = root

    with mock.patch("catalogmx.data.updater.DatasetResolver", return_value=resolver):
        updater = DataUpdater(cache_dir=tmp_path / "cache")
        assert updater.download_latest(force=True, verbose=False)

    resolver.fetch_dataset.assert_called_once_with(DATASET_ID)


def test_explicit_download_fails_closed_on_invalid_database(tmp_path: Path) -> None:
    root = tmp_path / "dynamic"
    root.mkdir()
    (root / "mexico_dynamic.sqlite3").write_text("invalid", encoding="utf-8")
    resolver = mock.Mock()
    resolver.fetch_dataset.return_value = root

    with mock.patch("catalogmx.data.updater.DatasetResolver", return_value=resolver):
        updater = DataUpdater(cache_dir=tmp_path / "cache")
        assert not updater.download_latest(verbose=False)


def test_local_version_comes_from_verified_resolver_cache(tmp_path: Path) -> None:
    root = tmp_path / "dynamic"
    _database(root, "2026-08-30")
    resolver = mock.Mock()
    resolver.cache_status.return_value = {
        "cached": True,
        "root": str(root),
        "fetched_at": "2026-08-28T10:00:00+00:00",
    }
    resolver.verify_cached_dataset.return_value = True

    updater = DataUpdater(cache_dir=tmp_path / "cache")
    with mock.patch.object(updater, "_resolver", return_value=resolver):
        assert updater.get_local_version() == "2026-08-30"
        assert updater.get_local_age_hours() is not None


def test_local_version_rejects_unverified_cache(tmp_path: Path) -> None:
    root = tmp_path / "dynamic"
    _database(root)
    resolver = mock.Mock()
    resolver.cache_status.return_value = {"cached": True, "root": str(root)}
    resolver.verify_cached_dataset.return_value = False

    updater = DataUpdater(cache_dir=tmp_path / "cache")
    with mock.patch.object(updater, "_resolver", return_value=resolver):
        assert updater.get_local_version() is None


def test_no_auto_update_uses_declared_bootstrap_when_cache_is_empty(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("CATALOGMX_SHARED_DATA", raising=False)
    updater = DataUpdater(cache_dir=tmp_path / "empty-cache")
    path = updater.get_database_path(auto_update=False)
    assert path == updater_module.EMBEDDED_DB
    assert updater._verify_database(path) is not None


def test_bootstrap_database_has_required_dynamic_tables() -> None:
    assert updater_module.EMBEDDED_DB.is_file()
    with sqlite3.connect(f"file:{updater_module.EMBEDDED_DB}?mode=ro", uri=True) as db:
        tables = {
            row[0]
            for row in db.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
        }
    assert {
        "_metadata",
        "udis",
        "tipo_cambio",
        "tiie",
        "cetes",
        "inflacion",
        "salarios_minimos",
    }.issubset(tables)


def test_clear_cache_delegates_and_removes_obsolete_legacy_files(
    tmp_path: Path,
) -> None:
    updater = DataUpdater(cache_dir=tmp_path)
    updater.cache_db.write_bytes(b"legacy")
    updater.version_file.write_text("{}", encoding="utf-8")
    resolver = mock.Mock()

    with mock.patch.object(updater, "_resolver", return_value=resolver):
        assert updater.clearCache()

    resolver.clear_cache.assert_called_once_with(DATASET_ID)
    assert not updater.cache_db.exists()
    assert not updater.version_file.exists()


def test_convenience_functions_delegate_to_singleton() -> None:
    singleton = mock.Mock()
    singleton.get_database_path.return_value = Path("/tmp/mexico_dynamic.sqlite3")
    singleton.get_local_version.return_value = "2026-08-31"
    singleton.download_latest.return_value = True

    with mock.patch.object(updater_module, "_default_updater", singleton):
        assert updater_module.get_database_path(False, 12) == Path("/tmp/mexico_dynamic.sqlite3")
        assert updater_module.get_version() == "2026-08-31"
        assert updater_module.update_now(force=True, verbose=False)

    singleton.get_database_path.assert_called_once_with(False, 12)
    singleton.download_latest.assert_called_once_with(force=True, verbose=False)


@pytest.mark.parametrize("data_mode", ["offline", "fetch-missing", "refresh"])
def test_explicit_data_mode_outranks_legacy_auto_update_flag(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, data_mode: str
) -> None:
    root = tmp_path / "dynamic"
    database = _database(root)
    resolver = mock.Mock()
    resolver.resolve_dataset_root.return_value = root
    monkeypatch.setenv("CATALOGMX_DATA_MODE", data_mode)

    with (
        mock.patch.object(updater_module, "AUTO_UPDATE_ENABLED", True),
        mock.patch(
            "catalogmx.data.updater.DatasetResolver", return_value=resolver
        ) as resolver_type,
    ):
        updater = DataUpdater(cache_dir=tmp_path / "cache")
        assert updater.auto_update() == database

    resolver_type.assert_called_once_with(
        cache_dir=tmp_path / "cache",
        mode=data_mode,
        cache_ttl_seconds=None,
    )


def test_environment_ttl_reaches_default_dynamic_consumer(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CATALOGMX_CACHE_TTL", "86400")
    updater = DataUpdater(cache_dir=tmp_path / "cache")
    resolver = updater._resolver(mode="refresh")
    assert resolver.cache_ttl_seconds == 86400


def test_registry_freshness_applies_when_no_legacy_or_environment_ttl(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("CATALOGMX_CACHE_TTL", raising=False)
    updater = DataUpdater(cache_dir=tmp_path / "cache")
    resolver = updater._resolver(mode="refresh")
    dataset = resolver._dataset(DATASET_ID)
    assert resolver.cache_ttl_seconds is None
    assert resolver._cache_ttl(dataset) == 2 * 86400


def test_download_latest_honors_explicit_offline_mode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("CATALOGMX_DATA_MODE", "offline")
    updater = DataUpdater(cache_dir=tmp_path / "cache")
    with mock.patch("catalogmx.data.updater.DatasetResolver") as resolver_type:
        resolver = resolver_type.return_value
        resolver.fetch_dataset.side_effect = RuntimeError(
            "cannot fetch or update datasets while CATALOGMX_DATA_MODE=offline"
        )
        assert updater.download_latest(verbose=False) is False

    resolver_type.assert_called_once_with(
        cache_dir=tmp_path / "cache",
        mode="offline",
        cache_ttl_seconds=None,
    )
    resolver.fetch_dataset.assert_called_once_with(DATASET_ID)
