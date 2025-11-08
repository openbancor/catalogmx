#!/usr/bin/env python3
"""
Convierte archivos CSV de SEPOMEX a formato catalogmx JSON.

Uso:
    python csv_to_catalogmx.py sepomex_db.csv

Formatos soportados:
    - SEPOMEX oficial (.xlsx, .csv, .txt)
    - IcaliaLabs sepomex_db.csv
    - Cualquier CSV con columnas estándar de códigos postales
"""

import csv
import json
import sys
from pathlib import Path
from typing import List, Dict

def detect_format(headers: List[str]) -> str:
    """Detecta el formato del CSV basándose en los headers"""
    headers_lower = [h.lower() for h in headers]

    if 'd_codigo' in headers_lower:
        return 'sepomex_oficial'
    elif 'zip_code' in headers_lower or 'codigo_postal' in headers_lower:
        return 'community'
    else:
        return 'unknown'

def convert_sepomex_oficial(row: Dict) -> Dict:
    """Convierte formato oficial SEPOMEX a catalogmx"""
    return {
        "cp": str(row.get('d_codigo', '')).zfill(5),
        "asentamiento": row.get('d_asenta', ''),
        "tipo_asentamiento": row.get('d_tipo_asenta', ''),
        "municipio": row.get('D_mnpio', ''),
        "estado": row.get('d_estado', ''),
        "ciudad": row.get('d_ciudad', '') or '',
        "cp_oficina": str(row.get('d_CP', '')).zfill(5) if row.get('d_CP') else '',
        "codigo_estado": str(row.get('c_estado', '')).zfill(2),
        "codigo_municipio": str(row.get('c_mnpio', '')).zfill(3)
    }

def convert_community(row: Dict) -> Dict:
    """Convierte formato community a catalogmx"""
    cp = row.get('zip_code') or row.get('codigo_postal', '')
    return {
        "cp": str(cp).zfill(5),
        "asentamiento": row.get('settlement') or row.get('colonia', ''),
        "tipo_asentamiento": row.get('settlement_type') or row.get('tipo_asentamiento', ''),
        "municipio": row.get('municipality') or row.get('municipio', ''),
        "estado": row.get('state') or row.get('estado', ''),
        "ciudad": row.get('city') or row.get('ciudad', '') or '',
        "cp_oficina": '',
        "codigo_estado": str(row.get('state_code', row.get('codigo_estado', ''))).zfill(2),
        "codigo_municipio": ''
    }

def convert_csv_to_catalogmx(csv_file: Path, output_file: Path = None):
    """Convierte CSV de SEPOMEX a formato catalogmx JSON"""

    if not csv_file.exists():
        print(f"Error: Archivo no encontrado: {csv_file}")
        sys.exit(1)

    print(f"Leyendo: {csv_file}")
    print(f"Tamaño: {csv_file.stat().st_size:,} bytes")

    codigos_postales = []

    # Detectar formato del CSV
    with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
        # Intentar diferentes delimitadores
        sample = f.read(1024)
        f.seek(0)

        delimiter = ',' if ',' in sample else '|' if '|' in sample else '\t'
        print(f"Delimitador detectado: '{delimiter}'")

        reader = csv.DictReader(f, delimiter=delimiter)
        headers = reader.fieldnames

        if not headers:
            print("Error: No se pudieron leer los headers del CSV")
            sys.exit(1)

        print(f"Headers encontrados: {', '.join(headers[:5])}...")

        format_type = detect_format(headers)
        print(f"Formato detectado: {format_type}")

        # Seleccionar función de conversión
        if format_type == 'sepomex_oficial':
            convert_func = convert_sepomex_oficial
        elif format_type == 'community':
            convert_func = convert_community
        else:
            print("Advertencia: Formato desconocido, intentando conversión genérica")
            convert_func = convert_community

        # Procesar filas
        for i, row in enumerate(reader, 1):
            try:
                cp_data = convert_func(row)
                if cp_data['cp'] and cp_data['cp'] != '00000':
                    codigos_postales.append(cp_data)

                if i % 10000 == 0:
                    print(f"  Procesadas {i:,} filas...")
            except Exception as e:
                print(f"Error en fila {i}: {e}")
                continue

    print(f"\nTotal procesados: {len(codigos_postales):,} códigos postales")

    # Crear catálogo en formato catalogmx
    catalog = {
        "metadata": {
            "catalog": "SEPOMEX",
            "version": "2025-11",
            "source": "Servicio Postal Mexicano",
            "description": "Catálogo completo de códigos postales de México",
            "last_updated": "2025-11-08",
            "total_records": len(codigos_postales),
            "notes": f"Convertido desde {csv_file.name}",
            "download_url": "https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/CodigoPostal_Exportar.aspx"
        },
        "codigos_postales": codigos_postales
    }

    # Determinar archivo de salida
    if output_file is None:
        output_file = Path(__file__).parent.parent / 'packages' / 'shared-data' / 'sepomex' / 'codigos_postales_completo.json'

    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nGuardando en: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    print(f"✓ Guardado exitosamente")
    print(f"✓ Tamaño del archivo: {output_file.stat().st_size:,} bytes")
    print(f"✓ Total de códigos postales: {len(codigos_postales):,}")

    # Mostrar estadísticas
    estados = {}
    for cp in codigos_postales:
        estado = cp['estado']
        estados[estado] = estados.get(estado, 0) + 1

    print(f"\nDistribución por estado (top 10):")
    for estado, count in sorted(estados.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {estado}: {count:,} códigos")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python csv_to_catalogmx.py <archivo.csv> [salida.json]")
        print("\nEjemplos:")
        print("  python csv_to_catalogmx.py sepomex_db.csv")
        print("  python csv_to_catalogmx.py CPdescarga.txt")
        print("  python csv_to_catalogmx.py sepomex.xlsx output.json")
        sys.exit(1)

    csv_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    convert_csv_to_catalogmx(csv_file, output_file)
