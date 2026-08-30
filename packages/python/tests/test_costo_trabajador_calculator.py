"""
Comprehensive tests for Worker Cost Calculator
Tests total employer cost calculations including all contributions and reserves
"""

import pytest

from catalogmx.calculators.costo_trabajador import (
    DIAS_VACACIONES_POR_ANTIGUEDAD,
    calcular_costo_total,
    obtener_dias_vacaciones,
)


class TestObtenerDiasVacaciones:
    """Tests for vacation days calculation based on seniority"""

    def test_primer_ano(self):
        """Test vacation days for first year of seniority"""
        dias = obtener_dias_vacaciones(1)
        assert dias == 12

    def test_segundo_ano(self):
        """Test vacation days for second year of seniority"""
        dias = obtener_dias_vacaciones(2)
        assert dias == 14

    def test_tercer_ano(self):
        """Test vacation days for third year of seniority"""
        dias = obtener_dias_vacaciones(3)
        assert dias == 16

    def test_cuarto_ano(self):
        """Test vacation days for fourth year of seniority"""
        dias = obtener_dias_vacaciones(4)
        assert dias == 18

    def test_quinto_ano(self):
        """Test vacation days for fifth year of seniority"""
        dias = obtener_dias_vacaciones(5)
        assert dias == 20

    def test_decimo_ano(self):
        """Test vacation days for tenth year of seniority"""
        dias = obtener_dias_vacaciones(10)
        assert dias == 22

    def test_onceavo_ano(self):
        """Test vacation days for eleventh year (increase to 24)"""
        dias = obtener_dias_vacaciones(11)
        assert dias == 24

    def test_quinceavo_ano(self):
        """Test vacation days for fifteenth year"""
        dias = obtener_dias_vacaciones(15)
        assert dias == 24

    def test_dieciseisavo_ano(self):
        """Test vacation days for sixteenth year (increase to 26)"""
        dias = obtener_dias_vacaciones(16)
        assert dias == 26

    def test_veinteavo_ano(self):
        """Test vacation days for twentieth year"""
        dias = obtener_dias_vacaciones(20)
        assert dias == 26

    def test_veintiunavo_ano(self):
        """Test vacation days for twenty-first year (increase to 28)"""
        dias = obtener_dias_vacaciones(21)
        assert dias == 28

    def test_veinticincoavo_ano(self):
        """Test vacation days for twenty-fifth year"""
        dias = obtener_dias_vacaciones(25)
        assert dias == 28

    def test_veintiseisavo_ano(self):
        """Test vacation days for twenty-sixth year (increase to 30)"""
        dias = obtener_dias_vacaciones(26)
        assert dias == 30

    def test_treintaavo_ano(self):
        """Test vacation days for thirtieth year"""
        dias = obtener_dias_vacaciones(30)
        assert dias == 30

    def test_treintayunavo_ano(self):
        """Test vacation days for thirty-first year (increase to 32)"""
        dias = obtener_dias_vacaciones(31)
        assert dias == 32

    def test_treintaycincoavo_ano(self):
        """Test vacation days for thirty-fifth year"""
        dias = obtener_dias_vacaciones(35)
        assert dias == 32

    def test_cuarentaavo_ano(self):
        """Test vacation days for fortieth year (max is 32)"""
        dias = obtener_dias_vacaciones(40)
        assert dias == 32

    def test_cincuentaavo_ano(self):
        """Test vacation days for fiftieth year (max is 32)"""
        dias = obtener_dias_vacaciones(50)
        assert dias == 32

    def test_cien_anos(self):
        """Test vacation days for 100 years (max is 32)"""
        dias = obtener_dias_vacaciones(100)
        assert dias == 32

    def test_cero_anos(self):
        """Test vacation days for zero years (should return minimum 12)"""
        dias = obtener_dias_vacaciones(0)
        assert dias == 12

    def test_antiguedad_negativa(self):
        """Test vacation days for negative seniority (should return minimum 12)"""
        dias = obtener_dias_vacaciones(-5)
        assert dias == 12

    def test_progresion_incrementa(self):
        """Test that vacation days never decrease with seniority"""
        dias_anterior = obtener_dias_vacaciones(1)
        for ano in range(2, 41):
            dias_actual = obtener_dias_vacaciones(ano)
            assert dias_actual >= dias_anterior
            dias_anterior = dias_actual

    def test_tabla_completa(self):
        """Test that all years in the table match expected values"""
        for ano, dias_esperados in DIAS_VACACIONES_POR_ANTIGUEDAD.items():
            dias = obtener_dias_vacaciones(ano)
            assert dias == dias_esperados


