import json
from pathlib import Path

import pytest

from catalogmx.validators.rfc import RFCValidator


VECTORS_PATH = (
    Path(__file__).resolve().parents[2]
    / "shared-data"
    / "tests"
    / "rfc_validation.json"
)


@pytest.mark.parametrize("case", json.loads(VECTORS_PATH.read_text(encoding="utf-8")))
def test_rfc_validation_shared(case: dict) -> None:
    assert RFCValidator(case["value"]).validate() is case["valid"]
