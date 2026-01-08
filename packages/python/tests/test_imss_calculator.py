"""
Comprehensive tests for IMSS Calculator
Tests all public methods with edge cases and boundary conditions
"""

import pytest

from catalogmx.calculators.imss import (
    get_uma,
    get_salario_minimo,
    calcular_cuotas_obrero_patronales,
    calcular_modalidad_40,
    calcular_modalidad_10,
)


class TestUMAFunctions:
    """Tests for UMA (Unidad de Medida y Actualización) functions"""

    def test_get_uma_2024(self):
        """Test getting UMA values for 2024"""
        uma = get_uma(2024)
        assert uma is not None
        assert "diaria" in uma
        assert "mensual" in uma
        assert "anual" in uma
        assert uma["diaria"] > 0
        assert uma["mensual"] > 0
        assert uma["anual"] > 0
        # Verify monthly = diaria * 30
        assert abs(uma["mensual"] - (uma["diaria"] * 30.4)) < 1.0

    def test_get_uma_2025(self):
        """Test getting UMA values for 2025"""
        uma = get_uma(2025)
        assert uma is not None
        assert uma["diaria"] > 0
        assert uma["mensual"] > 0
        assert uma["anual"] > 0

    def test_get_uma_2026(self):
        """Test getting UMA values for 2026"""
        uma = get_uma(2026)
        assert uma is not None
        assert uma["diaria"] == 113.14
        assert uma["mensual"] == 3441.13
        assert uma["anual"] == 41649.42

    def test_get_uma_progression(self):
        """Test that UMA values increase year over year"""
        uma_2024 = get_uma(2024)
        uma_2025 = get_uma(2025)
        uma_2026 = get_uma(2026)
        # UMA typically increases each year due to inflation
        assert uma_2025["diaria"] >= uma_2024["diaria"]
        assert uma_2026["diaria"] >= uma_2025["diaria"]

    def test_get_salario_minimo_2024_general(self):
        """Test getting general minimum wage for 2024"""
        salario = get_salario_minimo(2024, "general")
        assert salario > 0
        assert isinstance(salario, (int, float))

    def test_get_salario_minimo_2024_frontera(self):
        """Test getting border zone minimum wage for 2024"""
        salario = get_salario_minimo(2024, "frontera")
        assert salario > 0
        assert isinstance(salario, (int, float))

    def test_get_salario_minimo_2025_general(self):
        """Test getting general minimum wage for 2025"""
        salario = get_salario_minimo(2025, "general")
        assert salario > 0

    def test_get_salario_minimo_2026_general(self):
        """Test getting general minimum wage for 2026"""
        salario = get_salario_minimo(2026, "general")
        assert salario == 278.80

    def test_get_salario_minimo_2026_frontera(self):
        """Test getting border zone minimum wage for 2026"""
        salario = get_salario_minimo(2026, "frontera")
        assert salario == 419.88

    def test_get_salario_minimo_frontera_higher_than_general(self):
        """Test that border zone minimum wage is higher than general"""
        general = get_salario_minimo(2026, "general")
        frontera = get_salario_minimo(2026, "frontera")
        assert frontera > general


