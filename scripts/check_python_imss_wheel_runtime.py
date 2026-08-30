#!/usr/bin/env python3
"""Smoke-test IMSS APIs from a built wheel outside the repository checkout."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

SMOKE = r"""
import json
import sys
from importlib.resources import files

sys.path.insert(0, sys.argv[1])

from catalogmx.calculators.imss import (
    calcular_cuotas_obrero_patronales,
    calcular_modalidad_10,
    calcular_modalidad_40,
    get_uma,
)
from catalogmx.catalogs.sat.cfdi_4 import EstadoCfdiCatalog
from catalogmx.catalogs.sat.cfdi_4 import ClaveProdServCatalog

tables = json.loads(files("catalogmx.data").joinpath("imss-tables.json").read_text())
catalogs = json.loads(files("catalogmx.data").joinpath("imss-catalogs.json").read_text())
uma = get_uma(2026)
cuotas = calcular_cuotas_obrero_patronales(500, year=2026)
modalidad_40 = calcular_modalidad_40(15000, ultimo_sbc_mensual=12000, year=2026)
modalidad_10 = calcular_modalidad_10(10000, year=2026)

assert tables["uma"]["2026"]["diaria"] == uma["diaria"]
assert catalogs["tipos_trabajador"]
assert cuotas["total_imss"] > 0
assert modalidad_40["cuota_mensual"] > 0
assert modalidad_10["cuota_mensual"] > 0
assert EstadoCfdiCatalog.get_estado("DIF") == {"code": "DIF"}
assert EstadoCfdiCatalog.get_estado("cmx") == {"code": "CMX"}
assert ClaveProdServCatalog.get_clave("84111505")["id"] == "84111505"
assert ClaveProdServCatalog.search("contabilidad", limit=1)
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("wheel", type=Path)
    args = parser.parse_args()
    wheel = args.wheel.resolve(strict=True)

    with tempfile.TemporaryDirectory(prefix="catalogmx-wheel-smoke-") as temp_dir:
        install_dir = Path(temp_dir) / "site-packages"
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "--target",
                str(install_dir),
                str(wheel),
            ],
            check=True,
        )
        subprocess.run(
            [sys.executable, "-I", "-c", SMOKE, str(install_dir)],
            cwd=temp_dir,
            check=True,
        )


if __name__ == "__main__":
    main()
