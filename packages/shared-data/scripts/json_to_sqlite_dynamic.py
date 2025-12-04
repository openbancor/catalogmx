#!/usr/bin/env python3
"""
Migrar datos dinámicos de Banxico desde JSON a SQLite

Este script toma todos los archivos JSON de banxico/ y los migra a una
base de datos SQLite (mexico_dynamic.sqlite3) para permitir actualizaciones
independientes del código de la librería.

Uso:
    python scripts/json_to_sqlite_dynamic.py
    python scripts/json_to_sqlite_dynamic.py --output custom.db
"""

import json
import sqlite3
import sys
from pathlib import Path
from datetime import datetime


def load_json(file_path: Path) -> list[dict]:
    """
    Cargar JSON con manejo de ambos formatos (list y dict)

    :param file_path: Path al archivo JSON
    :return: Lista de diccionarios
    """
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    # Manejar ambos formatos: lista directa o dict con "items"
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # Intentar varias claves comunes
        for key in ["items", "data", "records"]:
            if key in data:
                return data[key]
        # Si es un dict con datos, retornar como lista de un elemento
        if any(k in data for k in ["fecha", "valor", "tipo_cambio"]):
            return [data]

    print(f"⚠️  Formato desconocido en {file_path}, retornando lista vacía")
    return []


