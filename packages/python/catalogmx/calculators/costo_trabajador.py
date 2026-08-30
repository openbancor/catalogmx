"""
Costo Total del Trabajador Calculator for Mexico
Calculates the true cost of hiring an employee in Mexico including all contributions and reserves

Official sources:
- Ley Federal del Trabajo (LFT)
- IMSS contribution tables
- Infonavit contributions
- State payroll tax laws
"""

import math
from typing import TypedDict

from catalogmx.calculators.impuestos import ImpuestosLocalesCalculator
from catalogmx.calculators.imss import (
    IMSSYear,
    calcular_cuotas_obrero_patronales,
    get_salario_minimo,
)


class CostoTotalResult(TypedDict):
    """Total worker cost calculation result"""

    salario_bruto_mensual: float
    cuotas_imss_patronales: float
    infonavit: float
    impuesto_nomina: float
    reserva_aguinaldo: float
    reserva_prima_vacacional: float
    reserva_vacaciones: float
    ptu_estimado: float
    costo_total_mensual: float
    costo_total_anual: float
    factor_costo: float


# Vacation days according to LFT 2023 (Article 76)
DIAS_VACACIONES_POR_ANTIGUEDAD = {
    1: 12,
    2: 14,
    3: 16,
    4: 18,
    5: 20,
    6: 22,
    7: 22,
    8: 22,
    9: 22,
    10: 22,
    11: 24,
    12: 24,
    13: 24,
    14: 24,
    15: 24,
    16: 26,
    17: 26,
    18: 26,
    19: 26,
    20: 26,
    21: 28,
    22: 28,
    23: 28,
    24: 28,
    25: 28,
    26: 30,
    27: 30,
    28: 30,
    29: 30,
    30: 30,
    31: 32,
    32: 32,
    33: 32,
    34: 32,
    35: 32,
}


def _assert_salario_mensual_bruto(salario_mensual_bruto: float, year: IMSSYear) -> None:
    """Reject an unsafe gross salary before calculating downstream contributions."""
    message = "El salario mensual bruto debe ser un número finito mayor o igual al salario mínimo mensual aplicable."
    if not isinstance(salario_mensual_bruto, (int, float)) or isinstance(
        salario_mensual_bruto, bool
    ):
        raise ValueError(message)
    if not math.isfinite(salario_mensual_bruto):
        raise ValueError(message)
    if salario_mensual_bruto < get_salario_minimo(year, "general") * 30:
        raise ValueError(message)


def obtener_dias_vacaciones(antiguedad_anos: int) -> int:
    """
    Get vacation days based on seniority according to LFT 2023

    Args:
        antiguedad_anos: Years of seniority (1-35+)

    Returns:
        Number of vacation days

    Examples:
        >>> obtener_dias_vacaciones(1)
        12
        >>> obtener_dias_vacaciones(5)
        20
        >>> obtener_dias_vacaciones(40)
        32
    """
    if antiguedad_anos <= 0:
        return 12
    elif antiguedad_anos <= 35:
        return DIAS_VACACIONES_POR_ANTIGUEDAD.get(antiguedad_anos, 32)
    else:
        return 32


