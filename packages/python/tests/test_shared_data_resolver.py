"""Compatibility tests for legacy shared-data paths backed by datasets."""

from __future__ import annotations

from pathlib import Path

import pytest

from catalogmx.utils import shared_data


def test_banxico_legacy_path_can_fall_through_to_dataset_resolver(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    target = tmp_path / "banks.json"
    target.write_text("[]\n", encoding="utf-8")
    monkeypatch.delenv("CATALOGMX_SHARED_DATA", raising=False)
    monkeypatch.setattr(shared_data, "_local_roots", lambda: [])

    from catalogmx.data import resolver

    calls = []

    def fake_get_dataset_path(dataset_id: str, *parts: str) -> Path:
        calls.append((dataset_id, parts))
        return target

    monkeypatch.setattr(resolver, "get_dataset_path", fake_get_dataset_path)
    assert shared_data.get_shared_data_path("banxico", "banks.json") == target
    assert calls == [("banxico.reference", ("banks.json",))]


def test_invalid_shared_data_override_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    missing = tmp_path / "missing"
    monkeypatch.setenv("CATALOGMX_SHARED_DATA", str(missing))
    with pytest.raises(FileNotFoundError, match="CATALOGMX_SHARED_DATA"):
        shared_data.get_shared_data_path("banxico", "banks.json")