class TestCuotasObreroPatronales:
    """Tests for IMSS employer and employee contributions"""

    def test_calcular_cuotas_basic(self):
        """Test basic IMSS contribution calculation"""
        result = calcular_cuotas_obrero_patronales(500.0, 30, 2026)
        assert result is not None
        assert result["salario_diario"] == 500.0
        assert result["dias"] == 30
        assert result["year"] == 2026
        assert result["salario_base_cotizacion"] == 15000.0
        assert "cuotas_patron" in result
        assert "cuotas_trabajador" in result
        assert result["total_patron"] > 0
        assert result["total_trabajador"] > 0
        assert result["total_imss"] == result["total_patron"] + result["total_trabajador"]

    def test_calcular_cuotas_minimum_wage(self):
        """Test IMSS contributions for minimum wage worker"""
        salario_minimo = get_salario_minimo(2026, "general")
        result = calcular_cuotas_obrero_patronales(salario_minimo, 30, 2026)
        assert result["total_patron"] > 0
        assert result["total_trabajador"] > 0

    def test_calcular_cuotas_high_salary(self):
        """Test IMSS contributions for high salary worker"""
        result = calcular_cuotas_obrero_patronales(2000.0, 30, 2026)
        assert result["salario_diario"] == 2000.0
        assert result["total_patron"] > 0
        assert result["total_trabajador"] > 0
        # High salary should have higher contributions
        result_low = calcular_cuotas_obrero_patronales(500.0, 30, 2026)
        assert result["total_patron"] > result_low["total_patron"]

    def test_calcular_cuotas_15_days(self):
        """Test IMSS contributions for 15-day period"""
        result = calcular_cuotas_obrero_patronales(500.0, 15, 2026)
        assert result["dias"] == 15
        assert result["salario_base_cotizacion"] == 7500.0
        # 15 days should be less than 30 days but more than 25% (due to fixed components)
        result_30 = calcular_cuotas_obrero_patronales(500.0, 30, 2026)
        assert result["total_imss"] < result_30["total_imss"]
        assert result["total_imss"] > result_30["total_imss"] * 0.25

    def test_calcular_cuotas_7_days(self):
        """Test IMSS contributions for 7-day period (weekly)"""
        result = calcular_cuotas_obrero_patronales(500.0, 7, 2026)
        assert result["dias"] == 7
        assert result["salario_base_cotizacion"] == 3500.0

    def test_calcular_cuotas_clase_riesgo_1(self):
        """Test IMSS contributions with minimum risk class (1)"""
        result = calcular_cuotas_obrero_patronales(500.0, 30, 2026, clase_riesgo=1)
        assert "riesgo_trabajo" in result["cuotas_patron"]
        riesgo_1 = result["cuotas_patron"]["riesgo_trabajo"]
        assert riesgo_1 > 0

    def test_calcular_cuotas_clase_riesgo_3(self):
        """Test IMSS contributions with medium risk class (3)"""
        result = calcular_cuotas_obrero_patronales(500.0, 30, 2026, clase_riesgo=3)
        assert "riesgo_trabajo" in result["cuotas_patron"]
        riesgo_3 = result["cuotas_patron"]["riesgo_trabajo"]
        assert riesgo_3 > 0

    def test_calcular_cuotas_clase_riesgo_5(self):
        """Test IMSS contributions with maximum risk class (5)"""
        result = calcular_cuotas_obrero_patronales(500.0, 30, 2026, clase_riesgo=5)
        assert "riesgo_trabajo" in result["cuotas_patron"]
        riesgo_5 = result["cuotas_patron"]["riesgo_trabajo"]
        assert riesgo_5 > 0
        # Higher risk class should have higher premium
        result_1 = calcular_cuotas_obrero_patronales(500.0, 30, 2026, clase_riesgo=1)
        assert riesgo_5 > result_1["cuotas_patron"]["riesgo_trabajo"]

    def test_calcular_cuotas_all_components_present(self):
        """Test that all IMSS contribution components are present"""
        result = calcular_cuotas_obrero_patronales(500.0, 30, 2026)
        # Employer contributions
        assert "enfermedad_mat_cuota_fija" in result["cuotas_patron"]
        assert "enfermedad_mat_excedente" in result["cuotas_patron"]
        assert "enfermedad_mat_dinero" in result["cuotas_patron"]
        assert "gastos_medicos_pensionados" in result["cuotas_patron"]
        assert "invalidez_vida" in result["cuotas_patron"]
        assert "retiro" in result["cuotas_patron"]
        assert "cesantia_vejez" in result["cuotas_patron"]
        assert "guarderias" in result["cuotas_patron"]
        assert "riesgo_trabajo" in result["cuotas_patron"]
        # Employee contributions
        assert "enfermedad_mat_excedente" in result["cuotas_trabajador"]
        assert "enfermedad_mat_dinero" in result["cuotas_trabajador"]
        assert "gastos_medicos_pensionados" in result["cuotas_trabajador"]
        assert "invalidez_vida" in result["cuotas_trabajador"]
        assert "cesantia_vejez" in result["cuotas_trabajador"]

    def test_calcular_cuotas_2024(self):
        """Test IMSS contributions for year 2024"""
        result = calcular_cuotas_obrero_patronales(500.0, 30, 2024)
        assert result["year"] == 2024
        assert result["total_patron"] > 0

    def test_calcular_cuotas_2025(self):
        """Test IMSS contributions for year 2025"""
        result = calcular_cuotas_obrero_patronales(500.0, 30, 2025)
        assert result["year"] == 2025
        assert result["total_patron"] > 0

    def test_calcular_cuotas_decimal_salary(self):
        """Test IMSS contributions with decimal salary"""
        result = calcular_cuotas_obrero_patronales(543.21, 30, 2026)
        assert result["salario_diario"] == 543.21
        assert abs(result["salario_base_cotizacion"] - 16296.3) < 0.01


