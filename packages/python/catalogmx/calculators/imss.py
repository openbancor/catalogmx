"""
IMSS (Instituto Mexicano del Seguro Social) Calculator for Mexico
Calculates employer/employee contributions and voluntary modalities (10, 40)
Uses centralized JSON tables from shared-data

Official sources:
- Ley del Seguro Social
- Sistema Único de Autodeterminación (SUA)
"""

import json
from pathlib import Path
from typing import Literal, TypedDict

IMSSYear = Literal[2024, 2025, 2026]
ZonaSalario = Literal["general", "frontera"]
ClaseRiesgo = Literal[1, 2, 3, 4, 5]


class CuotasIMSSResult(TypedDict):
    """IMSS contributions breakdown result"""

    salario_diario: float
    dias: int
    salario_base_cotizacion: float
    year: int
    cuotas_patron: dict[str, float]
    cuotas_trabajador: dict[str, float]
    total_patron: float
    total_trabajador: float
    total_imss: float


class Modalidad40Result(TypedDict):
    """Modalidad 40 calculation result"""

    salario_base_cotizacion: float
    year: int
    cuota_mensual: float
    porcentaje_total: float
    componentes: dict[str, float]


class Modalidad10Result(TypedDict):
    """Modalidad 10 calculation result"""

    salario_base_cotizacion: float
    year: int
    cuota_mensual: float
    cuota_fija_uma: float
    cuota_variable: float
    porcentaje_variable: float
    componentes: dict[str, float]


class UMAInfo(TypedDict):
    """UMA (Unidad de Medida y Actualización) information"""

    diaria: float
    mensual: float
    anual: float


# Load IMSS tables from centralized JSON
_IMSS_TABLES: dict | None = None
_IMSS_CATALOGS: dict | None = None


def _load_imss_tables() -> dict:
    """Load IMSS tables from shared JSON file"""
    global _IMSS_TABLES
    if _IMSS_TABLES is None:
        json_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "packages"
            / "shared-data"
            / "imss-tables.json"
        )
        with open(json_path, encoding="utf-8") as f:
            _IMSS_TABLES = json.load(f)
    return _IMSS_TABLES


def _load_imss_catalogs() -> dict:
    """Load IMSS catalogs from shared JSON file"""
    global _IMSS_CATALOGS
    if _IMSS_CATALOGS is None:
        json_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "packages"
            / "shared-data"
            / "imss-catalogs.json"
        )
        with open(json_path, encoding="utf-8") as f:
            _IMSS_CATALOGS = json.load(f)
    return _IMSS_CATALOGS


def get_uma(year: IMSSYear) -> UMAInfo:
    """
    Get UMA (Unidad de Medida y Actualización) values for a specific year

    Args:
        year: Year (2024, 2025, or 2026)

    Returns:
        UMA values (diaria, mensual, anual)

    Examples:
        >>> uma = get_uma(2026)
        >>> print(f"UMA diaria 2026: ${uma['diaria']}")
        UMA diaria 2026: $113.14
    """
    tables = _load_imss_tables()
    year_str = str(year)
    uma_data = tables["uma"][year_str]
    return UMAInfo(
        diaria=uma_data["diaria"],
        mensual=uma_data["mensual"],
        anual=uma_data["anual"],
    )


def get_salario_minimo(year: IMSSYear, zona: ZonaSalario = "general") -> float:
    """
    Get minimum wage for a specific year and zone

    Args:
        year: Year (2024, 2025, or 2026)
        zona: Zone type ("general" or "frontera")

    Returns:
        Daily minimum wage amount

    Examples:
        >>> salario = get_salario_minimo(2026, "general")
        >>> print(f"Salario mínimo general 2026: ${salario}")
        Salario mínimo general 2026: $278.80
    """
    tables = _load_imss_tables()
    year_str = str(year)
    return tables["salario_minimo"][year_str][zona]