class TestCalcularCostoTotal:
    """Tests for total worker cost calculation"""

    def test_calcular_costo_basico(self):
        """Test basic worker cost calculation"""
        result = calcular_costo_total(15000)
        assert result is not None
        assert result["salario_bruto_mensual"] == 15000
        assert result["cuotas_imss_patronales"] > 0
        assert result["infonavit"] > 0
        assert result["impuesto_nomina"] > 0
        assert result["reserva_aguinaldo"] > 0
        assert result["reserva_prima_vacacional"] > 0
        assert result["reserva_vacaciones"] > 0
        assert result["ptu_estimado"] == 0  # Default is False
        assert result["costo_total_mensual"] > 15000
        assert result["costo_total_anual"] == result["costo_total_mensual"] * 12
        assert result["factor_costo"] > 1.0

    def test_calcular_costo_con_ptu(self):
        """Test worker cost calculation with PTU included"""
        result = calcular_costo_total(15000, incluir_ptu=True)
        assert result["ptu_estimado"] > 0
        # PTU should be approximately 10% of annual salary / 12
        expected_ptu = (15000 * 12 * 0.10) / 12
        assert abs(result["ptu_estimado"] - expected_ptu) < 0.01

    def test_calcular_costo_sin_ptu(self):
        """Test worker cost calculation without PTU"""
        result = calcular_costo_total(15000, incluir_ptu=False)
        assert result["ptu_estimado"] == 0

    def test_calcular_costo_ptu_custom_percentage(self):
        """Test worker cost calculation with custom PTU percentage"""
        result = calcular_costo_total(15000, incluir_ptu=True, porcentaje_ptu=15.0)
        # PTU should be 15% of annual salary / 12
        expected_ptu = (15000 * 12 * 0.15) / 12
        assert abs(result["ptu_estimado"] - expected_ptu) < 0.01

    def test_calcular_costo_diferentes_estados(self):
        """Test worker cost calculation in different states (different payroll tax)"""
        # CDMX has 3% payroll tax
        result_cdmx = calcular_costo_total(15000, cve_estado="09")
        expected_nomina_cdmx = 15000 * 0.03
        assert abs(result_cdmx["impuesto_nomina"] - expected_nomina_cdmx) < 0.01

        # Jalisco (14) should have different rate
        result_jalisco = calcular_costo_total(15000, cve_estado="14")
        # Rates will differ
        assert result_jalisco["impuesto_nomina"] != result_cdmx["impuesto_nomina"]

    def test_calcular_costo_primer_ano(self):
        """Test worker cost calculation for first year employee (12 vacation days)"""
        result = calcular_costo_total(15000, antiguedad_anos=1)
        salario_diario = 15000 / 30.0
        dias_vacaciones = 12
        expected_vacaciones = (salario_diario * dias_vacaciones) / 12.0
        assert abs(result["reserva_vacaciones"] - expected_vacaciones) < 0.01

    def test_calcular_costo_quinto_ano(self):
        """Test worker cost calculation for fifth year employee (20 vacation days)"""
        result = calcular_costo_total(15000, antiguedad_anos=5)
        salario_diario = 15000 / 30.0
        dias_vacaciones = 20
        expected_vacaciones = (salario_diario * dias_vacaciones) / 12.0
        assert abs(result["reserva_vacaciones"] - expected_vacaciones) < 0.01

    def test_calcular_costo_decimo_ano(self):
        """Test worker cost calculation for tenth year employee (22 vacation days)"""
        result = calcular_costo_total(15000, antiguedad_anos=10)
        salario_diario = 15000 / 30.0
        dias_vacaciones = 22
        expected_vacaciones = (salario_diario * dias_vacaciones) / 12.0
        assert abs(result["reserva_vacaciones"] - expected_vacaciones) < 0.01

    def test_calcular_costo_aguinaldo_minimo(self):
        """Test worker cost calculation with minimum aguinaldo (15 days)"""
        result = calcular_costo_total(15000, dias_aguinaldo=15)
        salario_diario = 15000 / 30.0
        expected_aguinaldo = (salario_diario * 15) / 12.0
        assert abs(result["reserva_aguinaldo"] - expected_aguinaldo) < 0.01

    def test_calcular_costo_aguinaldo_generoso(self):
        """Test worker cost calculation with generous aguinaldo (30 days)"""
        result = calcular_costo_total(15000, dias_aguinaldo=30)
        salario_diario = 15000 / 30.0
        expected_aguinaldo = (salario_diario * 30) / 12.0
        assert abs(result["reserva_aguinaldo"] - expected_aguinaldo) < 0.01
        # 30 days should be double of 15 days
        result_15 = calcular_costo_total(15000, dias_aguinaldo=15)
        assert abs(result["reserva_aguinaldo"] - result_15["reserva_aguinaldo"] * 2) < 0.01

    def test_calcular_costo_prima_vacacional(self):
        """Test that vacation bonus is 25% of vacation reserve"""
        result = calcular_costo_total(15000, antiguedad_anos=1)
        expected_prima = result["reserva_vacaciones"] * 0.25
        assert abs(result["reserva_prima_vacacional"] - expected_prima) < 0.01

    def test_calcular_costo_infonavit(self):
        """Test that Infonavit is 5% of SBC"""
        result = calcular_costo_total(15000)
        salario_diario = 15000 / 30.0
        salario_base_cotizacion = salario_diario * 30
        expected_infonavit = salario_base_cotizacion * 0.05
        assert abs(result["infonavit"] - expected_infonavit) < 0.01

    def test_calcular_costo_year_2024(self):
        """Test worker cost calculation for year 2024"""
        result = calcular_costo_total(15000, year=2024)
        assert result["costo_total_mensual"] > 15000

    def test_calcular_costo_year_2025(self):
        """Test worker cost calculation for year 2025"""
        result = calcular_costo_total(15000, year=2025)
        assert result["costo_total_mensual"] > 15000

    def test_calcular_costo_year_2026(self):
        """Test worker cost calculation for year 2026"""
        result = calcular_costo_total(15000, year=2026)
        assert result["costo_total_mensual"] > 15000

    def test_calcular_costo_salario_minimo(self):
        """Test worker cost calculation for minimum wage worker"""
        from catalogmx.calculators.imss import get_salario_minimo

        salario_minimo = get_salario_minimo(2026, "general")
        salario_mensual = salario_minimo * 30
        result = calcular_costo_total(salario_mensual)
        assert result["costo_total_mensual"] > salario_mensual
        assert result["factor_costo"] > 1.0

    def test_calcular_costo_salario_alto(self):
        """Test worker cost calculation for high salary worker"""
        result = calcular_costo_total(50000)
        assert result["salario_bruto_mensual"] == 50000
        assert result["costo_total_mensual"] > 50000
        assert result["factor_costo"] > 1.0

    def test_calcular_costo_salario_muy_alto(self):
        """Test worker cost calculation for very high salary worker"""
        result = calcular_costo_total(100000)
        assert result["salario_bruto_mensual"] == 100000
        assert result["costo_total_mensual"] > 100000

    def test_calcular_costo_factor_incrementa_con_ptu(self):
        """Test that cost factor increases when PTU is included"""
        result_sin_ptu = calcular_costo_total(15000, incluir_ptu=False)
        result_con_ptu = calcular_costo_total(15000, incluir_ptu=True)
        assert result_con_ptu["factor_costo"] > result_sin_ptu["factor_costo"]
        assert result_con_ptu["costo_total_mensual"] > result_sin_ptu["costo_total_mensual"]

    def test_calcular_costo_anual_coherente(self):
        """Test that annual cost equals monthly cost * 12"""
        result = calcular_costo_total(15000)
        expected_anual = result["costo_total_mensual"] * 12
        assert abs(result["costo_total_anual"] - expected_anual) < 0.01

    def test_calcular_costo_componentes_suman_total(self):
        """Test that all cost components sum to total monthly cost"""
        result = calcular_costo_total(15000, incluir_ptu=True)
        suma_componentes = (
            result["salario_bruto_mensual"]
            + result["cuotas_imss_patronales"]
            + result["infonavit"]
            + result["impuesto_nomina"]
            + result["reserva_aguinaldo"]
            + result["reserva_prima_vacacional"]
            + result["reserva_vacaciones"]
            + result["ptu_estimado"]
        )
        assert abs(suma_componentes - result["costo_total_mensual"]) < 0.01

    def test_calcular_costo_decimal_salary(self):
        """Test worker cost calculation with decimal salary"""
        result = calcular_costo_total(15432.50)
        assert result["salario_bruto_mensual"] == 15432.50
        assert result["costo_total_mensual"] > 15432.50


