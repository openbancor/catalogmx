#!/usr/bin/env python3
"""Project SAT's c_Estado XSD enumeration to deterministic package JSON."""

from __future__ import annotations

import argparse
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
XSD = (
    REPO_ROOT
    / "packages"
    / "shared-data"
    / "sat"
    / "xsd"
    / "resources"
    / "www.sat.gob.mx"
    / "sitio_internet"
    / "cfd"
    / "catalogos"
    / "catCFDI.xsd"
)
OUTPUT = REPO_ROOT / "packages" / "shared-data" / "sat" / "cfdi_4.0" / "estado.json"
SOURCE_URL = "http://www.sat.gob.mx/sitio_internet/cfd/catalogos/catCFDI.xsd"
XS = {"xs": "http://www.w3.org/2001/XMLSchema"}


def render() -> str:
    root = ET.parse(XSD).getroot()
    simple_type = root.find("xs:simpleType[@name='c_Estado']", XS)
    if simple_type is None:
        raise RuntimeError("SAT catCFDI.xsd has no c_Estado simple type")
    codes = [
        item.attrib["value"]
        for item in simple_type.findall("xs:restriction/xs:enumeration", XS)
    ]
    if len(codes) != len(set(codes)) or not codes:
        raise RuntimeError("SAT c_Estado values are empty or duplicated")

    payload = {
        "_meta": {
            "catalog": "c_Estado",
            "authority": "SAT",
            "source": SOURCE_URL,
            "source_sha256": hashlib.sha256(XSD.read_bytes()).hexdigest(),
            "xsd_name": "c_Estado",
        },
        "data": [{"code": code} for code in codes],
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
                "c_Estado projection is stale; run scripts/sat/build_cfdi_estado.py"
            )
        return 0
    OUTPUT.write_text(expected, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
