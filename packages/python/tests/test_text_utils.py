"""
Tests for text normalization utilities.

Tests the catalogmx.utils.text module functions.
"""
from catalogmx.utils.text import normalize_text, normalize_for_search


class TestNormalizeText:
    """Test the normalize_text function."""

    def test_basic_functionality(self):
        """Test basic accent removal and uppercase conversion"""
        assert normalize_text("México") == "MEXICO"
        assert normalize_text("Querétaro") == "QUERETARO"
        assert normalize_text("San José") == "SAN JOSE"

    def test_case_normalization(self):
        """Test case normalization"""
        assert normalize_text("mexico") == "MEXICO"
        assert normalize_text("MeXiCo") == "MEXICO"
        assert normalize_text("MEXICO") == "MEXICO"

    def test_all_spanish_vowels(self):
        """Test all Spanish accented vowels"""
        assert normalize_text("á é í ó ú") == "A E I O U"
        assert normalize_text("Á É Í Ó Ú") == "A E I O U"

    def test_special_characters(self):
        """Test special characters like ñ"""
        assert normalize_text("Ñoño") == "NONO"
        assert normalize_text("niño") == "NINO"
        assert normalize_text("SEÑOR") == "SENOR"

    def test_empty_string(self):
        """Test empty string"""
        assert normalize_text("") == ""

    def test_whitespace(self):
        """Test whitespace handling"""
        assert normalize_text("  ") == "  "
        assert normalize_text("  México  ") == "  MEXICO  "
        assert normalize_text("San\tJosé") == "SAN\tJOSE"

    def test_numbers_and_symbols(self):
        """Test that numbers and symbols are preserved"""
        assert normalize_text("México 123") == "MEXICO 123"
        assert normalize_text("Calle #45-A") == "CALLE #45-A"

    def test_idempotent(self):
        """Test that function is idempotent"""
        text = "México"
        once = normalize_text(text)
        twice = normalize_text(once)
        assert once == twice

    def test_multiple_consecutive_accents(self):
        """Test multiple consecutive accented characters"""
        assert normalize_text("áéíóú") == "AEIOU"
        assert normalize_text("ÁÉÍÓÚ") == "AEIOU"

    def test_other_latin_characters(self):
        """Test other Latin characters with diacritics"""
        assert normalize_text("Müller") == "MULLER"
        assert normalize_text("François") == "FRANCOIS"
        assert normalize_text("Zürich") == "ZURICH"

    def test_very_long_string(self):
        """Test performance with very long strings"""
        long_text = "á" * 10000
        result = normalize_text(long_text)
        assert result == "A" * 10000
        assert len(result) == 10000


class TestNormalizeForSearch:
    """Test the normalize_for_search function."""

    def test_is_alias_for_normalize_text(self):
        """Test that normalize_for_search is an alias for normalize_text"""
        test_cases = [
            "México",
            "Querétaro",
            "San José",
            "Michoacán",
            "",
            "123",
        ]
        for text in test_cases:
            assert normalize_for_search(text) == normalize_text(text)


class TestRealWorldPatterns:
    """Test with real-world Mexican data patterns."""

    def test_mexican_states(self):
        """Test with actual Mexican state names"""
        states = [
            ("México", "MEXICO"),
            ("Nuevo León", "NUEVO LEON"),
            ("Querétaro", "QUERETARO"),
            ("Yucatán", "YUCATAN"),
            ("Michoacán", "MICHOACAN"),
            ("San Luis Potosí", "SAN LUIS POTOSI"),
        ]
        for state, expected in states:
            assert normalize_text(state) == expected

    def test_mexican_cities(self):
        """Test with actual Mexican city names"""
        cities = [
            ("Ciudad Juárez", "CIUDAD JUAREZ"),
            ("Mérida", "MERIDA"),
            ("Cancún", "CANCUN"),
            ("Torreón", "TORREON"),
            ("León", "LEON"),
        ]
        for city, expected in cities:
            assert normalize_text(city) == expected

    def test_postal_code_localities(self):
        """Test with common postal code locality names"""
        localities = [
            "Colonia Juárez",
            "Centro Histórico",
            "Santa María",
            "San Ángel",
            "Polanco",
        ]
        for locality in localities:
            normalized = normalize_text(locality)
            # Should not contain any accented characters
            assert not any(c in normalized for c in "áéíóúñÁÉÍÓÚÑ")
            # Should be uppercase
            assert normalized == normalized.upper()


class TestEdgeCases:
    """Test edge cases and potential issues."""

    def test_unicode_normalization_forms(self):
        """Test different Unicode normalization forms"""
        # NFD vs NFC forms of accented characters
        nfc = "México"  # Precomposed
        nfd = "Me\u0301xico"  # Decomposed (e + combining acute)
        assert normalize_text(nfc) == normalize_text(nfd)

    def test_mixed_accents_and_case(self):
        """Test mixed accents and case"""
        variations = [
            "méxico",
            "México",
            "MÉXICO",
            "MéXiCo",
            "mÉxIcO",
        ]
        results = [normalize_text(v) for v in variations]
        # All should produce the same result
        assert len(set(results)) == 1
        assert results[0] == "MEXICO"

    def test_partial_accent_strings(self):
        """Test strings with partial accents"""
        assert normalize_text("José Luis García") == "JOSE LUIS GARCIA"
        assert normalize_text("Maria Fernández") == "MARIA FERNANDEZ"
        assert normalize_text("Héctor Pérez") == "HECTOR PEREZ"

    def test_comparison_with_and_without_accents(self):
        """Test that strings with/without accents normalize identically"""
        pairs = [
            ("México", "Mexico"),
            ("Querétaro", "Queretaro"),
            ("San José", "San Jose"),
            ("Michoacán", "Michoacan"),
        ]
        for with_accent, without_accent in pairs:
            assert normalize_text(with_accent) == normalize_text(without_accent)
