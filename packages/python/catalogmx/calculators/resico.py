"""
RESICO (Régimen Simplificado de Confianza) Calculator for Mexico
Supports years: 2024, 2025, 2026

RESICO uses a DIRECT TAX RATE system (simpler than ISR):
- No deductions allowed
- No fixed fee (cuota fija)
- Tax = Total Income × Bracket Rate

Official source: Artículo 113-E LISR (Ley del Impuesto Sobre la Renta)
"""

import json
from pathlib import Path
from typing import Literal, TypedDict


RESICOYear = Literal[2024, 2025, 2026]
RESICOPeriod = Literal["mensual", "anual"]


class RESICOBracket(TypedDict):
    """RESICO tax bracket structure (simplified - no cuota fija)"""
    limiteInferior: float
    limiteSuperior: float
    tasa: float


class RESICOCalculationResult(TypedDict):
    """Complete RESICO calculation result"""
    ingreso: float
    periodo: str
    year: int
    limiteMaximo: float
    dentroDeLimite: bool
    bracket: dict
    resicoCalculado: float
    tasaEfectiva: float


# Load RESICO tables from centralized JSON
_RESICO_TABLES: dict | None = None


def _load_resico_tables() -> dict:
    """Load RESICO tables from shared JSON file"""
    global _RESICO_TABLES
    if _RESICO_TABLES is None:
        json_path = Path(__file__).parent.parent.parent.parent.parent / "packages" / "shared-data" / "resico-tables.json"
        with open(json_path, 'r', encoding='utf-8') as f:
            _RESICO_TABLES = json.load(f)
    return _RESICO_TABLES


def get_resico_brackets(year: RESICOYear, periodo: RESICOPeriod) -> list[RESICOBracket]:
    """
    Get RESICO tax brackets for a specific year and period

    Args:
        year: Tax year (2024, 2025, or 2026)
        periodo: Period (mensual or anual)

    Returns:
        List of RESICO tax brackets
    """
    tables = _load_resico_tables()
    year_str = str(year)

    brackets_data = tables["brackets"][year_str][periodo]

    brackets = []
    for b in brackets_data:
        bracket = RESICOBracket(
            limiteInferior=b["limiteInferior"],
            limiteSuperior=b["limiteSuperior"],
            tasa=b["tasa"]
        )
        brackets.append(bracket)

    return brackets


def calculate_resico(
    ingreso: float,
    periodo: RESICOPeriod = "mensual",
    year: RESICOYear = 2026
) -> RESICOCalculationResult:
    """
    Calculate RESICO (Régimen Simplificado de Confianza) tax

    RESICO uses a DIRECT TAX RATE system (not marginal like regular ISR):
    - No deductions allowed
    - No fixed fee (cuota fija)
    - Tax = Total Income × Bracket Rate

    Args:
        ingreso: Taxable income for the period
        periodo: Period (mensual or anual, default: mensual)
        year: Tax year (default: 2026)

    Returns:
        Complete RESICO calculation result

    Examples:
        >>> # Monthly income $50,000 → bracket 1.5% → ISR = $50,000 × 1.5% = $750
        >>> result = calculate_resico(50000, "mensual", 2026)
        >>> print(f"RESICO: ${result['resicoCalculado']:.2f}")
        RESICO: $750.00

        >>> # Annual income $500,000 → bracket 1.1% → ISR = $500,000 × 1.1% = $5,500
        >>> result = calculate_resico(500000, "anual", 2026)
        >>> print(f"RESICO anual: ${result['resicoCalculado']:.2f}")
        RESICO anual: $5500.00
    """
    tables = _load_resico_tables()

    # Get income limits
    limits = tables["limits"]["personaFisica"]
    limite_maximo = limits["ingresoMensualMaximo"] if periodo == "mensual" else limits["ingresoAnualMaximo"]
    dentro_de_limite = ingreso <= limite_maximo

    # Get brackets for year and period
    brackets = get_resico_brackets(year, periodo)

    # Find applicable bracket
    bracket = None
    for b in brackets:
        if b["limiteInferior"] <= ingreso <= b["limiteSuperior"]:
            bracket = b
            break

    if bracket is None:
        bracket = brackets[-1]  # Last bracket if not found

    # RESICO calculation: Direct rate on total income (NO cuota fija, NO excedente)
    resico_calculado = ingreso * (bracket["tasa"] / 100)

    # Effective rate (should equal bracket rate for RESICO)
    tasa_efectiva = (resico_calculado / ingreso * 100) if ingreso > 0 else 0

    return RESICOCalculationResult(
        ingreso=ingreso,
        periodo=periodo,
        year=year,
        limiteMaximo=limite_maximo,
        dentroDeLimite=dentro_de_limite,
        bracket=dict(bracket),
        resicoCalculado=resico_calculado,
        tasaEfectiva=tasa_efectiva
    )
