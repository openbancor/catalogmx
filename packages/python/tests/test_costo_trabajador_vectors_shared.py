import json
from pathlib import Path

import pytest

from catalogmx.calculators.costo_trabajador import calcular_costo_total


VECTORS_PATH = (
    Path(__file__).resolve().parents[2]
    / "shared-data"
    / "tests"
    / "costo_trabajador_vectors.json"
)


def _round(value: float) -> float:
    return round(value, 6)


@pytest.mark.parametrize("case", json.loads(VECTORS_PATH.read_text(encoding="utf-8")))
def test_costo_trabajador_vectors_shared(case: dict) -> None:
    result = calcular_costo_total(**case["input"])
    expected = case["expected"]

    for key, expected_value in expected.items():
        assert _round(result[key]) == expected_value
