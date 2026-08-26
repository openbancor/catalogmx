"""Tests for the SAT CFDI 4.0 release-artifact builder."""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "sat" / "build_cfdi_40.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("cfdi_40_builder", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def make_source(module: ModuleType, path: Path, *, extra_cfdi_table: bool = False) -> None:
    connection = sqlite3.connect(path)
    try:
        for index, table in enumerate(module.EXPECTED_TABLES):
            connection.execute(
                f'CREATE TABLE "{table}" (id TEXT PRIMARY KEY, value TEXT NOT NULL)'
            )
            connection.execute(
                f'INSERT INTO "{table}" VALUES (?, ?)',
                (f"{index:02d}", f"value-{index:02d}"),
            )
        connection.execute("CREATE TABLE ccp_31_test (id TEXT PRIMARY KEY)")
        connection.execute("INSERT INTO ccp_31_test VALUES ('unrelated')")
        if extra_cfdi_table:
            connection.execute("CREATE TABLE cfdi_40_future_catalog (id TEXT PRIMARY KEY)")
        connection.commit()
    finally:
        connection.close()


def test_builder_extracts_exact_cfdi_40_subset_with_stable_hash(tmp_path: Path):
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
    assert first_manifest["dataset_id"] == "sat.cfdi_4"
    assert first_manifest["dataset_version"] == "4.0"
    assert first_manifest["dataset"]["table_count"] == 25
    assert first_manifest["dataset"]["row_count"] == 25
    assert first_manifest["dataset"]["content_sha256"] == second_manifest[
        "dataset"
    ]["content_sha256"]
    assert first_manifest["ingestion"]["release"] == "v-test"

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
    assert "ccp_31_test" not in tables


def test_builder_fails_closed_when_cfdi_40_schema_changes(tmp_path: Path):
    module = load_module()
    source = tmp_path / "catalogs.db"
    make_source(module, source, extra_cfdi_table=True)

    with pytest.raises(RuntimeError, match="unexpected CFDI 4.0 schema"):
        module.build_from_source(source, tmp_path / "output", {"tag": "v-future"})