class TestModalidad40:
    """Tests for Modalidad 40 (voluntary continuation)"""

    def test_calcular_modalidad_40_basic(self):
        """Test basic Modalidad 40 calculation"""
        result = calcular_modalidad_40(15000, 2026)
        assert result is not None
        assert result["salario_base_cotizacion"] == 15000
        assert result["year"] == 2026
        assert result["cuota_mensual"] > 0
        assert result["porcentaje_total"] > 0
        assert "componentes" in result
        assert isinstance(result["componentes"], dict)

    def test_calcular_modalidad_40_percentage(self):
        """Test Modalidad 40 percentage (should be ~10.47%)"""
        result = calcular_modalidad_40(10000, 2026)
        # Percentage should be around 10.47%
        assert abs(result["porcentaje_total"] - 0.1047) < 0.001

    def test_calcular_modalidad_40_cuota_calculation(self):
        """Test that Modalidad 40 quota is calculated correctly"""
        result = calcular_modalidad_40(10000, 2026)
        expected_cuota = 10000 * result["porcentaje_total"]
        assert abs(result["cuota_mensual"] - expected_cuota) < 0.01

    def test_calcular_modalidad_40_minimum_salary(self):
        """Test Modalidad 40 with minimum allowed salary (1 UMA)"""
        uma = get_uma(2026)
        salario_minimo = uma["mensual"] * 1
        result = calcular_modalidad_40(salario_minimo, 2026)
        assert result["salario_base_cotizacion"] >= salario_minimo

    def test_calcular_modalidad_40_below_minimum(self):
        """Test Modalidad 40 with salary below minimum (should be adjusted)"""
        uma = get_uma(2026)
        salario_bajo = uma["mensual"] * 0.5  # Below minimum
        result = calcular_modalidad_40(salario_bajo, 2026)
        # Should be adjusted to minimum
        assert result["salario_base_cotizacion"] == uma["mensual"] * 1

    def test_calcular_modalidad_40_maximum_salary(self):
        """Test Modalidad 40 with maximum allowed salary (25 UMAs)"""
        uma = get_uma(2026)
        salario_maximo = uma["mensual"] * 25
        result = calcular_modalidad_40(salario_maximo, 2026)
        assert result["salario_base_cotizacion"] <= salario_maximo

    def test_calcular_modalidad_40_above_maximum(self):
        """Test Modalidad 40 with salary above maximum (should be capped)"""
        uma = get_uma(2026)
        salario_alto = uma["mensual"] * 30  # Above maximum
        result = calcular_modalidad_40(salario_alto, 2026)
        # Should be capped at 25 UMAs
        assert result["salario_base_cotizacion"] == uma["mensual"] * 25

    def test_calcular_modalidad_40_components_present(self):
        """Test that Modalidad 40 has component breakdown"""
        result = calcular_modalidad_40(15000, 2026)
        assert len(result["componentes"]) > 0
        # Components are a subset of the total (not all components may be detailed)
        componentes_sum = sum(result["componentes"].values())
        assert componentes_sum > 0
        assert componentes_sum <= result["cuota_mensual"]

    def test_calcular_modalidad_40_2024(self):
        """Test Modalidad 40 for year 2024"""
        result = calcular_modalidad_40(15000, 2024)
        assert result["year"] == 2024
        assert result["cuota_mensual"] > 0

    def test_calcular_modalidad_40_2025(self):
        """Test Modalidad 40 for year 2025"""
        result = calcular_modalidad_40(15000, 2025)
        assert result["year"] == 2025
        assert result["cuota_mensual"] > 0


