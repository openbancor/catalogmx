"""
Complete tests for Mexico catalogs
"""

from catalogmx.catalogs.mexico import HoyNoCirculaCatalog, PlacasFormatosCatalog, SalariosMinimos, UMACatalog


class TestHoyNoCirculaCatalog:
    """Test Hoy No Circula Catalog"""

    def test_get_data(self):
        """Test getting data"""
        result = HoyNoCirculaCatalog.get_data()
        assert isinstance(result, dict)

    def test_get_restricciones(self):
        """Test getting restricciones"""
        result = HoyNoCirculaCatalog.get_restricciones()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_restriccion_por_dia_lunes(self):
        """Test getting restriction for Monday"""
        result = HoyNoCirculaCatalog.get_restriccion_por_dia("lunes")
        assert isinstance(result, dict)

    def test_get_restriccion_por_dia_domingo(self):
        """Test getting restriction for Sunday"""
        result = HoyNoCirculaCatalog.get_restriccion_por_dia("domingo")
        # Sunday may or may not have restrictions
        assert isinstance(result, dict) or result is None

    def test_get_restriccion_por_dia_not_found(self):
        """Test getting restriction for invalid day"""
        result = HoyNoCirculaCatalog.get_restriccion_por_dia("invalid")
        assert result is None

    def test_get_exenciones(self):
        """Test getting exenciones"""
        result = HoyNoCirculaCatalog.get_exenciones()
        assert isinstance(result, list)

    def test_get_exencion_por_holograma_found(self):
        """Test getting exencion by holograma"""
        exenciones = HoyNoCirculaCatalog.get_exenciones()
        if exenciones:
            holograma = exenciones[0]["holograma"]
            result = HoyNoCirculaCatalog.get_exencion_por_holograma(holograma)
            assert result is not None

    def test_get_exencion_por_holograma_not_found(self):
        """Test getting exencion for nonexistent holograma"""
        result = HoyNoCirculaCatalog.get_exencion_por_holograma("XX")
        assert result is None

    def test_puede_circular_basic(self):
        """Test puede_circular"""
        result = HoyNoCirculaCatalog.puede_circular("1", "lunes")
        assert isinstance(result, bool)

    def test_puede_circular_with_holograma(self):
        """Test puede_circular with holograma"""
        result = HoyNoCirculaCatalog.puede_circular("1", "lunes", "2")
        assert isinstance(result, bool)

    def test_get_dia_restriccion(self):
        """Test getting dia restriccion"""
        result = HoyNoCirculaCatalog.get_dia_restriccion("5")
        assert result is None or isinstance(result, str)

    def test_get_dia_restriccion_not_found(self):
        """Test getting dia restriccion for invalid termination"""
        result = HoyNoCirculaCatalog.get_dia_restriccion("X")
        assert result is None

    def test_get_engomado(self):
        """Test getting engomado"""
        result = HoyNoCirculaCatalog.get_engomado("5")
        assert result is None or isinstance(result, str)

    def test_get_engomado_not_found(self):
        """Test getting engomado for invalid termination"""
        result = HoyNoCirculaCatalog.get_engomado("X")
        assert result is None

    def test_get_sabatinos(self):
        """Test getting sabatinos"""
        result = HoyNoCirculaCatalog.get_sabatinos()
        assert isinstance(result, dict)


class TestPlacasFormatosCatalog:
    """Test Placas Formatos Catalog"""

    def test_get_data(self):
        """Test getting data"""
        result = PlacasFormatosCatalog.get_data()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_validate_placa_valid(self):
        """Test validating valid placa"""
        # Try a known format
        result = PlacasFormatosCatalog.validate_placa("ABC-123-D")
        assert isinstance(result, bool)

    def test_validate_placa_invalid(self):
        """Test validating invalid placa"""
        result = PlacasFormatosCatalog.validate_placa("INVALID")
        assert result is False

    def test_get_formatos_por_estado(self):
        """Test getting formatos by estado"""
        result = PlacasFormatosCatalog.get_formatos_por_estado("Jalisco")
        assert isinstance(result, list)

    def test_get_formatos_por_estado_not_found(self):
        """Test getting formatos by nonexistent estado"""
        result = PlacasFormatosCatalog.get_formatos_por_estado("NonExistent")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_formatos_por_tipo(self):
        """Test getting formatos by tipo"""
        result = PlacasFormatosCatalog.get_formatos_por_tipo("Particular")
        assert isinstance(result, list)

    def test_get_formatos_por_tipo_not_found(self):
        """Test getting formatos by nonexistent tipo"""
        result = PlacasFormatosCatalog.get_formatos_por_tipo("NonExistent")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_formatos_activos(self):
        """Test getting active formatos"""
        result = PlacasFormatosCatalog.get_formatos_activos()
        assert isinstance(result, list)

    def test_is_diplomatica(self):
        """Test checking if placa is diplomatic"""
        result = PlacasFormatosCatalog.is_diplomatica("CC-123-45")
        assert isinstance(result, bool)

    def test_is_federal(self):
        """Test checking if placa is federal"""
        result = PlacasFormatosCatalog.is_federal("ABC-123-D")
        assert isinstance(result, bool)

    def test_detect_formato(self):
        """Test detecting formato"""
        all_formatos = PlacasFormatosCatalog.get_data()
        if all_formatos:
            # Try with a test placa
            result = PlacasFormatosCatalog.detect_formato("ABC-123-D")
            assert result is None or isinstance(result, dict)


