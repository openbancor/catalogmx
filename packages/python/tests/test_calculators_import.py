"""Test calculators module imports and basic functionality"""

import pytest


def test_isr_imports():
    """Test ISR calculator imports"""
    from catalogmx.calculators.isr import (
        ISRCalculationResult,
        ISRPeriod,
        ISRYear,
        calculate_isr,
        calculate_subsidy,
        get_isr_brackets,
    )

    assert ISRYear is not None
    assert ISRPeriod is not None
    assert callable(calculate_isr)
    assert callable(get_isr_brackets)
    assert callable(calculate_subsidy)


def test_resico_imports():
    """Test RESICO calculator imports"""
    from catalogmx.calculators.resico import (
        RESICOCalculationResult,
        RESICOPeriod,
        RESICOYear,
        calculate_resico,
        get_resico_brackets,
    )

    assert RESICOYear is not None
    assert RESICOPeriod is not None
    assert callable(calculate_resico)
    assert callable(get_resico_brackets)


def test_isr_calculation_basic():
    """Test basic ISR calculation"""
    from catalogmx.calculators.isr import calculate_isr

    result = calculate_isr(10000, periodo="mensual", year=2026)
    assert result is not None
    assert "ingresoGravable" in result
    assert "isrFinal" in result
    assert result["ingresoGravable"] == 10000


def test_resico_calculation_basic():
    """Test basic RESICO calculation"""
    from catalogmx.calculators.resico import calculate_resico

    result = calculate_resico(50000, periodo="mensual", year=2026)
    assert result is not None
    assert "ingreso" in result
    assert "resicoCalculado" in result
    assert result["ingreso"] == 50000
    assert result["resicoCalculado"] == 550.0  # 50000 × 1.1%


def test_isr_brackets_2026():
    """Test ISR brackets retrieval for 2026"""
    from catalogmx.calculators.isr import get_isr_brackets

    brackets = get_isr_brackets(2026, "mensual")
    assert len(brackets) > 0
    assert all("limiteInferior" in b for b in brackets)
    assert all("tasa" in b for b in brackets)


def test_resico_brackets_2026():
    """Test RESICO brackets retrieval for 2026"""
    from catalogmx.calculators.resico import get_resico_brackets

    brackets = get_resico_brackets(2026, "mensual")
    assert len(brackets) == 5  # 5 RESICO brackets
    assert all("limiteInferior" in b for b in brackets)
    assert all("tasa" in b for b in brackets)
    # Verify RESICO has no cuota fija
    assert all("cuotaFija" not in b for b in brackets)


def test_subsidy_calculation():
    """Test subsidy calculation"""
    from catalogmx.calculators.isr import calculate_subsidy

    # Low income should get subsidy (2026 flat system)
    subsidy_2026 = calculate_subsidy(5000, year=2026)
    assert subsidy_2026 >= 0

    # High income should get no subsidy
    subsidy_high = calculate_subsidy(50000, year=2026)
    assert subsidy_high == 0

    # Test 2024 tiered system
    subsidy_2024_low = calculate_subsidy(3000, year=2024)
    assert subsidy_2024_low > 0  # Should get subsidy in 2024 tiered system

    subsidy_2024_high = calculate_subsidy(50000, year=2024)
    assert subsidy_2024_high == 0  # High income gets no subsidy

    # Test 2025 flat system
    subsidy_2025_low = calculate_subsidy(5000, year=2025)
    assert subsidy_2025_low > 0


def test_isr_calculation_2024():
    """Test ISR calculation for 2024 (tiered subsidy)"""
    from catalogmx.calculators.isr import calculate_isr

    result = calculate_isr(10000, periodo="mensual", year=2024)
    assert result["year"] == 2024
    assert result["ingresoGravable"] == 10000
    assert "isrFinal" in result
    assert "subsidio" in result


def test_isr_calculation_2025():
    """Test ISR calculation for 2025 (flat subsidy)"""
    from catalogmx.calculators.isr import calculate_isr

    result = calculate_isr(10000, periodo="mensual", year=2025)
    assert result["year"] == 2025
    assert result["ingresoGravable"] == 10000
    assert "isrFinal" in result


def test_isr_different_periods():
    """Test ISR calculation with different periods"""
    from catalogmx.calculators.isr import calculate_isr

    # Test quincenal
    result_quincenal = calculate_isr(5000, periodo="quincenal", year=2026)
    assert result_quincenal["periodo"] == "quincenal"
    assert result_quincenal["ingresoGravable"] == 5000

    # Test semanal
    result_semanal = calculate_isr(2000, periodo="semanal", year=2026)
    assert result_semanal["periodo"] == "semanal"
    assert result_semanal["ingresoGravable"] == 2000

    # Test anual
    result_anual = calculate_isr(120000, periodo="anual", year=2026)
    assert result_anual["periodo"] == "anual"
    assert result_anual["ingresoGravable"] == 120000


