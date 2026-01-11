import json
from pathlib import Path

from catalogmx.calculators.impuestos import (
    IEPSCalculator,
    IVACalculator,
    ImpuestosLocalesCalculator,
    RetencionCalculator,
)


IVA_PATH = (
    Path(__file__).resolve().parents[2]
    / "shared-data"
    / "tests"
    / "iva_vectors.json"
)
IEPS_PATH = (
    Path(__file__).resolve().parents[2]
    / "shared-data"
    / "tests"
    / "ieps_vectors.json"
)
RETENCIONES_PATH = (
    Path(__file__).resolve().parents[2]
    / "shared-data"
    / "tests"
    / "retenciones_vectors.json"
)
LOCALES_PATH = (
    Path(__file__).resolve().parents[2]
    / "shared-data"
    / "tests"
    / "impuestos_locales_vectors.json"
)


def _round(value: float) -> float:
    return round(value, 6)


def test_iva_vectors_shared() -> None:
    data = json.loads(IVA_PATH.read_text(encoding="utf-8"))
    for case in data["calcular"]:
        result = IVACalculator.calcular(case["base"], case["tipo_tasa"], case["fecha"])
        expected = case["expected"]
        assert _round(result["iva"]) == expected["iva"]
        assert _round(result["total_con_iva"]) == expected["total_con_iva"]
        assert _round(result["tasa"]) == expected["tasa"]

    for case in data["calcular_incluido"]:
        result = IVACalculator.calcular_incluido(
            case["total_con_iva"], case["tipo_tasa"], case["fecha"]
        )
        expected = case["expected"]
        assert _round(result["iva"]) == expected["iva"]
        assert _round(result["base"]) == expected["base"]
        assert _round(result["tasa"]) == expected["tasa"]


def test_ieps_vectors_shared() -> None:
    data = json.loads(IEPS_PATH.read_text(encoding="utf-8"))
    for case in data["ad_valorem"]:
        result = IEPSCalculator.calcular_ad_valorem(case["base"], case["tasa"])
        expected = case["expected"]
        assert _round(result["ieps"]) == expected["ieps"]
        assert _round(result["tasa"]) == expected["tasa"]

    for case in data["cuota_fija"]:
        result = IEPSCalculator.calcular_cuota_fija(case["base"], case["cuota"])
        expected = case["expected"]
        assert _round(result["ieps"]) == expected["ieps"]
        assert _round(result["tasa"]) == expected["tasa"]

    for case in data["bebidas_alcoholicas"]:
        result = IEPSCalculator.calcular_bebidas_alcoholicas(
            case["valor"], case["grados_alcohol"]
        )
        expected = case["expected"]
        assert _round(result["ieps"]) == expected["ieps"]
        assert _round(result["tasa"]) == expected["tasa"]

    for case in data["cigarros"]:
        result = IEPSCalculator.calcular_cigarros(case["valor"], case["numero_cigarros"])
        expected = case["expected"]
        assert _round(result["ieps"]) == expected["ieps"]
        assert _round(result["tasa"]) == expected["tasa"]


def test_retenciones_vectors_shared() -> None:
    data = json.loads(RETENCIONES_PATH.read_text(encoding="utf-8"))
    for case in data["isr"]:
        result = RetencionCalculator.calcular_retencion_isr(case["base"], case["concepto"])
        expected = case["expected"]
        assert _round(result["retencion"]) == expected["retencion"]
        assert _round(result["tasa"]) == expected["tasa"]

    for case in data["iva"]:
        result = RetencionCalculator.calcular_retencion_iva(
            case["iva_trasladado"], case["concepto"]
        )
        expected = case["expected"]
        assert _round(result["retencion"]) == expected["retencion"]
        assert _round(result["tasa"]) == expected["tasa"]

    for case in data["honorarios"]:
        result = RetencionCalculator.calcular_honorarios(case["monto_sin_iva"])
        expected = case["expected"]
        assert _round(result["retencion"]) == expected["retencion"]
        assert _round(result["tasa"]) == expected["tasa"]

    for case in data["arrendamiento"]:
        result = RetencionCalculator.calcular_arrendamiento(case["monto_sin_iva"])
        expected = case["expected"]
        assert _round(result["retencion"]) == expected["retencion"]
        assert _round(result["tasa"]) == expected["tasa"]

    for case in data["fletes"]:
        result = RetencionCalculator.calcular_fletes(case["monto_sin_iva"])
        expected = case["expected"]
        assert _round(result["retencion"]) == expected["retencion"]
        assert _round(result["tasa"]) == expected["tasa"]


def test_impuestos_locales_vectors_shared() -> None:
    data = json.loads(LOCALES_PATH.read_text(encoding="utf-8"))
    for case in data["impuesto_nomina"]:
        result = ImpuestosLocalesCalculator.calcular_impuesto_nomina(
            case["total_percepciones"], case["cve_estado"]
        )
        assert _round(result) == case["expected"]

    for case in data["impuesto_hospedaje"]:
        result = ImpuestosLocalesCalculator.calcular_impuesto_hospedaje(
            case["monto_hospedaje"], case["cve_estado"]
        )
        assert _round(result) == case["expected"]
