"""
Tests for NSS (Número de Seguridad Social) validator
"""

import pytest

from catalogmx.validators.nss import (
    NSSCheckDigitError,
    NSSException,
    NSSLengthError,
    NSSStructureError,
    NSSValidator,
    generate_nss,
    get_nss_info,
    validate_nss,
)


class TestNSSValidator:
    """Test NSS validation functionality"""

    def test_valid_nss(self):
        """Test validation of valid NSS"""
        # Example NSS with valid check digit
        nss = "12345678903"
        validator = NSSValidator(nss)
        assert validator.validate() is True
        assert validator.is_valid() is True

    def test_valid_nss_with_whitespace(self):
        """Test validation of valid NSS with whitespace"""
        nss = "  12345678903  "
        validator = NSSValidator(nss)
        assert validator.is_valid() is True

    def test_invalid_length_short(self):
        """Test NSS with invalid length (too short)"""
        nss = "1234567890"  # 10 digits
        validator = NSSValidator(nss)
        with pytest.raises(NSSLengthError) as exc:
            validator.validate()
        assert "11 digits" in str(exc.value)
        assert validator.is_valid() is False

    def test_invalid_length_long(self):
        """Test NSS with invalid length (too long)"""
        nss = "123456789012"  # 12 digits
        validator = NSSValidator(nss)
        with pytest.raises(NSSLengthError):
            validator.validate()
        assert validator.is_valid() is False

    def test_invalid_structure_letters(self):
        """Test NSS with letters"""
        nss = "1234567890A"
        validator = NSSValidator(nss)
        with pytest.raises(NSSStructureError) as exc:
            validator.validate()
        assert "only digits" in str(exc.value)
        assert validator.is_valid() is False

    def test_invalid_structure_special_chars(self):
        """Test NSS with special characters"""
        nss = "12345678-03"
        validator = NSSValidator(nss)
        with pytest.raises(NSSStructureError):
            validator.validate()
        assert validator.is_valid() is False

    def test_invalid_check_digit(self):
        """Test NSS with invalid check digit"""
        # Generate a valid NSS first, then change the check digit
        nss = "12345678902"  # Wrong check digit
        validator = NSSValidator(nss)
        with pytest.raises(NSSCheckDigitError) as exc:
            validator.validate()
        assert "check digit" in str(exc.value)
        assert validator.is_valid() is False

    def test_none_nss(self):
        """Test with None input"""
        validator = NSSValidator(None)
        assert validator.is_valid() is False

    def test_empty_nss(self):
        """Test with empty string"""
        validator = NSSValidator("")
        assert validator.is_valid() is False

    def test_non_string_nss(self):
        """Test with non-string input"""
        validator = NSSValidator(12345678903)
        assert validator.nss == ""
        assert validator.is_valid() is False

    def test_calculate_check_digit(self):
        """Test check digit calculation"""
        nss_10 = "1234567890"
        check_digit = NSSValidator.calculate_check_digit(nss_10)
        assert len(check_digit) == 1
        assert check_digit.isdigit()

    def test_calculate_check_digit_invalid_length(self):
        """Test check digit calculation with wrong length"""
        with pytest.raises(NSSLengthError) as exc:
            NSSValidator.calculate_check_digit("123456789")
        assert "10 digits" in str(exc.value)

    def test_calculate_check_digit_non_numeric(self):
        """Test check digit calculation with non-numeric input"""
        with pytest.raises(NSSStructureError):
            NSSValidator.calculate_check_digit("123456789A")

    def test_verify_check_digit(self):
        """Test check digit verification"""
        nss = "12345678903"
        assert NSSValidator.verify_check_digit(nss) is True
        
        # Wrong check digit
        nss_wrong = "12345678902"
        assert NSSValidator.verify_check_digit(nss_wrong) is False

    def test_verify_check_digit_wrong_length(self):
        """Test verify_check_digit with wrong length"""
        assert NSSValidator.verify_check_digit("1234567890") is False

    def test_get_subdelegation(self):
        """Test extracting subdelegation code"""
        nss = "12345678903"
        validator = NSSValidator(nss)
        assert validator.get_subdelegation() == "12"

    def test_get_subdelegation_short_nss(self):
        """Test extracting subdelegation from short NSS"""
        validator = NSSValidator("1")
        assert validator.get_subdelegation() is None

    def test_get_year(self):
        """Test extracting year"""
        nss = "12345678903"
        validator = NSSValidator(nss)
        assert validator.get_year() == "34"

    def test_get_year_short_nss(self):
        """Test extracting year from short NSS"""
        validator = NSSValidator("123")
        assert validator.get_year() is None

    def test_get_serial(self):
        """Test extracting serial"""
        nss = "12345678903"
        validator = NSSValidator(nss)
        assert validator.get_serial() == "56"

    def test_get_serial_short_nss(self):
        """Test extracting serial from short NSS"""
        validator = NSSValidator("12345")
        assert validator.get_serial() is None

    def test_get_sequential(self):
        """Test extracting sequential number"""
        nss = "12345678903"
        validator = NSSValidator(nss)
        assert validator.get_sequential() == "7890"

    def test_get_sequential_short_nss(self):
        """Test extracting sequential from short NSS"""
        validator = NSSValidator("123456789")
        assert validator.get_sequential() is None

    def test_get_check_digit(self):
        """Test extracting check digit"""
        nss = "12345678903"
        validator = NSSValidator(nss)
        assert validator.get_check_digit() == "3"

    def test_get_check_digit_short_nss(self):
        """Test extracting check digit from short NSS"""
        validator = NSSValidator("1234567890")
        assert validator.get_check_digit() is None

    def test_get_parts_valid(self):
        """Test getting all parts of valid NSS"""
        nss = "12345678903"
        validator = NSSValidator(nss)
        parts = validator.get_parts()
        
        assert parts is not None
        assert parts["subdelegation"] == "12"
        assert parts["year"] == "34"
        assert parts["serial"] == "56"
        assert parts["sequential"] == "7890"
        assert parts["check_digit"] == "3"
        assert parts["nss"] == nss

    def test_get_parts_invalid(self):
        """Test getting parts of invalid NSS"""
        nss = "12345678902"  # Invalid check digit
        validator = NSSValidator(nss)
        parts = validator.get_parts()
        assert parts is None


