#!/usr/bin/env python3
"""Verify the installed fiscal wheel exposes PEP 561 types to a clean consumer."""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import venv
import zipfile
from pathlib import Path

CONSUMER = """\
from catalogmx.fiscal import FiscalDatasetId, FiscalManifest, FiscalManifestEntry
from catalogmx.fiscal import fiscal_entry, fiscal_manifest

dataset_id: FiscalDatasetId = \"uma\"
manifest: FiscalManifest = fiscal_manifest()
entry: FiscalManifestEntry | None = fiscal_entry(dataset_id, 2026)

reveal_type(manifest)
reveal_type(entry)
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("wheel", type=Path)
    args = parser.parse_args()
    wheel = args.wheel.resolve()

    with zipfile.ZipFile(wheel) as archive:
        if "catalogmx/py.typed" not in archive.namelist():
            raise SystemExit("wheel is missing catalogmx/py.typed")

    with tempfile.TemporaryDirectory(prefix="catalogmx-fiscal-types-") as temporary:
        root = Path(temporary)
        environment = root / "venv"
        venv.EnvBuilder(with_pip=True, symlinks=True).create(environment)
        python = environment / "bin" / "python"
        consumer = root / "consumer.py"
        consumer.write_text(CONSUMER, encoding="utf-8")

        subprocess.run(
            [python, "-m", "pip", "install", "mypy", str(wheel)],
            check=True,
        )
        result = subprocess.run(
            [
                python,
                "-m",
                "mypy",
                "--strict",
                "--disallow-any-expr",
                "--no-incremental",
                str(consumer),
            ],
            check=False,
            text=True,
            capture_output=True,
            cwd=root,
        )
        sys.stdout.write(result.stdout)
        sys.stderr.write(result.stderr)
        if result.returncode:
            return result.returncode
        if "Any" in result.stdout:
            raise SystemExit("fiscal wheel consumer revealed an Any type")
        if (
            "FiscalManifest" not in result.stdout
            or "FiscalManifestEntry" not in result.stdout
        ):
            raise SystemExit(
                "fiscal wheel consumer did not reveal the expected public types"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