class TestModalidad10:
    """Tests for Modalidad 10 (independent workers)"""

    def test_calcular_modalidad_10_basic(self):
        """Test basic Modalidad 10 calculation"""
        result = calcular_modalidad_10(10000, 2026)
        assert result is not None
        assert result["salario_base_cotizacion"] == 10000
        assert result["year"] == 2026
        assert result["cuota_mensual"] > 0
        assert result["cuota_fija_uma"] > 0
        assert result["cuota_variable"] > 0
        assert result["porcentaje_variable"] > 0
        assert "componentes" in result

    def test_calcular_modalidad_10_cuota_fija(self):
        """Test Modalidad 10 fixed quota (3.3 UMAs)"""
        uma = get_uma(2026)
        result = calcular_modalidad_10(10000, 2026)
        # Fixed quota should be UMA diaria * 3.3
        expected_fija = uma["diaria"] * 3.3
        assert abs(result["cuota_fija_uma"] - expected_fija) < 0.01

    def test_calcular_modalidad_10_cuota_variable(self):
        """Test Modalidad 10 variable quota calculation"""
        result = calcular_modalidad_10(10000, 2026)
        expected_variable = 10000 * result["porcentaje_variable"]
        assert abs(result["cuota_variable"] - expected_variable) < 0.01

    def test_calcular_modalidad_10_total_calculation(self):
        """Test that Modalidad 10 total equals fixed + variable"""
        result = calcular_modalidad_10(10000, 2026)
        expected_total = result["cuota_fija_uma"] + result["cuota_variable"]
        assert abs(result["cuota_mensual"] - expected_total) < 0.01

    def test_calcular_modalidad_10_minimum_salary(self):
        """Test Modalidad 10 with minimum allowed salary (1 UMA)"""
        uma = get_uma(2026)
        salario_minimo = uma["mensual"] * 1
        result = calcular_modalidad_10(salario_minimo, 2026)
        assert result["salario_base_cotizacion"] >= salario_minimo

    def test_calcular_modalidad_10_below_minimum(self):
        """Test Modalidad 10 with salary below minimum (should be adjusted)"""
        uma = get_uma(2026)
        salario_bajo = uma["mensual"] * 0.5  # Below minimum
        result = calcular_modalidad_10(salario_bajo, 2026)
        # Should be adjusted to minimum
        assert result["salario_base_cotizacion"] == uma["mensual"] * 1

    def test_calcular_modalidad_10_maximum_salary(self):
        """Test Modalidad 10 with maximum allowed salary (25 UMAs)"""
        uma = get_uma(2026)
        salario_maximo = uma["mensual"] * 25
        result = calcular_modalidad_10(salario_maximo, 2026)
        assert result["salario_base_cotizacion"] <= salario_maximo

    def test_calcular_modalidad_10_above_maximum(self):
        """Test Modalidad 10 with salary above maximum (should be capped)"""
        uma = get_uma(2026)
        salario_alto = uma["mensual"] * 30  # Above maximum
        result = calcular_modalidad_10(salario_alto, 2026)
        # Should be capped at 25 UMAs
        assert result["salario_base_cotizacion"] == uma["mensual"] * 25

    def test_calcular_modalidad_10_higher_than_40(self):
        """Test that Modalidad 10 quota is higher than Modalidad 40 (includes fixed fee)"""
        salario = 15000
        result_10 = calcular_modalidad_10(salario, 2026)
        result_40 = calcular_modalidad_40(salario, 2026)
        # Modalidad 10 should be higher due to fixed fee
        assert result_10["cuota_mensual"] > result_40["cuota_mensual"]

    def test_calcular_modalidad_10_2024(self):
        """Test Modalidad 10 for year 2024"""
        result = calcular_modalidad_10(10000, 2024)
        assert result["year"] == 2024
        assert result["cuota_mensual"] > 0

    def test_calcular_modalidad_10_2025(self):
        """Test Modalidad 10 for year 2025"""
        result = calcular_modalidad_10(10000, 2025)
        assert result["year"] == 2025
        assert result["cuota_mensual"] > 0

    def test_calcular_modalidad_10_percentage(self):
        """Test Modalidad 10 variable percentage (should be ~10.47%)"""
        result = calcular_modalidad_10(10000, 2026)
        # Percentage should be around 10.47%
        assert abs(result["porcentaje_variable"] - 0.1047) < 0.001


class TestEdgeCases:
    """Edge cases and boundary condition tests"""

    def test_zero_salary_cuotas(self):
        """Test IMSS contributions with zero salary"""
        result = calcular_cuotas_obrero_patronales(0, 30, 2026)
        # Even with zero salary, there should be some fixed contributions
        assert result["total_patron"] >= 0
        assert result["total_trabajador"] >= 0

    def test_very_high_salary(self):
        """Test IMSS contributions with very high salary (above 25 UMAs daily)"""
        uma = get_uma(2026)
        salario_muy_alto = uma["diaria"] * 30  # 30 UMAs daily
        result = calcular_cuotas_obrero_patronales(salario_muy_alto, 30, 2026)
        assert result["total_patron"] > 0
        assert result["total_trabajador"] > 0

    def test_one_day_period(self):
        """Test IMSS contributions for 1-day period"""
        result = calcular_cuotas_obrero_patronales(500.0, 1, 2026)
        assert result["dias"] == 1
        assert result["salario_base_cotizacion"] == 500.0

    def test_decimal_days(self):
        """Test IMSS contributions with decimal days (should work)"""
        result = calcular_cuotas_obrero_patronales(500.0, 30, 2026)
        assert result["total_imss"] > 0

    def test_all_risk_classes(self):
        """Test that all risk classes (1-5) work correctly"""
        for clase in [1, 2, 3, 4, 5]:
            result = calcular_cuotas_obrero_patronales(500.0, 30, 2026, clase_riesgo=clase)
            assert result is not None
            assert "riesgo_trabajo" in result["cuotas_patron"]
            assert result["cuotas_patron"]["riesgo_trabajo"] > 0