class TestNSSHelperFunctions:
    """Test NSS helper functions"""

    def test_validate_nss_valid(self):
        """Test validate_nss helper with valid NSS"""
        assert validate_nss("12345678903") is True

    def test_validate_nss_invalid(self):
        """Test validate_nss helper with invalid NSS"""
        assert validate_nss("12345678902") is False

    def test_validate_nss_none(self):
        """Test validate_nss helper with None"""
        assert validate_nss(None) is False

    def test_generate_nss_valid(self):
        """Test generating valid NSS"""
        nss = generate_nss("12", "34", "56", "7890")
        assert len(nss) == 11
        assert validate_nss(nss) is True

    def test_generate_nss_with_integers(self):
        """Test generating NSS with integer inputs"""
        nss = generate_nss(12, 34, 56, 7890)
        assert len(nss) == 11
        assert validate_nss(nss) is True

    def test_generate_nss_with_short_numbers(self):
        """Test generating NSS with short numbers (zero padding)"""
        nss = generate_nss("1", "2", "3", "456")
        assert len(nss) == 11
        assert nss[:2] == "01"
        assert nss[2:4] == "02"
        assert nss[4:6] == "03"
        assert nss[6:10] == "0456"
        assert validate_nss(nss) is True

    def test_generate_nss_invalid_subdelegation(self):
        """Test generating NSS with invalid subdelegation length"""
        with pytest.raises(NSSStructureError) as exc:
            generate_nss("12345", "34", "56", "7890")
        assert "Subdelegation must be 2 digits" in str(exc.value)

    def test_generate_nss_invalid_year(self):
        """Test generating NSS with invalid year length"""
        with pytest.raises(NSSStructureError) as exc:
            generate_nss("12", "12345", "56", "7890")
        assert "Year must be 2 digits" in str(exc.value)

    def test_generate_nss_invalid_serial(self):
        """Test generating NSS with invalid serial length"""
        with pytest.raises(NSSStructureError) as exc:
            generate_nss("12", "34", "12345", "7890")
        assert "Serial must be 2 digits" in str(exc.value)

    def test_generate_nss_invalid_sequential(self):
        """Test generating NSS with invalid sequential length"""
        with pytest.raises(NSSStructureError) as exc:
            generate_nss("12", "34", "56", "12345678")
        assert "Sequential must be 4 digits" in str(exc.value)

    def test_get_nss_info_valid(self):
        """Test get_nss_info helper with valid NSS"""
        nss = "12345678903"
        info = get_nss_info(nss)
        assert info is not None
        assert info["subdelegation"] == "12"
        assert info["year"] == "34"
        assert info["serial"] == "56"
        assert info["sequential"] == "7890"
        assert info["check_digit"] == "3"

    def test_get_nss_info_invalid(self):
        """Test get_nss_info helper with invalid NSS"""
        info = get_nss_info("12345678902")
        assert info is None

    def test_get_nss_info_none(self):
        """Test get_nss_info helper with None"""
        info = get_nss_info(None)
        assert info is None


