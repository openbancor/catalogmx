"""Public Python access to the generated fiscal data manifest."""

from __future__ import annotations

import re

import pytest

from catalogmx._fiscal_ids import FISCAL_DATASET_IDS
from catalogmx.fiscal import (
    assert_fiscal_data_verified,
    fiscal_dataset_ids,
    fiscal_entry,
    fiscal_manifest,
    fiscal_manifest_for_exercise,
    fiscal_sources,
)


def test_exposes_the_generated_fiscal_manifest_with_defensive_nested_data():
    manifest = fiscal_manifest()

    assert manifest["manifest_id"] == "catalogmx.fiscal"
    assert re.fullmatch(r"^[0-9a-f]{64}$", manifest["content_sha256"])
    assert FISCAL_DATASET_IDS == tuple(manifest["datasets"])

    manifest["datasets"]["uma"]["entries"]["2026"]["status"] = "pending_review"

    assert fiscal_entry("uma", 2026) is not None
    assert fiscal_entry("uma", 2026)["status"] == "verified"


def test_entry_and_sources_match_the_typescript_missing_entry_contract():
    assert fiscal_entry("uma", 1900) is None
    assert fiscal_sources("uma", 1900) == []

    entry = fiscal_entry("uma", 2026)
    assert entry is not None
    entry["status"] = "pending_review"
    assert fiscal_entry("uma", 2026)["status"] == "verified"

    sources = fiscal_sources("uma", 2026)
    assert sources[0]["source"] is not None
    sources[0]["source"]["authority"] = "mutated"
    assert fiscal_sources("uma", 2026)[0]["source"]["authority"] == "INEGI"


def test_manifest_for_exercise_returns_defensive_entries():
    exercise_manifest = fiscal_manifest_for_exercise(2026)

    assert exercise_manifest["exercise"] == 2026
    assert exercise_manifest["entries"]["uma"]["status"] == "verified"

    exercise_manifest["entries"]["uma"]["status"] = "pending_review"

    assert fiscal_manifest_for_exercise(2026)["entries"]["uma"]["status"] == "verified"


def test_assert_fiscal_data_verified_rejects_missing_and_pending_entries():
    assert assert_fiscal_data_verified("uma", 2026)["status"] == "verified"

    with pytest.raises(ValueError, match="No fiscal data for uma exercise 1900"):
        assert_fiscal_data_verified("uma", 1900)
    with pytest.raises(
        ValueError,
        match="Fiscal data isr_payroll exercise 2026 is pending_review, not verified",
    ):
        assert_fiscal_data_verified("isr_payroll", 2026)


def test_modalidad_10_uses_the_documented_legacy_status():
    entry = fiscal_entry("imss_modalidad_10", 2026)

    assert entry is not None
    assert entry["status"] == "legacy_unverified"
    assert "imss_modalidad_10" in fiscal_dataset_ids()
