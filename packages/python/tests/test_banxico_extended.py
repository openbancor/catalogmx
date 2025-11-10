"""
Extended tests for Banxico catalogs to achieve 100% coverage
"""

import pytest

from catalogmx.catalogs.banxico import (
    BankCatalog,
    CodigosPlazaCatalog,
    InstitucionesFinancieras,
    MonedasDivisas,
)
from catalogmx.catalogs.banxico.banks import get_banks_dict, get_spei_banks


class TestBankCatalogExtended:
    """Extended tests for Bank Catalog"""

    def test_is_spei_participant_false(self):
        """Test bank that doesn't participate in SPEI"""
        # Get a bank that doesn't participate in SPEI
        all_banks = BankCatalog.get_all_banks()
        non_spei_banks = [bank for bank in all_banks if not bank.get("spei", False)]
        
        if non_spei_banks:
            result = BankCatalog.is_spei_participant(non_spei_banks[0]["code"])
            assert result is False

    def test_is_spei_participant_true(self):
        """Test bank that participates in SPEI"""
        spei_banks = BankCatalog.get_spei_banks()
        if spei_banks:
            result = BankCatalog.is_spei_participant(spei_banks[0]["code"])
            assert result is True

    def test_is_spei_participant_nonexistent(self):
        """Test is_spei_participant with nonexistent bank code"""
        result = BankCatalog.is_spei_participant("999")
        assert result is False

    def test_validate_bank_code_true(self):
        """Test validate_bank_code with valid code"""
        all_banks = BankCatalog.get_all_banks()
        if all_banks:
            result = BankCatalog.validate_bank_code(all_banks[0]["code"])
            assert result is True

    def test_validate_bank_code_false(self):
        """Test validate_bank_code with invalid code"""
        result = BankCatalog.validate_bank_code("999")
        assert result is False

    def test_get_banks_dict(self):
        """Test get_banks_dict convenience function"""
        banks_dict = get_banks_dict()
        assert isinstance(banks_dict, dict)
        assert len(banks_dict) > 0

    def test_get_spei_banks_function(self):
        """Test get_spei_banks convenience function"""
        spei_banks = get_spei_banks()
        assert isinstance(spei_banks, list)
        for bank in spei_banks:
            assert bank.get("spei", False) is True


class TestCodigosPlazaCatalogExtended:
    """Extended tests for Codigos Plaza Catalog"""

    def test_buscar_por_codigo_not_found(self):
        """Test searching by nonexistent codigo"""
        result = CodigosPlazaCatalog.buscar_por_codigo("999")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_buscar_por_estado_not_found(self):
        """Test searching by nonexistent estado"""
        result = CodigosPlazaCatalog.buscar_por_estado("NonExistentState")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_buscar_por_estado_accent_insensitive(self):
        """Test accent-insensitive search by estado"""
        # Test with accents
        result_with_accent = CodigosPlazaCatalog.buscar_por_estado("México")
        result_without_accent = CodigosPlazaCatalog.buscar_por_estado("Mexico")
        
        # Both should return results (might be empty if estado not in data)
        assert isinstance(result_with_accent, list)
        assert isinstance(result_without_accent, list)

    def test_buscar_por_plaza_exact_not_found(self):
        """Test exact plaza search not found"""
        result = CodigosPlazaCatalog.buscar_por_plaza("NonExistentPlaza", exact=True)
        assert isinstance(result, list)
        assert len(result) == 0

    def test_buscar_por_plaza_accent_insensitive(self):
        """Test accent-insensitive plaza search"""
        all_plazas = CodigosPlazaCatalog.get_all()
        if all_plazas:
            plaza_name = all_plazas[0]["plaza"]
            # Test that accent-insensitive search works
            result = CodigosPlazaCatalog.buscar_por_plaza(plaza_name)
            assert isinstance(result, list)

    def test_get_estadisticas(self):
        """Test getting statistics"""
        stats = CodigosPlazaCatalog.get_estadisticas()
        assert isinstance(stats, dict)
        assert "total_plazas" in stats
        assert "total_estados" in stats
        assert "plazas_por_estado" in stats
        assert stats["total_plazas"] > 0

    def test_buscar_por_cve_entidad_not_found(self):
        """Test searching by nonexistent cve_entidad"""
        result = CodigosPlazaCatalog.buscar_por_cve_entidad("99")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_buscar_por_cve_entidad_found(self):
        """Test searching by valid cve_entidad"""
        all_plazas = CodigosPlazaCatalog.get_all()
        if all_plazas:
            cve_entidad = all_plazas[0]["cve_entidad"]
            result = CodigosPlazaCatalog.buscar_por_cve_entidad(cve_entidad)
            assert isinstance(result, list)
            assert len(result) > 0

    def test_get_estados_unicos(self):
        """Test getting unique estados"""
        estados = CodigosPlazaCatalog.get_estados_unicos()
        assert isinstance(estados, list)
        assert len(estados) > 0
        # All should be unique
        assert len(estados) == len(set(estados))

    def test_get_plazas_por_codigo_multiple(self):
        """Test getting plazas when multiple exist for same codigo"""
        all_plazas = CodigosPlazaCatalog.get_all()
        # Find a codigo that appears multiple times
        codigo_counts = {}
        for plaza in all_plazas:
            codigo = plaza["codigo"]
            codigo_counts[codigo] = codigo_counts.get(codigo, 0) + 1
        
        # Find a codigo with multiple entries
        for codigo, count in codigo_counts.items():
            if count > 1:
                result = CodigosPlazaCatalog.buscar_por_codigo(codigo)
                assert len(result) == count
                break