class TestEdgeCases:
    """Edge cases and boundary condition tests"""

    def test_rejects_invalid_monthly_gross_salary(self):
        """Reject an unsafe monthly salary at the public calculator boundary."""
        from catalogmx.calculators.imss import get_salario_minimo

        minimum_monthly_salary = get_salario_minimo(2026, "general") * 30
        invalid_salaries = [
            float("nan"),
            float("inf"),
            float("-inf"),
            None,
            "9451.20",
            True,
            0.0,
            -1.0,
            minimum_monthly_salary - 0.01,
            10**1000,
        ]

        for salario_mensual_bruto in invalid_salaries:
            with pytest.raises(
                ValueError,
                match="El salario mensual bruto debe ser un número finito mayor o igual al salario mínimo mensual aplicable.",
            ):
                calcular_costo_total(salario_mensual_bruto)

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("antiguedad_anos", -1),
            ("antiguedad_anos", 1.5),
            ("antiguedad_anos", True),
            ("dias_aguinaldo", 14),
            ("dias_aguinaldo", 15.5),
            ("dias_aguinaldo", True),
            ("porcentaje_ptu", float("nan")),
            ("porcentaje_ptu", -1),
            ("porcentaje_ptu", 101),
            ("incluir_ptu", 1),
        ],
    )
    def test_rejects_invalid_fiscal_inputs(self, field, value):
        with pytest.raises(ValueError, match=field):
            calcular_costo_total(15000, **{field: value})

    def test_zero_antiguedad(self):
        """Test worker cost calculation with zero seniority"""
        result = calcular_costo_total(15000, antiguedad_anos=0)
        # Should use minimum vacation days (12)
        salario_diario = 15000 / 30.0
        expected_vacaciones = (salario_diario * 12) / 12.0
        assert abs(result["reserva_vacaciones"] - expected_vacaciones) < 0.01

    def test_very_high_antiguedad(self):
        """Test worker cost calculation with very high seniority (100 years)"""
        result = calcular_costo_total(15000, antiguedad_anos=100)
        # Should use maximum vacation days (32)
        salario_diario = 15000 / 30.0
        expected_vacaciones = (salario_diario * 32) / 12.0
        assert abs(result["reserva_vacaciones"] - expected_vacaciones) < 0.01

    def test_zero_dias_aguinaldo(self):
        """Reject an aguinaldo below the statutory 15-day minimum."""
        with pytest.raises(ValueError, match="dias_aguinaldo"):
            calcular_costo_total(15000, dias_aguinaldo=0)

    def test_cien_dias_aguinaldo(self):
        """Test worker cost calculation with 100 aguinaldo days (very generous)"""
        result = calcular_costo_total(15000, dias_aguinaldo=100)
        salario_diario = 15000 / 30.0
        expected_aguinaldo = (salario_diario * 100) / 12.0
        assert abs(result["reserva_aguinaldo"] - expected_aguinaldo) < 0.01

    def test_zero_porcentaje_ptu(self):
        """Test worker cost calculation with zero PTU percentage"""
        result = calcular_costo_total(15000, incluir_ptu=True, porcentaje_ptu=0.0)
        assert result["ptu_estimado"] == 0

    def test_high_porcentaje_ptu(self):
        """Test worker cost calculation with high PTU percentage (50%)"""
        result = calcular_costo_total(15000, incluir_ptu=True, porcentaje_ptu=50.0)
        expected_ptu = (15000 * 12 * 0.50) / 12
        assert abs(result["ptu_estimado"] - expected_ptu) < 0.01

    def test_diferentes_combinaciones_parametros(self):
        """Test worker cost calculation with various parameter combinations"""
        # High salary, high seniority, with PTU
        result1 = calcular_costo_total(50000, "09", 20, 30, True, 15.0, 2026)
        assert result1["costo_total_mensual"] > 50000
        assert result1["factor_costo"] > 1.0

        # Low salary, low seniority, no PTU
        result2 = calcular_costo_total(8000, "14", 1, 15, False, 0, 2024)
        assert result2["costo_total_mensual"] > 8000
        assert result2["factor_costo"] > 1.0

        # Medium salary, medium seniority, with PTU
        result3 = calcular_costo_total(25000, "23", 10, 20, True, 10.0, 2025)
        assert result3["costo_total_mensual"] > 25000
        assert result3["factor_costo"] > 1.0


