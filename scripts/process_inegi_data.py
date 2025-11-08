#!/usr/bin/env python3
"""
Convierte archivos de INEGI a formato catalogmx JSON.

Uso:
    python process_inegi_data.py municipios.txt
    python process_inegi_data.py municipios.xlsx

Formatos soportados:
    - INEGI Marco Geoestadístico (.txt tab-separated)
    - INEGI Excel (.xlsx)
    - JSON genérico con municipios
"""

import json
import sys
from pathlib import Path
from typing import List, Dict

def process_inegi_txt(file_path: Path) -> List[Dict]:
    """Procesa archivo TXT tab-separated de INEGI"""
    municipios = []

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    print(f"Procesando {len(lines)} líneas...")

    # Skip header
    for i, line in enumerate(lines[1:], 1):
        if not line.strip():
            continue

        parts = line.split('\t')
        if len(parts) >= 4:
            cve_entidad = parts[0].strip()
            nom_entidad = parts[1].strip()
            cve_municipio = parts[2].strip()
            nom_municipio = parts[3].strip()

            if cve_entidad and cve_municipio:
                municipios.append({
                    "cve_entidad": cve_entidad.zfill(2),
                    "nom_entidad": nom_entidad,
                    "cve_municipio": cve_municipio.zfill(3),
                    "nom_municipio": nom_municipio,
                    "cve_completa": f"{cve_entidad.zfill(2)}{cve_municipio.zfill(3)}"
                })

        if i % 500 == 0:
            print(f"  Procesadas {i:,} filas...")

    return municipios

def process_inegi_excel(file_path: Path) -> List[Dict]:
    """Procesa archivo Excel de INEGI"""
    try:
        import pandas as pd
    except ImportError:
        print("Error: pandas no está instalado")
        print("Instala con: pip install pandas openpyxl")
        sys.exit(1)

    print(f"Leyendo Excel: {file_path}")
    df = pd.read_excel(file_path)

    print(f"Columnas encontradas: {', '.join(df.columns.tolist())}")

    municipios = []

    # Detectar nombres de columnas (pueden variar)
    col_estado_cve = None
    col_estado_nom = None
    col_mun_cve = None
    col_mun_nom = None

    for col in df.columns:
        col_lower = col.lower()
        if 'entidad' in col_lower and 'cve' in col_lower:
            col_estado_cve = col
        elif 'entidad' in col_lower and ('nom' in col_lower or 'nombre' in col_lower):
            col_estado_nom = col
        elif 'munic' in col_lower and 'cve' in col_lower:
            col_mun_cve = col
        elif 'munic' in col_lower and ('nom' in col_lower or 'nombre' in col_lower):
            col_mun_nom = col

    if not all([col_estado_cve, col_estado_nom, col_mun_cve, col_mun_nom]):
        print("Error: No se pudieron identificar todas las columnas necesarias")
        print("Columnas detectadas:")
        print(f"  Estado clave: {col_estado_cve}")
        print(f"  Estado nombre: {col_estado_nom}")
        print(f"  Municipio clave: {col_mun_cve}")
        print(f"  Municipio nombre: {col_mun_nom}")
        sys.exit(1)

    print(f"\nProcesando {len(df)} registros...")

    for _, row in df.iterrows():
        cve_entidad = str(row[col_estado_cve]).zfill(2)
        nom_entidad = str(row[col_estado_nom])
        cve_municipio = str(row[col_mun_cve]).zfill(3)
        nom_municipio = str(row[col_mun_nom])

        if cve_entidad and cve_municipio:
            municipios.append({
                "cve_entidad": cve_entidad,
                "nom_entidad": nom_entidad,
                "cve_municipio": cve_municipio,
                "nom_municipio": nom_municipio,
                "cve_completa": f"{cve_entidad}{cve_municipio}"
            })

    return municipios

