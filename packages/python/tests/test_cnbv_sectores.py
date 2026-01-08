"""Tests for CNBV sectors catalog."""

import pytest

from catalogmx.catalogs.cnbv.sectores import (
    ReguladorFinanciero,
    SectoresCNBV,
)


class TestSectoresCNBV:
    """Tests for SectoresCNBV catalog."""

    def test_get_all_returns_list(self):
        """Test that get_all returns a list."""
        sectores = SectoresCNBV.get_all()
        assert isinstance(sectores, list)

    def test_get_all_has_sectors(self):
        """Test that there are sectors in the catalog."""
        sectores = SectoresCNBV.get_all()
        assert len(sectores) > 0

    def test_sector_has_required_fields(self):
        """Test that sectors have required fields."""
        sectores = SectoresCNBV.get_all()
        for sector in sectores[:3]:
            assert "id" in sector
            assert "nombre" in sector

    def test_get_by_id_valid(self):
        """Test getting a sector by valid ID."""
        sectores = SectoresCNBV.get_all()
        if sectores:
            first_id = sectores[0]["id"]
            sector = SectoresCNBV.get_by_id(first_id)
            assert sector is not None
            assert sector["id"] == first_id

    def test_get_by_id_invalid(self):
        """Test getting a sector by invalid ID."""
        sector = SectoresCNBV.get_by_id("INVALID_ID_12345")
        assert sector is None

    def test_is_valid_with_valid_id(self):
        """Test is_valid with valid ID."""
        sectores = SectoresCNBV.get_all()
        if sectores:
            first_id = sectores[0]["id"]
            assert SectoresCNBV.is_valid(first_id) is True

    def test_is_valid_with_invalid_id(self):
        """Test is_valid with invalid ID."""
        assert SectoresCNBV.is_valid("INVALID_ID_12345") is False

    def test_search_by_name(self):
        """Test searching sectors by name."""
        results = SectoresCNBV.search("banca")
        assert isinstance(results, list)
        # Should find at least one banking-related sector

    def test_search_by_description(self):
        """Test searching sectors by description."""
        results = SectoresCNBV.search("financier")
        assert isinstance(results, list)

    def test_search_empty_query(self):
        """Test searching with empty query."""
        results = SectoresCNBV.search("")
        assert isinstance(results, list)

    def test_search_not_found(self):
        """Test searching for non-existent term."""
        results = SectoresCNBV.search("xyz12345notfound")
        assert results == []

    def test_get_by_regulador(self):
        """Test getting sectors by regulator."""
        results = SectoresCNBV.get_by_regulador("CNBV")
        assert isinstance(results, list)

    def test_get_by_regulador_case_insensitive(self):
        """Test that regulador search is case-insensitive."""
        results1 = SectoresCNBV.get_by_regulador("CNBV")
        results2 = SectoresCNBV.get_by_regulador("cnbv")
        assert len(results1) == len(results2)

    def test_get_by_regulador_not_found(self):
        """Test getting sectors by non-existent regulator."""
        results = SectoresCNBV.get_by_regulador("INVALID_REG")
        assert results == []

    def test_count(self):
        """Test sector count."""
        count = SectoresCNBV.count()
        assert count > 0
        assert count == len(SectoresCNBV.get_all())


class TestReguladorFinanciero:
    """Tests for ReguladorFinanciero catalog."""

    def test_get_all_returns_list(self):
        """Test that get_all returns a list."""
        reguladores = ReguladorFinanciero.get_all()
        assert isinstance(reguladores, list)

    def test_get_all_has_regulators(self):
        """Test that there are regulators in the catalog."""
        reguladores = ReguladorFinanciero.get_all()
        assert len(reguladores) > 0

    def test_regulador_has_required_fields(self):
        """Test that regulators have required fields."""
        reguladores = ReguladorFinanciero.get_all()
        for reg in reguladores[:3]:
            assert "id" in reg
            assert "nombre" in reg
            assert "siglas" in reg

    def test_get_by_id_valid(self):
        """Test getting a regulator by valid ID."""
        reguladores = ReguladorFinanciero.get_all()
        if reguladores:
            first_id = reguladores[0]["id"]
            reg = ReguladorFinanciero.get_by_id(first_id)
            assert reg is not None
            assert reg["id"] == first_id

    def test_get_by_id_invalid(self):
        """Test getting a regulator by invalid ID."""
        reg = ReguladorFinanciero.get_by_id("INVALID_ID_12345")
        assert reg is None

    def test_get_by_siglas_valid(self):
        """Test getting a regulator by siglas."""
        # CNBV should be a common regulator
        reg = ReguladorFinanciero.get_by_siglas("CNBV")
        if reg:
            assert reg["siglas"].upper() == "CNBV"

    def test_get_by_siglas_case_insensitive(self):
        """Test that siglas search is case-insensitive."""
        reg1 = ReguladorFinanciero.get_by_siglas("CNBV")
        reg2 = ReguladorFinanciero.get_by_siglas("cnbv")
        # Both should return same result or None
        if reg1:
            assert reg2 is not None
            assert reg1["id"] == reg2["id"]

    def test_get_by_siglas_invalid(self):
        """Test getting a regulator by invalid siglas."""
        reg = ReguladorFinanciero.get_by_siglas("INVALID_SIGLAS")
        assert reg is None

    def test_count(self):
        """Test regulator count."""
        count = ReguladorFinanciero.count()
        assert count > 0
        assert count == len(ReguladorFinanciero.get_all())


class TestCNBVDataIntegrity:
    """Tests for CNBV data integrity."""

    def test_sectors_have_unique_ids(self):
        """Test that all sector IDs are unique."""
        sectores = SectoresCNBV.get_all()
        ids = [s["id"] for s in sectores]
        assert len(ids) == len(set(ids))

    def test_regulators_have_unique_ids(self):
        """Test that all regulator IDs are unique."""
        reguladores = ReguladorFinanciero.get_all()
        ids = [r["id"] for r in reguladores]
        assert len(ids) == len(set(ids))

    def test_regulators_have_unique_siglas(self):
        """Test that all regulator siglas are unique."""
        reguladores = ReguladorFinanciero.get_all()
        siglas = [r["siglas"] for r in reguladores]
        assert len(siglas) == len(set(siglas))
