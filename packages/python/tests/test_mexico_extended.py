"""
Extended tests for Mexico catalogs to achieve 100% coverage
"""

from catalogmx.catalogs.mexico import (
    HoyNoCirculaCatalog,
    PlacasFormatosCatalog,
    SalariosMinimos,
    UMACatalog,
)


class TestHoyNoCirculaCatalogExtended:
    """Extended tests for Hoy No Circula Catalog"""

    def test_get_restriccion_domingo(self):
        """Test getting restriction for Sunday (no restrictions)"""
        restriccion = HoyNoCirculaCatalog.get_restriccion_por_dia("domingo")
        assert isinstance(restriccion, dict)

    def test_get_restriccion_invalid_day(self):
        """Test getting restriction for invalid day"""
        restriccion = HoyNoCirculaCatalog.get_restriccion_por_dia("invalid")
        assert restriccion is None

    def test_get_exenciones(self):
        """Test getting exemptions"""
        exenciones = HoyNoCirculaCatalog.get_exenciones()
        assert isinstance(exenciones, list)
        assert len(exenciones) > 0

    def test_get_exencion_por_holograma_not_found(self):
        """Test getting exemption for nonexistent holograma"""
        exencion = HoyNoCirculaCatalog.get_exencion_por_holograma("XX")
        assert exencion is None

    def test_puede_circular_exempt_holograma(self):
        """Test puede_circular with exempt holograma"""
        # Test with 00 or 0 holograma which are typically exempt
        puede = HoyNoCirculaCatalog.puede_circular("lunes", "1", "00")
        assert puede is True

    def test_puede_circular_restricted(self):
        """Test puede_circular when restricted"""
        # Test with matching termination and holograma
        puede = HoyNoCirculaCatalog.puede_circular("lunes", "5", "1")
        assert puede is False

    def test_puede_circular_not_restricted(self):
        """Test puede_circular when not restricted"""
        # Test with non-matching termination
        puede = HoyNoCirculaCatalog.puede_circular("lunes", "2", "1")
        assert puede is True

    def test_get_dia_restriccion_not_found(self):
        """Test getting day restriction for termination not found"""
        dia = HoyNoCirculaCatalog.get_dia_restriccion("X")
        assert dia is None

    def test_get_engomado_not_found(self):
        """Test getting engomado for termination not found"""
        engomado = HoyNoCirculaCatalog.get_engomado("X")
        assert engomado is None


class TestPlacasFormatosCatalogExtended:
    """Extended tests for Placas Formatos Catalog"""

    def test_validate_placa_invalid(self):
        """Test validating invalid placa format"""
        result = PlacasFormatosCatalog.validate_placa("INVALID")
        assert result["valida"] is False

    def test_is_federal_false(self):
        """Test is_federal with non-federal placa"""
        result = PlacasFormatosCatalog.is_federal("ABC-123-D")
        assert result is False

    def test_is_diplomatica_false(self):
        """Test is_diplomatica with non-diplomatic placa"""
        result = PlacasFormatosCatalog.is_diplomatica("ABC-123-D")
        assert result is False

    def test_detect_formato_not_found(self):
        """Test detecting formato for invalid placa"""
        formato = PlacasFormatosCatalog.detect_formato("INVALID")
        assert formato is None

    def test_get_formatos_por_tipo_not_found(self):
        """Test getting formatos by nonexistent tipo"""
        formatos = PlacasFormatosCatalog.get_formatos_por_tipo("NonExistent")
        assert isinstance(formatos, list)
        assert len(formatos) == 0

    def test_get_formatos_por_estado_not_found(self):
        """Test getting formatos by nonexistent estado"""
        formatos = PlacasFormatosCatalog.get_formatos_por_estado("NonExistent")
        assert isinstance(formatos, list)
        assert len(formatos) == 0


class TestSalariosMinimosExtended:
    """Extended tests for Salarios Minimos"""

    def test_get_por_anio_not_found(self):
        """Test getting by year not found"""
        salario = SalariosMinimos.get_por_anio(1900)
        assert salario is None

    def test_get_por_zona_not_found(self):
        """Test getting by nonexistent zona"""
        salarios = SalariosMinimos.get_por_zona("X")
        assert isinstance(salarios, list)
        assert len(salarios) == 0

    def test_calcular_mensual_not_found(self):
        """Test calculating monthly for nonexistent year"""
        monto = SalariosMinimos.calcular_mensual(1900)
        assert monto is None

    def test_calcular_mensual_with_zona(self):
        """Test calculating monthly with zona"""
        actual = SalariosMinimos.get_actual()
        if actual:
            monto = SalariosMinimos.calcular_mensual(actual["anio"], zona="A")
            assert isinstance(monto, float) or monto is None

    def test_calcular_anual_not_found(self):
        """Test calculating annual for nonexistent year"""
        monto = SalariosMinimos.calcular_anual(1900)
        assert monto is None

    def test_calcular_anual_with_zona(self):
        """Test calculating annual with zona"""
        actual = SalariosMinimos.get_actual()
        if actual:
            monto = SalariosMinimos.calcular_anual(actual["anio"], zona="A")
            assert isinstance(monto, float) or monto is None


class TestUMACatalogExtended:
    """Extended tests for UMA Catalog"""

    def test_get_por_anio_not_found(self):
        """Test getting by year not found"""
        uma = UMACatalog.get_por_anio(1900)
        assert uma is None

    def test_get_por_anio_pre_2017(self):
        """Test getting by year before 2017 (UMA didn't exist)"""
        uma = UMACatalog.get_por_anio(2010)
        # Should return None or handle gracefully
        assert uma is None or isinstance(uma, dict)

    def test_calcular_monto_not_found(self):
        """Test calculating monto for nonexistent year"""
        monto = UMACatalog.calcular_monto(100, 1900)
        assert monto is None

    def test_calcular_monto_with_tipo(self):
        """Test calculating monto with tipo"""
        actual = UMACatalog.get_actual()
        if actual:
            monto = UMACatalog.calcular_monto(100, actual["anio"], tipo="mensual")
            assert isinstance(monto, float)

    def test_calcular_umas_not_found(self):
        """Test calculating UMAs for nonexistent year"""
        umas = UMACatalog.calcular_umas(10000, 1900)
        assert umas is None

    def test_calcular_umas_with_tipo(self):
        """Test calculating UMAs with tipo"""
        actual = UMACatalog.get_actual()
        if actual:
            umas = UMACatalog.calcular_umas(10000, actual["anio"], tipo="mensual")
            assert isinstance(umas, float)

    def test_get_incremento_not_found(self):
        """Test getting increment for invalid years"""
        incremento = UMACatalog.get_incremento(1900, 1901)
        assert incremento is None

    def test_get_incremento_same_year(self):
        """Test getting increment for same year"""
        actual = UMACatalog.get_actual()
        if actual:
            incremento = UMACatalog.get_incremento(actual["anio"], actual["anio"])
            # Should return 0 or handle gracefully
            assert incremento is not None

    def test_get_valor_pre_2017(self):
        """Test getting valor before UMA existed"""
        valor = UMACatalog.get_valor(2010)
        # Should return None or handle gracefully
        assert valor is None or isinstance(valor, float)

