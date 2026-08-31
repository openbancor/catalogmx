"""Keep the packaged c_Estado projection equal to the reviewed SAT XSD."""

from __future__ import annotations

import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
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
CATALOG = REPO_ROOT / "packages" / "shared-data" / "sat" / "cfdi_4.0" / "estado.json"
XS = {"xs": "http://www.w3.org/2001/XMLSchema"}


def test_cfdi_estado_projection_matches_sat_xsd() -> None:
    root = ET.parse(XSD).getroot()
    simple_type = root.find("xs:simpleType[@name='c_Estado']", XS)
    assert simple_type is not None
    expected = [
        item.attrib["value"]
        for item in simple_type.findall("xs:restriction/xs:enumeration", XS)
    ]

    document = json.loads(CATALOG.read_text())
    assert document["_meta"]["xsd_name"] == "c_Estado"
    assert (
        document["_meta"]["source_sha256"]
        == hashlib.sha256(XSD.read_bytes()).hexdigest()
    )
    assert [item["code"] for item in document["data"]] == expected
    assert {"DIF", "CMX", "UN"} <= set(expected)
