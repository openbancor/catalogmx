"""Verify the bounded Worker-safe CFDI Nómina product projection."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
FULL_CATALOG = (
    REPO_ROOT / "packages" / "shared-data" / "sat" / "cfdi_4.0" / "clave_prod_serv.json"
)
PROJECTION = (
    REPO_ROOT
    / "packages"
    / "shared-data"
    / "sat"
    / "cfdi_4.0"
    / "nomina_clave_prod_serv.json"
)


def test_nomina_projection_is_exact_and_not_a_partial_general_catalog() -> None:
    source = json.loads(FULL_CATALOG.read_text(encoding="utf-8"))
    document = json.loads(PROJECTION.read_text(encoding="utf-8"))
    expected = next(item for item in source if item["id"] == "84111505")

    assert document["_meta"]["profile"] == "cfdi.nomina"
    assert (
        document["_meta"]["source_sha256"]
        == hashlib.sha256(FULL_CATALOG.read_bytes()).hexdigest()
    )
    assert document["_meta"]["payroll_guide_sha256"] == (
        "b1da7fc079ec8c88ad584955aa17307aefa423cf51abee9f6a1c3e94b5fb68c6"
    )
    assert document["data"] == [
        {
            "code": expected["id"],
            "description": expected["descripcion"],
            "valid_from": expected["fechaInicioVigencia"],
            "valid_to": expected["fechaFinVigencia"],
        }
    ]
