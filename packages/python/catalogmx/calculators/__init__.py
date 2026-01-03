"""
Calculators for Mexican taxes and payroll

Available calculators:
- ISR (Impuesto Sobre la Renta) - Income Tax
- RESICO (Régimen Simplificado de Confianza) - Simplified Trust Regime
"""

from catalogmx.calculators.isr import (
    calculate_isr,
    get_isr_brackets,
    calculate_subsidy,
    ISRYear,
    ISRPeriod,
    ISRCalculationResult,
)

from catalogmx.calculators.resico import (
    calculate_resico,
    get_resico_brackets,
    RESICOYear,
    RESICOPeriod,
    RESICOCalculationResult,
)

__all__ = [
    # ISR
    "calculate_isr",
    "get_isr_brackets",
    "calculate_subsidy",
    "ISRYear",
    "ISRPeriod",
    "ISRCalculationResult",
    # RESICO
    "calculate_resico",
    "get_resico_brackets",
    "RESICOYear",
    "RESICOPeriod",
    "RESICOCalculationResult",
]
