"""
IMSS (Instituto Mexicano del Seguro Social) calculator for Mexico.

The calculator consumes the centralized shared-data tables. Exercise-specific
CEAV rates are selected from the historical schedule instead of a flat legacy
rate. Modalidad 40 uses monthly amounts and requires the last registered monthly
SBC so an eligibility-sensitive calculation cannot silently assume its floor.
"""

import json
import math
from pathlib import Path
from typing import Literal, TypedDict

IMSSYear = Literal[2024, 2025, 2026]
ZonaSalario = Literal["general", "frontera"]
ClaseRiesgo = Literal[1, 2, 3, 4, 5]


class CuotasIMSSResult(TypedDict):
    """IMSS contributions breakdown result."""

    salario_diario: float
    dias: int
    salario_base_cotizacion: float
    year: int
    uma_diaria: float
    ceav_patron_rate: float
    cuotas_patron: dict[str, float]
    cuotas_trabajador: dict[str, float]
    total_patron: float
    total_trabajador: float
    total_imss: float


class Modalidad40Result(TypedDict):
    """Modalidad 40 calculation result."""

    salario_base_cotizacion: float
    ultimo_sbc_mensual: float
    year: int
    uma_mensual: float
    cuota_mensual: float
    porcentaje_total: float
    componentes: dict[str, float]


class Modalidad10Result(TypedDict):
    """Legacy Modalidad 10 calculation result pending source review."""

    salario_base_cotizacion: float
    year: int
    cuota_mensual: float
    cuota_fija_uma: float
    cuota_variable: float
    porcentaje_variable: float
    componentes: dict[str, float]


class UMAInfo(TypedDict):
    """UMA (Unidad de Medida y Actualización) information."""

    diaria: float
    mensual: float
    anual: float


_IMSS_TABLES: dict | None = None
_IMSS_CATALOGS: dict | None = None


def _load_imss_tables() -> dict:
    """Load IMSS tables from the shared JSON file."""
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
    """Load IMSS catalogs from the shared JSON file."""
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
    """Return the UMA published for an exercise."""
    tables = _load_imss_tables()
    uma_data = tables["uma"][str(year)]
    return UMAInfo(
        diaria=uma_data["diaria"],
        mensual=uma_data["mensual"],
        anual=uma_data["anual"],
    )


def get_salario_minimo(year: IMSSYear, zona: ZonaSalario = "general") -> float:
    """Return the daily minimum wage for an exercise and zone."""
    tables = _load_imss_tables()
    return float(tables["salario_minimo"][str(year)][zona])


def _almost_equal(left: float, right: float) -> bool:
    return abs(left - right) < 0.005


def _get_ceav_patron_rate(salario_diario: float, year: IMSSYear) -> float:
    """Select the employer CEAV rate, preserving the special 1-SM row."""
    tables = _load_imss_tables()
    rates = tables["cuotas_imss"]["retiro_cesantia_vejez"]["cesantia_vejez"][
        "patron_por_ejercicio"
    ][str(year)]
    if len(rates) != 8:
        raise ValueError(f"No se encontró tarifa CEAV patronal para {year}")

    minimum = tables["salario_minimo"][str(year)]
    if _almost_equal(salario_diario, float(minimum["general"])) or _almost_equal(
        salario_diario, float(minimum["frontera"])
    ):
        return float(rates[0]["tasa"])

    uma_diaria = get_uma(year)["diaria"]
    ratio = salario_diario / uma_diaria
    if ratio <= 1.5:
        index = 1
    elif ratio <= 2.0:
        index = 2
    elif ratio <= 2.5:
        index = 3
    elif ratio <= 3.0:
        index = 4
    elif ratio <= 3.5:
        index = 5
    elif ratio <= 4.0:
        index = 6
    else:
        index = 7
    return float(rates[index]["tasa"])


