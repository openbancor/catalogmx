"""Tests for the canonical SAT Nómina 1.2 release-artifact builder."""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "sat" / "build_nomina_12.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("nomina_12_builder", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def make_source(
    module: ModuleType,
    path: Path,
    *,
    extra_nomina_table: bool = False,
    omit_table: str | None = None,
) -> None:
    connection = sqlite3.connect(path)
    try:
        for index, table in enumerate(module.EXPECTED_TABLES):
            if table == omit_table:
                continue
            connection.execute(
                f'CREATE TABLE "{table}" (id TEXT PRIMARY KEY, texto TEXT NOT NULL)'
            )
            connection.execute(
                f'INSERT INTO "{table}" VALUES (?, ?)',
                (f"{index:03d}", f"value-{index:03d}"),
            )

        for table in module.KNOWN_AUXILIARY_TABLES:
            connection.execute(
                f'CREATE TABLE "{table}" (id TEXT PRIMARY KEY, texto TEXT NOT NULL)'
            )
            connection.execute(
                f'INSERT INTO "{table}" VALUES (?, ?)',
                ("aux", table),
            )

        connection.execute("CREATE TABLE cfdi_40_test (id TEXT PRIMARY KEY)")
        connection.execute("INSERT INTO cfdi_40_test VALUES ('unrelated')")
        if extra_nomina_table:
            connection.execute("CREATE TABLE nomina_future_catalog (id TEXT PRIMARY KEY)")
        connection.commit()
    finally:
        connection.close()


def test_builder_extracts_exact_13_catnomina_tables(tmp_path: Path):
    module = load_module()
    source = tmp_path / "catalogs.db"
    make_source(module, source)

    first_db, first_manifest_path, first_manifest = module.build_from_source(
        source,
        tmp_path / "first",
        {"tag": "v-test", "asset_sha256": "abc123"},
    )
    _, _, second_manifest = module.build_from_source(
        source,
        tmp_path / "second",
        {"tag": "v-test", "asset_sha256": "abc123"},
    )

    assert first_db.exists()
    assert first_manifest_path.exists()
    assert first_manifest["dataset_id"] == "sat.nomina_1_2"
    assert first_manifest["dataset_version"] == "1.2-revision-e"
    assert first_manifest["dataset"]["table_count"] == 13
    assert first_manifest["dataset"]["row_count"] == 13
    assert first_manifest["dataset"]["content_sha256"] == second_manifest[
        "dataset"
    ]["content_sha256"]
    assert first_manifest["ingestion"]["release"] == "v-test"
    assert first_manifest["excluded_auxiliary_tables"] == list(
        module.KNOWN_AUXILIARY_TABLES
    )

    output = sqlite3.connect(first_db)
    try:
        tables = {
            row[0]
            for row in output.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
    finally:
        output.close()

    assert set(module.EXPECTED_TABLES) <= tables
    assert set(module.KNOWN_AUXILIARY_TABLES).isdisjoint(tables)
    assert "cfdi_40_test" not in tables


def test_builder_fails_closed_when_nomina_table_family_changes(tmp_path: Path):
    module = load_module()
    source = tmp_path / "catalogs.db"
    make_source(module, source, extra_nomina_table=True)

    with pytest.raises(RuntimeError, match="unexpected Nómina 1.2 schema"):
        module.build_from_source(source, tmp_path / "output", {"tag": "v-future"})


def test_builder_fails_closed_when_expected_catalog_is_missing(tmp_path: Path):
    module = load_module()
    source = tmp_path / "catalogs.db"
    missing = module.EXPECTED_TABLES[0]
    make_source(module, source, omit_table=missing)

    with pytest.raises(RuntimeError, match="unexpected Nómina 1.2 schema"):
        module.build_from_source(source, tmp_path / "output", {"tag": "v-missing"})