def calcular_cuotas_obrero_patronales(
    salario_diario: float,
    dias: int = 30,
    year: IMSSYear = 2026,
    clase_riesgo: ClaseRiesgo = 1,
) -> CuotasIMSSResult:
    """
    Calculate IMSS employer and employee contributions

    Args:
        salario_diario: Daily wage
        dias: Number of days (default: 30)
        year: Year (default: 2026)
        clase_riesgo: Work risk class 1-5 (default: 1 - minimum risk)

    Returns:
        Complete breakdown of IMSS contributions

    Examples:
        >>> result = calcular_cuotas_obrero_patronales(500.0, 30, 2026)
        >>> print(f"Total patrón: ${result['total_patron']:.2f}")
        >>> print(f"Total trabajador: ${result['total_trabajador']:.2f}")
    """
    tables = _load_imss_tables()
    uma = get_uma(year)
    cuotas = tables["cuotas_imss"]

    # Calculate base salary for contributions
    salario_base = salario_diario * dias

    # Límite de 3 UMAs diario para algunas cuotas
    uma_diaria = uma["diaria"]
    tres_uma_mensual = uma_diaria * 3 * 30

    # Initialize contribution dictionaries
    cuotas_patron: dict[str, float] = {}
    cuotas_trabajador: dict[str, float] = {}

    # 1. Enfermedad y Maternidad
    em = cuotas["enfermedad_maternidad"]

    # Cuota fija (sobre 3 UMAs)
    cuotas_patron["enfermedad_mat_cuota_fija"] = (
        uma_diaria * 3 * dias * em["prestaciones_en_especie"]["patron"]
    )

    # Excedente de 3 UMAs
    if salario_diario > tres_uma_mensual / 30:
        excedente_base = salario_base - tres_uma_mensual
        cuotas_patron["enfermedad_mat_excedente"] = (
            excedente_base * em["prestaciones_en_especie_excedente"]["patron"]
        )
        cuotas_trabajador["enfermedad_mat_excedente"] = (
            excedente_base * em["prestaciones_en_especie_excedente"]["trabajador"]
        )
    else:
        cuotas_patron["enfermedad_mat_excedente"] = 0.0
        cuotas_trabajador["enfermedad_mat_excedente"] = 0.0

    # Prestaciones en dinero
    cuotas_patron["enfermedad_mat_dinero"] = salario_base * em["prestaciones_en_dinero"]["patron"]
    cuotas_trabajador["enfermedad_mat_dinero"] = (
        salario_base * em["prestaciones_en_dinero"]["trabajador"]
    )

    # Gastos médicos pensionados
    cuotas_patron["gastos_medicos_pensionados"] = (
        salario_base * em["gastos_medicos_pensionados"]["patron"]
    )
    cuotas_trabajador["gastos_medicos_pensionados"] = (
        salario_base * em["gastos_medicos_pensionados"]["trabajador"]
    )

    # 2. Invalidez y Vida
    iv = cuotas["invalidez_vida"]
    cuotas_patron["invalidez_vida"] = salario_base * iv["patron"]
    cuotas_trabajador["invalidez_vida"] = salario_base * iv["trabajador"]

    # 3. Retiro, Cesantía y Vejez
    rcv = cuotas["retiro_cesantia_vejez"]
    cuotas_patron["retiro"] = salario_base * rcv["retiro"]["patron"]
    cuotas_patron["cesantia_vejez"] = salario_base * rcv["cesantia_vejez"]["patron"]
    cuotas_trabajador["cesantia_vejez"] = salario_base * rcv["cesantia_vejez"]["trabajador"]

    # 4. Guarderías y Prestaciones Sociales
    gps = cuotas["guarderias_prestaciones_sociales"]
    cuotas_patron["guarderias"] = salario_base * gps["patron"]

    # 5. Riesgos de Trabajo
    rt = cuotas["riesgo_trabajo"]
    prima_riesgo = rt[f"clase_{clase_riesgo}"]
    cuotas_patron["riesgo_trabajo"] = salario_base * prima_riesgo

    # Calculate totals
    total_patron = sum(cuotas_patron.values())
    total_trabajador = sum(cuotas_trabajador.values())

    return CuotasIMSSResult(
        salario_diario=salario_diario,
        dias=dias,
        salario_base_cotizacion=salario_base,
        year=year,
        cuotas_patron=cuotas_patron,
        cuotas_trabajador=cuotas_trabajador,
        total_patron=total_patron,
        total_trabajador=total_trabajador,
        total_imss=total_patron + total_trabajador,
    )