class TestNSSExceptions:
    """Test NSS exception hierarchy"""

    def test_nss_exception_base(self):
        """Test NSSException is base exception"""
        exc = NSSException("test")
        assert isinstance(exc, Exception)

    def test_nss_length_error_inheritance(self):
        """Test NSSLengthError inherits from NSSException"""
        exc = NSSLengthError("test")
        assert isinstance(exc, NSSException)

    def test_nss_structure_error_inheritance(self):
        """Test NSSStructureError inherits from NSSException"""
        exc = NSSStructureError("test")
        assert isinstance(exc, NSSException)

    def test_nss_check_digit_error_inheritance(self):
        """Test NSSCheckDigitError inherits from NSSException"""
        exc = NSSCheckDigitError("test")
        assert isinstance(exc, NSSException)


class TestNSSCheckDigitAlgorithm:
    """Test the check digit calculation algorithm (modified Luhn) with various examples"""

    def test_check_digit_all_zeros(self):
        """Test check digit with all zeros"""
        nss_10 = "0000000000"
        check_digit = NSSValidator.calculate_check_digit(nss_10)
        assert check_digit == "0"

    def test_check_digit_all_ones(self):
        """Test check digit with all ones"""
        nss_10 = "1111111111"
        check_digit = NSSValidator.calculate_check_digit(nss_10)
        assert len(check_digit) == 1
        assert check_digit.isdigit()

    def test_check_digit_all_nines(self):
        """Test check digit with all nines"""
        nss_10 = "9999999999"
        check_digit = NSSValidator.calculate_check_digit(nss_10)
        assert len(check_digit) == 1
        assert check_digit.isdigit()

    def test_check_digit_alternating(self):
        """Test check digit with alternating digits"""
        nss_10 = "0123456789"
        check_digit = NSSValidator.calculate_check_digit(nss_10)
        assert len(check_digit) == 1
        assert check_digit.isdigit()

    def test_multiple_valid_nss(self):
        """Test multiple valid NSS examples"""
        # Generate several NSS with different patterns
        test_cases = [
            ("12", "34", "56", "7890"),
            ("01", "02", "03", "0456"),
            ("99", "99", "99", "9999"),
            ("55", "66", "77", "8888"),
        ]
        
        for subdel, year, serial, seq in test_cases:
            nss = generate_nss(subdel, year, serial, seq)
            validator = NSSValidator(nss)
            assert validator.is_valid(), f"NSS {nss} should be valid"
            
            # Verify check digit calculation
            nss_10 = nss[:10]
            calculated_digit = NSSValidator.calculate_check_digit(nss_10)
            assert calculated_digit == nss[10], f"Check digit mismatch for {nss}"

    def test_luhn_algorithm_double_digit_handling(self):
        """Test that the algorithm correctly handles products > 9"""
        # The Luhn algorithm should sum the digits of products > 9
        # For example: 8 * 2 = 16 -> 1 + 6 = 7
        nss_10 = "8888888888"
        check_digit = NSSValidator.calculate_check_digit(nss_10)
        assert len(check_digit) == 1
        assert check_digit.isdigit()
        
        # Verify the calculation produces a valid NSS
        nss = nss_10 + check_digit
        assert validate_nss(nss) is True

