"""
Calculators for Mexican taxes and payroll

Available calculators:
- ISR (Impuesto Sobre la Renta) - Income Tax
- RESICO (Régimen Simplificado de Confianza) - Simplified Trust Regime
"""

from catalogmx.calculators.isr import (
    ISRCalculationResult,
    ISRPeriod,
    ISRYear,
    calculate_isr,
    calculate_subsidy,
    get_isr_brackets,
)
from catalogmx.calculators.resico import (
    RESICOCalculationResult,
    RESICOPeriod,
    RESICOYear,
    calculate_resico,
    get_resico_brackets,
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