def calcular_costo_total(
    salario_mensual_bruto: float,
    cve_estado: str = "09",
    antiguedad_anos: int = 1,
    dias_aguinaldo: int = 15,
    incluir_ptu: bool = False,
    porcentaje_ptu: float = 10.0,
    year: IMSSYear = 2026,
) -> CostoTotalResult:
    """
    Calculate the total cost of employing a worker in Mexico

    This calculator helps employers understand the true cost of hiring someone
    by including all mandatory contributions, taxes, and labor law reserves.

    Args:
        salario_mensual_bruto: Monthly gross salary (base pay)
        cve_estado: State code for payroll tax calculation (default: "09" CDMX)
        antiguedad_anos: Years of seniority (affects vacation days, default: 1)
        dias_aguinaldo: Aguinaldo days (minimum 15, default: 15)
        incluir_ptu: Include PTU (profit sharing) reserve (default: False)
        porcentaje_ptu: PTU percentage if included (default: 10.0%)
        year: Year for IMSS calculations (default: 2026)

    Returns:
        Complete breakdown of employer costs including:
        - IMSS employer contributions
        - Infonavit (5% of SBC)
        - Payroll tax (varies by state)
        - Aguinaldo reserve
        - Vacation bonus reserve
        - Vacation pay reserve
        - Optional PTU reserve

    Examples:
        >>> # Calculate cost for $15,000/month employee in CDMX
        >>> result = calcular_costo_total(15000, "09", 1)
        >>> print(f"Total monthly cost: ${result['costo_total_mensual']:.2f}")
        Total monthly cost: $18750.00

        >>> # Calculate with PTU included
        >>> result = calcular_costo_total(20000, "09", 3, incluir_ptu=True)
        >>> print(f"Factor: {result['factor_costo']:.2f}x")
        Factor: 1.35x
    """
    _assert_salario_mensual_bruto(salario_mensual_bruto, year)

    # 1. Calculate daily wage (assuming 30-day month for calculation purposes)
    salario_diario = salario_mensual_bruto / 30.0

    # 2. Calculate IMSS employer contributions
    cuotas_imss = calcular_cuotas_obrero_patronales(
        salario_diario=salario_diario, dias=30, year=year
    )
    cuotas_imss_patronales = cuotas_imss["total_patron"]

    # 3. Calculate Infonavit (5% of SBC)
    salario_base_cotizacion = cuotas_imss["salario_base_cotizacion"]
    infonavit = salario_base_cotizacion * 0.05

    # 4. Calculate payroll tax (varies by state, typically 2-3%)
    impuesto_nomina = ImpuestosLocalesCalculator.calcular_impuesto_nomina(
        total_percepciones=salario_mensual_bruto, cve_estado=cve_estado
    )

    # 5. Calculate monthly reserves

    # Aguinaldo: dias_aguinaldo / 12 months
    reserva_aguinaldo = (salario_diario * dias_aguinaldo) / 12.0

    # Vacation days based on seniority (LFT 2023)
    dias_vacaciones = obtener_dias_vacaciones(antiguedad_anos)

    # Vacation reserve: vacation days / 12 months
    reserva_vacaciones = (salario_diario * dias_vacaciones) / 12.0

    # Vacation bonus (prima vacacional): 25% of vacation days value
    reserva_prima_vacacional = reserva_vacaciones * 0.25

    # 6. Optional PTU reserve
    ptu_estimado = 0.0
    if incluir_ptu:
        # PTU is typically calculated on annual salary
        # We estimate monthly reserve as (annual_salary * ptu_percentage) / 12
        ptu_estimado = (salario_mensual_bruto * 12 * (porcentaje_ptu / 100)) / 12.0

    # 7. Calculate totals
    costo_total_mensual = (
        salario_mensual_bruto
        + cuotas_imss_patronales
        + infonavit
        + impuesto_nomina
        + reserva_aguinaldo
        + reserva_prima_vacacional
        + reserva_vacaciones
        + ptu_estimado
    )

    costo_total_anual = costo_total_mensual * 12

    # Factor: how much the real cost is compared to base salary
    factor_costo = costo_total_mensual / salario_mensual_bruto

    return CostoTotalResult(
        salario_bruto_mensual=salario_mensual_bruto,
        cuotas_imss_patronales=cuotas_imss_patronales,
        infonavit=infonavit,
        impuesto_nomina=impuesto_nomina,
        reserva_aguinaldo=reserva_aguinaldo,
        reserva_prima_vacacional=reserva_prima_vacacional,
        reserva_vacaciones=reserva_vacaciones,
        ptu_estimado=ptu_estimado,
        costo_total_mensual=costo_total_mensual,
        costo_total_anual=costo_total_anual,
        factor_costo=factor_costo,
    )
