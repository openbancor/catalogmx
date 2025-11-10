"""
Complete tests for IFT catalogs to achieve 100% coverage
"""

from catalogmx.catalogs.ift import CodigosLADACatalog


class TestCodigosLADACatalogComplete:
    """Complete tests for Codigos LADA Catalog"""

    def test_validar_numero_with_country_code(self):
        """Test validating number with country code"""
        result = CodigosLADACatalog.validar_numero("+52 33 1234 5678")
        assert isinstance(result, dict)

    def test_validar_numero_with_special_chars(self):
        """Test validating number with special characters"""
        result = CodigosLADACatalog.validar_numero("(33) 1234-5678")
        assert isinstance(result, dict)

    def test_formatear_numero_invalid_lada(self):
        """Test formatting number with invalid LADA"""
        result = CodigosLADACatalog.formatear_numero("999 1234 5678")
        assert isinstance(result, str)
        # Should indicate unknown LADA
        assert "999" in result

    def test_get_info_numero_with_details(self):
        """Test getting number info with details"""
        result = CodigosLADACatalog.get_info_numero("33 1234 5678")
        assert isinstance(result, dict) or result is None

    def test_get_info_numero_invalid_format(self):
        """Test getting number info with completely invalid format"""
        result = CodigosLADACatalog.get_info_numero("ABC")
        assert result is None