def calcular_cuotas_obrero_patronales(
    salario_diario: float,
    dias: int = 30,
    year: IMSSYear = 2026,
    clase_riesgo: ClaseRiesgo = 1,
) -> CuotasIMSSResult:
    """Calculate IMSS employer and employee contributions."""
    tables = _load_imss_tables()
    uma = get_uma(year)
    cuotas = tables["cuotas_imss"]
    salario_base = salario_diario * dias
    uma_diaria = uma["diaria"]

    cuotas_patron: dict[str, float] = {}
    cuotas_trabajador: dict[str, float] = {}

    em = cuotas["enfermedad_maternidad"]

    # Fixed sickness/maternity quota: 20.4% of one UMA per insured day.
    cuotas_patron["enfermedad_mat_cuota_fija"] = (
        uma_diaria * dias * float(em["prestaciones_en_especie"]["patron"])
    )

    # Excess applies only to the daily SBC portion above the configured UMA threshold.
    threshold_factor = float(em["prestaciones_en_especie_excedente"].get("umbral_uma", 3))
    threshold = threshold_factor * uma_diaria
    excedente_base = max(0.0, salario_diario - threshold) * dias
    cuotas_patron["enfermedad_mat_excedente"] = excedente_base * float(
        em["prestaciones_en_especie_excedente"]["patron"]
    )
    cuotas_trabajador["enfermedad_mat_excedente"] = excedente_base * float(
        em["prestaciones_en_especie_excedente"]["trabajador"]
    )

    cuotas_patron["enfermedad_mat_dinero"] = salario_base * float(
        em["prestaciones_en_dinero"]["patron"]
    )
    cuotas_trabajador["enfermedad_mat_dinero"] = salario_base * float(
        em["prestaciones_en_dinero"]["trabajador"]
    )
    cuotas_patron["gastos_medicos_pensionados"] = salario_base * float(
        em["gastos_medicos_pensionados"]["patron"]
    )
    cuotas_trabajador["gastos_medicos_pensionados"] = salario_base * float(
        em["gastos_medicos_pensionados"]["trabajador"]
    )

    iv = cuotas["invalidez_vida"]
    cuotas_patron["invalidez_vida"] = salario_base * float(iv["patron"])
    cuotas_trabajador["invalidez_vida"] = salario_base * float(iv["trabajador"])

    rcv = cuotas["retiro_cesantia_vejez"]
    cuotas_patron["retiro"] = salario_base * float(rcv["retiro"]["patron"])
    ceav_patron_rate = _get_ceav_patron_rate(salario_diario, year)
    cuotas_patron["cesantia_vejez"] = salario_base * ceav_patron_rate
    cuotas_trabajador["cesantia_vejez"] = salario_base * float(rcv["cesantia_vejez"]["trabajador"])

    gps = cuotas["guarderias_prestaciones_sociales"]
    cuotas_patron["guarderias"] = salario_base * float(gps["patron"])

    rt = cuotas["riesgo_trabajo"]
    prima_riesgo = float(rt[f"clase_{clase_riesgo}"])
    cuotas_patron["riesgo_trabajo"] = salario_base * prima_riesgo

    total_patron = sum(cuotas_patron.values())
    total_trabajador = sum(cuotas_trabajador.values())

    return CuotasIMSSResult(
        salario_diario=salario_diario,
        dias=dias,
        salario_base_cotizacion=salario_base,
        year=year,
        uma_diaria=uma_diaria,
        ceav_patron_rate=ceav_patron_rate,
        cuotas_patron=cuotas_patron,
        cuotas_trabajador=cuotas_trabajador,
        total_patron=total_patron,
        total_trabajador=total_trabajador,
        total_imss=total_patron + total_trabajador,
    )


def calcular_modalidad_40(
    salario_base_cotizacion: float,
    ultimo_sbc_mensual: float,
    year: IMSSYear,
) -> Modalidad40Result:
    """Calculate Modalidad 40 using explicit monthly salary amounts.

    The requested monthly SBC must be at least the last registered monthly SBC.
    The upper limit remains 25 monthly UMA. The last SBC is mandatory so this
    function cannot silently represent an ineligible salary as a valid enrollment.
    """
    tables = _load_imss_tables()
    uma = get_uma(year)
    mod40 = tables["modalidad_40"]
    if str(year) not in mod40["referencia_por_ejercicio"]:
        raise ValueError(f"No se encontró tarifa de Modalidad 40 para {year}")

    uma_mensual = uma["mensual"]
    salario_maximo = uma_mensual * float(mod40["limites_salario"]["maximo_uma"])

    if not math.isfinite(ultimo_sbc_mensual) or ultimo_sbc_mensual <= 0:
        raise ValueError("El último SBC mensual debe ser mayor que cero")
    if ultimo_sbc_mensual > salario_maximo:
        raise ValueError("El último SBC mensual excede el tope de 25 UMA")
    if salario_base_cotizacion < ultimo_sbc_mensual:
        raise ValueError("El SBC de Modalidad 40 no puede ser menor al último SBC registrado")
    if salario_base_cotizacion > salario_maximo:
        salario_base_cotizacion = salario_maximo

    dias_uma_mensual = uma_mensual / uma["diaria"]
    salario_diario_equivalente = salario_base_cotizacion / dias_uma_mensual
    ceav_patron_rate = _get_ceav_patron_rate(salario_diario_equivalente, year)

    componentes: dict[str, float] = {
        "cesantia_vejez_patron": salario_base_cotizacion * ceav_patron_rate,
    }
    porcentaje_total = ceav_patron_rate
    for key, value in mod40["calculo"]["componentes_constantes"].items():
        rate = float(value)
        porcentaje_total += rate
        componentes[key] = salario_base_cotizacion * rate

    cuota_mensual = salario_base_cotizacion * porcentaje_total
    return Modalidad40Result(
        salario_base_cotizacion=salario_base_cotizacion,
        ultimo_sbc_mensual=ultimo_sbc_mensual,
        year=year,
        uma_mensual=uma_mensual,
        cuota_mensual=cuota_mensual,
        porcentaje_total=porcentaje_total,
        componentes=componentes,
    )


def calcular_modalidad_10(
    salario_base_cotizacion: float, year: IMSSYear = 2026
) -> Modalidad10Result:
    """Calculate the legacy Modalidad 10 model pending its dedicated audit."""
    tables = _load_imss_tables()
    uma = get_uma(year)
    mod10 = tables["modalidad_10"]

    uma_mensual = uma["mensual"]
    salario_minimo = uma_mensual * float(mod10["limites_salario"]["minimo_uma"])
    salario_maximo = uma_mensual * float(mod10["limites_salario"]["maximo_uma"])

    if salario_base_cotizacion < salario_minimo:
        salario_base_cotizacion = salario_minimo
    elif salario_base_cotizacion > salario_maximo:
        salario_base_cotizacion = salario_maximo

    cuota_fija_uma = uma["diaria"] * float(mod10["cuota_mensual"]["cuota_fija_uma_factor"])
    porcentaje_variable = float(mod10["cuota_mensual"]["porcentaje_variable"])
    cuota_variable = salario_base_cotizacion * porcentaje_variable
    cuota_mensual = cuota_fija_uma + cuota_variable

    componentes: dict[str, float] = {
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
