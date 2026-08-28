"""Regression tests for the final code/data lifecycle runtime contract."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from click.testing import CliRunner

from catalogmx.cli import main
from catalogmx.data.resolver import DatasetResolver


CONTRACT = {
    "schema_version": 1,
    "datasets": {
        "example.reference": {
            "artifact": {
                "channel": "data-example-1-latest",
                "discovery": "release-pointer",
                "file": "example.sqlite3",
                "format": "file",
                "manifest": "example.manifest.json",
                "mount_path": "example",
                "version": "1",
            },
            "freshness": {"mode": "interval", "max_age_days": 31},
        }
    },
    "profiles": {"empty": {"datasets": []}},
}


def _state(age_seconds: int) -> dict[str, str]:
    fetched = datetime.now(timezone.utc) - timedelta(seconds=age_seconds)
    return {"fetched_at": fetched.isoformat()}


def test_registry_freshness_remains_default_ttl() -> None:
    resolver = DatasetResolver(contract=CONTRACT, mode="offline")
    dataset = resolver._dataset("example.reference")
    assert resolver._cache_ttl(dataset) == 31 * 86400
    assert not resolver._cache_is_stale(dataset, _state(86400))


def test_cache_ttl_constructor_overrides_dataset_sla() -> None:
    resolver = DatasetResolver(contract=CONTRACT, mode="offline", cache_ttl_seconds=86400)
    dataset = resolver._dataset("example.reference")
    assert resolver._cache_ttl(dataset) == 86400
    assert resolver._cache_is_stale(dataset, _state(86401))


def test_cache_ttl_environment_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CATALOGMX_CACHE_TTL", "86400")
    resolver = DatasetResolver(contract=CONTRACT, mode="offline")
    assert resolver.cache_ttl_seconds == 86400


@pytest.mark.parametrize("value", ["0", "-1", "abc"])
def test_cache_ttl_rejects_invalid_values(monkeypatch: pytest.MonkeyPatch, value: str) -> None:
    monkeypatch.setenv("CATALOGMX_CACHE_TTL", value)
    with pytest.raises(ValueError, match="CATALOGMX_CACHE_TTL"):
        DatasetResolver(contract=CONTRACT, mode="offline")


def test_top_level_fetch_alias_is_available_without_network_for_empty_profile() -> None:
    result = CliRunner().invoke(main, ["fetch", "--profile", "core"])
    assert result.exit_code == 0, result.output
    assert "core: no external datasets required" in result.output


def test_structured_data_fetch_surface_is_preserved() -> None:
    result = CliRunner().invoke(main, ["data", "fetch", "--profile", "core"])
    assert result.exit_code == 0, result.output
    assert "core: no external datasets required" in result.output
