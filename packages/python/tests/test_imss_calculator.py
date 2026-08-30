"""Tests for the audited IMSS calculator surfaces."""

import pytest

from catalogmx.calculators.imss import (
    calcular_cuotas_obrero_patronales,
    calcular_modalidad_10,
    calcular_modalidad_40,
    get_ceav_patron_rate,
    get_salario_minimo,
    get_uma,
)


class TestUMAFunctions:
    def test_get_uma_history(self) -> None:
        assert get_uma(2024) == {
            "diaria": 108.57,
            "mensual": 3300.53,
            "anual": 39606.36,
        }
        assert get_uma(2025) == {
            "diaria": 113.14,
            "mensual": 3439.46,
            "anual": 41273.52,
        }
        assert get_uma(2026) == {
            "diaria": 117.31,
            "mensual": 3566.22,
            "anual": 42794.64,
        }

    def test_uma_progression(self) -> None:
        assert get_uma(2024)["diaria"] < get_uma(2025)["diaria"] < get_uma(2026)["diaria"]

    def test_minimum_wages_2026(self) -> None:
        assert get_salario_minimo(2026, "general") == 315.04
        assert get_salario_minimo(2026, "frontera") == 440.87
        assert get_salario_minimo(2026, "frontera") > get_salario_minimo(2026, "general")


class TestCuotasObreroPatronales:
    def test_basic_contribution_breakdown(self) -> None:
        result = calcular_cuotas_obrero_patronales(500.0, 30, 2026)
        assert result["salario_diario"] == 500.0
        assert result["dias"] == 30
        assert result["year"] == 2026
        assert result["salario_base_cotizacion"] == 15000.0
        assert result["uma_diaria"] == 117.31
        assert result["total_patron"] > 0
        assert result["total_trabajador"] > 0
        assert result["total_imss"] == pytest.approx(
            result["total_patron"] + result["total_trabajador"]
        )

    def test_fixed_sickness_maternity_quota_uses_one_uma(self) -> None:
        result = calcular_cuotas_obrero_patronales(500.0, 30, 2026, clase_riesgo=2)
        assert result["cuotas_patron"]["enfermedad_mat_cuota_fija"] == pytest.approx(717.9372)

    def test_ceav_uses_special_minimum_wage_row(self) -> None:
        salario_minimo = get_salario_minimo(2026, "general")
        result = calcular_cuotas_obrero_patronales(salario_minimo, 30, 2026)
        assert result["ceav_patron_rate"] == 0.0315

    @pytest.mark.parametrize(
        ("salario_diario", "zona"),
        [
            (float("nan"), "general"),
            (float("inf"), "general"),
            (0.0, "general"),
            (-1.0, "general"),
            (315.03, "general"),
            (440.86, "frontera"),
        ],
    )
    def test_ceav_selector_rejects_invalid_daily_sbc(
        self, salario_diario: float, zona: str
    ) -> None:
        with pytest.raises(ValueError):
            get_ceav_patron_rate(salario_diario, 2026, zona=zona)  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        ("salario_diario", "zona", "expected_rate"),
        [(315.04, "general", 0.0315), (440.87, "frontera", 0.0315)],
    )
    def test_ceav_selector_preserves_each_zone_minimum_wage_row(
        self, salario_diario: float, zona: str, expected_rate: float
    ) -> None:
        assert get_ceav_patron_rate(salario_diario, 2026, zona=zona) == expected_rate  # type: ignore[arg-type]

    def test_ceav_selector_rejects_invalid_wage_zone_at_runtime(self) -> None:
        with pytest.raises(ValueError):
            get_ceav_patron_rate(315.04, 2026, zona="otra")  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        ("salario_diario", "zona"),
        [
            (float("nan"), "general"),
            (float("inf"), "general"),
            (0.0, "general"),
            (-1.0, "general"),
            (315.03, "general"),
            (440.86, "frontera"),
        ],
    )
    def test_ordinary_contributions_reject_invalid_daily_sbc(
        self, salario_diario: float, zona: str
    ) -> None:
        with pytest.raises(ValueError):
            calcular_cuotas_obrero_patronales(salario_diario, 30, 2026, zona=zona)  # type: ignore[arg-type]

    @pytest.mark.parametrize("salario_diario", [None, "315.04", True])
    def test_ordinary_contributions_reject_nonnumeric_or_boolean_daily_sbc(
        self, salario_diario: object
    ) -> None:
        with pytest.raises(ValueError):
            calcular_cuotas_obrero_patronales(salario_diario, 30, 2026)  # type: ignore[arg-type]

    @pytest.mark.parametrize("dias", [float("nan"), float("inf"), 0.0, -1.0])
    def test_ordinary_contributions_reject_invalid_days(self, dias: float) -> None:
        with pytest.raises(ValueError):
            calcular_cuotas_obrero_patronales(315.04, dias, 2026)  # type: ignore[arg-type]

    @pytest.mark.parametrize("dias", [None, "30", True])
    def test_ordinary_contributions_reject_nonnumeric_or_boolean_days(self, dias: object) -> None:
        with pytest.raises(ValueError):
            calcular_cuotas_obrero_patronales(315.04, dias, 2026)  # type: ignore[arg-type]

    @pytest.mark.parametrize("clase_riesgo", [0, 6, 1.5])
    def test_ordinary_contributions_reject_invalid_risk_class(self, clase_riesgo: float) -> None:
        with pytest.raises(ValueError):
            calcular_cuotas_obrero_patronales(315.04, 30, 2026, clase_riesgo=clase_riesgo)  # type: ignore[arg-type]

    def test_ordinary_contributions_reject_invalid_wage_zone_at_runtime(self) -> None:
        with pytest.raises(ValueError):
            calcular_cuotas_obrero_patronales(315.04, 30, 2026, zona="otra")  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        ("year", "expected_rate"),
        [(2024, 0.05331), (2025, 0.06422), (2026, 0.07513)],
    )
    def test_ceav_top_band_history(self, year: int, expected_rate: float) -> None:
        result = calcular_cuotas_obrero_patronales(500.0, 30, year)  # type: ignore[arg-type]
        assert result["ceav_patron_rate"] == expected_rate

    def test_excess_quota_is_zero_below_threshold(self) -> None:
        result = calcular_cuotas_obrero_patronales(get_salario_minimo(2026), 30, 2026)
        assert result["cuotas_patron"]["enfermedad_mat_excedente"] == 0.0
        assert result["cuotas_trabajador"]["enfermedad_mat_excedente"] == 0.0

    def test_period_days_scale_salary_base(self) -> None:
        result = calcular_cuotas_obrero_patronales(500.0, 15, 2026)
        assert result["salario_base_cotizacion"] == 7500.0
        assert result["dias"] == 15

    def test_risk_class_changes_employer_contribution(self) -> None:
        low = calcular_cuotas_obrero_patronales(500.0, 30, 2026, clase_riesgo=1)
        high = calcular_cuotas_obrero_patronales(500.0, 30, 2026, clase_riesgo=5)
        assert high["cuotas_patron"]["riesgo_trabajo"] > low["cuotas_patron"]["riesgo_trabajo"]
        assert high["total_patron"] > low["total_patron"]

    def test_all_expected_components_are_present(self) -> None:
        result = calcular_cuotas_obrero_patronales(500.0, 30, 2026)
        assert {
            "enfermedad_mat_cuota_fija",
            "enfermedad_mat_excedente",
            "enfermedad_mat_dinero",
            "gastos_medicos_pensionados",
            "invalidez_vida",
            "retiro",
            "cesantia_vejez",
            "guarderias",
            "riesgo_trabajo",
        } <= result["cuotas_patron"].keys()
        assert {
            "enfermedad_mat_excedente",
            "enfermedad_mat_dinero",
            "gastos_medicos_pensionados",
            "invalidez_vida",
            "cesantia_vejez",
        } <= result["cuotas_trabajador"].keys()


