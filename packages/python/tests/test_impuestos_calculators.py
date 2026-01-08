"""
Comprehensive tests for Tax Calculators (IVA, IEPS, Retenciones, Impuestos Locales)
Tests all public methods with edge cases and error handling
"""

import pytest
from datetime import datetime

from catalogmx.calculators.impuestos import (
    IVACalculator,
    IEPSCalculator,
    RetencionCalculator,
    ImpuestosLocalesCalculator,
)


class TestIVACalculator:
    """Tests for IVA (Value Added Tax) Calculator"""

    def test_get_tasa_vigente_general_current(self):
        """Test getting current general IVA rate"""
        tasa = IVACalculator.get_tasa_vigente()
        assert tasa is not None
        assert tasa["tipo"] == "general"
        assert tasa["tasa"] == 16.0

    def test_get_tasa_vigente_frontera(self):
        """Test getting border zone IVA rate"""
        tasa = IVACalculator.get_tasa_vigente(tipo_tasa="frontera")
        assert tasa is not None
        assert tasa["tipo"] == "frontera"
        assert tasa["tasa"] == 8.0

    def test_get_tasa_vigente_tasa_cero(self):
        """Test getting zero rate"""
        tasa = IVACalculator.get_tasa_vigente(tipo_tasa="tasa_cero")
        assert tasa is not None
        assert tasa["tipo"] == "tasa_cero"
        assert tasa["tasa"] == 0.0

    def test_get_tasa_vigente_specific_date_string(self):
        """Test getting rate for specific date as string"""
        tasa = IVACalculator.get_tasa_vigente(fecha="2024-01-01", tipo_tasa="general")
        assert tasa is not None
        assert tasa["tasa"] == 16.0

    def test_get_tasa_vigente_specific_date_datetime(self):
        """Test getting rate for specific date as datetime object"""
        fecha = datetime(2024, 6, 15)
        tasa = IVACalculator.get_tasa_vigente(fecha=fecha, tipo_tasa="general")
        assert tasa is not None
        assert tasa["tasa"] == 16.0

    def test_calcular_general_rate(self):
        """Test IVA calculation with general rate (16%)"""
        result = IVACalculator.calcular(1000)
        assert result["base"] == 1000
        assert result["tasa"] == 16.0
        assert result["iva"] == 160.0
        assert result["total_con_iva"] == 1160.0
        assert result["tipo_tasa"] == "general"

    def test_calcular_frontera_rate(self):
        """Test IVA calculation with border rate (8%)"""
        result = IVACalculator.calcular(1000, tipo_tasa="frontera")
        assert result["base"] == 1000
        assert result["tasa"] == 8.0
        assert result["iva"] == 80.0
        assert result["total_con_iva"] == 1080.0
        assert result["tipo_tasa"] == "frontera"

    def test_calcular_tasa_cero(self):
        """Test IVA calculation with zero rate (0%)"""
        result = IVACalculator.calcular(1000, tipo_tasa="tasa_cero")
        assert result["base"] == 1000
        assert result["tasa"] == 0.0
        assert result["iva"] == 0.0
        assert result["total_con_iva"] == 1000.0
        assert result["tipo_tasa"] == "tasa_cero"

    def test_calcular_zero_base(self):
        """Test IVA calculation with zero base amount"""
        result = IVACalculator.calcular(0)
        assert result["base"] == 0
        assert result["iva"] == 0.0
        assert result["total_con_iva"] == 0.0

    def test_calcular_decimal_base(self):
        """Test IVA calculation with decimal base amount"""
        result = IVACalculator.calcular(1234.56)
        assert result["base"] == 1234.56
        assert abs(result["iva"] - 197.5296) < 0.01
        assert abs(result["total_con_iva"] - 1432.0896) < 0.01

    def test_calcular_incluido_general(self):
        """Test IVA breakdown when included in total (16%)"""
        result = IVACalculator.calcular_incluido(1160)
        assert abs(result["base"] - 1000.0) < 0.01
        assert result["tasa"] == 16.0
        assert abs(result["iva"] - 160.0) < 0.01
        assert result["total_con_iva"] == 1160
        assert result["tipo_tasa"] == "general"

    def test_calcular_incluido_frontera(self):
        """Test IVA breakdown when included in total (8%)"""
        result = IVACalculator.calcular_incluido(1080, tipo_tasa="frontera")
        assert abs(result["base"] - 1000.0) < 0.01
        assert result["tasa"] == 8.0
        assert abs(result["iva"] - 80.0) < 0.01
        assert result["total_con_iva"] == 1080
        assert result["tipo_tasa"] == "frontera"

    def test_calcular_incluido_zero_total(self):
        """Test IVA breakdown with zero total"""
        result = IVACalculator.calcular_incluido(0)
        assert result["base"] == 0.0
        assert result["iva"] == 0.0
        assert result["total_con_iva"] == 0

    def test_calcular_incluido_decimal_total(self):
        """Test IVA breakdown with decimal total"""
        result = IVACalculator.calcular_incluido(2500.50)
        assert abs(result["total_con_iva"] - 2500.50) < 0.01
        assert result["base"] + result["iva"] == pytest.approx(result["total_con_iva"], rel=1e-9)

    def test_get_all_tasas(self):
        """Test getting all historical IVA rates"""
        tasas = IVACalculator.get_all_tasas()
        assert isinstance(tasas, list)
        assert len(tasas) > 0
        # Verify structure
        for tasa in tasas:
            assert "tipo" in tasa
            assert "tasa" in tasa
            assert "vigencia_inicio" in tasa
            assert "descripcion" in tasa


