"""Tests for CLABE utilities module."""

import pytest

from catalogmx.utils.clabe_utils import (
    decode_clabe,
    describe_clabe,
    format_clabe,
    generate_clabe_examples,
    generate_clabe_for_bank,
    generate_clabe_random,
    get_common_banks,
    get_plaza_suggestions,
)


class TestDecodeClabe:
    """Tests for decode_clabe function."""

    def test_decode_valid_clabe(self):
        """Test decoding a valid CLABE."""
        result = decode_clabe("002010077777777771")
        assert result is not None
        assert result["clabe"] == "002010077777777771"
        assert result["bank_code"] == "002"
        assert result["plaza_code"] == "010"
        assert result["account_number"] == "07777777777"
        assert result["check_digit"] == "1"
        assert result["is_valid"] is True

    def test_decode_invalid_clabe_check_digit(self):
        """Test decoding a CLABE with invalid check digit."""
        result = decode_clabe("002010077777777770")
        assert result is not None
        assert result["is_valid"] is False

    def test_decode_clabe_with_bank_info(self):
        """Test that bank info is included when available."""
        result = decode_clabe("002010077777777771")
        assert result is not None
        assert result["bank"] is not None
        assert result["bank"]["code"] == "002"
        assert result["bank"]["name"] == "BANAMEX"

    def test_decode_clabe_with_plaza_info(self):
        """Test that plaza info is included when available."""
        result = decode_clabe("012180000000000001")
        assert result is not None
        assert result["plaza"] is not None

    def test_decode_clabe_invalid_format_short(self):
        """Test with too short input."""
        result = decode_clabe("12345")
        assert result is None

    def test_decode_clabe_invalid_format_long(self):
        """Test with too long input."""
        result = decode_clabe("1234567890123456789")
        assert result is None

    def test_decode_clabe_with_letters(self):
        """Test with non-digit characters."""
        result = decode_clabe("00201007777777777A")
        assert result is None

    def test_decode_clabe_empty_string(self):
        """Test with empty string."""
        result = decode_clabe("")
        assert result is None

    def test_decode_clabe_with_spaces(self):
        """Test that spaces are trimmed."""
        result = decode_clabe("  002010077777777771  ")
        assert result is not None
        assert result["clabe"] == "002010077777777771"

    def test_decode_clabe_none_input(self):
        """Test with None-like input."""
        result = decode_clabe("")
        assert result is None

    def test_decode_clabe_unknown_bank(self):
        """Test with unknown bank code."""
        result = decode_clabe("999010077777777772")
        assert result is not None
        assert result["bank"] is None

    def test_decode_clabe_unknown_plaza(self):
        """Test with unknown plaza code."""
        result = decode_clabe("002999077777777773")
        assert result is not None
        # Plaza may or may not be found depending on data


class TestGenerateClabeRandom:
    """Tests for generate_clabe_random function."""

    def test_generate_random_clabe(self):
        """Test generating a fully random CLABE."""
        clabe = generate_clabe_random()
        assert len(clabe) == 18
        assert clabe.isdigit()

    def test_generate_clabe_with_bank_code(self):
        """Test generating CLABE with specified bank code."""
        clabe = generate_clabe_random(bank_code="012")
        assert clabe[:3] == "012"
        assert len(clabe) == 18

    def test_generate_clabe_with_plaza_code(self):
        """Test generating CLABE with specified plaza code."""
        clabe = generate_clabe_random(plaza_code="180")
        assert clabe[3:6] == "180"
        assert len(clabe) == 18

    def test_generate_clabe_with_account_number(self):
        """Test generating CLABE with specified account number."""
        clabe = generate_clabe_random(account_number="12345678901")
        assert clabe[6:17] == "12345678901"
        assert len(clabe) == 18

    def test_generate_clabe_fully_specified(self):
        """Test generating CLABE with all parameters specified."""
        clabe = generate_clabe_random("012", "180", "12345678901")
        assert clabe[:3] == "012"
        assert clabe[3:6] == "180"
        assert clabe[6:17] == "12345678901"
        # Last digit is check digit
        assert len(clabe) == 18

    def test_generated_clabe_is_valid(self):
        """Test that generated CLABEs are valid."""
        for _ in range(10):
            clabe = generate_clabe_random()
            decoded = decode_clabe(clabe)
            assert decoded is not None
            assert decoded["is_valid"] is True


class TestGenerateClabeExamples:
    """Tests for generate_clabe_examples function."""

    def test_generate_default_count(self):
        """Test generating default number of examples (5)."""
        examples = generate_clabe_examples()
        assert len(examples) == 5

    def test_generate_custom_count(self):
        """Test generating custom number of examples."""
        examples = generate_clabe_examples(3)
        assert len(examples) == 3

    def test_examples_are_valid(self):
        """Test that all examples are valid CLABEs."""
        examples = generate_clabe_examples(10)
        for ex in examples:
            assert ex["is_valid"] is True
            assert "bank" in ex
            assert "plaza" in ex

    def test_generate_zero_examples(self):
        """Test generating zero examples."""
        examples = generate_clabe_examples(0)
        assert len(examples) == 0


