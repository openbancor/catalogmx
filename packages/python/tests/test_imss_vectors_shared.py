import json
from pathlib import Path

import pytest

from catalogmx.calculators import get_ceav_patron_rate, get_uma_for_date
from catalogmx.calculators.imss import (
    calcular_cuotas_obrero_patronales,
    calcular_modalidad_10,
    calcular_modalidad_40,
)

VECTORS_PATH = Path(__file__).resolve().parents[2] / "shared-data" / "tests" / "imss_vectors.json"


def _round(value: float) -> float:
    return round(value, 6)


def test_public_date_aware_uma_helper() -> None:
    assert get_uma_for_date("2026-01-31")["diaria"] == 113.14
    assert get_uma_for_date("2026-02-01")["diaria"] == 117.31


def test_public_date_aware_uma_helper_rejects_non_date_strings() -> None:
    for invalid in ("2026-01-31junk", "2026-01-31T23:59:00", "2026-02-31"):
        with pytest.raises(ValueError, match="Fecha inválida"):
            get_uma_for_date(invalid)


def test_public_ceav_selector_uses_only_applicable_wage_zone() -> None:
    assert get_ceav_patron_rate(315.04, 2026, zona="general") == pytest.approx(0.0315)
    assert get_ceav_patron_rate(440.87, 2026, zona="general") == pytest.approx(0.06613)
    assert get_ceav_patron_rate(440.87, 2026, zona="frontera") == pytest.approx(0.0315)


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


def test_imss_date_must_match_selected_exercise() -> None:
    with pytest.raises(ValueError, match="no pertenece al ejercicio 2026"):
        calcular_cuotas_obrero_patronales(500, 30, 2026, 2, "2025-12-31")
    with pytest.raises(ValueError, match="no pertenece al ejercicio 2026"):
        calcular_modalidad_40(15000, 12000, 2026, "2025-12-31")
    with pytest.raises(ValueError, match="no pertenece al ejercicio 2026"):
        calcular_modalidad_10(10000, 2026, "2025-12-31")
