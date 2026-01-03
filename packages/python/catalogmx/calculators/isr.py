"""
ISR (Impuesto Sobre la Renta) Calculator for Mexico
Supports multi-year calculations: 2024, 2025, 2026
Uses centralized JSON tables from shared-data

Official source: Anexo 8 RMF (Resolución Miscelánea Fiscal)
"""

import json
from pathlib import Path
from typing import Literal, TypedDict

ISRYear = Literal[2024, 2025, 2026]
ISRPeriod = Literal["diaria", "semanal", "decenal", "quincenal", "mensual", "anual"]


class ISRBracket(TypedDict):
    """Tax bracket structure"""

    limiteInferior: float
    limiteSuperior: float | None
    cuotaFija: float
    tasa: float


class ISRSubsidyBracket(TypedDict):
    """Subsidy bracket for tiered system (2024)"""

    desde: float
    hasta: float | None
    subsidio: float


class ISRSubsidyFlat(TypedDict):
    """Flat subsidy system (2025/2026)"""

    amount: float
    maxIncome: float


class ISRCalculationResult(TypedDict):
    """Complete ISR calculation result"""

    ingresoGravable: float
    periodo: str
    year: int
    ingresoMensualizado: float
    bracket: dict
    excedente: float
    impuestoMarginal: float
    isrAntesSubsidio: float
    subsidio: float
    isrFinal: float
    tasaEfectiva: float


# Load ISR tables from centralized JSON
_ISR_TABLES: dict | None = None


def _load_isr_tables() -> dict:
    """Load ISR tables from shared JSON file"""
    global _ISR_TABLES
    if _ISR_TABLES is None:
        # Path from catalogmx/calculators/isr.py -> packages/shared-data/isr-tables.json
        # Go up: isr.py -> calculators -> catalogmx -> python -> packages -> catalogmx (root)
        json_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "packages"
            / "shared-data"
            / "isr-tables.json"
        )
        with open(json_path, encoding="utf-8") as f:
            _ISR_TABLES = json.load(f)
    return _ISR_TABLES


# Period mapping
PERIOD_MAPPING = {
    "diaria": "daily",
    "semanal": "weekly",
    "decenal": "monthly",  # No specific decenal table, use monthly
    "quincenal": "biweekly",
    "mensual": "monthly",
    "anual": "annual",
}

# Period factors for conversion
PERIOD_FACTORS = {
    "diaria": 30.4,
    "semanal": 4.33,
    "decenal": 3.0,
    "quincenal": 2.0,
    "mensual": 1.0,
    "anual": 1 / 12,
}


def get_isr_brackets(year: ISRYear, period: ISRPeriod) -> list[ISRBracket]:
    """
    Get ISR tax brackets for a specific year and period

    Args:
        year: Tax year (2024, 2025, or 2026)
        period: Payment period

    Returns:
        List of tax brackets
    """
    tables = _load_isr_tables()
    year_str = str(year)
    period_key = PERIOD_MAPPING[period]

    brackets_data = tables["brackets"][year_str][period_key]

    # Convert None to float('inf') for limiteSuperior
    brackets = []
    for b in brackets_data:
        bracket = ISRBracket(
            limiteInferior=b["limiteInferior"],
            limiteSuperior=float("inf") if b["limiteSuperior"] is None else b["limiteSuperior"],
            cuotaFija=b["cuotaFija"],
            tasa=b["tasa"],
        )
        brackets.append(bracket)

    return brackets


def calculate_subsidy(income: float, year: ISRYear) -> float:
    """
    Calculate employment subsidy (subsidio al empleo) for a given income

    Args:
        income: Monthly income amount
        year: Tax year

    Returns:
        Subsidy amount
    """
    tables = _load_isr_tables()
    year_str = str(year)
    subsidy_data = tables["subsidies"][year_str]

    if subsidy_data["type"] == "tiered":
        # 2024: tiered system
        monthly_data = subsidy_data["monthly"]
        for s in monthly_data:
            hasta = float("inf") if s["hasta"] is None else s["hasta"]
            if s["desde"] <= income <= hasta:
                return s["subsidio"]
        return 0.0
    else:
        # 2025/2026: flat system
        flat_data = subsidy_data["monthly"]
        if income <= flat_data["maxIncome"]:
            return flat_data["amount"]
        return 0.0


