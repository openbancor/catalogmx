import json
from pathlib import Path

import pytest

from catalogmx.validators.clabe import generate_clabe


VECTORS_PATH = (
    Path(__file__).resolve().parents[2]
    / "shared-data"
    / "tests"
    / "clabe_vectors.json"
)


@pytest.mark.parametrize("case", json.loads(VECTORS_PATH.read_text(encoding="utf-8")))
def test_clabe_vectors_shared(case: dict) -> None:
    clabe = generate_clabe(
        case["bank_code"],
        case["branch_code"],
        case["account_number"],
    )
    assert clabe == case["clabe"]