class TestIEPSCalculator:
    """Tests for IEPS (Special Production and Services Tax) Calculator"""

    def test_calcular_ad_valorem(self):
        """Test IEPS ad valorem calculation"""
        result = IEPSCalculator.calcular_ad_valorem(1000, 26.5)
        assert result["base"] == 1000
        assert result["tasa"] == 26.5
        assert result["ieps"] == 265.0
        assert result["tipo_calculo"] == "ad_valorem"
        assert result["unidad"] is None
        assert result["cantidad"] is None

    def test_calcular_ad_valorem_zero_base(self):
        """Test IEPS ad valorem with zero base"""
        result = IEPSCalculator.calcular_ad_valorem(0, 26.5)
        assert result["base"] == 0
        assert result["ieps"] == 0.0

    def test_calcular_ad_valorem_decimal(self):
        """Test IEPS ad valorem with decimal values"""
        result = IEPSCalculator.calcular_ad_valorem(1234.56, 53.0)
        assert result["base"] == 1234.56
        assert result["tasa"] == 53.0
        assert abs(result["ieps"] - 654.3168) < 0.01

    def test_calcular_cuota_fija(self):
        """Test IEPS fixed quota calculation"""
        result = IEPSCalculator.calcular_cuota_fija(100, 1.0, "litro")
        assert result["base"] == 100
        assert result["tasa"] == 1.0
        assert result["ieps"] == 100.0
        assert result["tipo_calculo"] == "cuota_fija"
        assert result["unidad"] == "litro"
        assert result["cantidad"] == 100

    def test_calcular_cuota_fija_zero_quantity(self):
        """Test IEPS fixed quota with zero quantity"""
        result = IEPSCalculator.calcular_cuota_fija(0, 1.0, "litro")
        assert result["ieps"] == 0.0

    def test_calcular_cuota_fija_decimal_quantity(self):
        """Test IEPS fixed quota with decimal quantity"""
        result = IEPSCalculator.calcular_cuota_fija(50.5, 0.508, "cigarro")
        assert result["base"] == 50.5
        assert result["tasa"] == 0.508
        assert abs(result["ieps"] - 25.654) < 0.01

    def test_calcular_bebidas_alcoholicas_beer(self):
        """Test IEPS for beer (up to 14 degrees alcohol) - 26.5% rate"""
        result = IEPSCalculator.calcular_bebidas_alcoholicas(1000, 5)
        assert result["base"] == 1000
        assert result["tasa"] == 26.5
        assert result["ieps"] == 265.0
        assert result["tipo_calculo"] == "ad_valorem"

    def test_calcular_bebidas_alcoholicas_wine(self):
        """Test IEPS for wine (14-20 degrees alcohol) - 30% rate"""
        result = IEPSCalculator.calcular_bebidas_alcoholicas(1000, 15)
        assert result["tasa"] == 30.0
        assert result["ieps"] == 300.0

    def test_calcular_bebidas_alcoholicas_spirits(self):
        """Test IEPS for spirits (over 20 degrees alcohol) - 53% rate"""
        result = IEPSCalculator.calcular_bebidas_alcoholicas(1000, 40)
        assert result["tasa"] == 53.0
        assert result["ieps"] == 530.0

    def test_calcular_bebidas_alcoholicas_boundary_14_degrees(self):
        """Test IEPS at 14 degrees boundary (should use 26.5% rate)"""
        result = IEPSCalculator.calcular_bebidas_alcoholicas(1000, 14)
        assert result["tasa"] == 26.5

    def test_calcular_bebidas_alcoholicas_boundary_14_01_degrees(self):
        """Test IEPS at 14.01 degrees boundary (should use 30% rate)"""
        result = IEPSCalculator.calcular_bebidas_alcoholicas(1000, 14.01)
        assert result["tasa"] == 30.0

    def test_calcular_bebidas_alcoholicas_boundary_20_degrees(self):
        """Test IEPS at 20 degrees boundary (should use 30% rate)"""
        result = IEPSCalculator.calcular_bebidas_alcoholicas(1000, 20)
        assert result["tasa"] == 30.0

    def test_calcular_bebidas_alcoholicas_boundary_20_01_degrees(self):
        """Test IEPS at 20.01 degrees boundary (should use 53% rate)"""
        result = IEPSCalculator.calcular_bebidas_alcoholicas(1000, 20.01)
        assert result["tasa"] == 53.0

    def test_calcular_bebidas_alcoholicas_zero_value(self):
        """Test IEPS for alcoholic beverages with zero value"""
        result = IEPSCalculator.calcular_bebidas_alcoholicas(0, 5)
        assert result["ieps"] == 0.0

    def test_calcular_cigarros(self):
        """Test IEPS for cigarettes (160% + $0.508 per cigarette)"""
        result = IEPSCalculator.calcular_cigarros(100, 20)
        assert result["base"] == 100
        assert result["tasa"] == 160
        # 100 * 160% = 160, 20 * 0.508 = 10.16, total = 170.16
        assert abs(result["ieps"] - 170.16) < 0.01
        assert result["tipo_calculo"] == "ad_valorem"
        assert result["cantidad"] == 20

    def test_calcular_cigarros_zero_value(self):
        """Test IEPS for cigarettes with zero value but some cigarettes"""
        result = IEPSCalculator.calcular_cigarros(0, 20)
        # 0 * 160% = 0, 20 * 0.508 = 10.16
        assert abs(result["ieps"] - 10.16) < 0.01

    def test_calcular_cigarros_zero_cigarettes(self):
        """Test IEPS for cigarettes with zero cigarettes"""
        result = IEPSCalculator.calcular_cigarros(100, 0)
        # 100 * 160% = 160, 0 * 0.508 = 0
        assert result["ieps"] == 160.0

    def test_calcular_cigarros_large_pack(self):
        """Test IEPS for large cigarette pack (100 cigarettes)"""
        result = IEPSCalculator.calcular_cigarros(500, 100)
        # 500 * 160% = 800, 100 * 0.508 = 50.8
        assert abs(result["ieps"] - 850.8) < 0.01

    def test_get_categoria_bebidas_alcoholicas(self):
        """Test getting IEPS category for alcoholic beverages"""
        categoria = IEPSCalculator.get_categoria("bebidas_alcoholicas")
        assert categoria is not None
        assert categoria["categoria"] == "bebidas_alcoholicas"
        assert "descripcion" in categoria
        assert "tasas" in categoria
        assert isinstance(categoria["tasas"], list)

    def test_get_categoria_not_found(self):
        """Test getting non-existent IEPS category"""
        categoria = IEPSCalculator.get_categoria("categoria_inexistente")
        assert categoria is None

    def test_get_all_categorias(self):
        """Test getting all IEPS categories"""
        categorias = IEPSCalculator.get_all_categorias()
        assert isinstance(categorias, list)
        assert len(categorias) > 0
        # Verify structure
        for categoria in categorias:
            assert "categoria" in categoria
            assert "descripcion" in categoria
            assert "tasas" in categoria


