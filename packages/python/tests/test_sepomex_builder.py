"""Tests for the fail-closed SEPOMEX release-artifact builder."""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "sepomex" / "build_postal_codes.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("sepomex_builder", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def source_rows(module: ModuleType) -> list[tuple[str, ...]]:
    rows: list[tuple[str, ...]] = []
    for state in range(1, 33):
        state_code = f"{state:02d}"
        postal_code = f"{state * 1000:05d}"
        rows.append(
            (
                postal_code,
                f"Colonia Águila {state}",
                "Colonia",
                f"Municipio {state}",
                f"Estado {state}",
                f"Ciudad {state}",
                postal_code,
                state_code,
                postal_code,
                "",
                "09",
                "001",
                f"{state:04d}",
                "Urbano",
                "01",
            )
        )
    return rows


def write_source(
    module: ModuleType,
    path: Path,
    rows: list[tuple[str, ...]],
    *,
    header: tuple[str, ...] | None = None,
) -> None:
    lines = [
        "Catálogo Nacional de Códigos Postales - prueba",
        "|".join(header or module.EXPECTED_COLUMNS),
    ]
    lines.extend("|".join(row) for row in rows)
    path.write_bytes(("\r\n".join(lines) + "\r\n").encode("cp1252"))


def test_builder_preserves_full_source_schema_and_has_stable_semantic_hash(
    tmp_path: Path,
):
    module = load_module()
    rows = source_rows(module)
    first_source = tmp_path / "first.txt"
    second_source = tmp_path / "second.txt"
    write_source(module, first_source, rows)
    write_source(module, second_source, list(reversed(rows)))

    first_db, first_manifest_path, first_manifest = module.build_from_source(
        first_source,
        tmp_path / "first",
        source_metadata={"last_modified": "Mon, 24 Aug 2026 12:00:00 GMT"},
        min_records=len(rows),
    )
    _, _, second_manifest = module.build_from_source(
        second_source,
        tmp_path / "second",
        source_metadata={"last_modified": "Mon, 24 Aug 2026 12:00:00 GMT"},
        min_records=len(rows),
    )

    assert first_db.exists()
    assert first_manifest_path.exists()
    assert first_manifest["dataset_id"] == "sepomex.codigos_postales"
    assert first_manifest["dataset_version"] == "1"
    assert first_manifest["dataset"]["record_count"] == 32
    assert first_manifest["dataset"]["unique_postal_codes"] == 32
    assert first_manifest["dataset"]["state_count"] == 32
    assert first_manifest["dataset"]["columns"] == list(module.EXPECTED_COLUMNS)
    assert first_manifest["dataset"]["content_sha256"] == second_manifest[
        "dataset"
    ]["content_sha256"]
    assert first_manifest["ingestion"]["source_encoding"] == "cp1252"

    connection = sqlite3.connect(first_db)
    try:
        count = connection.execute("SELECT COUNT(*) FROM postal_codes").fetchone()[0]
        columns = [
            row[1] for row in connection.execute("PRAGMA table_info(postal_codes)")
        ]
    finally:
        connection.close()

    assert count == 32
    assert columns[1:] == list(module.EXPECTED_COLUMNS)


def test_builder_fails_closed_on_source_schema_drift(tmp_path: Path):
    module = load_module()
    source = tmp_path / "bad-schema.txt"
    bad_header = (*module.EXPECTED_COLUMNS[:-1], "unexpected_column")
    write_source(module, source, source_rows(module), header=bad_header)

    with pytest.raises(RuntimeError, match="expected 15-column TXT header"):
        module.build_from_source(
            source,
            tmp_path / "output",
            min_records=32,
        )


def test_builder_fails_closed_on_incomplete_national_coverage(tmp_path: Path):
    module = load_module()
    source = tmp_path / "missing-state.txt"
    rows = source_rows(module)[:-1]
    write_source(module, source, rows)

    with pytest.raises(RuntimeError, match="unexpected state coverage"):
        module.build_from_source(
            source,
            tmp_path / "output",
            min_records=len(rows),
        )
