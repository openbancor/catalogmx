"""Tests for the Banxico dynamic release publication manifest."""

from __future__ import annotations

import importlib.util
import sqlite3
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "banxico" / "build_dynamic_manifest.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("banxico_dynamic_manifest", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def create_database(path: Path) -> None:
    db = sqlite3.connect(path)
    db.executescript(
        """
        CREATE TABLE _metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        INSERT INTO _metadata VALUES ('version', '2026-08-27');
        INSERT INTO _metadata VALUES ('source', 'banxico');
        INSERT INTO _metadata VALUES ('schema_version', '1.0');

        CREATE TABLE udis (
            fecha TEXT PRIMARY KEY, valor REAL, anio INTEGER, mes INTEGER,
            tipo TEXT, moneda TEXT, notas TEXT, updated_at TEXT
        );
        CREATE TABLE tipo_cambio (
            fecha TEXT, fuente TEXT, tipo_cambio REAL, anio INTEGER, mes INTEGER,
            moneda_origen TEXT, moneda_destino TEXT, updated_at TEXT,
            PRIMARY KEY (fecha, fuente)
        );
        CREATE TABLE tiie (
            fecha TEXT, plazo INTEGER, tasa REAL, anio INTEGER, mes INTEGER,
            updated_at TEXT, PRIMARY KEY (fecha, plazo)
        );
        CREATE TABLE cetes (
            fecha TEXT, plazo INTEGER, tasa REAL, anio INTEGER, mes INTEGER,
            updated_at TEXT, PRIMARY KEY (fecha, plazo)
        );
        CREATE TABLE inflacion (
            fecha TEXT PRIMARY KEY, anio INTEGER, mes INTEGER, inpc REAL,
            inflacion_mensual REAL, inflacion_anual REAL, updated_at TEXT
        );
        CREATE TABLE salarios_minimos (
            fecha TEXT, zona TEXT, salario_diario REAL, anio INTEGER, mes INTEGER,
            updated_at TEXT, PRIMARY KEY (fecha, zona)
        );

        INSERT INTO udis VALUES
            ('2026-08-27', 8.1, 2026, 8, 'diario', 'MXN', NULL, 'volatile-1');
        INSERT INTO tipo_cambio VALUES
            ('2026-08-27', 'FIX', 18.5, 2026, 8, 'USD', 'MXN', 'volatile-1');
        INSERT INTO tiie VALUES
            ('2026-08-27', 28, 8.0, 2026, 8, 'volatile-1');
        INSERT INTO cetes VALUES
            ('2026-08-27', 28, 7.5, 2026, 8, 'volatile-1');
        INSERT INTO inflacion VALUES
            ('2026-08-01', 2026, 8, 140.0, 0.3, 4.1, 'volatile-1');
        INSERT INTO salarios_minimos VALUES
            ('2026-01-01', 'general', 300.0, 2026, 1, 'volatile-1');
        """
    )
    db.commit()
    db.close()


def test_manifest_matches_dataset_resolver_file_contract(tmp_path: Path):
    module = load_module()
    database = tmp_path / module.OUTPUT_NAME
    create_database(database)

    validation = module.validate_database(
        database, minimum_counts={name: 1 for name in module.TABLE_COLUMNS}
    )
    manifest = module.build_manifest(database)

    assert validation["data_version"] == "2026-08-27"
    assert manifest["schema_version"] == 1
    assert manifest["dataset_id"] == "banxico.sie_dynamic"
    assert manifest["dataset_version"] == "1"
    assert manifest["data_version"] == "2026-08-27"
    assert manifest["dataset"]["file"] == "mexico_dynamic.sqlite3"
    assert manifest["dataset"]["format"] == "file"
    assert manifest["dataset"]["mount_path"] == "dynamic"
    assert len(manifest["dataset"]["file_sha256"]) == 64
    assert len(manifest["dataset"]["content_sha256"]) == 64
    assert manifest["dataset"]["row_count"] == 6


def test_semantic_hash_ignores_volatile_updated_at(tmp_path: Path):
    module = load_module()
    database = tmp_path / module.OUTPUT_NAME
    create_database(database)

    db = sqlite3.connect(database)
    before = module.semantic_hash(db)
    db.execute("UPDATE udis SET updated_at = 'volatile-2'")
    db.commit()
    after_timestamp = module.semantic_hash(db)
    db.execute("UPDATE udis SET valor = 8.2")
    db.commit()
    after_value = module.semantic_hash(db)
    db.close()

    assert after_timestamp == before
    assert after_value != before


def test_validation_fails_closed_on_missing_table(tmp_path: Path):
    module = load_module()
    database = tmp_path / module.OUTPUT_NAME
    create_database(database)
    db = sqlite3.connect(database)
    db.execute("DROP TABLE tiie")
    db.commit()
    db.close()

    with pytest.raises(RuntimeError, match="missing tables: tiie"):
        module.validate_database(database, minimum_counts={})


def test_validation_rejects_implausibly_small_table(tmp_path: Path):
    module = load_module()
    database = tmp_path / module.OUTPUT_NAME
    create_database(database)

    with pytest.raises(RuntimeError, match="udis looks incomplete"):
        module.validate_database(database, minimum_counts={"udis": 2})


def test_validation_requires_banxico_source_metadata(tmp_path: Path):
    module = load_module()
    database = tmp_path / module.OUTPUT_NAME
    create_database(database)
    db = sqlite3.connect(database)
    db.execute("UPDATE _metadata SET value = 'unknown' WHERE key = 'source'")
    db.commit()
    db.close()

    with pytest.raises(RuntimeError, match="source is not banxico"):
        module.validate_database(database, minimum_counts={})
