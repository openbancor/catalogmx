"""
Tests for new Banxico catalogs (UDI, Tipo de Cambio, TIIE, CETES, Inflación, Salarios Mínimos)
"""

import pytest
from catalogmx.catalogs.banxico import (
    UDICatalog,
    TipoCambioUSDCatalog,
    TIIE28Catalog,
    CETES28Catalog,
    InflacionAnualCatalog,
    SalariosMinimosCatalog
)


class TestUDICatalog:
    """Tests for UDI Catalog"""

    def test_get_data(self):
        """Test getting all UDI data"""
        data = UDICatalog.get_data()
        assert isinstance(data, list)
        assert len(data) > 1000  # Should have thousands of records

    def test_get_actual(self):
        """Test getting most recent UDI"""
        record = UDICatalog.get_actual()
        assert isinstance(record, dict)
        assert "valor" in record
        assert "fecha" in record
        assert "tipo" in record

    def test_get_por_fecha(self):
        """Test getting UDI by date"""
        # Test with a known date
        record = UDICatalog.get_por_fecha("2024-01-01")
        if record:  # May not exist for exact date
            assert isinstance(record, dict)
            assert "valor" in record

    def test_pesos_a_udis(self):
        """Test converting pesos to UDIs"""
        result = UDICatalog.pesos_a_udis(10000, "2024-01-01")
        if result is not None:
            assert isinstance(result, float)
            assert result > 0

    def test_udis_a_pesos(self):
        """Test converting UDIs to pesos"""
        result = UDICatalog.udis_a_pesos(100, "2024-01-01")
        if result is not None:
            assert isinstance(result, float)
            assert result > 0


class TestTipoCambioUSDCatalog:
    """Tests for USD/MXN Exchange Rate Catalog"""

    def test_get_data(self):
        """Test getting all exchange rate data"""
        data = TipoCambioUSDCatalog.get_data()
        assert isinstance(data, list)
        assert len(data) > 1000  # Should have thousands of records

    def test_get_actual(self):
        """Test getting most recent exchange rate"""
        record = TipoCambioUSDCatalog.get_actual()
        assert isinstance(record, dict)
        assert "tipo_cambio" in record
        assert "fecha" in record

    def test_get_valor_actual(self):
        """Test getting current exchange rate value"""
        rate = TipoCambioUSDCatalog.get_valor_actual()
        assert isinstance(rate, float)
        assert rate > 10  # MXN per USD should be reasonable

    def test_usd_a_mxn(self):
        """Test converting USD to MXN"""
        result = TipoCambioUSDCatalog.usd_a_mxn(100, "2024-01-01")
        if result is not None:
            assert isinstance(result, float)
            assert result > 1000  # 100 USD should be more than 1000 MXN

    def test_mxn_a_usd(self):
        """Test converting MXN to USD"""
        result = TipoCambioUSDCatalog.mxn_a_usd(20000, "2024-01-01")
        if result is not None:
            assert isinstance(result, float)
            assert result < 200  # 20000 MXN should be less than 200 USD


class TestTIIE28Catalog:
    """Tests for TIIE 28-day Catalog"""

    def test_get_data(self):
        """Test getting all TIIE data"""
        data = TIIE28Catalog.get_data()
        assert isinstance(data, list)
        assert len(data) > 1000  # Should have thousands of records

    def test_get_actual(self):
        """Test getting most recent TIIE rate"""
        record = TIIE28Catalog.get_actual()
        assert isinstance(record, dict)
        assert "tasa" in record
        assert "fecha" in record

    def test_get_tasa_actual(self):
        """Test getting current TIIE rate value"""
        rate = TIIE28Catalog.get_tasa_actual()
        assert isinstance(rate, float)
        assert rate > 0 and rate < 50  # Reasonable interest rate range

    def test_calcular_interes(self):
        """Test calculating interest using TIIE"""
        result = TIIE28Catalog.calcular_interes(10000, "2024-01-01", "2024-01-31")
        if result is not None:
            assert isinstance(result, float)
            assert result >= 0