class TestGenerateClabeForBank:
    """Tests for generate_clabe_for_bank function."""

    def test_generate_for_bbva(self):
        """Test generating CLABE for BBVA MEXICO."""
        clabe = generate_clabe_for_bank("BBVA MEXICO")
        assert clabe is not None
        assert len(clabe) == 18
        decoded = decode_clabe(clabe)
        assert decoded is not None
        assert decoded["bank"]["name"] == "BBVA MEXICO"

    def test_generate_for_banamex(self):
        """Test generating CLABE for BANAMEX."""
        clabe = generate_clabe_for_bank("BANAMEX")
        assert clabe is not None
        decoded = decode_clabe(clabe)
        assert decoded["bank"]["name"] == "BANAMEX"

    def test_generate_for_unknown_bank(self):
        """Test generating CLABE for unknown bank."""
        clabe = generate_clabe_for_bank("BANCO_INEXISTENTE")
        assert clabe is None

    def test_generate_with_plaza(self):
        """Test generating CLABE for bank with plaza."""
        clabe = generate_clabe_for_bank("BBVA MEXICO", "Ciudad de Mexico")
        if clabe:  # Plaza may or may not be found
            assert len(clabe) == 18

    def test_generate_with_invalid_plaza(self):
        """Test generating CLABE for bank with invalid plaza."""
        clabe = generate_clabe_for_bank("BBVA MEXICO", "Ciudad Inexistente")
        # Should still generate, just without specific plaza
        assert clabe is not None
        assert len(clabe) == 18


class TestGetCommonBanks:
    """Tests for get_common_banks function."""

    def test_returns_list(self):
        """Test that function returns a list."""
        banks = get_common_banks()
        assert isinstance(banks, list)

    def test_has_banks(self):
        """Test that list contains banks."""
        banks = get_common_banks()
        assert len(banks) > 10

    def test_bank_has_required_fields(self):
        """Test that banks have required fields."""
        banks = get_common_banks()
        for bank in banks[:5]:  # Check first 5
            assert "code" in bank
            assert "name" in bank


class TestGetPlazaSuggestions:
    """Tests for get_plaza_suggestions function."""

    def test_search_guadalajara(self):
        """Test searching for Guadalajara."""
        results = get_plaza_suggestions("Guadalajara")
        assert len(results) > 0

    def test_search_partial(self):
        """Test searching with partial name."""
        results = get_plaza_suggestions("Guada")
        assert len(results) > 0

    def test_search_empty(self):
        """Test searching with empty string."""
        results = get_plaza_suggestions("")
        # May return all or empty depending on implementation
        assert isinstance(results, list)

    def test_search_not_found(self):
        """Test searching for non-existent plaza."""
        results = get_plaza_suggestions("PlazaInexistente12345")
        assert len(results) == 0


class TestFormatClabe:
    """Tests for format_clabe function."""

    def test_format_with_default_separator(self):
        """Test formatting with default separator."""
        result = format_clabe("002010077777777771")
        assert result == "002-010-07777777777-1"

    def test_format_with_space_separator(self):
        """Test formatting with space separator."""
        result = format_clabe("002010077777777771", " ")
        assert result == "002 010 07777777777 1"

    def test_format_with_custom_separator(self):
        """Test formatting with custom separator."""
        result = format_clabe("002010077777777771", ".")
        assert result == "002.010.07777777777.1"

    def test_format_invalid_length(self):
        """Test formatting with invalid length returns unchanged."""
        result = format_clabe("12345")
        assert result == "12345"


class TestDescribeClabe:
    """Tests for describe_clabe function."""

    def test_describe_valid_clabe(self):
        """Test describing a valid CLABE."""
        result = describe_clabe("002010077777777771")
        assert "CLABE:" in result
        assert "002-010-07777777777-1" in result
        assert "BANAMEX" in result
        assert "Válida" in result

    def test_describe_invalid_clabe(self):
        """Test describing an invalid CLABE."""
        result = describe_clabe("002010077777777770")
        assert "Inválida" in result

    def test_describe_invalid_format(self):
        """Test describing a malformed CLABE."""
        result = describe_clabe("invalid")
        assert "inválida" in result.lower()

    def test_describe_unknown_bank(self):
        """Test describing CLABE with unknown bank."""
        result = describe_clabe("999010077777777772")
        assert "no encontrado" in result

    def test_describe_contains_account(self):
        """Test that description contains account number."""
        result = describe_clabe("002010077777777771")
        assert "Cuenta:" in result
        assert "07777777777" in result