class TestRetencionCalculator:
    """Tests for Tax Withholding Calculator (ISR and IVA)"""

    def test_get_retencion_isr_honorarios(self):
        """Test getting ISR withholding info for professional fees"""
        retencion = RetencionCalculator.get_retencion_isr("honorarios")
        assert retencion is not None
        assert retencion["concepto"] == "honorarios"
        assert retencion["tasa"] == 10.0
        assert "descripcion" in retencion

    def test_get_retencion_isr_arrendamiento(self):
        """Test getting ISR withholding info for rent"""
        retencion = RetencionCalculator.get_retencion_isr("arrendamiento")
        assert retencion is not None
        assert retencion["concepto"] == "arrendamiento"
        assert retencion["tasa"] == 10.0

    def test_get_retencion_isr_fletes(self):
        """Test getting ISR withholding info for freight"""
        retencion = RetencionCalculator.get_retencion_isr("fletes")
        assert retencion is not None
        assert retencion["concepto"] == "fletes"
        assert retencion["tasa"] == 4.0

    def test_get_retencion_isr_not_found(self):
        """Test getting non-existent ISR withholding"""
        retencion = RetencionCalculator.get_retencion_isr("concepto_inexistente")
        assert retencion is None

    def test_get_retencion_iva_servicios_profesionales(self):
        """Test getting IVA withholding info for professional services"""
        retencion = RetencionCalculator.get_retencion_iva("servicios_profesionales")
        assert retencion is not None
        assert retencion["concepto"] == "servicios_profesionales"
        assert abs(retencion["tasa"] - 66.67) < 0.01  # 2/3 parts

    def test_get_retencion_iva_not_found(self):
        """Test getting non-existent IVA withholding"""
        retencion = RetencionCalculator.get_retencion_iva("concepto_inexistente")
        assert retencion is None

    def test_calcular_retencion_isr_honorarios(self):
        """Test ISR withholding calculation for professional fees (10%)"""
        result = RetencionCalculator.calcular_retencion_isr(10000, "honorarios")
        assert result["concepto"] == "honorarios"
        assert result["base"] == 10000
        assert result["tasa"] == 10.0
        assert result["retencion"] == 1000.0
        assert result["impuesto_base"] is None

    def test_calcular_retencion_isr_arrendamiento(self):
        """Test ISR withholding calculation for rent (10%)"""
        result = RetencionCalculator.calcular_retencion_isr(15000, "arrendamiento")
        assert result["concepto"] == "arrendamiento"
        assert result["base"] == 15000
        assert result["tasa"] == 10.0
        assert result["retencion"] == 1500.0

    def test_calcular_retencion_isr_fletes(self):
        """Test ISR withholding calculation for freight (4%)"""
        result = RetencionCalculator.calcular_retencion_isr(10000, "fletes")
        assert result["concepto"] == "fletes"
        assert result["base"] == 10000
        assert result["tasa"] == 4.0
        assert result["retencion"] == 400.0

    def test_calcular_retencion_isr_zero_base(self):
        """Test ISR withholding with zero base"""
        result = RetencionCalculator.calcular_retencion_isr(0, "honorarios")
        assert result["retencion"] == 0.0

    def test_calcular_retencion_isr_decimal_base(self):
        """Test ISR withholding with decimal base"""
        result = RetencionCalculator.calcular_retencion_isr(12345.67, "honorarios")
        assert result["base"] == 12345.67
        assert abs(result["retencion"] - 1234.567) < 0.01

    def test_calcular_retencion_isr_not_found(self):
        """Test ISR withholding calculation with non-existent concept"""
        with pytest.raises(ValueError, match="No se encontró retención ISR"):
            RetencionCalculator.calcular_retencion_isr(10000, "concepto_inexistente")

    def test_calcular_retencion_iva_servicios_profesionales(self):
        """Test IVA withholding calculation for professional services (2/3 parts)"""
        result = RetencionCalculator.calcular_retencion_iva(160, "servicios_profesionales")
        assert result["concepto"] == "servicios_profesionales"
        assert result["base"] == 160
        assert abs(result["tasa"] - 66.67) < 0.01
        assert abs(result["retencion"] - 106.67) < 0.1
        assert result["impuesto_base"] == 160

    def test_calcular_retencion_iva_zero_base(self):
        """Test IVA withholding with zero base"""
        result = RetencionCalculator.calcular_retencion_iva(0, "servicios_profesionales")
        assert result["retencion"] == 0.0

    def test_calcular_retencion_iva_not_found(self):
        """Test IVA withholding calculation with non-existent concept"""
        with pytest.raises(ValueError, match="No se encontró retención IVA"):
            RetencionCalculator.calcular_retencion_iva(160, "concepto_inexistente")

    def test_calcular_honorarios(self):
        """Test professional fees withholding helper method"""
        result = RetencionCalculator.calcular_honorarios(10000)
        assert result["concepto"] == "honorarios"
        assert result["retencion"] == 1000.0

    def test_calcular_arrendamiento(self):
        """Test rent withholding helper method"""
        result = RetencionCalculator.calcular_arrendamiento(15000)
        assert result["concepto"] == "arrendamiento"
        assert result["retencion"] == 1500.0

    def test_calcular_fletes(self):
        """Test freight withholding helper method"""
        result = RetencionCalculator.calcular_fletes(10000)
        assert result["concepto"] == "fletes"
        assert result["retencion"] == 400.0

    def test_get_all_retenciones_isr(self):
        """Test getting all ISR withholding concepts"""
        retenciones = RetencionCalculator.get_all_retenciones_isr()
        assert isinstance(retenciones, list)
        assert len(retenciones) > 0
        # Verify structure
        for retencion in retenciones:
            assert "concepto" in retencion
            assert "tasa" in retencion
            assert "descripcion" in retencion

    def test_get_all_retenciones_iva(self):
        """Test getting all IVA withholding concepts"""
        retenciones = RetencionCalculator.get_all_retenciones_iva()
        assert isinstance(retenciones, list)
        assert len(retenciones) > 0
        # Verify structure
        for retencion in retenciones:
            assert "concepto" in retencion
            assert "tasa" in retencion
            assert "descripcion" in retencion


