import datetime
import json
from pathlib import Path

import pytest

from catalogmx.validators.rfc import RFCGenerator


VECTORS_PATH = (
    Path(__file__).resolve().parents[2]
    / "shared-data"
    / "tests"
    / "rfc_vectors.json"
)


@pytest.mark.parametrize("case", json.loads(VECTORS_PATH.read_text(encoding="utf-8")))
def test_rfc_vectors_shared(case: dict) -> None:
    fecha = datetime.date.fromisoformat(case["fecha"])

    if case["type"] == "fisica":
        rfc = RFCGenerator.generate_fisica(
            nombre=case["nombre"],
            paterno=case["apellido_paterno"],
            materno=case["apellido_materno"],
            fecha=fecha,
        )
    else:
        rfc = RFCGenerator.generate_moral(
            razon_social=case["razon_social"],
            fecha=fecha,
        )

    assert rfc == case["rfc"]
