"""
Tests for CLABE (Clave Bancaria Estandarizada) validator
"""

import pytest

from catalogmx.validators.clabe import (
    CLABECheckDigitError,
    CLABEException,
    CLABELengthError,
    CLABEStructureError,
    CLABEValidator,
    generate_clabe,
    get_clabe_info,
    validate_clabe,
)


class TestCLABEValidator:
    """Test CLABE validation functionality"""

    def test_valid_clabe(self):
        """Test validation of valid CLABE"""
        # Real CLABE example
        clabe = "002010077777777771"
        validator = CLABEValidator(clabe)
        assert validator.validate() is True
        assert validator.is_valid() is True

    def test_valid_clabe_with_whitespace(self):
        """Test validation of valid CLABE with whitespace"""
        clabe = "  002010077777777771  "
        validator = CLABEValidator(clabe)
        assert validator.is_valid() is True

    def test_invalid_length_short(self):
        """Test CLABE with invalid length (too short)"""
        clabe = "00201007777777777"  # 17 digits
        validator = CLABEValidator(clabe)
        with pytest.raises(CLABELengthError) as exc:
            validator.validate()
        assert "18 digits" in str(exc.value)
        assert validator.is_valid() is False

    def test_invalid_length_long(self):
        """Test CLABE with invalid length (too long)"""
        clabe = "0020100777777777711"  # 19 digits
        validator = CLABEValidator(clabe)
        with pytest.raises(CLABELengthError):
            validator.validate()
        assert validator.is_valid() is False

    def test_invalid_structure_letters(self):
        """Test CLABE with letters"""
        clabe = "00201007777777777A"
        validator = CLABEValidator(clabe)
        with pytest.raises(CLABEStructureError) as exc:
            validator.validate()
        assert "only digits" in str(exc.value)
        assert validator.is_valid() is False

    def test_invalid_structure_special_chars(self):
        """Test CLABE with special characters"""
        clabe = "002010077777777-71"
        validator = CLABEValidator(clabe)
        with pytest.raises(CLABEStructureError):
            validator.validate()
        assert validator.is_valid() is False

    def test_invalid_check_digit(self):
        """Test CLABE with invalid check digit"""
        clabe = "002010077777777770"  # Wrong check digit (should be 1)
        validator = CLABEValidator(clabe)
        with pytest.raises(CLABECheckDigitError) as exc:
            validator.validate()
        assert "check digit" in str(exc.value)
        assert validator.is_valid() is False

    def test_none_clabe(self):
        """Test with None input"""
        validator = CLABEValidator(None)
        assert validator.is_valid() is False

    def test_empty_clabe(self):
        """Test with empty string"""
        validator = CLABEValidator("")
        assert validator.is_valid() is False

    def test_non_string_clabe(self):
        """Test with non-string input"""
        validator = CLABEValidator(123456789012345678)
        assert validator.clabe == ""
        assert validator.is_valid() is False

    def test_calculate_check_digit(self):
        """Test check digit calculation"""
        clabe_17 = "00201007777777777"
        check_digit = CLABEValidator.calculate_check_digit(clabe_17)
        assert check_digit == "1"

    def test_calculate_check_digit_invalid_length(self):
        """Test check digit calculation with wrong length"""
        with pytest.raises(CLABELengthError) as exc:
            CLABEValidator.calculate_check_digit("0020100777777777")
        assert "17 digits" in str(exc.value)

    def test_calculate_check_digit_non_numeric(self):
        """Test check digit calculation with non-numeric input"""
        with pytest.raises(CLABEStructureError):
            CLABEValidator.calculate_check_digit("0020100777777777A")

    def test_verify_check_digit(self):
        """Test check digit verification"""
        assert CLABEValidator.verify_check_digit("002010077777777771") is True
        assert CLABEValidator.verify_check_digit("002010077777777770") is False

    def test_verify_check_digit_wrong_length(self):
        """Test verify_check_digit with wrong length"""
        assert CLABEValidator.verify_check_digit("00201007777777777") is False

    def test_get_bank_code(self):
        """Test extracting bank code"""
        clabe = "002010077777777771"
        validator = CLABEValidator(clabe)
        assert validator.get_bank_code() == "002"

    def test_get_bank_code_short_clabe(self):
        """Test extracting bank code from short CLABE"""
        validator = CLABEValidator("00")
        assert validator.get_bank_code() is None

    def test_get_branch_code(self):
        """Test extracting branch code"""
        clabe = "002010077777777771"
        validator = CLABEValidator(clabe)
        assert validator.get_branch_code() == "010"

    def test_get_branch_code_short_clabe(self):
        """Test extracting branch code from short CLABE"""
        validator = CLABEValidator("00201")
        assert validator.get_branch_code() is None

    def test_get_account_number(self):
        """Test extracting account number"""
        clabe = "002010077777777771"
        validator = CLABEValidator(clabe)
        assert validator.get_account_number() == "07777777777"

    def test_get_account_number_short_clabe(self):
        """Test extracting account number from short CLABE"""
        validator = CLABEValidator("002010077")
        assert validator.get_account_number() is None

    def test_get_check_digit(self):
        """Test extracting check digit"""
        clabe = "002010077777777771"
        validator = CLABEValidator(clabe)
        assert validator.get_check_digit() == "1"

    def test_get_check_digit_short_clabe(self):
        """Test extracting check digit from short CLABE"""
        validator = CLABEValidator("00201007777777777")
        assert validator.get_check_digit() is None

    def test_get_parts_valid(self):
        """Test getting all parts of valid CLABE"""
        clabe = "002010077777777771"
        validator = CLABEValidator(clabe)
        parts = validator.get_parts()
        
        assert parts is not None
        assert parts["bank_code"] == "002"
        assert parts["branch_code"] == "010"
        assert parts["account_number"] == "07777777777"
        assert parts["check_digit"] == "1"
        assert parts["clabe"] == clabe

    def test_get_parts_invalid(self):
        """Test getting parts of invalid CLABE"""
        clabe = "002010077777777770"  # Invalid check digit
        validator = CLABEValidator(clabe)
        parts = validator.get_parts()
        assert parts is None


