"""
Complete tests for Banxico catalogs based on actual APIs
"""

from catalogmx.catalogs.banxico import InstitucionesFinancieras, MonedasDivisas, BankCatalog


class TestInstitucionesFinancierasComplete:
    """Complete tests for Instituciones Financieras"""

    def test_get_all(self):
        """Test getting all institutions"""
        result = InstitucionesFinancieras.get_all()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_por_codigo_found(self):
        """Test getting institution by code"""
        all_inst = InstitucionesFinancieras.get_all()
        if all_inst:
            codigo = all_inst[0]["codigo"]
            result = InstitucionesFinancieras.get_por_codigo(codigo)
            assert result is not None
            assert result["codigo"] == codigo

    def test_get_por_codigo_not_found(self):
        """Test getting institution by nonexistent code"""
        result = InstitucionesFinancieras.get_por_codigo("999")
        assert result is None

    def test_buscar_por_tipo(self):
        """Test searching by tipo"""
        result = InstitucionesFinancieras.buscar_por_tipo("banco")
        assert isinstance(result, list)

    def test_buscar_por_tipo_not_found(self):
        """Test searching by nonexistent tipo"""
        result = InstitucionesFinancieras.buscar_por_tipo("NonExistent12345XYZ")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_por_regulador(self):
        """Test getting by regulador"""
        result = InstitucionesFinancieras.get_por_regulador("CNBV")
        assert isinstance(result, list)

    def test_get_por_regulador_not_found(self):
        """Test getting by nonexistent regulador"""
        result = InstitucionesFinancieras.get_por_regulador("NONEXISTENT")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_bancos(self):
        """Test getting bancos"""
        result = InstitucionesFinancieras.get_bancos()
        assert isinstance(result, list)

    def test_get_sofomes(self):
        """Test getting SOFOMes"""
        result = InstitucionesFinancieras.get_sofomes()
        assert isinstance(result, list)

    def test_get_sector_popular(self):
        """Test getting sector popular"""
        result = InstitucionesFinancieras.get_sector_popular()
        assert isinstance(result, list)

    def test_get_seguros_y_fianzas(self):
        """Test getting seguros y fianzas"""
        result = InstitucionesFinancieras.get_seguros_y_fianzas()
        assert isinstance(result, list)

    def test_get_mercado_valores(self):
        """Test getting mercado valores"""
        result = InstitucionesFinancieras.get_mercado_valores()
        assert isinstance(result, list)

    def test_get_fintech(self):
        """Test getting fintech institutions"""
        result = InstitucionesFinancieras.get_fintech()
        assert isinstance(result, list)

    def test_get_retiro(self):
        """Test getting retiro institutions"""
        result = InstitucionesFinancieras.get_retiro()
        assert isinstance(result, list)

    def test_validar_codigo_true(self):
        """Test validating existing code"""
        all_inst = InstitucionesFinancieras.get_all()
        if all_inst:
            result = InstitucionesFinancieras.validar_codigo(all_inst[0]["codigo"])
            assert result is True

    def test_validar_codigo_false(self):
        """Test validating nonexistent code"""
        result = InstitucionesFinancieras.validar_codigo("999")
        assert result is False

    def test_get_descripcion_regulador_cnbv(self):
        """Test getting CNBV description"""
        result = InstitucionesFinancieras.get_descripcion_regulador("CNBV")
        assert result is not None
        assert "Comisión" in result

    def test_get_descripcion_regulador_cnsf(self):
        """Test getting CNSF description"""
        result = InstitucionesFinancieras.get_descripcion_regulador("CNSF")
        assert result is not None

    def test_get_descripcion_regulador_consar(self):
        """Test getting CONSAR description"""
        result = InstitucionesFinancieras.get_descripcion_regulador("CONSAR")
        assert result is not None

    def test_get_descripcion_regulador_condusef(self):
        """Test getting CONDUSEF description"""
        result = InstitucionesFinancieras.get_descripcion_regulador("CONDUSEF")
        assert result is not None

    def test_get_descripcion_regulador_shcp(self):
        """Test getting SHCP description"""
        result = InstitucionesFinancieras.get_descripcion_regulador("SHCP")
        assert result is not None

    def test_get_descripcion_regulador_not_found(self):
        """Test getting nonexistent regulador"""
        result = InstitucionesFinancieras.get_descripcion_regulador("NONEXISTENT")
        assert result is None

    def test_get_descripcion_regulador_lowercase(self):
        """Test getting regulador with lowercase"""
        result = InstitucionesFinancieras.get_descripcion_regulador("cnbv")
        assert result is not None


