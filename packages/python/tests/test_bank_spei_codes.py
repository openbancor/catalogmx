"""Tests for the 5-digit SPEI participant code model of BankCatalog."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from catalogmx.catalogs.banxico import BankCatalog

SNAPSHOT = (
    Path(__file__).resolve().parents[2] / "shared-data" / "banxico" / "spei_institutions.json"
)
HISTORICAL = ("143", "608", "630")
NEW_PARTICIPANTS = {"40170": "REVOLUT BANK", "90660": "Altor", "90714": "PPBALANCEMX"}


def test_lookup_by_five_digit_spei_code():
    bank = BankCatalog.get_bank_by_spei_code("40012")
    assert bank is not None
    assert bank["code"] == "012"
    assert bank["spei_code"] == "40012"
    assert bank["status"] == "active"


def test_lookup_by_three_digit_clabe_code_keeps_compatibility():
    assert BankCatalog.get_bank_by_clabe_code("012") == BankCatalog.get_bank_by_code("012")
    assert BankCatalog.get_bank_by_code("12")["spei_code"] == "40012"


def test_spei_code_lookup_rejects_unknown_and_malformed():
    assert BankCatalog.get_bank_by_spei_code("99999") is None
    assert BankCatalog.get_bank_by_spei_code("012") is None
    assert BankCatalog.get_bank_by_spei_code("abcde") is None


def test_banxico_central_bank_uses_its_four_digit_official_key():
    bank = BankCatalog.get_bank_by_spei_code("2001")
    assert bank is not None and bank["code"] == "001"


def test_validate_spei_code_matches_three_digit_code():
    assert BankCatalog.validate_spei_code("40012", "012") is True
    assert BankCatalog.validate_spei_code("40012", "014") is False
    assert BankCatalog.validate_spei_code("40012") is True
    assert BankCatalog.validate_spei_code("90000") is False
    assert BankCatalog.validate_spei_code("2001", "001") is True


def test_new_participants_present_without_invented_data():
    for spei_code, name in NEW_PARTICIPANTS.items():
        bank = BankCatalog.get_bank_by_spei_code(spei_code)
        assert bank is not None
        assert bank["name"] == name
        assert bank["code"] == spei_code[-3:]
        assert bank["spei"] is True
        assert bank["full_name"] is None
        assert bank["rfc"] is None
        assert bank["tipo_institucion"] is None


@pytest.mark.parametrize("code", HISTORICAL)
def test_disaffiliated_banks_resolve_by_three_digits_with_historical_mark(code):
    bank = BankCatalog.get_bank_by_code(code)
    assert bank is not None
    assert bank["status"] == "historical"
    assert bank["spei_code"] is None
    assert bank["spei"] is False
    assert bank["spei_disaffiliated"] is True
    assert bank["spei_disaffiliation_date"] is None
    assert BankCatalog.is_spei_participant(code) is False


def test_active_listing_excludes_historical_and_flag_includes_them():
    active = {b["code"] for b in BankCatalog.get_spei_banks()}
    assert not active & set(HISTORICAL)
    with_hist = {b["code"] for b in BankCatalog.get_spei_banks(include_historical=True)}
    assert set(HISTORICAL) <= with_hist
    assert active < with_hist
    assert all(b["spei_code"] for b in BankCatalog.get_spei_banks())


def test_get_all_banks_still_returns_whole_catalog():
    codes = {b["code"] for b in BankCatalog.get_all_banks()}
    assert set(HISTORICAL) <= codes
    assert len(codes) == 100


def test_active_spei_codes_match_official_snapshot_and_three_digit_suffix():
    snapshot = {item["banxico_key"] for item in json.loads(SNAPSHOT.read_text("utf-8"))}
    banks = BankCatalog.get_spei_banks()
    assert {b["spei_code"] for b in banks} == snapshot
    assert len(snapshot) == 97
    for bank in banks:
        assert bank["code"] == bank["spei_code"][-3:]
        assert BankCatalog.validate_spei_code(bank["spei_code"], bank["code"])


def test_provenance_fields_present_on_every_record():
    for bank in BankCatalog.get_all_banks():
        assert bank["spei_verified_at"] == "2026-10-27"
        assert "instituciones.do" in bank["spei_source"]


def test_default_listing_excludes_historical_even_when_spei_flag_is_true(monkeypatch):
    BankCatalog.get_all_banks()
    rows = BankCatalog._data + [
        {"code": "999", "name": "OLD", "spei": True, "status": "historical", "spei_code": None}
    ]
    monkeypatch.setattr(BankCatalog, "_data", rows)
    assert "999" not in {b["code"] for b in BankCatalog.get_spei_banks()}
    assert "999" in {b["code"] for b in BankCatalog.get_spei_banks(include_historical=True)}