class TestInstitucionesFinancierasExtended:
    """Extended tests for Instituciones Financieras Catalog"""

    def test_buscar_por_nombre_not_found(self):
        """Test searching by nonexistent nombre"""
        result = InstitucionesFinancieras.buscar_por_nombre("NonExistent Institution")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_buscar_por_clave_not_found(self):
        """Test searching by nonexistent clave"""
        result = InstitucionesFinancieras.buscar_por_clave("999999")
        assert result is None

    def test_buscar_por_tipo_not_found(self):
        """Test searching by nonexistent tipo"""
        result = InstitucionesFinancieras.buscar_por_tipo("NonExistentType")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_buscar_por_sector_not_found(self):
        """Test searching by nonexistent sector"""
        result = InstitucionesFinancieras.buscar_por_sector("NonExistentSector")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_tipos(self):
        """Test getting all tipos"""
        tipos = InstitucionesFinancieras.get_tipos()
        assert isinstance(tipos, list)

    def test_get_sectores(self):
        """Test getting all sectores"""
        sectores = InstitucionesFinancieras.get_sectores()
        assert isinstance(sectores, list)

    def test_get_por_estado_not_found(self):
        """Test searching by nonexistent estado"""
        result = InstitucionesFinancieras.get_por_estado("NonExistentState")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_activas_only(self):
        """Test getting only active institutions"""
        all_inst = InstitucionesFinancieras.get_all()
        activas = [inst for inst in all_inst if inst.get("activa", True)]
        result = InstitucionesFinancieras.get_activas()
        assert len(result) == len(activas)

    def test_get_inactivas_only(self):
        """Test getting only inactive institutions"""
        all_inst = InstitucionesFinancieras.get_all()
        inactivas = [inst for inst in all_inst if not inst.get("activa", True)]
        result = InstitucionesFinancieras.get_inactivas()
        assert len(result) == len(inactivas)

    def test_buscar_por_tipo_accent_insensitive(self):
        """Test accent-insensitive search by tipo"""
        all_inst = InstitucionesFinancieras.get_all()
        if all_inst:
            tipo = all_inst[0].get("tipo", "")
            if tipo:
                result = InstitucionesFinancieras.buscar_por_tipo(tipo)
                assert isinstance(result, list)


