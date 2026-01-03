"""
Calculators for Mexican taxes and payroll

Available calculators:
- ISR (Impuesto Sobre la Renta) - Income Tax
"""

from catalogmx.calculators.isr import (
    calculate_isr,
    get_isr_brackets,
    calculate_subsidy,
    ISRYear,
    ISRPeriod,
    ISRCalculationResult,
)

__all__ = [
    "calculate_isr",
    "get_isr_brackets",
    "calculate_subsidy",
    "ISRYear",
    "ISRPeriod",
    "ISRCalculationResult",
]
