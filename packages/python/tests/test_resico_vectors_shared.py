import json
from pathlib import Path

import pytest

from catalogmx.calculators.resico import calculate_resico


VECTORS_PATH = (
    Path(__file__).resolve().parents[2]
    / "shared-data"
    / "tests"
    / "resico_vectors.json"
)


def _round(value: float) -> float:
    return round(value, 6)


@pytest.mark.parametrize("case", json.loads(VECTORS_PATH.read_text(encoding="utf-8")))
def test_resico_vectors_shared(case: dict) -> None:
    result = calculate_resico(case["ingreso"], case["periodo"], case["year"])
    expected = case["expected"]

    assert _round(result["resicoCalculado"]) == expected["resicoCalculado"]
    assert _round(result["tasaEfectiva"]) == expected["tasaEfectiva"]
