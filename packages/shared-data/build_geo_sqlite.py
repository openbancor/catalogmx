#!/usr/bin/env python3
"""
Build geographic SQLite database for Portal Geografico de Mexico.

Creates tables for:
- geo_estados: 32 Mexican states with INEGI codes
- geo_municipios: 2,478 municipalities with population data
- geo_zonas_metropolitanas: 92 metropolitan zones (CONAPO 2020)
- geo_municipio_zm: Municipality-to-zone relationship table

Data sources:
- INEGI: states.json, municipios_completo.json
- CONAPO: municipios_tipologia.csv (zonas metropolitanas 2020)
"""

from __future__ import annotations

import csv
import json
import re
import sqlite3
from pathlib import Path
from typing import Any

DATA_ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT = DATA_ROOT / "sqlite" / "geo_mexico.db"

# Source files
STATES_JSON = DATA_ROOT / "inegi" / "states.json"
MUNICIPIOS_JSON = DATA_ROOT / "inegi" / "municipios_completo.json"
ZONAS_CSV = DATA_ROOT / "conapo" / "municipios_tipologia.csv"


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    import unicodedata

    # Normalize unicode characters
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    # Convert to lowercase and replace spaces/special chars with hyphens
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    return text


def create_database(path: Path) -> sqlite3.Connection:
    """Create a new SQLite database with optimized settings."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    # Also remove any WAL files from previous runs
    for ext in ["-wal", "-shm"]:
        wal_path = path.with_suffix(path.suffix + ext)
        if wal_path.exists():
            wal_path.unlink()
    conn = sqlite3.connect(str(path))
    # Use DELETE mode from the start for browser compatibility
    # WAL mode can cause issues when VACUUM is run
    pragmas = [
        "PRAGMA journal_mode=DELETE;",
        "PRAGMA synchronous=OFF;",
        "PRAGMA foreign_keys=ON;",
        "PRAGMA temp_store=MEMORY;",
    ]
    for pragma in pragmas:
        conn.execute(pragma)
    return conn


def create_tables(conn: sqlite3.Connection) -> None:
    """Create geographic tables."""
    conn.executescript(
        """
        -- Estados (32 states + extranjero)
        CREATE TABLE geo_estados (
            cve_inegi TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            nombre_slug TEXT NOT NULL,
            abreviatura TEXT NOT NULL,
            codigo_rfc TEXT NOT NULL
        );

        -- Municipios (2,478 municipalities)
        CREATE TABLE geo_municipios (
            cve_inegi TEXT PRIMARY KEY,
            cve_entidad TEXT NOT NULL,
            cve_municipio TEXT NOT NULL,
            nombre TEXT NOT NULL,
            nombre_slug TEXT NOT NULL,
            estado TEXT NOT NULL,
            estado_slug TEXT NOT NULL,
            poblacion_total INTEGER,
            poblacion_masculina INTEGER,
            poblacion_femenina INTEGER,
            viviendas_habitadas INTEGER,
            cabecera TEXT,
            FOREIGN KEY (cve_entidad) REFERENCES geo_estados(cve_inegi)
        );

        -- Zonas Metropolitanas (92 zones - CONAPO 2020)
        CREATE TABLE geo_zonas_metropolitanas (
            zm_id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            nombre_slug TEXT NOT NULL,
            tipo TEXT NOT NULL,
            num_municipios INTEGER DEFAULT 0
        );

        -- Relacion Municipio-ZM (many-to-many)
        CREATE TABLE geo_municipio_zm (
            cve_inegi TEXT NOT NULL,
            zm_id TEXT NOT NULL,
            es_central INTEGER DEFAULT 0,
            es_exterior INTEGER DEFAULT 0,
            PRIMARY KEY (cve_inegi, zm_id),
            FOREIGN KEY (cve_inegi) REFERENCES geo_municipios(cve_inegi),
            FOREIGN KEY (zm_id) REFERENCES geo_zonas_metropolitanas(zm_id)
        );

        -- Indexes for common queries
        CREATE INDEX idx_municipios_estado ON geo_municipios(cve_entidad);
        CREATE INDEX idx_municipios_nombre ON geo_municipios(nombre);
        CREATE INDEX idx_municipios_slug ON geo_municipios(nombre_slug);
        CREATE INDEX idx_estados_slug ON geo_estados(nombre_slug);
        CREATE INDEX idx_zm_nombre ON geo_zonas_metropolitanas(nombre);
        CREATE INDEX idx_zm_slug ON geo_zonas_metropolitanas(nombre_slug);
        CREATE INDEX idx_mzm_zm ON geo_municipio_zm(zm_id);
        """
    )
    conn.commit()


def import_estados(conn: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    """Import states from INEGI JSON."""
    if not STATES_JSON.exists():
        print(f"[geo] WARNING: {STATES_JSON} not found")
        return {}

    with open(STATES_JSON, encoding="utf-8") as f:
        states = json.load(f)

    states_map: dict[str, dict[str, Any]] = {}
    rows = []

    for state in states:
        cve = state["clave_inegi"]
        # Skip extranjero (99)
        if cve == "99":
            continue

        nombre = state["name"].title()
        # Special cases for proper title case
        nombre = nombre.replace("De ", "de ").replace(" Y ", " y ")
        if nombre.startswith("de "):
            nombre = "D" + nombre[1:]

        row = {
            "cve_inegi": cve,
            "nombre": nombre,
            "nombre_slug": slugify(nombre),
            "abreviatura": state["abbreviation"],
            "codigo_rfc": state["code"],
        }
        rows.append(row)
        states_map[cve] = row

    conn.executemany(
        """
        INSERT INTO geo_estados (cve_inegi, nombre, nombre_slug, abreviatura, codigo_rfc)
        VALUES (:cve_inegi, :nombre, :nombre_slug, :abreviatura, :codigo_rfc)
        """,
        rows,
    )
    conn.commit()
    print(f"[geo] Imported {len(rows)} estados")
    return states_map


def import_municipios(
    conn: sqlite3.Connection, states_map: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    """Import municipalities from INEGI JSON."""
    if not MUNICIPIOS_JSON.exists():
        print(f"[geo] WARNING: {MUNICIPIOS_JSON} not found")
        return {}

    with open(MUNICIPIOS_JSON, encoding="utf-8") as f:
        municipios = json.load(f)

    muni_map: dict[str, dict[str, Any]] = {}
    rows = []

    for muni in municipios:
        cve_entidad = muni["cve_entidad"]
        if cve_entidad not in states_map:
            continue

        estado = states_map[cve_entidad]
        cve_inegi = muni["cve_completa"]

        row = {
            "cve_inegi": cve_inegi,
            "cve_entidad": cve_entidad,
            "cve_municipio": muni["cve_municipio"],
            "nombre": muni["nom_municipio"],
            "nombre_slug": slugify(muni["nom_municipio"]),
            "estado": estado["nombre"],
            "estado_slug": estado["nombre_slug"],
            "poblacion_total": muni.get("poblacion_total"),
            "poblacion_masculina": muni.get("poblacion_masculina"),
            "poblacion_femenina": muni.get("poblacion_femenina"),
            "viviendas_habitadas": muni.get("viviendas_habitadas"),
            "cabecera": muni.get("nom_cabecera"),
        }
        rows.append(row)
        muni_map[cve_inegi] = row

    conn.executemany(
        """
        INSERT INTO geo_municipios (
            cve_inegi, cve_entidad, cve_municipio, nombre, nombre_slug,
            estado, estado_slug, poblacion_total, poblacion_masculina,
            poblacion_femenina, viviendas_habitadas, cabecera
        ) VALUES (
            :cve_inegi, :cve_entidad, :cve_municipio, :nombre, :nombre_slug,
            :estado, :estado_slug, :poblacion_total, :poblacion_masculina,
            :poblacion_femenina, :viviendas_habitadas, :cabecera
        )
        """,
        rows,
    )
    conn.commit()
    print(f"[geo] Imported {len(rows)} municipios")
    return muni_map


def import_zonas_metropolitanas(conn: sqlite3.Connection) -> None:
    """Import metropolitan zones from CONAPO CSV."""
    if not ZONAS_CSV.exists():
        print(f"[geo] WARNING: {ZONAS_CSV} not found")
        return

    zonas: dict[str, dict[str, Any]] = {}
    municipio_zm_rows: list[dict[str, Any]] = []

    with open(ZONAS_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            zm_id = row["clave_metropoli"]
            zm_nombre = row["nombre"]
            zm_tipo = row["tipo"]

            # Build zona if not exists
            if zm_id not in zonas:
                zonas[zm_id] = {
                    "zm_id": zm_id,
                    "nombre": zm_nombre,
                    "nombre_slug": slugify(zm_nombre),
                    "tipo": zm_tipo,
                    "num_municipios": 0,
                }

            zonas[zm_id]["num_municipios"] += 1

            # Build municipio-zm relationship
            cve_entidad = row["clave_entidad"].zfill(2)
            cve_municipio = row["clave_municipio"].zfill(3)
            cve_inegi = cve_entidad + cve_municipio

            # Determine if central or exterior
            es_central = (
                row.get("centrales_conurbacion_fisica", "").lower() == "true"
                or row.get("centrales_integracion_funcional", "").lower() == "true"
                or row.get("centrales_capital_200khab", "").lower() == "true"
                or row.get("centrales_0100khab", "").lower() == "true"
                or row.get("centrales_50khab", "").lower() == "true"
            )
            es_exterior = (
                row.get("exteriores_integracion_funcional", "").lower() == "true"
                or row.get("exteriores_continuidad_geografica", "").lower() == "true"
            )

            municipio_zm_rows.append(
                {
                    "cve_inegi": cve_inegi,
                    "zm_id": zm_id,
                    "es_central": 1 if es_central else 0,
                    "es_exterior": 1 if es_exterior else 0,
                }
            )

    # Insert zonas metropolitanas
    conn.executemany(
        """
        INSERT INTO geo_zonas_metropolitanas (zm_id, nombre, nombre_slug, tipo, num_municipios)
        VALUES (:zm_id, :nombre, :nombre_slug, :tipo, :num_municipios)
        """,
        list(zonas.values()),
    )

    # Insert municipio-zm relationships
    conn.executemany(
        """
        INSERT OR IGNORE INTO geo_municipio_zm (cve_inegi, zm_id, es_central, es_exterior)
        VALUES (:cve_inegi, :zm_id, :es_central, :es_exterior)
        """,
        municipio_zm_rows,
    )

    conn.commit()
    print(f"[geo] Imported {len(zonas)} zonas metropolitanas")
    print(f"[geo] Imported {len(municipio_zm_rows)} municipio-zona relationships")


def create_views(conn: sqlite3.Connection) -> None:
    """Create useful views for common queries."""
    conn.executescript(
        """
        -- View: Municipios with their zona metropolitana (if any)
        CREATE VIEW v_municipio_completo AS
        SELECT
            m.*,
            zm.zm_id,
            zm.nombre AS zm_nombre,
            zm.nombre_slug AS zm_slug,
            zm.tipo AS zm_tipo,
            mzm.es_central,
            mzm.es_exterior
        FROM geo_municipios m
        LEFT JOIN geo_municipio_zm mzm ON m.cve_inegi = mzm.cve_inegi
        LEFT JOIN geo_zonas_metropolitanas zm ON mzm.zm_id = zm.zm_id;

        -- View: Estados with municipality counts and population
        CREATE VIEW v_estado_stats AS
        SELECT
            e.cve_inegi,
            e.nombre,
            e.nombre_slug,
            e.abreviatura,
            COUNT(m.cve_inegi) AS num_municipios,
            SUM(m.poblacion_total) AS poblacion_total,
            SUM(m.viviendas_habitadas) AS viviendas_habitadas
        FROM geo_estados e
        LEFT JOIN geo_municipios m ON e.cve_inegi = m.cve_entidad
        GROUP BY e.cve_inegi;

        -- View: Zonas metropolitanas with states list
        CREATE VIEW v_zona_metropolitana_completa AS
        SELECT
            zm.*,
            GROUP_CONCAT(DISTINCT m.estado) AS estados,
            SUM(m.poblacion_total) AS poblacion_total
        FROM geo_zonas_metropolitanas zm
        JOIN geo_municipio_zm mzm ON zm.zm_id = mzm.zm_id
        JOIN geo_municipios m ON mzm.cve_inegi = m.cve_inegi
        GROUP BY zm.zm_id;
        """
    )
    conn.commit()
    print("[geo] Created views")


def finalize_database(conn: sqlite3.Connection) -> None:
    """Finalize database for production use."""
    conn.commit()  # Ensure all data is committed
    conn.execute("ANALYZE;")
    conn.commit()
    # Note: VACUUM can corrupt database in some SQLite versions, skip it
    print("[geo] Database finalized")


def main() -> None:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output SQLite file (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    output_path: Path = args.output
    if not output_path.is_absolute():
        output_path = output_path.resolve()

    print(f"[geo] Building geographic database: {output_path}")
    conn = create_database(output_path)

    try:
        create_tables(conn)
        states_map = import_estados(conn)
        import_municipios(conn, states_map)
        import_zonas_metropolitanas(conn)
        create_views(conn)
        finalize_database(conn)
        print(f"[geo] Database ready: {output_path}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