def calculate_isr(
    ingreso_gravable: float, periodo: ISRPeriod = "mensual", year: ISRYear = 2026
) -> ISRCalculationResult:
    """
    Calculate ISR (Income Tax) for Mexico

    Args:
        ingreso_gravable: Taxable income for the period
        periodo: Payment period (default: mensual)
        year: Tax year (default: 2026)

    Returns:
        Complete calculation result with breakdown

    Examples:
        >>> result = calculate_isr(15000, "mensual", 2026)
        >>> print(f"ISR: ${result['isrFinal']:.2f}")
        ISR: $1234.56

        >>> result = calculate_isr(500, "diaria", 2026)
        >>> print(f"ISR diario: ${result['isrFinal']:.2f}")
        ISR diario: $45.67
    """
    # For 2026, use period-specific tables directly
    use_period_tables = year == 2026 and periodo in [
        "diaria",
        "semanal",
        "quincenal",
        "mensual",
        "anual",
    ]

    if use_period_tables:
        # Use official tables for the period (no conversion needed)
        brackets = get_isr_brackets(year, periodo)

        # Find applicable bracket
        bracket = None
        for b in brackets:
            if b["limiteInferior"] <= ingreso_gravable <= b["limiteSuperior"]:
                bracket = b
                break

        if bracket is None:
            bracket = brackets[-1]  # Last bracket (highest income)

        # Calculate excess over lower limit
        excedente = ingreso_gravable - bracket["limiteInferior"]

        # Calculate marginal tax
        impuesto_marginal = excedente * (bracket["tasa"] / 100)

        # Add fixed fee
        isr_antes_subsidio = bracket["cuotaFija"] + impuesto_marginal

        # Calculate subsidy (convert to monthly equivalent)
        factor = PERIOD_FACTORS[periodo]
        ingreso_mensual_equivalente = ingreso_gravable * factor
        subsidio_mensual = calculate_subsidy(ingreso_mensual_equivalente, year)
        subsidio_prorrateado = subsidio_mensual / factor

        # Final ISR
        isr_final = max(0, isr_antes_subsidio - subsidio_prorrateado)

        tasa_efectiva = (isr_final / ingreso_gravable * 100) if ingreso_gravable > 0 else 0

        return ISRCalculationResult(
            ingresoGravable=ingreso_gravable,
            periodo=periodo,
            year=year,
            ingresoMensualizado=ingreso_mensual_equivalente,
            bracket=dict(bracket),
            excedente=excedente,
            impuestoMarginal=impuesto_marginal,
            isrAntesSubsidio=isr_antes_subsidio,
            subsidio=subsidio_prorrateado,
            isrFinal=isr_final,
            tasaEfectiva=tasa_efectiva,
        )

    # For 2024/2025 or decenal period, use factor-based conversion
    brackets = get_isr_brackets(year, "mensual")

    # Convert to monthly
    factor = PERIOD_FACTORS[periodo]
    ingreso_mensualizado = ingreso_gravable * factor

    # Find applicable bracket
    bracket = None
    for b in brackets:
        if b["limiteInferior"] <= ingreso_mensualizado <= b["limiteSuperior"]:
            bracket = b
            break

    if bracket is None:
        bracket = brackets[-1]

    # Calculate excess over lower limit
    excedente = ingreso_mensualizado - bracket["limiteInferior"]

    # Calculate marginal tax
    impuesto_marginal = excedente * (bracket["tasa"] / 100)

    # Add fixed fee
    isr_antes_subsidio = bracket["cuotaFija"] + impuesto_marginal

    # Calculate subsidy
    subsidio = calculate_subsidy(ingreso_mensualizado, year)

    # Final ISR (monthly)
    isr_final_mensual = max(0, isr_antes_subsidio - subsidio)

    # Convert back to original period
    isr_periodo = isr_final_mensual / factor

    tasa_efectiva = (isr_periodo / ingreso_gravable * 100) if ingreso_gravable > 0 else 0

    return ISRCalculationResult(
        ingresoGravable=ingreso_gravable,
        periodo=periodo,
        year=year,
        ingresoMensualizado=ingreso_mensualizado,
        bracket=dict(bracket),
        excedente=excedente,
        impuestoMarginal=impuesto_marginal,
        isrAntesSubsidio=isr_antes_subsidio,
        subsidio=subsidio,
        isrFinal=isr_periodo,
        tasaEfectiva=tasa_efectiva,
    )