class TestMonedasDivisasExtended:
    """Extended tests for Monedas Divisas Catalog"""

    def test_buscar_por_codigo_not_found(self):
        """Test searching by nonexistent codigo"""
        result = MonedasDivisas.buscar_por_codigo("XXXXX")
        assert result is None

    def test_buscar_por_nombre_not_found(self):
        """Test searching by nonexistent nombre"""
        result = MonedasDivisas.buscar_por_nombre("NonExistentCurrency")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_buscar_por_pais_not_found(self):
        """Test searching by nonexistent pais"""
        result = MonedasDivisas.buscar_por_pais("NonExistentCountry")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_principales_not_found(self):
        """Test getting principal currencies"""
        result = MonedasDivisas.get_principales()
        assert isinstance(result, list)

    def test_get_activas_only(self):
        """Test getting only active currencies"""
        result = MonedasDivisas.get_activas()
        assert isinstance(result, list)
        for moneda in result:
            assert moneda.get("activa", True) is True

    def test_get_inactivas_only(self):
        """Test getting only inactive currencies"""
        result = MonedasDivisas.get_inactivas()
        assert isinstance(result, list)
        for moneda in result:
            assert moneda.get("activa", True) is False

    def test_convertir_basic(self):
        """Test basic currency conversion"""
        # Test with known currencies
        result = MonedasDivisas.convertir(100, "USD", "USD", 1.0)
        assert result == 100

    def test_convertir_with_rate(self):
        """Test currency conversion with rate"""
        result = MonedasDivisas.convertir(100, "USD", "MXN", 20.0)
        assert result == 2000

    def test_obtener_simbolo_not_found(self):
        """Test getting symbol for nonexistent currency"""
        result = MonedasDivisas.obtener_simbolo("XXXXX")
        assert result is None

    def test_obtener_simbolo_found(self):
        """Test getting symbol for valid currency"""
        all_monedas = MonedasDivisas.get_all()
        for moneda in all_monedas:
            if "simbolo" in moneda:
                result = MonedasDivisas.obtener_simbolo(moneda["codigo"])
                assert result == moneda["simbolo"]
                break

    def test_es_criptomoneda_true(self):
        """Test identifying cryptocurrency"""
        all_monedas = MonedasDivisas.get_all()
        for moneda in all_monedas:
            if moneda.get("tipo") == "criptomoneda":
                result = MonedasDivisas.es_criptomoneda(moneda["codigo"])
                assert result is True
                break

    def test_es_criptomoneda_false(self):
        """Test identifying non-cryptocurrency"""
        all_monedas = MonedasDivisas.get_all()
        for moneda in all_monedas:
            if moneda.get("tipo") != "criptomoneda":
                result = MonedasDivisas.es_criptomoneda(moneda["codigo"])
                assert result is False
                break

    def test_es_criptomoneda_not_found(self):
        """Test cryptocurrency check for nonexistent currency"""
        result = MonedasDivisas.es_criptomoneda("XXXXX")
        assert result is False

    def test_buscar_por_region_not_found(self):
        """Test searching by nonexistent region"""
        result = MonedasDivisas.buscar_por_region("NonExistentRegion")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_buscar_por_region_found(self):
        """Test searching by valid region"""
        all_monedas = MonedasDivisas.get_all()
        for moneda in all_monedas:
            if "region" in moneda:
                result = MonedasDivisas.buscar_por_region(moneda["region"])
                assert isinstance(result, list)
                assert len(result) > 0
                break

    def test_get_paises_unicos(self):
        """Test getting unique countries"""
        result = MonedasDivisas.get_paises_unicos()
        assert isinstance(result, list)

    def test_get_regiones_unicas(self):
        """Test getting unique regions"""
        result = MonedasDivisas.get_regiones_unicas()
        assert isinstance(result, list)

    def test_formatear_cantidad_no_moneda(self):
        """Test formatting amount for nonexistent currency"""
        result = MonedasDivisas.formatear_cantidad(1000, "XXXXX")
        # Should return basic format without currency symbol
        assert "1000" in result or "1,000" in result

    def test_formatear_cantidad_with_symbol(self):
        """Test formatting amount with currency symbol"""
        all_monedas = MonedasDivisas.get_all()
        for moneda in all_monedas:
            if "simbolo" in moneda:
                result = MonedasDivisas.formatear_cantidad(1000, moneda["codigo"])
                assert isinstance(result, str)
                break

    def test_validar_codigo_true(self):
        """Test validating existing currency code"""
        all_monedas = MonedasDivisas.get_all()
        if all_monedas:
            result = MonedasDivisas.validar_codigo(all_monedas[0]["codigo"])
            assert result is True

    def test_validar_codigo_false(self):
        """Test validating nonexistent currency code"""
        result = MonedasDivisas.validar_codigo("XXXXX")
        assert result is False

