import json
from pathlib import Path

import pytest

from catalogmx.calculators.isr import calculate_isr


VECTORS_PATH = (
    Path(__file__).resolve().parents[2]
    / "shared-data"
    / "tests"
    / "isr_vectors.json"
)


def _round(value: float) -> float:
    return round(value, 6)


@pytest.mark.parametrize("case", json.loads(VECTORS_PATH.read_text(encoding="utf-8")))
def test_isr_vectors_shared(case: dict) -> None:
    result = calculate_isr(case["ingreso"], case["periodo"], case["year"])
    expected = case["expected"]

    assert _round(result["isrFinal"]) == expected["isrFinal"]
    assert _round(result["subsidio"]) == expected["subsidio"]
    assert _round(result["isrAntesSubsidio"]) == expected["isrAntesSubsidio"]
    assert _round(result["tasaEfectiva"]) == expected["tasaEfectiva"]
