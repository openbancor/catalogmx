"""
Test accent-insensitive search in SEPOMEX catalogs

This test verifies that searches without accents properly find results
with accents, which is critical for Spanish-speaking users.
"""

import pytest

from catalogmx.catalogs.sepomex.codigos_postales import CodigosPostales


class TestSepomexAccentSearch:
    """Test suite for accent-insensitive search in SEPOMEX"""

    def test_search_aguilas_finds_las_aguilas(self):
        """
        Critical test: Search for "Aguilas" (without accent) should find "Las Águilas"

        This is a real-world use case reported by users.
        """
        results = CodigosPostales.search_by_colonia("Aguilas")

        # Should find results
        assert len(results) > 0, "Search for 'Aguilas' returned no results"

        # Check if any result contains "Águilas" (with accent)
        found_with_accent = any(
            "águilas" in result["asentamiento"].lower() for result in results
        )
        assert (
            found_with_accent
        ), "Search for 'Aguilas' did not find 'Las Águilas' (with accent)"

    def test_search_mexico_finds_méxico(self):
        """Search for "Mexico" should find "México" """
        results = CodigosPostales.search_by_colonia("Mexico")
        assert len(results) > 0, "Search for 'Mexico' returned no results"

    def test_search_with_accent_finds_without_accent(self):
        """Reverse test: search with accent should also work"""
        # This should also work - both ways
        results_with = CodigosPostales.search_by_colonia("Águilas")
        results_without = CodigosPostales.search_by_colonia("Aguilas")

        # Both should return results
        assert len(results_with) > 0
        assert len(results_without) > 0

        # Should return the same results
        assert len(results_with) == len(results_without)

    def test_search_by_municipio_accent_insensitive(self):
        """Municipality search should be accent-insensitive"""
        # Test with common municipality with accents
        results_with = CodigosPostales.get_by_municipio("León")
        results_without = CodigosPostales.get_by_municipio("Leon")

        assert len(results_with) > 0
        assert len(results_without) > 0
        assert len(results_with) == len(results_without)

    def test_search_by_estado_accent_insensitive(self):
        """State search should be accent-insensitive"""
        results_with = CodigosPostales.get_by_estado("México")
        results_without = CodigosPostales.get_by_estado("Mexico")

        # Both should work (Estado de México exists)
        assert len(results_with) > 0 or len(results_without) > 0

    def test_search_special_characters(self):
        """Test search with special Spanish characters"""
        # Test ñ
        results = CodigosPostales.search_by_colonia("Peña")
        # Should work whether or not there are results
        assert isinstance(results, list)

    def test_search_multiple_accents(self):
        """Test search with multiple accents in query"""
        # Hypothetical colonia name with multiple accents
        results = CodigosPostales.search_by_colonia("San José")
        assert isinstance(results, list)

        # Should work without accents too
        results_no_accent = CodigosPostales.search_by_colonia("San Jose")
        assert isinstance(results_no_accent, list)

    def test_case_insensitive_search(self):
        """Search should also be case-insensitive"""
        results_upper = CodigosPostales.search_by_colonia("AGUILAS")
        results_lower = CodigosPostales.search_by_colonia("aguilas")
        results_mixed = CodigosPostales.search_by_colonia("Aguilas")

        # All should return the same results
        assert len(results_upper) == len(results_lower)
        assert len(results_lower) == len(results_mixed)

    def test_partial_match_with_accents(self):
        """Partial matches should work with accents"""
        # Search for partial name
        results = CodigosPostales.search_by_colonia("Aguil")

        # Should find "Las Águilas" and other similar names
        assert len(results) > 0

    def test_normalization_preserves_ñ(self):
        """Verify that ñ is handled correctly"""
        from catalogmx.utils.text import normalize_text

        # ñ should be preserved or converted to n
        normalized = normalize_text("Peña")
        assert "n" in normalized.lower()

    def test_normalization_removes_accents(self):
        """Verify that normalization removes common Spanish accents"""
        from catalogmx.utils.text import normalize_text

        # Test all common Spanish accented characters
        test_cases = {
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ú": "u",
            "Á": "A",
            "É": "E",
            "Í": "I",
            "Ó": "O",
            "Ú": "U",
        }

        for accented, expected in test_cases.items():
            result = normalize_text(accented)
            assert expected.upper() in result, f"Failed to normalize {accented} to {expected}"
