"""Tests for Nómina 1.2 JSON compatibility views."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
import sys
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "sat" / "build_nomina_12.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("nomina_12_compat_builder", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def make_canonical_database(module: ModuleType, path: Path) -> None:
    connection = sqlite3.connect(path)
    try:
        for table in module.EXPECTED_TABLES:
            if table == "nomina_bancos":
                connection.execute(
                    f'CREATE TABLE "{table}" ('
                    "id TEXT PRIMARY KEY, texto TEXT NOT NULL, "
                    "razon_social TEXT NOT NULL, vigencia_desde TEXT NOT NULL, "
                    "vigencia_hasta TEXT NOT NULL)"
                )
                connection.execute(
                    f'INSERT INTO "{table}" VALUES (?, ?, ?, ?, ?)',
                    ("002", "Banamex", "Banco Nacional de México, S.A.", "2017-01-01", ""),
                )
            elif table in {
                "nomina_tipos_deducciones",
                "nomina_tipos_otros_pagos",
                "nomina_tipos_percepciones",
            }:
                connection.execute(
                    f'CREATE TABLE "{table}" ('
                    "id TEXT PRIMARY KEY, texto TEXT NOT NULL, "
                    "vigencia_desde TEXT NOT NULL, vigencia_hasta TEXT NOT NULL)"
                )
                connection.execute(
                    f'INSERT INTO "{table}" VALUES (?, ?, ?, ?)',
                    ("001", f"Description for {table}", "2026-01-01", ""),
                )
            else:
                connection.execute(
                    f'CREATE TABLE "{table}" (id TEXT PRIMARY KEY, texto TEXT NOT NULL)'
                )
                code = "10" if table == "nomina_tipos_contratos" else "01"
                connection.execute(
                    f'INSERT INTO "{table}" VALUES (?, ?)',
                    (code, f"Description for {table}"),
                )
        connection.commit()
    finally:
        connection.close()


def test_renderer_writes_exact_13_views_with_stable_aliases(tmp_path: Path):
    module = load_module()
    database = tmp_path / "sat_nomina_12.sqlite3"
    output_dir = tmp_path / "views"
    make_canonical_database(module, database)

    # Non-SAT convenience metadata must survive a canonical refresh.
    output_dir.mkdir()
    (output_dir / "periodicidad_pago.json").write_text(
        json.dumps([{"code": "01", "days": 1}]), encoding="utf-8"
    )
    (output_dir / "riesgo_puesto.json").write_text(
        json.dumps(
            [
                {
                    "code": "01",
                    "prima_minima": 0.5,
                    "prima_media": 0.54355,
                    "prima_maxima": 0.625,
                }
            ]
        ),
        encoding="utf-8",
    )

    counts = module.render_compatibility_views(database, output_dir)

    assert set(counts) == set(module.COMPATIBILITY_VIEWS.values())
    assert len(counts) == 13
    assert {path.name for path in output_dir.glob("*.json")} == set(
        module.COMPATIBILITY_VIEWS.values()
    )

    contrato = json.loads((output_dir / "tipo_contrato.json").read_text(encoding="utf-8"))
    assert contrato == [
        {
            "code": "10",
            "description": "Description for nomina_tipos_contratos",
            "descripcion": "Description for nomina_tipos_contratos",
        }
    ]

    banco = json.loads((output_dir / "banco.json").read_text(encoding="utf-8"))[0]
    assert banco["name"] == "Banamex"
    assert banco["full_name"] == "Banco Nacional de México, S.A."
    assert banco["razon_social"] == banco["full_name"]
    assert banco["valid_from"] == "2017-01-01"
    assert banco["valid_to"] is None

    periodicidad = json.loads(
        (output_dir / "periodicidad_pago.json").read_text(encoding="utf-8")
    )[0]
    assert periodicidad["days"] == 1
    assert periodicidad["description"] == periodicidad["descripcion"]

    riesgo = json.loads((output_dir / "riesgo_puesto.json").read_text(encoding="utf-8"))[0]
    assert riesgo["prima_media"] == 0.54355

    deduccion = json.loads(
        (output_dir / "tipo_deduccion.json").read_text(encoding="utf-8")
    )[0]
    assert deduccion["valid_from"] == "2026-01-01"
    assert deduccion["valid_to"] is None


def test_renderer_removes_stale_rows_instead_of_merging_sat_data(tmp_path: Path):
    module = load_module()
    database = tmp_path / "sat_nomina_12.sqlite3"
    output_dir = tmp_path / "views"
    make_canonical_database(module, database)
    output_dir.mkdir()
    (output_dir / "tipo_contrato.json").write_text(
        json.dumps(
            [
                {"code": "01", "description": "stale"},
                {"code": "99", "description": "stale"},
            ]
        ),
        encoding="utf-8",
    )

    module.render_compatibility_views(database, output_dir)

    contrato = json.loads((output_dir / "tipo_contrato.json").read_text(encoding="utf-8"))
    assert [item["code"] for item in contrato] == ["10"]