class TestModalidad40:
    def test_historical_rates(self) -> None:
        assert calcular_modalidad_40(10000, 8000, 2024)["porcentaje_total"] == 0.11681
        assert calcular_modalidad_40(12000, 10000, 2025)["porcentaje_total"] == 0.12484
        assert calcular_modalidad_40(15000, 12000, 2026)["porcentaje_total"] == 0.14438

    def test_requires_candidate_not_below_last_registered_sbc(self) -> None:
        with pytest.raises(ValueError, match="no puede ser menor al último SBC"):
            calcular_modalidad_40(10000, 12000, 2026)

    def test_rejects_invalid_last_sbc(self) -> None:
        with pytest.raises(ValueError, match="debe ser mayor que cero"):
            calcular_modalidad_40(15000, 0, 2026)

    def test_caps_candidate_at_25_uma(self) -> None:
        uma = get_uma(2026)
        result = calcular_modalidad_40(uma["mensual"] * 30, 12000, 2026)
        assert result["salario_base_cotizacion"] == pytest.approx(uma["mensual"] * 25)

    def test_rejects_last_sbc_above_25_uma(self) -> None:
        uma = get_uma(2026)
        with pytest.raises(ValueError, match="excede el tope de 25 UMA"):
            calcular_modalidad_40(uma["mensual"] * 30, uma["mensual"] * 26, 2026)

    def test_preserves_special_one_minimum_wage_ceav_band(self) -> None:
        uma = get_uma(2026)
        monthly_minimum = get_salario_minimo(2026, "general") * (uma["mensual"] / uma["diaria"])
        result = calcular_modalidad_40(monthly_minimum, monthly_minimum, 2026)
        assert result["porcentaje_total"] == pytest.approx(0.10075)

    def test_result_exposes_monthly_units_and_components(self) -> None:
        result = calcular_modalidad_40(15000, 12000, 2026)
        assert result["salario_base_cotizacion"] == 15000
        assert result["ultimo_sbc_mensual"] == 12000
        assert result["uma_mensual"] == 3566.22
        assert result["cuota_mensual"] == pytest.approx(
            result["salario_base_cotizacion"] * result["porcentaje_total"]
        )
        assert result["componentes"]["cesantia_vejez_patron"] > 0


class TestModalidad10Legacy:
    def test_legacy_model_remains_available_pending_audit(self) -> None:
        result = calcular_modalidad_10(10000, 2026)
        assert result["salario_base_cotizacion"] == 10000
        assert result["cuota_fija_uma"] == pytest.approx(387.123)
        assert result["porcentaje_variable"] == 0.1047
        assert result["cuota_mensual"] == pytest.approx(1434.123)

    def test_legacy_bounds_are_preserved_until_follow_up_audit(self) -> None:
        uma = get_uma(2026)
        low = calcular_modalidad_10(100.0, 2026)
        high = calcular_modalidad_10(uma["mensual"] * 30, 2026)
        assert low["salario_base_cotizacion"] == uma["mensual"]
        assert high["salario_base_cotizacion"] == uma["mensual"] * 25
