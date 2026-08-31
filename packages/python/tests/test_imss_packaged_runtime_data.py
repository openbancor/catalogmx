"""Contract tests for IMSS data shipped inside the Python distribution."""

from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_packaged_imss_tables_match_canonical_shared_data() -> None:
    """The package-local runtime copy must exactly match its canonical source."""
    packaged = files("catalogmx.data").joinpath("imss-tables.json").read_bytes()
    canonical = (REPO_ROOT / "packages/shared-data/imss-tables.json").read_bytes()

    assert packaged == canonical
    assert json.loads(packaged)["uma"]["2026"]["diaria"] > 0


def test_packaged_imss_catalogs_match_canonical_shared_data() -> None:
    """IMSS catalog APIs must not depend on the repository checkout either."""
    packaged = files("catalogmx.data").joinpath("imss-catalogs.json").read_bytes()
    canonical = (REPO_ROOT / "packages/shared-data/imss-catalogs.json").read_bytes()

    assert packaged == canonical
    assert json.loads(packaged)["tipos_trabajador"]