def test_isr_high_income_bracket():
    """Test ISR with very high income to hit last bracket"""
    from catalogmx.calculators.isr import calculate_isr

    # Very high income to ensure we hit the last bracket
    result = calculate_isr(500000, periodo="mensual", year=2026)
    assert result["ingresoGravable"] == 500000
    assert result["isrFinal"] > 0
    assert result["tasaEfectiva"] > 0


def test_resico_edge_cases():
    """Test RESICO with edge cases"""
    from catalogmx.calculators.resico import calculate_resico

    # Minimum income
    result_min = calculate_resico(0.01, periodo="mensual", year=2026)
    assert result_min["resicoCalculado"] >= 0

    # Income at bracket boundary
    result_boundary = calculate_resico(25000, periodo="mensual", year=2026)
    assert result_boundary["ingreso"] == 25000

    # Annual period
    result_annual = calculate_resico(1000000, periodo="anual", year=2026)
    assert result_annual["periodo"] == "anual"
    assert result_annual["dentroDeLimite"] is True

    # Income exceeding limit
    result_exceed = calculate_resico(400000, periodo="mensual", year=2026)
    assert result_exceed["dentroDeLimite"] is False


def test_isr_brackets_all_years():
    """Test ISR brackets for all years"""
    from catalogmx.calculators.isr import get_isr_brackets

    # Test 2024
    brackets_2024 = get_isr_brackets(2024, "mensual")
    assert len(brackets_2024) > 0

    # Test 2025
    brackets_2025 = get_isr_brackets(2025, "mensual")
    assert len(brackets_2025) > 0

    # Test 2026
    brackets_2026 = get_isr_brackets(2026, "mensual")
    assert len(brackets_2026) > 0


def test_resico_brackets_all_years():
    """Test RESICO brackets for all years"""
    from catalogmx.calculators.resico import get_resico_brackets

    # Test 2024
    brackets_2024 = get_resico_brackets(2024, "mensual")
    assert len(brackets_2024) == 5

    # Test 2025
    brackets_2025 = get_resico_brackets(2025, "mensual")
    assert len(brackets_2025) == 5

    # Test 2026
    brackets_2026 = get_resico_brackets(2026, "mensual")
    assert len(brackets_2026) == 5


def test_isr_zero_income():
    """Test ISR calculation with zero income (edge case for bracket fallback)"""
    from catalogmx.calculators.isr import calculate_isr

    # Zero income for 2026 (triggers bracket fallback at line 199-205)
    result_2026 = calculate_isr(0.0, periodo="mensual", year=2026)
    assert result_2026["ingresoGravable"] == 0.0
    assert result_2026["isrFinal"] >= 0
    assert result_2026["year"] == 2026

    # Zero income for 2024 (triggers subsidy fallback at line 152 and bracket fallback at line 250-256)
    result_2024 = calculate_isr(0.0, periodo="mensual", year=2024)
    assert result_2024["ingresoGravable"] == 0.0
    assert result_2024["isrFinal"] >= 0
    assert result_2024["subsidio"] >= 0

    # Zero income for 2025 (triggers bracket fallback in factor-based path)
    result_2025 = calculate_isr(0.0, periodo="mensual", year=2025)
    assert result_2025["ingresoGravable"] == 0.0
    assert result_2025["isrFinal"] >= 0


def test_isr_negative_income():
    """Test ISR calculation with negative income (defensive edge case)"""
    from catalogmx.calculators.isr import calculate_isr

    # Negative income should still calculate (uses last bracket fallback)
    result = calculate_isr(-1000, periodo="mensual", year=2026)
    assert result["ingresoGravable"] == -1000
    # ISR calculation should handle negative gracefully
    assert "isrFinal" in result


def test_isr_decenal_period_2024():
    """Test ISR with decenal period for 2024 (uses factor-based path lines 250-256)"""
    from catalogmx.calculators.isr import calculate_isr

    # Decenal period uses monthly brackets with factor conversion (line 241-256)
    result = calculate_isr(3000, periodo="decenal", year=2024)
    assert result["periodo"] == "decenal"
    assert result["year"] == 2024
    assert result["ingresoGravable"] == 3000
    assert result["ingresoMensualizado"] == 9000  # 3000 * 3.0
    assert "isrFinal" in result


def test_subsidy_extreme_high_income_2024():
    """Test subsidy calculation with extremely high income in 2024"""
    from catalogmx.calculators.isr import calculate_subsidy

    # Very high income (way beyond all brackets) - should get subsidy = 0
    subsidy = calculate_subsidy(1000000, year=2024)
    assert subsidy == 0.0
