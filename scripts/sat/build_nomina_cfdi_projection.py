#!/usr/bin/env python3
"""Build the bounded CFDI product/service projection required by Nómina."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE = (
    REPO_ROOT / "packages" / "shared-data" / "sat" / "cfdi_4.0" / "clave_prod_serv.json"
)
OUTPUT = (
    REPO_ROOT
    / "packages"
    / "shared-data"
    / "sat"
    / "cfdi_4.0"
    / "nomina_clave_prod_serv.json"
)
PAYROLL_GUIDE = (
    "https://www.sat.gob.mx/cs/Satellite?blobcol=urldata&blobkey=id&"
    "blobtable=MungoBlobs&blobwhere=1461173081850&ssbinary=true"
)
PAYROLL_GUIDE_SHA256 = (
    "b1da7fc079ec8c88ad584955aa17307aefa423cf51abee9f6a1c3e94b5fb68c6"
)
NOMINA_CLAVE_PROD_SERV = "84111505"


def render() -> str:
    catalog = json.loads(SOURCE.read_text(encoding="utf-8"))
    matches = [item for item in catalog if item.get("id") == NOMINA_CLAVE_PROD_SERV]
    if len(matches) != 1:
        raise RuntimeError("c_ClaveProdServ must contain exactly one active Nómina key")
    item = matches[0]
    if item.get("fechaFinVigencia"):
        raise RuntimeError("SAT Nómina product/service key is no longer active")

    payload = {
        "_meta": {
            "profile": "cfdi.nomina",
            "authority": "SAT",
            "payroll_guide": PAYROLL_GUIDE,
            "payroll_guide_sha256": PAYROLL_GUIDE_SHA256,
            "source": "sat/cfdi_4.0/clave_prod_serv.json",
            "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "scope": "Nómina-only projection; not a partial ClaveProdServCatalog",
        },
        "data": [
            {
                "code": item["id"],
                "description": item["descripcion"],
                "valid_from": item["fechaInicioVigencia"],
                "valid_to": item["fechaFinVigencia"],
            }
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = render()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != expected:
            raise SystemExit(
                "CFDI Nómina projection is stale; run scripts/sat/build_nomina_cfdi_projection.py"
            )
        return 0
    OUTPUT.write_text(expected, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
