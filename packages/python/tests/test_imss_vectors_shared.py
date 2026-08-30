import json
from pathlib import Path

import pytest

from catalogmx.calculators import get_uma_for_date
from catalogmx.calculators.imss import (
    calcular_cuotas_obrero_patronales,
    calcular_modalidad_10,
    calcular_modalidad_40,
)


VECTORS_PATH = (
    Path(__file__).resolve().parents[2]
    / "shared-data"
    / "tests"
    / "imss_vectors.json"
)


def _round(value: float) -> float:
    return round(value, 6)


def test_public_date_aware_uma_helper() -> None:
    assert get_uma_for_date("2026-01-31")["diaria"] == 113.14
    assert get_uma_for_date("2026-02-01")["diaria"] == 117.31


def test_imss_cuotas_obrero_patronales_vectors_shared() -> None:
    data = json.loads(VECTORS_PATH.read_text(encoding="utf-8"))
    for case in data["cuotas_obrero_patronales"]:
        result = calcular_cuotas_obrero_patronales(
            salario_diario=case["salario_diario"],
            dias=case["dias"],
            year=case["year"],
            clase_riesgo=case["clase_riesgo"],
            fecha=case.get("fecha"),
        )
        expected = case["expected"]
        assert _round(result["total_imss"]) == expected["total_imss"]
        assert _round(result["total_patron"]) == expected["total_patron"]
        assert _round(result["total_trabajador"]) == expected["total_trabajador"]


def test_imss_modalidad_40_vectors_shared() -> None:
    data = json.loads(VECTORS_PATH.read_text(encoding="utf-8"))
    for case in data["modalidad_40"]:
        result = calcular_modalidad_40(
            salario_base_cotizacion=case["salario_base_cotizacion"],
            ultimo_sbc_mensual=case["ultimo_sbc_mensual"],
            year=case["year"],
        )
        expected = case["expected"]
        assert _round(result["cuota_mensual"]) == expected["cuota_mensual"]
        assert _round(result["porcentaje_total"]) == expected["porcentaje_total"]


def test_imss_modalidad_10_vectors_shared() -> None:
    data = json.loads(VECTORS_PATH.read_text(encoding="utf-8"))
    for case in data["modalidad_10"]:
        result = calcular_modalidad_10(
            salario_base_cotizacion=case["salario_base_cotizacion"],
            year=case["year"],
        )
        expected = case["expected"]
        assert _round(result["cuota_mensual"]) == expected["cuota_mensual"]
        assert _round(result["cuota_fija_uma"]) == expected["cuota_fija_uma"]


def test_modalidad_40_rejects_non_finite_requested_salary() -> None:
    with pytest.raises(ValueError, match="debe ser mayor que cero"):
        calcular_modalidad_40(float("nan"), 10000, 2026)
    with pytest.raises(ValueError, match="debe ser mayor que cero"):
        calcular_modalidad_40(float("inf"), 10000, 2026)
