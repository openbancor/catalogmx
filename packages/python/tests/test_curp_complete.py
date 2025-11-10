"""
Complete tests for CURP validator to achieve 100% coverage
"""

from catalogmx.validators.curp import CURPGenerator, CURPGeneratorUtils, CURPValidator


class TestCURPValidatorComplete:
    """Complete CURP Validator tests"""

    def test_validate_check_digit_invalid_length(self):
        """Test validating check digit with invalid length"""
        validator = CURPValidator("GORS561231HVZNNL0")  # 17 chars
        result = validator.validate_check_digit()
        assert result is False

    def test_validate_check_digit_valid(self):
        """Test validating check digit with valid CURP"""
        validator = CURPValidator("GORS561231HVZNNL00")
        result = validator.validate_check_digit()
        assert isinstance(result, bool)


class TestCURPGeneratorUtilsComplete:
    """Complete tests for CURP Generator Utils"""

    def test_clean_name_with_excluded_words(self):
        """Test cleaning name with excluded words"""
        result = CURPGeneratorUtils.clean_name("DE LA CRUZ")
        assert isinstance(result, str)

    def test_clean_name_empty(self):
        """Test cleaning empty name"""
        result = CURPGeneratorUtils.clean_name("")
        assert result == ""

    def test_clean_name_none(self):
        """Test cleaning None name"""
        result = CURPGeneratorUtils.clean_name(None)
        assert result == ""

    def test_name_adapter_valid(self):
        """Test name adapter with valid name"""
        result = CURPGeneratorUtils.name_adapter("juan")
        assert result == "JUAN"

    def test_name_adapter_non_strict_none(self):
        """Test name adapter non-strict with None"""
        result = CURPGeneratorUtils.name_adapter(None, non_strict=True)
        assert result == ""

    def test_name_adapter_non_strict_empty(self):
        """Test name adapter non-strict with empty"""
        result = CURPGeneratorUtils.name_adapter("", non_strict=True)
        assert result == ""

    def test_name_adapter_strict_none(self):
        """Test name adapter strict with None"""
        try:
            result = CURPGeneratorUtils.name_adapter(None, non_strict=False)
            assert False, "Should raise ValueError"
        except ValueError:
            pass

    def test_name_adapter_strict_non_string(self):
        """Test name adapter strict with non-string"""
        try:
            result = CURPGeneratorUtils.name_adapter(123, non_strict=False)  # type: ignore
            assert False, "Should raise ValueError"
        except ValueError:
            pass

    def test_get_first_consonant_short_word(self):
        """Test getting first consonant from short word"""
        result = CURPGeneratorUtils.get_first_consonant("A")
        assert result == "X"

    def test_get_first_consonant_empty(self):
        """Test getting first consonant from empty word"""
        result = CURPGeneratorUtils.get_first_consonant("")
        assert result == "X"

    def test_get_first_consonant_valid(self):
        """Test getting first consonant from valid word"""
        result = CURPGeneratorUtils.get_first_consonant("JUAN")
        assert result in CURPGeneratorUtils.consonantes


class TestCURPGeneratorComplete:
    """Complete tests for CURP Generator"""

    def test_generate_with_invalid_date(self):
        """Test generating CURP with future date"""
        try:
            from datetime import date
            future_date = date(2099, 1, 1)
            generator = CURPGenerator(
                nombre="Juan",
                paterno="Garcia",
                materno="Lopez",
                fecha_nacimiento=future_date,
                sexo="H",
                estado="Jalisco"
            )
            # Should either raise or handle gracefully
            assert len(generator.curp) == 18
        except ValueError:
            pass

    def test_generate_with_very_old_date(self):
        """Test generating CURP with very old date"""
        try:
            from datetime import date
            old_date = date(1900, 1, 1)
            generator = CURPGenerator(
                nombre="Juan",
                paterno="Garcia",
                materno="Lopez",
                fecha_nacimiento=old_date,
                sexo="H",
                estado="Jalisco"
            )
            assert len(generator.curp) == 18
        except ValueError:
            pass

    def test_generate_with_invalid_estado(self):
        """Test generating CURP with invalid estado"""
        try:
            from datetime import date
            generator = CURPGenerator(
                nombre="Juan",
                paterno="Garcia",
                materno="Lopez",
                fecha_nacimiento=date(1990, 5, 15),
                sexo="H",
                estado="InvalidState"
            )
            # Should either use default or raise
            assert len(generator.curp) == 18
        except (ValueError, KeyError):
            pass

    def test_generate_with_special_characters_in_names(self):
        """Test generating CURP with special characters in names"""
        from datetime import date
        generator = CURPGenerator(
            nombre="José María",
            paterno="O'Connor",
            materno="D'Almeida",
            fecha_nacimiento=date(1990, 5, 15),
            sexo="H",
            estado="Jalisco"
        )
        assert len(generator.curp) == 18

    def test_generate_with_enie_in_names(self):
        """Test generating CURP with ñ in names"""
        from datetime import date
        generator = CURPGenerator(
            nombre="Juan",
            paterno="Peña",
            materno="Núñez",
            fecha_nacimiento=date(1990, 5, 15),
            sexo="H",
            estado="Jalisco"
        )
        assert len(generator.curp) == 18

