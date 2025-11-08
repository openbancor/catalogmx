#!/usr/bin/env python3
"""
Script para descargar y procesar TIGIE (Tarifa de Import/Export de México)

La TIGIE contiene ~20,000 fracciones arancelarias con códigos NICO de 10 dígitos.

Fuentes oficiales:
- SNICE (oficial): https://www.snice.gob.mx
- SIICEX: http://www.siicex.gob.mx
- VUCEM: https://www.ventanillaunica.gob.mx

Este script puede:
1. Descargar TIGIE desde fuentes públicas
2. Procesar y validar estructura
3. Generar SQLite database
4. Crear índices para búsqueda rápida

Uso:
    python scripts/download_tigie.py --download
    python scripts/download_tigie.py --process tigie_data.xlsx
    python scripts/download_tigie.py --build-db
"""

import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False
    print("⚠️  Advertencia: openpyxl no instalado. Instalar con: pip install openpyxl")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  Advertencia: requests no instalado. Instalar con: pip install requests")


class TIGIEProcessor:
    """Procesador de datos TIGIE"""

    def __init__(self):
        self.fracciones: List[Dict] = []
        self.capitulos: Dict[str, str] = {}
        self.partidas: Dict[str, str] = {}

    def parse_excel(self, excel_path: Path) -> bool:
        """
        Parsea archivo Excel de TIGIE

        Formato esperado:
        - Columna A: NICO (10 dígitos)
        - Columna B: Fracción (8 dígitos)
        - Columna C: Descripción
        - Columna D: Unidad de medida
        - Columna E: IGI (Impuesto General de Importación)
        - Columna F: IGE (Impuesto General de Exportación)
        """
        if not OPENPYXL_AVAILABLE:
            print("❌ Error: openpyxl requerido para procesar Excel")
            return False

        try:
            print(f"📖 Abriendo {excel_path}...")
            workbook = openpyxl.load_workbook(excel_path, read_only=True)
            sheet = workbook.active

            print(f"📊 Procesando filas...")
            row_count = 0

            for row in sheet.iter_rows(min_row=2, values_only=True):  # Skip header
                # Validar que tengamos al menos NICO y descripción
                if not row[0] or not row[2]:
                    continue

                nico = str(row[0]).strip()
                descripcion = str(row[2]).strip()

                # Validar formato NICO (10 dígitos)
                if not re.match(r'^\d{10}$', nico):
                    continue

                fraccion = nico[:8]
                capitulo = fraccion[:2]
                partida = fraccion[:4]

                # Extraer datos
                fraccion_data = {
                    'nico': nico,
                    'fraccion': fraccion,
                    'capitulo': capitulo,
                    'partida': partida,
                    'descripcion': descripcion,
                    'unidad_medida': str(row[3]).strip() if row[3] else '',
                    'igi': float(row[4]) if row[4] and row[4] != '' else 0.0,
                    'ige': float(row[5]) if row[5] and row[5] != '' else 0.0,
                }

                self.fracciones.append(fraccion_data)
                row_count += 1

                if row_count % 1000 == 0:
                    print(f"   Procesadas {row_count} fracciones...")

            workbook.close()

            print(f"✅ Total procesadas: {row_count} fracciones arancelarias")
            return True

        except Exception as e:
            print(f"❌ Error procesando Excel: {e}")
            return False

    def build_sqlite_database(self, db_path: Path) -> bool:
        """
        Construye base de datos SQLite con fracciones arancelarias

        Incluye:
        - Tabla fracciones con todos los campos
        - Índices en NICO, fracción, capítulo, partida
        - Full-text search en descripción
        """
        if not self.fracciones:
            print("❌ Error: No hay fracciones cargadas")
            return False

        try:
            print(f"🗄️  Creando base de datos SQLite en {db_path}...")

            # Eliminar DB existente
            if db_path.exists():
                db_path.unlink()

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # Crear tabla
            cursor.execute("""
                CREATE TABLE fracciones_arancelarias (
                    nico TEXT PRIMARY KEY,
                    fraccion TEXT NOT NULL,
                    capitulo TEXT NOT NULL,
                    partida TEXT NOT NULL,
                    descripcion TEXT NOT NULL,
                    unidad_medida TEXT,
                    igi REAL DEFAULT 0.0,
                    ige REAL DEFAULT 0.0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Crear índices
            print("📇 Creando índices...")

            cursor.execute("""
                CREATE INDEX idx_fraccion ON fracciones_arancelarias(fraccion)
            """)

            cursor.execute("""
                CREATE INDEX idx_capitulo ON fracciones_arancelarias(capitulo)
            """)

            cursor.execute("""
                CREATE INDEX idx_partida ON fracciones_arancelarias(partida)
            """)

            # Crear tabla FTS5 para búsqueda full-text
            cursor.execute("""
                CREATE VIRTUAL TABLE fracciones_fts USING fts5(
                    nico,
                    descripcion,
                    content='fracciones_arancelarias',
                    content_rowid='rowid'
                )
            """)

            # Insertar datos
            print(f"💾 Insertando {len(self.fracciones)} registros...")

            cursor.executemany("""
                INSERT INTO fracciones_arancelarias
                (nico, fraccion, capitulo, partida, descripcion, unidad_medida, igi, ige)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                (
                    f['nico'],
                    f['fraccion'],
                    f['capitulo'],
                    f['partida'],
                    f['descripcion'],
                    f['unidad_medida'],
                    f['igi'],
                    f['ige']
                )
                for f in self.fracciones
            ])

            # Poblar índice FTS
            cursor.execute("""
                INSERT INTO fracciones_fts(nico, descripcion)
                SELECT nico, descripcion FROM fracciones_arancelarias
            """)

            # Crear tabla de metadatos
            cursor.execute("""
                CREATE TABLE metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)

            cursor.execute("""
                INSERT INTO metadata (key, value) VALUES
                ('version', ?),
                ('total_records', ?),
                ('created_at', ?),
                ('source', 'TIGIE')
            """, (
                datetime.now().strftime('%Y-Q%m'),
                str(len(self.fracciones)),
                datetime.utcnow().isoformat()
            ))

            conn.commit()
            conn.close()

            print(f"✅ Base de datos creada exitosamente")
            print(f"   Ubicación: {db_path}")
            print(f"   Tamaño: {db_path.stat().st_size / 1024 / 1024:.2f} MB")

            return True

        except Exception as e:
            print(f"❌ Error creando base de datos: {e}")
            return False

    def export_to_json(self, json_path: Path, limit: Optional[int] = None) -> bool:
        """
        Exporta fracciones a JSON (para muestra o catálogo pequeño)

        Args:
            json_path: Ruta del archivo JSON de salida
            limit: Opcional - limitar número de registros (para testing)
        """
        if not self.fracciones:
            print("❌ Error: No hay fracciones cargadas")
            return False

        try:
            fracciones_export = self.fracciones[:limit] if limit else self.fracciones

            data = {
                "metadata": {
                    "catalog": "c_FraccionArancelaria",
                    "source": "TIGIE",
                    "version": datetime.now().strftime('%Y-Q%m'),
                    "total_records": len(fracciones_export),
                    "created_at": datetime.utcnow().isoformat() + 'Z',
                    "notes": "Tarifa de Ley de Impuestos Generales de Importación y Exportación"
                },
                "fracciones": fracciones_export
            }

            json_path.parent.mkdir(parents=True, exist_ok=True)

            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"✅ Exportado a JSON: {json_path}")
            print(f"   Registros: {len(fracciones_export)}")

            return True

        except Exception as e:
            print(f"❌ Error exportando JSON: {e}")
            return False

    def generate_statistics(self):
        """Genera estadísticas del catálogo TIGIE"""
        if not self.fracciones:
            print("❌ Error: No hay fracciones cargadas")
            return

        print("\n" + "="*80)
        print("📊 ESTADÍSTICAS TIGIE")
        print("="*80)

        total = len(self.fracciones)
        capitulos = set(f['capitulo'] for f in self.fracciones)
        partidas = set(f['partida'] for f in self.fracciones)

        print(f"\n📈 Totales:")
        print(f"   Fracciones (NICO 10 dígitos): {total:,}")
        print(f"   Fracciones (8 dígitos):       {len(set(f['fraccion'] for f in self.fracciones)):,}")
        print(f"   Capítulos (2 dígitos):        {len(capitulos)}")
        print(f"   Partidas (4 dígitos):         {len(partidas):,}")

        # Top capítulos
        capitulo_counts = {}
        for f in self.fracciones:
            cap = f['capitulo']
            capitulo_counts[cap] = capitulo_counts.get(cap, 0) + 1

        print(f"\n📦 Top 10 Capítulos por cantidad de fracciones:")
        for cap, count in sorted(capitulo_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   Capítulo {cap}: {count:,} fracciones")

        # Impuestos
        con_igi = sum(1 for f in self.fracciones if f['igi'] > 0)
        con_ige = sum(1 for f in self.fracciones if f['ige'] > 0)

        print(f"\n💰 Impuestos:")
        print(f"   Con IGI > 0: {con_igi:,} ({con_igi/total*100:.1f}%)")
        print(f"   Con IGE > 0: {con_ige:,} ({con_ige/total*100:.1f}%)")


def download_tigie_from_public_source():
    """
    Intenta descargar TIGIE desde fuentes públicas

    Nota: La fuente oficial SNICE requiere autenticación.
    Este método busca en fuentes públicas alternativas.
    """
    if not REQUESTS_AVAILABLE:
        print("❌ Error: requests requerido para descargar")
        return False

    print("🌐 Buscando fuentes públicas de TIGIE...")
    print("⚠️  Nota: SNICE oficial requiere autenticación")
    print("   Alternativa: Descargar manualmente desde:")
    print("   - https://www.snice.gob.mx")
    print("   - http://www.siicex.gob.mx")
    print("   - https://www.ventanillaunica.gob.mx")

    # TODO: Implementar descarga desde fuentes públicas si existen
    # Por ahora, instrucciones para descarga manual

    return False


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Descarga y procesa TIGIE (Fracciones Arancelarias)'
    )

    parser.add_argument(
        '--download',
        action='store_true',
        help='Intenta descargar TIGIE desde fuentes públicas'
    )

    parser.add_argument(
        '--process',
        type=str,
        metavar='FILE',
        help='Procesa archivo Excel de TIGIE'
    )

    parser.add_argument(
        '--build-db',
        action='store_true',
        help='Construye base de datos SQLite'
    )

    parser.add_argument(
        '--export-json',
        action='store_true',
        help='Exporta a JSON (solo para muestra)'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='Genera estadísticas'
    )

    args = parser.parse_args()

    processor = TIGIEProcessor()

    # Descargar
    if args.download:
        download_tigie_from_public_source()
        return 0

    # Procesar Excel
    if args.process:
        excel_path = Path(args.process)

        if not excel_path.exists():
            print(f"❌ Error: Archivo no encontrado: {excel_path}")
            return 1

        if not processor.parse_excel(excel_path):
            return 1

        if args.stats:
            processor.generate_statistics()

        # Build database
        if args.build_db:
            db_path = Path(__file__).parent.parent / 'packages' / 'shared-data' / 'sat' / 'tigie.db'
            processor.build_sqlite_database(db_path)

        # Export JSON sample
        if args.export_json:
            json_path = Path(__file__).parent.parent / 'packages' / 'shared-data' / 'sat' / 'tigie_sample.json'
            processor.export_to_json(json_path, limit=100)  # Solo 100 registros de muestra

        return 0

    # Mostrar ayuda si no hay argumentos
    parser.print_help()
    return 0


if __name__ == '__main__':
    sys.exit(main())
