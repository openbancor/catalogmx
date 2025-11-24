"""
Build a combined mexico.sqlite3 from existing SQLite sources.

Tables produced:
- codigos_postales_completo: merged from packages/shared-data/sqlite/sepomex.db
- clave_prod_serv: mapped from packages/shared-data/sqlite/clave_prod_serv.db
- localidades: empty placeholder (create schema so webapp queries do not fail)

This is a lightweight builder for demo/Pages; it does not attempt to be the
full production dataset.
"""

from __future__ import annotations

import shutil
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SQLITE_DIR = ROOT / "packages" / "shared-data" / "sqlite"
OUTPUT_DB = SQLITE_DIR / "mexico.sqlite3"


def ensure_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def copy_codigos_postales(conn: sqlite3.Connection, src_db: Path) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS codigos_postales_completo (
            cp TEXT,
            asentamiento TEXT,
            tipo_asentamiento TEXT,
            municipio TEXT,
            estado TEXT,
            ciudad TEXT,
            cp_oficina TEXT,
            codigo_estado TEXT,
            codigo_municipio TEXT,
            zona TEXT
        )
        """
    )
    if not src_db.exists():
        return
    src = sqlite3.connect(src_db)
    try:
        cur = src.execute("SELECT cp, asentamiento, municipio, estado FROM codigos_postales")
        rows = cur.fetchall()
        conn.executemany(
            """
            INSERT INTO codigos_postales_completo
            (cp, asentamiento, tipo_asentamiento, municipio, estado, ciudad, cp_oficina, codigo_estado, codigo_municipio, zona)
            VALUES (?, ?, NULL, ?, ?, NULL, NULL, NULL, NULL, NULL)
            """,
            rows,
        )
    finally:
        src.close()


def copy_clave_prod_serv(conn: sqlite3.Connection, src_db: Path) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS clave_prod_serv (
            id TEXT PRIMARY KEY,
            descripcion TEXT,
            incluirIVATrasladado TEXT,
            incluirIEPSTrasladado TEXT,
            complementoQueDebeIncluir TEXT,
            fechaInicioVigencia TEXT,
            fechaFinVigencia TEXT,
            estimuloFranjaFronteriza TEXT,
            palabrasSimilares TEXT
        )
        """
    )
    if not src_db.exists():
        return
    src = sqlite3.connect(src_db)
    try:
        cur = src.execute(
            "SELECT clave, descripcion, incluye_iva, incluye_ieps, complemento, palabras_similares, fecha_inicio_vigencia, fecha_fin_vigencia FROM clave_prod_serv"
        )
        rows = cur.fetchall()
        mapped = [
            (
                clave,
                descripcion,
                "Sí" if iva else "No",
                "Sí" if ieps else "No",
                complemento or "",
                fecha_ini or "",
                fecha_fin or "",
                "",
                palabras or "",
            )
            for clave, descripcion, iva, ieps, complemento, palabras, fecha_ini, fecha_fin in rows
        ]
        conn.executemany(
            """
            INSERT INTO clave_prod_serv
            (id, descripcion, incluirIVATrasladado, incluirIEPSTrasladado, complementoQueDebeIncluir,
             fechaInicioVigencia, fechaFinVigencia, estimuloFranjaFronteriza, palabrasSimilares)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            mapped,
        )
    finally:
        src.close()


def create_localidades_placeholder(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS localidades (
            cvegeo TEXT,
            cve_entidad TEXT,
            cve_municipio TEXT,
            cve_localidad TEXT,
            nom_localidad TEXT,
            nom_municipio TEXT,
            nom_entidad TEXT,
            latitud REAL,
            longitud REAL,
            altitud REAL,
            poblacion_total INTEGER
        )
        """
    )


def build():
    ensure_dir(OUTPUT_DB)
    if OUTPUT_DB.exists():
        OUTPUT_DB.unlink()

    conn = sqlite3.connect(OUTPUT_DB)
    try:
        copy_codigos_postales(conn, SQLITE_DIR / "sepomex.db")
        copy_clave_prod_serv(conn, SQLITE_DIR / "clave_prod_serv.db")
        create_localidades_placeholder(conn)
        conn.commit()
    finally:
        conn.close()
    print(f"mexico.sqlite3 built at {OUTPUT_DB}")


if __name__ == "__main__":
    build()