def migrate_udis(db: sqlite3.Connection, data_dir: Path) -> int:
    """Migrar UDIs desde banxico/udis.json"""
    json_path = data_dir / "banxico" / "udis.json"
    if not json_path.exists():
        print(f"⚠️  No existe {json_path}, saltando UDIs")
        return 0

    print(f"📊 Migrando UDIs desde {json_path}...")
    udis = load_json(json_path)

    inserted = 0
    for record in udis:
        fecha = record.get("fecha")
        valor = record.get("valor")

        if not fecha or not valor:
            continue

        db.execute(
            """
            INSERT OR REPLACE INTO udis (fecha, valor, anio, mes, tipo, moneda, notas)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                fecha,
                valor,
                record.get("año") or record.get("anio"),
                record.get("mes"),
                record.get("tipo", "oficial_banxico"),
                record.get("moneda", "MXN"),
                record.get("notas"),
            ),
        )
        inserted += 1

    print(f"✅ Insertados {inserted:,} registros de UDIs")
    return inserted


def migrate_tipo_cambio(db: sqlite3.Connection, data_dir: Path) -> int:
    """Migrar tipo de cambio desde banxico/tipo_cambio_*.json"""
    total_inserted = 0

    # Tipo de cambio FIX (diario)
    json_path = data_dir / "banxico" / "tipo_cambio_usd.json"
    if json_path.exists():
        print(f"📊 Migrando Tipo de Cambio FIX desde {json_path}...")
        tipo_cambio = load_json(json_path)

        for record in tipo_cambio:
            fecha = record.get("fecha")
            tc = record.get("tipo_cambio")

            if not fecha or not tc:
                continue

            db.execute(
                """
                INSERT OR REPLACE INTO tipo_cambio
                (fecha, fuente, tipo_cambio, anio, mes, moneda_origen, moneda_destino)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    fecha,
                    "FIX",
                    tc,
                    record.get("año") or record.get("anio"),
                    record.get("mes"),
                    "USD",
                    "MXN",
                ),
            )
            total_inserted += 1

        print(f"✅ Insertados {total_inserted:,} registros de Tipo de Cambio FIX")

    # Tipo de cambio histórico
    json_path_hist = data_dir / "banxico" / "tipo_cambio_hist.json"
    if json_path_hist.exists():
        print(f"📊 Migrando Tipo de Cambio Histórico desde {json_path_hist}...")
        tipo_cambio_hist = load_json(json_path_hist)

        hist_inserted = 0
        for record in tipo_cambio_hist:
            fecha = record.get("fecha")
            tc = record.get("tipo_cambio")

            if not fecha or not tc:
                continue

            # Insertar solo si no existe ya un FIX para esa fecha
            db.execute(
                """
                INSERT OR IGNORE INTO tipo_cambio
                (fecha, fuente, tipo_cambio, anio, mes, moneda_origen, moneda_destino)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    fecha,
                    "historico",
                    tc,
                    record.get("año") or record.get("anio"),
                    record.get("mes"),
                    "USD",
                    "MXN",
                ),
            )
            hist_inserted += 1

        print(f"✅ Insertados {hist_inserted:,} registros de Tipo de Cambio Histórico")
        total_inserted += hist_inserted

    return total_inserted


def migrate_tiie(db: sqlite3.Connection, data_dir: Path) -> int:
    """Migrar TIIE desde banxico/tiie_*.json"""
    total_inserted = 0

    # TIIE 28 días
    json_path = data_dir / "banxico" / "tiie_28.json"
    if json_path.exists():
        print(f"📊 Migrando TIIE 28 días desde {json_path}...")
        tiie = load_json(json_path)

        for record in tiie:
            fecha = record.get("fecha")
            tasa = record.get("tasa") or record.get("valor")

            if not fecha or tasa is None:
                continue

            db.execute(
                """
                INSERT OR REPLACE INTO tiie (fecha, plazo, tasa, anio, mes)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    fecha,
                    28,
                    tasa,
                    record.get("año") or record.get("anio"),
                    record.get("mes"),
                ),
            )
            total_inserted += 1

        print(f"✅ Insertados {total_inserted:,} registros de TIIE 28")

    # TIIE 91 días (si existe)
    json_path_91 = data_dir / "banxico" / "tiie_91.json"
    if json_path_91.exists():
        print(f"📊 Migrando TIIE 91 días desde {json_path_91}...")
        tiie_91 = load_json(json_path_91)

        inserted_91 = 0
        for record in tiie_91:
            fecha = record.get("fecha")
            tasa = record.get("tasa") or record.get("valor")

            if not fecha or tasa is None:
                continue

            db.execute(
                """
                INSERT OR REPLACE INTO tiie (fecha, plazo, tasa, anio, mes)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    fecha,
                    91,
                    tasa,
                    record.get("año") or record.get("anio"),
                    record.get("mes"),
                ),
            )
            inserted_91 += 1

        print(f"✅ Insertados {inserted_91:,} registros de TIIE 91")
        total_inserted += inserted_91

    return total_inserted


def migrate_cetes(db: sqlite3.Connection, data_dir: Path) -> int:
    """Migrar CETES desde banxico/cetes_*.json"""
    total_inserted = 0

    # CETES 28 días
    json_path = data_dir / "banxico" / "cetes_28.json"
    if json_path.exists():
        print(f"📊 Migrando CETES 28 días desde {json_path}...")
        cetes = load_json(json_path)

        for record in cetes:
            fecha = record.get("fecha")
            tasa = record.get("tasa") or record.get("valor")

            if not fecha or tasa is None:
                continue

            db.execute(
                """
                INSERT OR REPLACE INTO cetes (fecha, plazo, tasa, anio, mes)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    fecha,
                    28,
                    tasa,
                    record.get("año") or record.get("anio"),
                    record.get("mes"),
                ),
            )
            total_inserted += 1

        print(f"✅ Insertados {total_inserted:,} registros de CETES 28")

    # CETES otros plazos (si existen)
    for plazo in [91, 182, 364]:
        json_path_plazo = data_dir / "banxico" / f"cetes_{plazo}.json"
        if json_path_plazo.exists():
            print(f"📊 Migrando CETES {plazo} días desde {json_path_plazo}...")
            cetes_plazo = load_json(json_path_plazo)

            inserted_plazo = 0
            for record in cetes_plazo:
                fecha = record.get("fecha")
                tasa = record.get("tasa") or record.get("valor")

                if not fecha or tasa is None:
                    continue

                db.execute(
                    """
                    INSERT OR REPLACE INTO cetes (fecha, plazo, tasa, anio, mes)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        fecha,
                        plazo,
                        tasa,
                        record.get("año") or record.get("anio"),
                        record.get("mes"),
                    ),
                )
                inserted_plazo += 1

            print(f"✅ Insertados {inserted_plazo:,} registros de CETES {plazo}")
            total_inserted += inserted_plazo

    return total_inserted


def migrate_inflacion(db: sqlite3.Connection, data_dir: Path) -> int:
    """Migrar inflación desde banxico/inflacion_*.json"""
    json_path = data_dir / "banxico" / "inflacion_anual.json"
    if not json_path.exists():
        print(f"⚠️  No existe {json_path}, saltando inflación")
        return 0

    print(f"📊 Migrando Inflación desde {json_path}...")
    inflacion = load_json(json_path)

    inserted = 0
    for record in inflacion:
        fecha = record.get("fecha")

        if not fecha:
            continue

        db.execute(
            """
            INSERT OR REPLACE INTO inflacion
            (fecha, anio, mes, inpc, inflacion_mensual, inflacion_anual)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                fecha,
                record.get("año") or record.get("anio"),
                record.get("mes"),
                record.get("inpc"),
                record.get("inflacion_mensual"),
                record.get("inflacion_anual") or record.get("valor"),
            ),
        )
        inserted += 1

    print(f"✅ Insertados {inserted:,} registros de Inflación")
    return inserted


