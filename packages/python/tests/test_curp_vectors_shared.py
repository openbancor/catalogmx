import datetime
import json
from pathlib import Path

import pytest

from catalogmx.validators.curp import CURPGenerator


VECTORS_PATH = (
    Path(__file__).resolve().parents[2]
    / "shared-data"
    / "tests"
    / "curp_vectors.json"
)


@pytest.mark.parametrize("case", json.loads(VECTORS_PATH.read_text(encoding="utf-8")))
def test_curp_vectors_shared(case: dict) -> None:
    fecha = datetime.date.fromisoformat(case["fecha"])
    curp = CURPGenerator(
        nombre=case["nombre"],
        paterno=case["apellido_paterno"],
        materno=case["apellido_materno"],
        fecha_nacimiento=fecha,
        sexo=case["sexo"],
        estado=case["estado"],
    ).curp

    assert curp == case["curp"]
