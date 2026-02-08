"""Cross-module integration tests for Python package."""

from __future__ import annotations

import json
from pathlib import Path

from catalogmx import is_valid_clabe, is_valid_curp, is_valid_nss, is_valid_rfc
from catalogmx.calculators import calculate_isr
from catalogmx.catalogs.mexico import SalariosMinimos, UMACatalog


def _load_validation_vectors(file_name: str) -> list[dict]:
    tests_path = Path(__file__).resolve().parents[2] / "shared-data" / "tests" / file_name
    with open(tests_path, encoding="utf-8") as f:
        return json.load(f)


def _first_valid_value(file_name: str) -> str:
    vectors = _load_validation_vectors(file_name)
    return next(v["value"] for v in vectors if v["valid"])


def test_integration_validators_with_shared_vectors() -> None:
    valid_rfc = _first_valid_value("rfc_validation.json")
    valid_curp = _first_valid_value("curp_validation.json")
    valid_clabe = _first_valid_value("clabe_validation.json")
    valid_nss = _first_valid_value("nss_validation.json")

    assert is_valid_rfc(valid_rfc) is True
    assert is_valid_curp(valid_curp) is True
    assert is_valid_clabe(valid_clabe) is True
    assert is_valid_nss(valid_nss) is True


def test_integration_catalogs_and_isr_calculation() -> None:
    salario_actual = SalariosMinimos.get_actual()
    uma_actual = UMACatalog.get_actual()
    assert salario_actual is not None
    assert uma_actual is not None

    salario_2024 = SalariosMinimos.get_por_anio(2024)
    uma_2024 = UMACatalog.get_por_anio(2024)
    assert salario_2024 is not None
    assert uma_2024 is not None
    assert float(salario_2024["resto_pais"]) > 0
    assert float(uma_2024["valor_diario"]) > 0

    isr_result = calculate_isr(15000.0, "mensual", 2026)
    assert isr_result["isrFinal"] > 0
    assert isr_result["isrFinal"] < isr_result["ingresoGravable"]