def migrate_salarios_minimos(db: sqlite3.Connection, data_dir: Path) -> int:
    """Migrar salarios mínimos desde banxico/salarios_minimos.json"""
    json_path = data_dir / "banxico" / "salarios_minimos.json"
    if not json_path.exists():
        print(f"⚠️  No existe {json_path}, saltando salarios mínimos")
        return 0

    print(f"📊 Migrando Salarios Mínimos desde {json_path}...")
    salarios = load_json(json_path)

    inserted = 0
    for record in salarios:
        fecha = record.get("fecha")
        salario = record.get("salario_diario") or record.get("valor")
        zona = record.get("zona", "general")

        if not fecha or not salario:
            continue

        db.execute(
            """
            INSERT OR REPLACE INTO salarios_minimos
            (fecha, zona, salario_diario, anio, mes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                fecha,
                zona,
                salario,
                record.get("año") or record.get("anio"),
                record.get("mes"),
            ),
        )
        inserted += 1

    print(f"✅ Insertados {inserted:,} registros de Salarios Mínimos")
    return inserted


def create_database(db_path: Path, schema_path: Path, data_dir: Path) -> None:
    """
    Crear base de datos SQLite y migrar todos los datos

    :param db_path: Path donde crear la base de datos
    :param schema_path: Path al schema SQL
    :param data_dir: Path al directorio shared-data
    """
    print(f"\n🚀 Creando base de datos: {db_path}")
    print(f"📂 Directorio de datos: {data_dir}")
    print(f"📄 Schema: {schema_path}\n")

    # Crear base de datos
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row

    # Cargar schema
    print("📋 Cargando schema...")
    with open(schema_path, encoding="utf-8") as f:
        db.executescript(f.read())
    print("✅ Schema cargado correctamente\n")

    # Migrar datos
    total_records = 0

    total_records += migrate_udis(db, data_dir)
    total_records += migrate_tipo_cambio(db, data_dir)
    total_records += migrate_tiie(db, data_dir)
    total_records += migrate_cetes(db, data_dir)
    total_records += migrate_inflacion(db, data_dir)
    total_records += migrate_salarios_minimos(db, data_dir)

    # Commit y cerrar
    db.commit()
    print(f"\n💾 Commit de cambios...")

    # Estadísticas finales
    print("\n" + "=" * 60)
    print("📊 ESTADÍSTICAS FINALES")
    print("=" * 60)

    cursor = db.execute("SELECT COUNT(*) as count FROM udis")
    print(f"  UDIs:              {cursor.fetchone()['count']:>10,} registros")

    cursor = db.execute("SELECT COUNT(*) as count FROM tipo_cambio")
    print(f"  Tipo de Cambio:    {cursor.fetchone()['count']:>10,} registros")

    cursor = db.execute("SELECT COUNT(*) as count FROM tiie")
    print(f"  TIIE:              {cursor.fetchone()['count']:>10,} registros")

    cursor = db.execute("SELECT COUNT(*) as count FROM cetes")
    print(f"  CETES:             {cursor.fetchone()['count']:>10,} registros")

    cursor = db.execute("SELECT COUNT(*) as count FROM inflacion")
    print(f"  Inflación:         {cursor.fetchone()['count']:>10,} registros")

    cursor = db.execute("SELECT COUNT(*) as count FROM salarios_minimos")
    print(f"  Salarios Mínimos:  {cursor.fetchone()['count']:>10,} registros")

    print(f"  {'─' * 40}")
    print(f"  TOTAL:             {total_records:>10,} registros\n")

    # Metadata
    cursor = db.execute("SELECT key, value FROM _metadata ORDER BY key")
    print("📋 Metadata:")
    for row in cursor:
        print(f"  {row['key']:20} = {row['value']}")

    # Tamaño del archivo
    db_size = db_path.stat().st_size / (1024 * 1024)  # MB
    print(f"\n💾 Tamaño del archivo: {db_size:.2f} MB")

    db.close()
    print("\n✅ Base de datos creada exitosamente!")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrar datos dinámicos de Banxico desde JSON a SQLite"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="mexico_dynamic.sqlite3",
        help="Nombre del archivo de salida (default: mexico_dynamic.sqlite3)",
    )
    parser.add_argument(
        "--data-dir",
        default=None,
        help="Directorio de datos (default: auto-detectar shared-data)",
    )

    args = parser.parse_args()

    # Detectar directorios
    script_dir = Path(__file__).parent
    shared_data_dir = script_dir.parent

    if args.data_dir:
        data_dir = Path(args.data_dir)
    else:
        data_dir = shared_data_dir

    schema_path = shared_data_dir / "schema_dynamic.sql"
    db_path = shared_data_dir / args.output

    # Verificar que existen los directorios necesarios
    if not data_dir.exists():
        print(f"❌ Error: No existe el directorio {data_dir}")
        sys.exit(1)

    if not schema_path.exists():
        print(f"❌ Error: No existe el schema {schema_path}")
        sys.exit(1)

    banxico_dir = data_dir / "banxico"
    if not banxico_dir.exists():
        print(f"❌ Error: No existe el directorio {banxico_dir}")
        sys.exit(1)

    # Crear base de datos
    try:
        create_database(db_path, schema_path, data_dir)
    except Exception as e:
        print(f"\n❌ Error creando base de datos: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