class TestCLABEHelperFunctions:
    """Test CLABE helper functions"""

    def test_validate_clabe_valid(self):
        """Test validate_clabe helper with valid CLABE"""
        assert validate_clabe("002010077777777771") is True

    def test_validate_clabe_invalid(self):
        """Test validate_clabe helper with invalid CLABE"""
        assert validate_clabe("002010077777777770") is False

    def test_validate_clabe_none(self):
        """Test validate_clabe helper with None"""
        assert validate_clabe(None) is False

    def test_generate_clabe_valid(self):
        """Test generating valid CLABE"""
        clabe = generate_clabe("002", "010", "07777777777")
        assert clabe == "002010077777777771"
        assert validate_clabe(clabe) is True

    def test_generate_clabe_with_integers(self):
        """Test generating CLABE with integer inputs"""
        clabe = generate_clabe(2, 10, 7777777777)
        assert clabe == "002010077777777771"
        assert validate_clabe(clabe) is True

    def test_generate_clabe_with_short_numbers(self):
        """Test generating CLABE with short numbers (zero padding)"""
        clabe = generate_clabe("2", "10", "77777")
        assert clabe == "002010000077777778"
        assert validate_clabe(clabe) is True

    def test_generate_clabe_invalid_bank_code(self):
        """Test generating CLABE with invalid bank code length"""
        with pytest.raises(CLABEStructureError) as exc:
            generate_clabe("12345", "010", "07777777777")
        assert "Bank code must be 3 digits" in str(exc.value)

    def test_generate_clabe_invalid_branch_code(self):
        """Test generating CLABE with invalid branch code length"""
        with pytest.raises(CLABEStructureError) as exc:
            generate_clabe("002", "12345", "07777777777")
        assert "Branch code must be 3 digits" in str(exc.value)

    def test_generate_clabe_invalid_account_number(self):
        """Test generating CLABE with invalid account number length"""
        with pytest.raises(CLABEStructureError) as exc:
            generate_clabe("002", "010", "123456789012345")
        assert "Account number must be 11 digits" in str(exc.value)

    def test_get_clabe_info_valid(self):
        """Test get_clabe_info helper with valid CLABE"""
        info = get_clabe_info("002010077777777771")
        assert info is not None
        assert info["bank_code"] == "002"
        assert info["branch_code"] == "010"
        assert info["account_number"] == "07777777777"
        assert info["check_digit"] == "1"

    def test_get_clabe_info_invalid(self):
        """Test get_clabe_info helper with invalid CLABE"""
        info = get_clabe_info("002010077777777770")
        assert info is None

    def test_get_clabe_info_none(self):
        """Test get_clabe_info helper with None"""
        info = get_clabe_info(None)
        assert info is None


class TestCLABEExceptions:
    """Test CLABE exception hierarchy"""

    def test_clabe_exception_base(self):
        """Test CLABEException is base exception"""
        exc = CLABEException("test")
        assert isinstance(exc, Exception)

    def test_clabe_length_error_inheritance(self):
        """Test CLABELengthError inherits from CLABEException"""
        exc = CLABELengthError("test")
        assert isinstance(exc, CLABEException)

    def test_clabe_structure_error_inheritance(self):
        """Test CLABEStructureError inherits from CLABEException"""
        exc = CLABEStructureError("test")
        assert isinstance(exc, CLABEException)

    def test_clabe_check_digit_error_inheritance(self):
        """Test CLABECheckDigitError inherits from CLABEException"""
        exc = CLABECheckDigitError("test")
        assert isinstance(exc, CLABEException)


class TestCLABECheckDigitAlgorithm:
    """Test the check digit calculation algorithm with various examples"""

    def test_check_digit_all_zeros(self):
        """Test check digit with all zeros"""
        clabe_17 = "00000000000000000"
        check_digit = CLABEValidator.calculate_check_digit(clabe_17)
        assert check_digit == "0"

    def test_check_digit_all_ones(self):
        """Test check digit with all ones"""
        clabe_17 = "11111111111111111"
        check_digit = CLABEValidator.calculate_check_digit(clabe_17)
        assert len(check_digit) == 1
        assert check_digit.isdigit()

    def test_check_digit_all_nines(self):
        """Test check digit with all nines"""
        clabe_17 = "99999999999999999"
        check_digit = CLABEValidator.calculate_check_digit(clabe_17)
        assert len(check_digit) == 1
        assert check_digit.isdigit()

    def test_weight_pattern(self):
        """Test the weight pattern [3,7,1] * 6"""
        assert CLABEValidator.WEIGHTS == [3, 7, 1] * 6
        assert len(CLABEValidator.WEIGHTS) == 18

    def test_multiple_valid_clabes(self):
        """Test multiple valid CLABE examples"""
        valid_clabes = [
            "002010077777777771",
            "012180001234567891",
            "014180655555555509",
        ]
        
        for clabe in valid_clabes:
            validator = CLABEValidator(clabe)
            assert validator.is_valid(), f"CLABE {clabe} should be valid"
            
            # Verify check digit calculation
            clabe_17 = clabe[:17]
            calculated_digit = CLABEValidator.calculate_check_digit(clabe_17)
            assert calculated_digit == clabe[17], f"Check digit mismatch for {clabe}"

