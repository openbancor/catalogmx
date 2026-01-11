import json
from pathlib import Path

import pytest

from catalogmx.validators.nss import generate_nss


VECTORS_PATH = (
    Path(__file__).resolve().parents[2]
    / "shared-data"
    / "tests"
    / "nss_vectors.json"
)


@pytest.mark.parametrize("case", json.loads(VECTORS_PATH.read_text(encoding="utf-8")))
def test_nss_vectors_shared(case: dict) -> None:
    nss = generate_nss(
        case["subdelegacion"],
        case["registro_anio"],
        case["nacimiento_anio"],
        case["secuencial"],
    )
    assert nss == case["nss"]
