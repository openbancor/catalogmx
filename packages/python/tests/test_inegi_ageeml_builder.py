"""Tests for the reproducible INEGI AGEEML release builder."""

from __future__ import annotations

import csv
import importlib.util
import io
import sqlite3
import sys
import zipfile
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "inegi" / "build_ageeml.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("ageeml_builder", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def source_header() -> list[str]:
    return [
        "MAPA",
        "Estatus",
        "CVE_ENT",
        "NOM_ENT",
        "NOM_ABR",
        "CVE_MUN",
        "NOM_MUN",
        "CVE_LOC",
        "NOM_LOC",
        "AMBITO",
        "LATITUD",
        "LONGITUD",
        "LAT_DECIMAL",
        "LON_DECIMAL",
        "ALTITUD",
        "CVE_CARTA",
        "POB_TOTAL",
        "POB_MASCULINA",
        "POB_FEMENINA",
        "TOTAL DE VIVIENDAS HABITADAS",
    ]


def source_rows() -> list[list[str]]:
    rows: list[list[str]] = []
    for state in range(1, 33):
        cve_ent = f"{state:02d}"
        cve_mun = "001"
        cve_loc = "0001"
        rows.append(
            [
                cve_ent + cve_mun + cve_loc,
                "",
                cve_ent,
                f"estado {state}",
                f"e{state}",
                cve_mun,
                f"municipio {state}",
                cve_loc,
                f"localidad {state}",
                "U",
                "20°00'00\"N",
                "100°00'00\"W",
                f"{20 + state / 100:.6f}",
                f"{-100 - state / 100:.6f}",
                "1000",
                "F14A01",
                "100",
                "48",
                "52",
                "30",
            ]
        )

    rows.append(
        [
            "CD0010001",
            "Baja",
            "CD",
            "chihuahua - durango",
            "CD",
            "001",
            "zona interestatal",
            "0001",
            "localidad interestatal",
            "R",
            "-",
            "-",
            "*",
            "*",
            "-",
            "-",
            "-",
            "-",
            "-",
            "-",
        ]
    )
    return rows


def write_zip(
    path: Path,
    rows: list[list[str]],
    *,
    header: list[str] | None = None,
    member_name: str = "AGEEML_20268123456_utf.csv",
) -> None:
    buffer = io.StringIO(newline="")
    writer = csv.writer(buffer)
    writer.writerow(header or source_header())
    writer.writerows(rows)

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(member_name, buffer.getvalue().encode("utf-8-sig"))


def test_builder_preserves_states_interstate_zones_and_stable_content_hash(
    tmp_path: Path,
):
    module = load_module()
    rows = source_rows()
    first_zip = tmp_path / "first.zip"
    second_zip = tmp_path / "second.zip"
    write_zip(first_zip, rows)
    write_zip(second_zip, list(reversed(rows)))

    first_db, first_manifest_path, first_manifest = module.build_from_source(
        first_zip,
        tmp_path / "first",
        source_metadata={"last_modified": "Wed, 26 Aug 2026 12:00:00 GMT"},
        min_records=len(rows),
    )
    _, _, second_manifest = module.build_from_source(
        second_zip,
        tmp_path / "second",
        source_metadata={"last_modified": "Wed, 26 Aug 2026 12:00:00 GMT"},
        min_records=len(rows),
    )

    assert first_db.exists()
    assert first_manifest_path.exists()
    assert first_manifest["dataset_id"] == "inegi.ageeml"
    assert first_manifest["dataset_version"] == "1"
    assert first_manifest["dataset"]["record_count"] == 33
    assert first_manifest["dataset"]["state_count"] == 32
    assert first_manifest["dataset"]["interstate_codes"] == ["CD"]
    assert first_manifest["dataset"]["inactive_count"] == 1
    assert first_manifest["dataset"]["content_sha256"] == second_manifest[
        "dataset"
    ]["content_sha256"]

    connection = sqlite3.connect(first_db)
    try:
        stored = connection.execute(
            "SELECT CVEGEO, CVE_ENT, LAT_DECIMAL, POB_TOTAL "
            "FROM localities WHERE CVE_ENT = 'CD'"
        ).fetchone()
    finally:
        connection.close()

    assert stored == ("CD0010001", "CD", None, None)


def test_builder_fails_closed_on_source_schema_drift(tmp_path: Path):
    module = load_module()
    source = tmp_path / "missing-column.zip"
    header = [value for value in source_header() if value != "CVE_LOC"]
    truncated_rows = []
    cve_loc_index = source_header().index("CVE_LOC")
    for row in source_rows():
        truncated_rows.append(row[:cve_loc_index] + row[cve_loc_index + 1 :])
    write_zip(source, truncated_rows, header=header)

    with pytest.raises(RuntimeError, match="missing required columns"):
        module.build_from_source(source, tmp_path / "output", min_records=32)


def test_builder_fails_closed_on_incomplete_state_coverage(tmp_path: Path):
    module = load_module()
    source = tmp_path / "missing-state.zip"
    rows = [row for row in source_rows() if row[2] != "32"]
    write_zip(source, rows)

    with pytest.raises(RuntimeError, match="unexpected state coverage"):
        module.build_from_source(
            source,
            tmp_path / "output",
            min_records=len(rows),
        )


def test_builder_requires_exactly_one_utf_ageeml_csv(tmp_path: Path):
    module = load_module()
    source = tmp_path / "ambiguous.zip"
    with zipfile.ZipFile(source, "w") as archive:
        archive.writestr("AGEEML_one_utf.csv", "x\n")
        archive.writestr("AGEEML_two_utf.csv", "x\n")

    with pytest.raises(RuntimeError, match="expected exactly one AGEEML"):
        module.build_from_source(source, tmp_path / "output", min_records=1)
