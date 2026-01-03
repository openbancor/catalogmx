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

    # Low income should get subsidy
    subsidy = calculate_subsidy(5000, year=2026)
    assert subsidy >= 0

    # High income should get no subsidy
    subsidy = calculate_subsidy(50000, year=2026)
    assert subsidy == 0