class TestCETES28Catalog:
    """Tests for CETES 28-day Catalog"""

    def test_get_data(self):
        """Test getting all CETES data"""
        data = CETES28Catalog.get_data()
        assert isinstance(data, list)
        assert len(data) > 1000  # Should have thousands of records

    def test_get_actual(self):
        """Test getting most recent CETES rate"""
        record = CETES28Catalog.get_actual()
        assert isinstance(record, dict)
        assert "tasa" in record
        assert "fecha" in record
        assert record.get("instrumento") == "CETES"

    def test_get_tasa_actual(self):
        """Test getting current CETES rate value"""
        rate = CETES28Catalog.get_tasa_actual()
        assert isinstance(rate, float)
        assert rate > 0 and rate < 20  # Reasonable CETES rate range

    def test_calcular_rendimiento(self):
        """Test calculating CETES return"""
        result = CETES28Catalog.calcular_rendimiento(10000, "2024-01-01", "2024-01-31")
        if result is not None:
            assert isinstance(result, float)
            assert result >= 10000  # Should at least return principal


class TestInflacionAnualCatalog:
    """Tests for Annual Inflation Catalog"""

    def test_get_data(self):
        """Test getting all inflation data"""
        data = InflacionAnualCatalog.get_data()
        assert isinstance(data, list)
        assert len(data) > 100  # Should have many records

    def test_get_actual(self):
        """Test getting most recent inflation rate"""
        record = InflacionAnualCatalog.get_actual()
        assert isinstance(record, dict)
        assert "inflacion_anual" in record
        assert "fecha" in record

    def test_get_tasa_actual(self):
        """Test getting current inflation rate"""
        rate = InflacionAnualCatalog.get_tasa_actual()
        assert isinstance(rate, float)
        assert rate >= 0 and rate < 50  # Reasonable inflation rate

    def test_ajustar_por_inflacion(self):
        """Test adjusting amount for inflation"""
        result = InflacionAnualCatalog.ajustar_por_inflacion(10000, "2023-01-01", "2024-01-01")
        if result is not None:
            assert isinstance(result, float)
            assert result > 0


class TestSalariosMinimosCatalog:
    """Tests for Minimum Wage Catalog"""

    def test_get_data(self):
        """Test getting all minimum wage data"""
        data = SalariosMinimosCatalog.get_data()
        assert isinstance(data, list)
        assert len(data) > 500  # Should have many records

    def test_get_actual_general(self):
        """Test getting most recent minimum wage for general zone"""
        record = SalariosMinimosCatalog.get_actual_general()
        assert isinstance(record, dict)
        assert "salario_minimo" in record
        assert "zona" in record
        assert record.get("zona") == "general"

    def test_get_actual_frontera(self):
        """Test getting most recent minimum wage for border zone"""
        record = SalariosMinimosCatalog.get_actual_frontera()
        assert isinstance(record, dict)
        assert "salario_minimo" in record
        assert "zona" in record
        assert record.get("zona") == "frontera_norte"

    def test_get_salario_actual_zona(self):
        """Test getting current salary for specific zone"""
        general_salary = SalariosMinimosCatalog.get_salario_actual_zona("general")
        border_salary = SalariosMinimosCatalog.get_salario_actual_zona("frontera_norte")

        assert isinstance(general_salary, float)
        assert isinstance(border_salary, float)
        assert border_salary >= general_salary  # Border zone should have higher minimum wage

    def test_get_por_fecha_zona(self):
        """Test getting minimum wage by date and zone"""
        record = SalariosMinimosCatalog.get_por_fecha_zona("2024-01-01", "general")
        if record:  # May not exist for exact date
            assert isinstance(record, dict)
            assert "salario_minimo" in record
            assert record.get("zona") == "general"