class TestMonedasDivisasComplete:
    """Complete tests for Monedas Divisas"""

    def test_get_all(self):
        """Test getting all currencies"""
        result = MonedasDivisas.get_all()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_por_codigo_usd(self):
        """Test getting USD"""
        result = MonedasDivisas.get_por_codigo("USD")
        assert result is not None
        assert result["codigo_iso"] == "USD"

    def test_get_por_codigo_not_found(self):
        """Test getting nonexistent currency"""
        result = MonedasDivisas.get_por_codigo("XXXXX")
        assert result is None

    def test_get_por_codigo_lowercase(self):
        """Test getting currency with lowercase code"""
        result = MonedasDivisas.get_por_codigo("usd")
        assert result is not None

    def test_get_por_pais(self):
        """Test getting currencies by country"""
        result = MonedasDivisas.get_por_pais("México")
        assert isinstance(result, list)

    def test_get_por_pais_case_insensitive(self):
        """Test getting currencies by country (case insensitive)"""
        result = MonedasDivisas.get_por_pais("MÉXICO")
        assert isinstance(result, list)

    def test_get_por_pais_not_found(self):
        """Test getting currencies by nonexistent country"""
        result = MonedasDivisas.get_por_pais("NonExistentCountry12345")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_con_tipo_cambio_banxico(self):
        """Test getting currencies with Banxico exchange rate"""
        result = MonedasDivisas.get_con_tipo_cambio_banxico()
        assert isinstance(result, list)
        for moneda in result:
            assert moneda["tipo_cambio_banxico"] is True

    def test_get_con_tipo_cambio_fix(self):
        """Test getting currencies with FIX exchange rate"""
        result = MonedasDivisas.get_con_tipo_cambio_fix()
        assert isinstance(result, list)
        for moneda in result:
            assert moneda.get("tipo_cambio_fix", False) is True

    def test_get_por_region_america_norte(self):
        """Test getting currencies by North America region"""
        result = MonedasDivisas.get_por_region("America del Norte")
        assert isinstance(result, list)
        codigos = [m["codigo_iso"] for m in result]
        assert "USD" in codigos or "MXN" in codigos or "CAD" in codigos

    def test_get_por_region_america_latina(self):
        """Test getting currencies by Latin America region"""
        result = MonedasDivisas.get_por_region("America Latina")
        assert isinstance(result, list)

    def test_get_por_region_europa(self):
        """Test getting currencies by Europe region"""
        result = MonedasDivisas.get_por_region("Europa")
        assert isinstance(result, list)

    def test_get_por_region_asia_pacifico(self):
        """Test getting currencies by Asia-Pacific region"""
        result = MonedasDivisas.get_por_region("Asia-Pacifico")
        assert isinstance(result, list)

    def test_get_por_region_africa(self):
        """Test getting currencies by Africa region"""
        result = MonedasDivisas.get_por_region("Africa")
        assert isinstance(result, list)

    def test_get_por_region_not_found(self):
        """Test getting currencies by nonexistent region"""
        result = MonedasDivisas.get_por_region("NonExistentRegion")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_principales(self):
        """Test getting principal currencies"""
        result = MonedasDivisas.get_principales()
        assert isinstance(result, list)
        assert len(result) > 0
        codigos = [m["codigo_iso"] for m in result]
        assert "MXN" in codigos
        assert "USD" in codigos

    def test_get_latam(self):
        """Test getting LATAM currencies"""
        result = MonedasDivisas.get_latam()
        assert isinstance(result, list)
        assert len(result) > 0
        codigos = [m["codigo_iso"] for m in result]
        assert "MXN" in codigos

    def test_validar_codigo_iso_true(self):
        """Test validating existing ISO code"""
        assert MonedasDivisas.validar_codigo_iso("USD") is True
        assert MonedasDivisas.validar_codigo_iso("MXN") is True

    def test_validar_codigo_iso_false(self):
        """Test validating nonexistent ISO code"""
        assert MonedasDivisas.validar_codigo_iso("XXXXX") is False

    def test_validar_codigo_iso_case_insensitive(self):
        """Test validating ISO code (case insensitive)"""
        assert MonedasDivisas.validar_codigo_iso("usd") is True
        assert MonedasDivisas.validar_codigo_iso("Usd") is True

    def test_get_formato_moneda_usd(self):
        """Test getting format for USD"""
        result = MonedasDivisas.get_formato_moneda("USD")
        assert result is not None
        assert "simbolo" in result
        assert "decimales" in result
        assert "formato_ejemplo" in result

    def test_get_formato_moneda_not_found(self):
        """Test getting format for nonexistent currency"""
        result = MonedasDivisas.get_formato_moneda("XXXXX")
        assert result is None

    def test_formatear_monto_usd(self):
        """Test formatting amount in USD"""
        result = MonedasDivisas.formatear_monto(1234.56, "USD")
        assert isinstance(result, str)
        assert "1" in result
        assert "234" in result

    def test_formatear_monto_jpy(self):
        """Test formatting amount in JPY (0 decimals)"""
        result = MonedasDivisas.formatear_monto(1234.56, "JPY")
        assert isinstance(result, str)

    def test_formatear_monto_not_found(self):
        """Test formatting amount for nonexistent currency"""
        result = MonedasDivisas.formatear_monto(1234.56, "XXXXX")
        assert isinstance(result, str)
        assert "1234.56" in result

    def test_get_mxn(self):
        """Test getting MXN"""
        result = MonedasDivisas.get_mxn()
        assert result is not None
        assert result["codigo_iso"] == "MXN"

    def test_get_usd(self):
        """Test getting USD"""
        result = MonedasDivisas.get_usd()
        assert result is not None
        assert result["codigo_iso"] == "USD"

    def test_get_eur(self):
        """Test getting EUR"""
        result = MonedasDivisas.get_eur()
        assert result is not None
        assert result["codigo_iso"] == "EUR"

    def test_buscar_por_nombre(self):
        """Test searching by name"""
        result = MonedasDivisas.buscar_por_nombre("dólar")
        assert isinstance(result, list)

    def test_buscar_por_nombre_case_insensitive(self):
        """Test searching by name (case insensitive)"""
        result = MonedasDivisas.buscar_por_nombre("DÓLAR")
        assert isinstance(result, list)

    def test_buscar_por_nombre_not_found(self):
        """Test searching by nonexistent name"""
        result = MonedasDivisas.buscar_por_nombre("NonExistentCurrency12345")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_activas(self):
        """Test getting active currencies"""
        result = MonedasDivisas.get_activas()
        assert isinstance(result, list)
        for moneda in result:
            assert moneda["activa"] is True

    def test_get_info_tipo_cambio_fix(self):
        """Test getting FIX exchange rate info"""
        result = MonedasDivisas.get_info_tipo_cambio_fix()
        assert isinstance(result, dict)
        assert "descripcion" in result
        assert "horario" in result
        assert "uso" in result


class TestBankCatalogComplete:
    """Complete tests for Bank Catalog"""

    def test_get_bank_by_code_not_found(self):
        """Test getting bank by nonexistent code"""
        result = BankCatalog.get_bank_by_code("999")
        assert result is None

    def test_get_bank_by_name_not_found(self):
        """Test getting bank by nonexistent name"""
        result = BankCatalog.get_bank_by_name("NonExistentBank12345")
        assert result is None

    def test_is_spei_participant_nonexistent(self):
        """Test SPEI participant check for nonexistent bank"""
        result = BankCatalog.is_spei_participant("999")
        assert result is False

    def test_validate_bank_code_false(self):
        """Test validating nonexistent bank code"""
        result = BankCatalog.validate_bank_code("999")
        assert result is False

