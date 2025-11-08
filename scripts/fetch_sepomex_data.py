#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fetch SEPOMEX Postal Codes

This script downloads the official Mexican postal code catalog from SEPOMEX
(Servicio Postal Mexicano).

The catalog contains approximately 150,000 postal codes with:
- Código Postal (5 digits)
- Tipo de Asentamiento (Colony, Fraccionamiento, Barrio, etc.)
- Nombre del Asentamiento
- Municipio
- Estado
- Ciudad

Official Source:
https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/CodigoPostal_Exportar.aspx

Output:
- CSV file with all postal codes
- SQLite database for efficient querying
- JSON samples for testing

Usage:
    python scripts/fetch_sepomex_data.py

    # Custom output directory
    python scripts/fetch_sepomex_data.py --output data/sepomex

    # Skip SQLite generation
    python scripts/fetch_sepomex_data.py --no-sqlite
"""

import argparse
import csv
import json
import sqlite3
import sys
from pathlib import Path
from datetime import datetime
import requests
from io import StringIO

# SEPOMEX Data URL
# Note: SEPOMEX sometimes changes the URL format
SEPOMEX_URL = "https://www.correosdemexico.gob.mx/datosabiertos/cp/cpdescarga.txt"

# Alternative: Download from official page
# https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/CodigoPostal_Exportar.aspx


def download_sepomex_data(output_dir, force=False):
    """
    Download SEPOMEX postal code data

    Args:
        output_dir: Output directory path
        force: Force download even if file exists

    Returns:
        Path to downloaded CSV file or None if failed
    """
    output_csv = output_dir / 'postal_codes.txt'

    # Check if file exists
    if output_csv.exists() and not force:
        print(f"⏭️  File already exists: {output_csv}")
        print("   Use --force to redownload")
        return output_csv

    print("📥 Downloading SEPOMEX postal code data...")
    print(f"   Source: {SEPOMEX_URL}")

    try:
        response = requests.get(SEPOMEX_URL, timeout=60)
        response.raise_for_status()

        # Save to file
        with open(output_csv, 'w', encoding='latin-1') as f:
            f.write(response.text)

        print(f"✅ Downloaded successfully")
        print(f"   📁 Saved to: {output_csv}")
        print(f"   📊 Size: {len(response.text):,} bytes")

        return output_csv

    except requests.RequestException as e:
        print(f"❌ Failed to download: {e}")
        print()
        print("⚠️  Alternative: Manual download")
        print("   1. Visit: https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/CodigoPostal_Exportar.aspx")
        print("   2. Download the TXT file")
        print(f"   3. Save as: {output_csv}")
        return None


def parse_sepomex_csv(csv_path):
    """
    Parse SEPOMEX CSV file

    SEPOMEX format (pipe-delimited):
    d_codigo|d_asenta|d_tipo_asenta|D_mnpio|d_estado|d_ciudad|d_CP|c_estado|c_oficina|c_CP|c_tipo_asenta|c_mnpio|id_asenta_cpcons|d_zona|c_cve_ciudad

    Args:
        csv_path: Path to CSV file

    Yields:
        Dictionary with postal code information
    """
    with open(csv_path, 'r', encoding='latin-1') as f:
        reader = csv.DictReader(f, delimiter='|')

        for row in reader:
            yield {
                'codigo_postal': row.get('d_codigo', '').strip(),
                'asentamiento': row.get('d_asenta', '').strip(),
                'tipo_asentamiento': row.get('d_tipo_asenta', '').strip(),
                'municipio': row.get('D_mnpio', '').strip(),
                'estado': row.get('d_estado', '').strip(),
                'ciudad': row.get('d_ciudad', '').strip(),
                'codigo_estado': row.get('c_estado', '').strip(),
                'codigo_municipio': row.get('c_mnpio', '').strip(),
                'codigo_tipo_asentamiento': row.get('c_tipo_asenta', '').strip(),
                'zona': row.get('d_zona', '').strip(),
            }


def create_sqlite_database(csv_path, db_path):
    """
    Create SQLite database from CSV file

    Args:
        csv_path: Path to CSV file
        db_path: Path to output SQLite database

    Returns:
        Number of records inserted
    """
    print("🗄️  Creating SQLite database...")

    # Remove existing database
    if db_path.exists():
        db_path.unlink()

    # Create database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table
    cursor.execute("""
        CREATE TABLE postal_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_postal TEXT NOT NULL,
            asentamiento TEXT,
            tipo_asentamiento TEXT,
            municipio TEXT,
            estado TEXT,
            ciudad TEXT,
            codigo_estado TEXT,
            codigo_municipio TEXT,
            codigo_tipo_asentamiento TEXT,
            zona TEXT
        )
    """)

    # Create indexes for fast lookups
    cursor.execute("CREATE INDEX idx_codigo_postal ON postal_codes(codigo_postal)")
    cursor.execute("CREATE INDEX idx_estado ON postal_codes(estado)")
    cursor.execute("CREATE INDEX idx_municipio ON postal_codes(municipio)")
    cursor.execute("CREATE INDEX idx_asentamiento ON postal_codes(asentamiento)")

    # Insert data
    count = 0
    batch = []
    batch_size = 1000

    for record in parse_sepomex_csv(csv_path):
        batch.append((
            record['codigo_postal'],
            record['asentamiento'],
            record['tipo_asentamiento'],
            record['municipio'],
            record['estado'],
            record['ciudad'],
            record['codigo_estado'],
            record['codigo_municipio'],
            record['codigo_tipo_asentamiento'],
            record['zona'],
        ))

        if len(batch) >= batch_size:
            cursor.executemany("""
                INSERT INTO postal_codes (
                    codigo_postal, asentamiento, tipo_asentamiento,
                    municipio, estado, ciudad, codigo_estado,
                    codigo_municipio, codigo_tipo_asentamiento, zona
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, batch)
            count += len(batch)
            batch = []
            print(f"   Inserted {count:,} records...", end='\r')

    # Insert remaining records
    if batch:
        cursor.executemany("""
            INSERT INTO postal_codes (
                codigo_postal, asentamiento, tipo_asentamiento,
                municipio, estado, ciudad, codigo_estado,
                codigo_municipio, codigo_tipo_asentamiento, zona
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, batch)
        count += len(batch)

    conn.commit()
    conn.close()

    print(f"\n✅ SQLite database created")
    print(f"   📁 Path: {db_path}")
    print(f"   📊 Records: {count:,}")

    return count


def create_sample_json(csv_path, json_path, limit=100):
    """
    Create a sample JSON file for testing

    Args:
        csv_path: Path to CSV file
        json_path: Path to output JSON file
        limit: Number of records to include
    """
    print(f"📝 Creating sample JSON ({limit} records)...")

    records = []
    for i, record in enumerate(parse_sepomex_csv(csv_path)):
        if i >= limit:
            break
        records.append(record)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            '_meta': {
                'source': 'SEPOMEX - Servicio Postal Mexicano',
                'url': SEPOMEX_URL,
                'downloaded': datetime.now().isoformat(),
                'total_records': limit,
                'note': 'This is a sample. Full data is in postal_codes.db'
            },
            'postal_codes': records
        }, f, ensure_ascii=False, indent=2)

    print(f"✅ Sample JSON created: {json_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Download SEPOMEX postal code data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output directory (default: packages/shared-data/sepomex/)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force download even if file exists'
    )
    parser.add_argument(
        '--no-sqlite',
        action='store_true',
        help='Skip SQLite database generation'
    )
    parser.add_argument(
        '--sample-size',
        type=int,
        default=100,
        help='Number of records in sample JSON (default: 100)'
    )

    args = parser.parse_args()

    # Determine output directory
    if args.output:
        output_dir = args.output
    else:
        script_dir = Path(__file__).parent
        output_dir = script_dir.parent / 'packages' / 'shared-data' / 'sepomex'

    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("🇲🇽 SEPOMEX Postal Code Downloader")
    print("=" * 70)
    print(f"📁 Output directory: {output_dir}")
    print()

    # Download data
    csv_path = download_sepomex_data(output_dir, args.force)
    if not csv_path:
        return 1

    print()

    # Create SQLite database
    if not args.no_sqlite:
        db_path = output_dir / 'postal_codes.db'
        try:
            count = create_sqlite_database(csv_path, db_path)
            print()
        except Exception as e:
            print(f"❌ Failed to create SQLite database: {e}")
            print()

    # Create sample JSON
    json_path = output_dir / 'postal_codes_sample.json'
    try:
        create_sample_json(csv_path, json_path, args.sample_size)
    except Exception as e:
        print(f"❌ Failed to create sample JSON: {e}")

    print()
    print("=" * 70)
    print("✅ SEPOMEX data download complete!")
    print("=" * 70)
    print()
    print("📊 Files created:")
    print(f"   - {csv_path.name} (raw data)")
    if not args.no_sqlite:
        print(f"   - postal_codes.db (SQLite database for querying)")
    print(f"   - postal_codes_sample.json (sample for testing)")
    print()
    print("💡 Usage example:")
    print("   ```python")
    print("   import sqlite3")
    print(f"   conn = sqlite3.connect('{db_path}')")
    print("   cursor = conn.cursor()")
    print("   cursor.execute('SELECT * FROM postal_codes WHERE codigo_postal = ?', ('01000',))")
    print("   results = cursor.fetchall()")
    print("   ```")

    return 0


if __name__ == '__main__':
    sys.exit(main())
