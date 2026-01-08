"""
Calculators for Mexican taxes and payroll

Available calculators:
- ISR (Impuesto Sobre la Renta) - Income Tax
- RESICO (Régimen Simplificado de Confianza) - Simplified Trust Regime
- IMSS (Instituto Mexicano del Seguro Social) - Social Security Contributions
- IVA (Impuesto al Valor Agregado) - Value Added Tax
- IEPS (Impuesto Especial sobre Producción y Servicios) - Special Production and Services Tax
- Retenciones (Withholdings) - ISR and IVA withholdings
- Impuestos Locales (Local Taxes) - State and municipal taxes
- Costo Trabajador (Worker Cost) - Total cost of employing a worker
"""

from catalogmx.calculators.costo_trabajador import (
    CostoTotalResult,
    calcular_costo_total,
    obtener_dias_vacaciones,
)
from catalogmx.calculators.impuestos import (
    IEPSCalculationResult,
    IEPSCalculator,
    IEPSCategoria,
    IEPSTasa,
    ImpuestoEstatal,
    ImpuestosLocalesCalculator,
    IVACalculationResult,
    IVACalculator,
    IVATasa,
    RetencionCalculationResult,
    RetencionCalculator,
    RetencionISR,
    RetencionIVA,
)
from catalogmx.calculators.imss import (
    ClaseRiesgo,
    CuotasIMSSResult,
    IMSSYear,
    Modalidad10Result,
    Modalidad40Result,
    UMAInfo,
    ZonaSalario,
    calcular_cuotas_obrero_patronales,
    calcular_modalidad_10,
    calcular_modalidad_40,
    get_salario_minimo,
    get_uma,
)
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
    # IMSS
    "calcular_cuotas_obrero_patronales",
    "calcular_modalidad_40",
    "calcular_modalidad_10",
    "get_uma",
    "get_salario_minimo",
    "IMSSYear",
    "ZonaSalario",
    "ClaseRiesgo",
    "CuotasIMSSResult",
    "Modalidad40Result",
    "Modalidad10Result",
    "UMAInfo",
    # IVA
    "IVACalculator",
    "IVACalculationResult",
    "IVATasa",
    # IEPS
    "IEPSCalculator",
    "IEPSCalculationResult",
    "IEPSCategoria",
    "IEPSTasa",
    # Retenciones
    "RetencionCalculator",
    "RetencionCalculationResult",
    "RetencionISR",
    "RetencionIVA",
    # Impuestos Locales
    "ImpuestosLocalesCalculator",
    "ImpuestoEstatal",
    # Costo Trabajador
    "calcular_costo_total",
    "obtener_dias_vacaciones",
    "CostoTotalResult",
]