def calcular_modalidad_40(
    salario_base_cotizacion: float, year: IMSSYear = 2026
) -> Modalidad40Result:
    """
    Calculate Modalidad 40 voluntary IMSS contributions
    (Continuación voluntaria en el régimen obligatorio)

    Modalidad 40 allows workers who left formal employment to continue
    contributing to IMSS to increase their pension amount.

    Args:
        salario_base_cotizacion: Monthly base salary (between 1 and 25 UMAs)
        year: Year (default: 2026)

    Returns:
        Modalidad 40 calculation result

    Examples:
        >>> result = calcular_modalidad_40(15000, 2026)
        >>> print(f"Cuota mensual: ${result['cuota_mensual']:.2f}")
    """
    tables = _load_imss_tables()
    uma = get_uma(year)
    mod40 = tables["modalidad_40"]

    # Validate salary limits
    uma_mensual = uma["mensual"]
    salario_minimo = uma_mensual * mod40["limites_salario"]["minimo_uma"]
    salario_maximo = uma_mensual * mod40["limites_salario"]["maximo_uma"]

    if salario_base_cotizacion < salario_minimo:
        salario_base_cotizacion = salario_minimo
    elif salario_base_cotizacion > salario_maximo:
        salario_base_cotizacion = salario_maximo

    # Calculate monthly contribution (10.47% total)
    porcentaje_total = mod40["cuota_mensual"]["porcentaje_total"]
    cuota_mensual = salario_base_cotizacion * porcentaje_total

    # Get component breakdown
    componentes = {
        key: salario_base_cotizacion * value
        for key, value in mod40["cuota_mensual"]["componentes"].items()
    }

    return Modalidad40Result(
        salario_base_cotizacion=salario_base_cotizacion,
        year=year,
        cuota_mensual=cuota_mensual,
        porcentaje_total=porcentaje_total,
        componentes=componentes,
    )


def calcular_modalidad_10(
    salario_base_cotizacion: float, year: IMSSYear = 2026
) -> Modalidad10Result:
    """
    Calculate Modalidad 10 voluntary IMSS contributions
    (Incorporación voluntaria al régimen obligatorio - trabajadores independientes)

    Modalidad 10 allows independent workers to enroll in IMSS and access
    all social security benefits including healthcare, retirement, and more.

    Args:
        salario_base_cotizacion: Monthly base salary (between 1 and 25 UMAs)
        year: Year (default: 2026)

    Returns:
        Modalidad 10 calculation result

    Examples:
        >>> result = calcular_modalidad_10(10000, 2026)
        >>> print(f"Cuota mensual: ${result['cuota_mensual']:.2f}")
    """
    tables = _load_imss_tables()
    uma = get_uma(year)
    mod10 = tables["modalidad_10"]

    # Validate salary limits
    uma_mensual = uma["mensual"]
    salario_minimo = uma_mensual * mod10["limites_salario"]["minimo_uma"]
    salario_maximo = uma_mensual * mod10["limites_salario"]["maximo_uma"]

    if salario_base_cotizacion < salario_minimo:
        salario_base_cotizacion = salario_minimo
    elif salario_base_cotizacion > salario_maximo:
        salario_base_cotizacion = salario_maximo

    # Fixed fee: 3.3 UMAs for healthcare
    cuota_fija_uma = uma["diaria"] * mod10["cuota_mensual"]["cuota_fija_uma_factor"]

    # Variable percentage: 10.47%
    porcentaje_variable = mod10["cuota_mensual"]["porcentaje_variable"]
    cuota_variable = salario_base_cotizacion * porcentaje_variable

    # Total monthly contribution
    cuota_mensual = cuota_fija_uma + cuota_variable

    # Get component breakdown
    componentes = {
        "prestaciones_en_especie_fija": cuota_fija_uma,
    }
    for key, value in mod10["cuota_mensual"]["componentes"].items():
        if isinstance(value, (int, float)):
            componentes[key] = salario_base_cotizacion * value

    return Modalidad10Result(
        salario_base_cotizacion=salario_base_cotizacion,
        year=year,
        cuota_mensual=cuota_mensual,
        cuota_fija_uma=cuota_fija_uma,
        cuota_variable=cuota_variable,
        porcentaje_variable=porcentaje_variable,
        componentes=componentes,
    )
