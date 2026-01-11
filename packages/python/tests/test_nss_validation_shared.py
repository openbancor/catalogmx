import json
from pathlib import Path

import pytest

from catalogmx.validators.nss import NSSValidator


VECTORS_PATH = (
    Path(__file__).resolve().parents[2]
    / "shared-data"
    / "tests"
    / "nss_validation.json"
)


@pytest.mark.parametrize("case", json.loads(VECTORS_PATH.read_text(encoding="utf-8")))
def test_nss_validation_shared(case: dict) -> None:
    assert NSSValidator(case["value"]).is_valid() is case["valid"]