class TestImpuestosLocalesCalculator:
    """Tests for State and Municipal Tax Calculator"""

    def test_get_impuesto_nomina_cdmx(self):
        """Test getting payroll tax rate for CDMX (09)"""
        impuesto = ImpuestosLocalesCalculator.get_impuesto_nomina("09")
        assert impuesto is not None
        assert impuesto["cve_estado"] == "09"
        assert impuesto["estado"] == "Ciudad de México"
        assert impuesto["tasa"] == 3.0

    def test_get_impuesto_nomina_with_leading_zero(self):
        """Test getting payroll tax with state code that has leading zero"""
        impuesto = ImpuestosLocalesCalculator.get_impuesto_nomina("05")
        assert impuesto is not None
        assert impuesto["cve_estado"] == "05"

    def test_get_impuesto_nomina_without_leading_zero(self):
        """Test getting payroll tax with state code without leading zero"""
        impuesto = ImpuestosLocalesCalculator.get_impuesto_nomina("9")
        assert impuesto is not None
        assert impuesto["cve_estado"] == "09"
        assert impuesto["estado"] == "Ciudad de México"

    def test_get_impuesto_nomina_not_found(self):
        """Test getting payroll tax for non-existent state"""
        impuesto = ImpuestosLocalesCalculator.get_impuesto_nomina("99")
        assert impuesto is None

    def test_calcular_impuesto_nomina_cdmx(self):
        """Test payroll tax calculation for CDMX (3%)"""
        impuesto = ImpuestosLocalesCalculator.calcular_impuesto_nomina(100000, "09")
        assert impuesto == 3000.0

    def test_calcular_impuesto_nomina_zero_payroll(self):
        """Test payroll tax calculation with zero payroll"""
        impuesto = ImpuestosLocalesCalculator.calcular_impuesto_nomina(0, "09")
        assert impuesto == 0.0

    def test_calcular_impuesto_nomina_decimal_payroll(self):
        """Test payroll tax calculation with decimal payroll"""
        impuesto = ImpuestosLocalesCalculator.calcular_impuesto_nomina(123456.78, "09")
        assert abs(impuesto - 3703.7034) < 0.01

    def test_calcular_impuesto_nomina_not_found(self):
        """Test payroll tax calculation for non-existent state"""
        with pytest.raises(ValueError, match="No se encontró tasa de impuesto sobre nómina"):
            ImpuestosLocalesCalculator.calcular_impuesto_nomina(100000, "99")

    def test_get_impuesto_hospedaje_quintana_roo(self):
        """Test getting lodging tax rate for Quintana Roo (23)"""
        impuesto = ImpuestosLocalesCalculator.get_impuesto_hospedaje("23")
        assert impuesto is not None
        assert impuesto["cve_estado"] == "23"
        assert impuesto["estado"] == "Quintana Roo"
        assert impuesto["tasa"] > 0

    def test_get_impuesto_hospedaje_not_found(self):
        """Test getting lodging tax for non-existent state"""
        impuesto = ImpuestosLocalesCalculator.get_impuesto_hospedaje("99")
        assert impuesto is None

    def test_calcular_impuesto_hospedaje(self):
        """Test lodging tax calculation"""
        # Get a valid state first
        impuesto_info = ImpuestosLocalesCalculator.get_impuesto_hospedaje("23")
        if impuesto_info:
            impuesto = ImpuestosLocalesCalculator.calcular_impuesto_hospedaje(5000, "23")
            expected = 5000 * (impuesto_info["tasa"] / 100)
            assert abs(impuesto - expected) < 0.01

    def test_calcular_impuesto_hospedaje_zero_amount(self):
        """Test lodging tax calculation with zero amount"""
        impuesto = ImpuestosLocalesCalculator.calcular_impuesto_hospedaje(0, "23")
        assert impuesto == 0.0

    def test_calcular_impuesto_hospedaje_not_found(self):
        """Test lodging tax calculation for non-existent state"""
        with pytest.raises(ValueError, match="No se encontró tasa de impuesto sobre hospedaje"):
            ImpuestosLocalesCalculator.calcular_impuesto_hospedaje(5000, "99")

    def test_get_all_impuestos_nomina(self):
        """Test getting all payroll tax rates"""
        impuestos = ImpuestosLocalesCalculator.get_all_impuestos_nomina()
        assert isinstance(impuestos, list)
        assert len(impuestos) == 32  # 32 states in Mexico
        # Verify structure
        for impuesto in impuestos:
            assert "estado" in impuesto
            assert "cve_estado" in impuesto
            assert "tasa" in impuesto
            assert "base" in impuesto

    def test_get_all_impuestos_hospedaje(self):
        """Test getting all lodging tax rates"""
        impuestos = ImpuestosLocalesCalculator.get_all_impuestos_hospedaje()
        assert isinstance(impuestos, list)
        assert len(impuestos) == 32  # 32 states in Mexico
        # Verify structure
        for impuesto in impuestos:
            assert "estado" in impuesto
            assert "cve_estado" in impuesto
            assert "tasa" in impuesto
            assert "base" in impuesto