def process_json(file_path: Path) -> List[Dict]:
    """Procesa JSON genérico y convierte a formato catalogmx"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    municipios = []

    # Detectar estructura
    if isinstance(data, list):
        items = data
    elif isinstance(data, dict):
        # Intentar encontrar la lista de municipios
        for key in ['municipios', 'municipalities', 'data', 'items']:
            if key in data:
                items = data[key]
                break
        else:
            print("Error: No se pudo encontrar la lista de municipios en el JSON")
            sys.exit(1)
    else:
        print("Error: Formato JSON no reconocido")
        sys.exit(1)

    print(f"Procesando {len(items)} municipios...")

    for item in items:
        # Intentar mapear campos comunes
        cve_entidad = item.get('cve_entidad') or item.get('state_code') or item.get('estado_codigo')
        nom_entidad = item.get('nom_entidad') or item.get('state_name') or item.get('estado')
        cve_municipio = item.get('cve_municipio') or item.get('municipality_code') or item.get('municipio_codigo')
        nom_municipio = item.get('nom_municipio') or item.get('municipality_name') or item.get('municipio')

        if cve_entidad and cve_municipio:
            municipios.append({
                "cve_entidad": str(cve_entidad).zfill(2),
                "nom_entidad": str(nom_entidad),
                "cve_municipio": str(cve_municipio).zfill(3),
                "nom_municipio": str(nom_municipio),
                "cve_completa": f"{str(cve_entidad).zfill(2)}{str(cve_municipio).zfill(3)}"
            })

    return municipios

def convert_to_catalogmx(input_file: Path, output_file: Path = None):
    """Convierte archivo de INEGI a formato catalogmx"""

    if not input_file.exists():
        print(f"Error: Archivo no encontrado: {input_file}")
        sys.exit(1)

    print(f"=" * 80)
    print(f"Procesando: {input_file}")
    print(f"Tamaño: {input_file.stat().st_size:,} bytes")
    print(f"=" * 80)

    # Detectar formato por extensión
    extension = input_file.suffix.lower()

    if extension == '.txt':
        municipios = process_inegi_txt(input_file)
    elif extension in ['.xlsx', '.xls']:
        municipios = process_inegi_excel(input_file)
    elif extension == '.json':
        municipios = process_json(input_file)
    else:
        print(f"Error: Formato no soportado: {extension}")
        print("Formatos soportados: .txt, .xlsx, .xls, .json")
        sys.exit(1)

    print(f"\n✓ Total procesados: {len(municipios):,} municipios")

    # Crear catálogo en formato catalogmx
    catalog = {
        "metadata": {
            "catalog": "INEGI_Municipios",
            "version": "2025",
            "source": "INEGI - Marco Geoestadístico Nacional",
            "description": "Catálogo completo de municipios y alcaldías de México",
            "last_updated": "2025-11-08",
            "total_records": len(municipios),
            "notes": f"Convertido desde {input_file.name}. Total: {len(municipios)} unidades territoriales",
            "download_url": "https://www.inegi.org.mx/app/ageeml/"
        },
        "municipios": municipios
    }

    # Determinar archivo de salida
    if output_file is None:
        output_file = Path(__file__).parent.parent / 'packages' / 'shared-data' / 'inegi' / 'municipios_completo.json'

    output_file.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nGuardando en: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)

    print(f"✓ Guardado exitosamente")
    print(f"✓ Tamaño del archivo: {output_file.stat().st_size:,} bytes")

    # Mostrar estadísticas
    estados = {}
    for mun in municipios:
        estado = mun['nom_entidad']
        estados[estado] = estados.get(estado, 0) + 1

    print(f"\nDistribución por estado:")
    for estado, count in sorted(estados.items(), key=lambda x: x[1], reverse=True):
        print(f"  {estado}: {count:,} municipios")

    print(f"\n{'=' * 80}")
    print(f"Conversión completada exitosamente")
    print(f"Total: {len(municipios):,} municipios")
    print(f"{'=' * 80}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python process_inegi_data.py <archivo> [salida.json]")
        print("\nEjemplos:")
        print("  python process_inegi_data.py municipios_inegi.txt")
        print("  python process_inegi_data.py marco_geo.xlsx")
        print("  python process_inegi_data.py data.json output.json")
        print("\nFormatos soportados:")
        print("  - TXT tab-separated (oficial INEGI)")
        print("  - Excel (.xlsx, .xls)")
        print("  - JSON genérico")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    convert_to_catalogmx(input_file, output_file)