class TestRealisticScenarios:
    """Realistic workplace scenarios"""

    def test_empleado_nuevo_salario_minimo(self):
        """Test cost for new employee at minimum wage"""
        from catalogmx.calculators.imss import get_salario_minimo

        salario_minimo_diario = get_salario_minimo(2026, "general")
        salario_mensual = salario_minimo_diario * 30
        result = calcular_costo_total(
            salario_mensual,
            cve_estado="09",
            antiguedad_anos=1,
            dias_aguinaldo=15,
            incluir_ptu=False,
        )
        # Factor should be between 1.20 and 1.60 for minimum wage (higher due to fixed costs)
        assert 1.20 < result["factor_costo"] < 1.60

    def test_empleado_senior_salario_competitivo(self):
        """Test cost for senior employee with competitive salary"""
        result = calcular_costo_total(
            35000,
            cve_estado="09",
            antiguedad_anos=8,
            dias_aguinaldo=20,
            incluir_ptu=True,
            porcentaje_ptu=10.0,
        )
        # Factor should be between 1.25 and 1.45
        assert 1.20 < result["factor_costo"] < 1.50
        assert result["ptu_estimado"] > 0

    def test_ejecutivo_alto_nivel(self):
        """Test cost for high-level executive"""
        result = calcular_costo_total(
            80000,
            cve_estado="09",
            antiguedad_anos=15,
            dias_aguinaldo=30,
            incluir_ptu=True,
            porcentaje_ptu=15.0,
        )
        assert result["costo_total_mensual"] > 80000
        assert result["factor_costo"] > 1.0
        # High salaries typically have lower factor due to IMSS caps
        assert result["factor_costo"] < 1.60

    def test_trabajador_experiencia_media(self):
        """Test cost for worker with medium experience"""
        result = calcular_costo_total(
            18000,
            cve_estado="14",
            antiguedad_anos=5,
            dias_aguinaldo=15,
            incluir_ptu=False,
            year=2026,
        )
        assert 1.20 < result["factor_costo"] < 1.45
        assert result["reserva_vacaciones"] > 0
        assert result["reserva_aguinaldo"] > 0

    def test_comparacion_con_sin_ptu(self):
        """Test comparison of cost with and without PTU"""
        base_params = {
            "salario_mensual_bruto": 20000,
            "cve_estado": "09",
            "antiguedad_anos": 5,
            "dias_aguinaldo": 15,
            "year": 2026,
        }

        result_sin_ptu = calcular_costo_total(**base_params, incluir_ptu=False)
        result_con_ptu = calcular_costo_total(**base_params, incluir_ptu=True, porcentaje_ptu=10.0)

        # PTU should add approximately 10% to annual salary / 12 = 0.833% monthly
        diferencia = result_con_ptu["costo_total_mensual"] - result_sin_ptu["costo_total_mensual"]
        expected_diferencia = (20000 * 12 * 0.10) / 12
        assert abs(diferencia - expected_diferencia) < 0.01