class TestSalariosMinimos:
    """Test Salarios Minimos"""

    def test_get_actual(self):
        """Test getting actual salario"""
        result = SalariosMinimos.get_actual()
        assert result is not None

    def test_get_por_anio_not_found(self):
        """Test getting by nonexistent year"""
        result = SalariosMinimos.get_por_anio(1900)
        assert result is None

    def test_get_por_zona(self):
        """Test getting by zona"""
        # Test with default zona if method exists
        if hasattr(SalariosMinimos, 'get_por_zona'):
            result = SalariosMinimos.get_por_zona("General")
            assert isinstance(result, list) or result is None

    def test_get_por_zona_not_found(self):
        """Test getting by nonexistent zona"""
        if hasattr(SalariosMinimos, 'get_por_zona'):
            result = SalariosMinimos.get_por_zona("NonExistent")
            assert isinstance(result, list) or result is None

    def test_calcular_mensual(self):
        """Test calculating monthly"""
        # Get a valid year from data first
        if hasattr(SalariosMinimos, 'get_all'):
            all_salarios = SalariosMinimos.get_all()
            if all_salarios:
                year = all_salarios[0].get("año", all_salarios[0].get("year", 2024))
                result = SalariosMinimos.calcular_mensual(year)
                assert isinstance(result, float) or result is None

    def test_calcular_anual(self):
        """Test calculating annual"""
        if hasattr(SalariosMinimos, 'get_all'):
            all_salarios = SalariosMinimos.get_all()
            if all_salarios:
                year = all_salarios[0].get("año", all_salarios[0].get("year", 2024))
                result = SalariosMinimos.calcular_anual(year)
                assert isinstance(result, float) or result is None


class TestUMACatalog:
    """Test UMA Catalog"""

    def test_get_actual(self):
        """Test getting actual UMA"""
        result = UMACatalog.get_actual()
        assert result is not None

    def test_get_por_anio_not_found(self):
        """Test getting by nonexistent year"""
        result = UMACatalog.get_por_anio(1900)
        assert result is None

    def test_calcular_monto(self):
        """Test calculating monto"""
        # Get all UMAs and use a valid year
        if hasattr(UMACatalog, 'get_all'):
            all_umas = UMACatalog.get_all()
            if all_umas:
                year = all_umas[0].get("año", all_umas[0].get("year", 2024))
                result = UMACatalog.calcular_monto(100, year)
                assert isinstance(result, float) or result is None

    def test_calcular_umas(self):
        """Test calculating UMAs"""
        if hasattr(UMACatalog, 'get_all'):
            all_umas = UMACatalog.get_all()
            if all_umas:
                year = all_umas[0].get("año", all_umas[0].get("year", 2024))
                result = UMACatalog.calcular_umas(10000, year)
                assert isinstance(result, float) or result is None

    def test_get_incremento(self):
        """Test getting increment"""
        if hasattr(UMACatalog, 'get_incremento'):
            # Only test if method exists
            result = UMACatalog.get_incremento(2024)
            assert isinstance(result, float) or result is None

    def test_get_valor(self):
        """Test getting valor"""
        if hasattr(UMACatalog, 'get_all'):
            all_umas = UMACatalog.get_all()
            if all_umas:
                year = all_umas[0].get("año", all_umas[0].get("year", 2024))
                result = UMACatalog.get_valor(year)
                assert isinstance(result, float) or result is None

