#!/usr/bin/env python3
"""
Process INEGI localities file to catalogmx format (filtered by population).

This script processes the INEGI AGEEML localidades file and converts it
to the catalogmx JSON format, filtering by minimum population.
"""

import json
import csv
from pathlib import Path
from datetime import datetime

def parse_inegi_localidades(file_path, min_poblacion=1000):
    """Parse INEGI tab-delimited localidades file with population filter."""
    
    localidades = []
    total_procesados = 0
    
    print(f"📖 Leyendo archivo: {file_path}")
    print(f"🔍 Filtro: Población >= {min_poblacion:,} habitantes")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        # Read tab-separated file
        reader = csv.DictReader(f, delimiter='\t')
        
        for row in reader:
            total_procesados += 1
            
            # Remove quotes from values and handle missing data
            def safe_int(value):
                """Convert to int, handle '-' and empty values"""
                val = value.strip('"').strip()
                if not val or val == '-' or val == '*':
                    return 0
                try:
                    return int(val)
                except ValueError:
                    return 0
            
            def safe_float(value):
                """Convert to float for coordinates"""
                val = value.strip('"').strip()
                if not val or val == '-':
                    return None
                try:
                    return float(val)
                except ValueError:
                    return None
            
            poblacion_total = safe_int(row['POB_TOTAL'])
            
            # Filtrar por población mínima
            if poblacion_total < min_poblacion:
                continue
            
            loc_data = {
                "cvegeo": row['CVEGEO'].strip('"'),
                "cve_entidad": row['CVE_ENT'].strip('"').zfill(2),
                "nom_entidad": row['NOM_ENT'].strip('"'),
                "nom_abr_entidad": row['NOM_ABR'].strip('"'),
                "cve_municipio": row['CVE_MUN'].strip('"').zfill(3),
                "nom_municipio": row['NOM_MUN'].strip('"'),
                "cve_localidad": row['CVE_LOC'].strip('"').zfill(4),
                "nom_localidad": row['NOM_LOC'].strip('"'),
                "ambito": row['AMBITO'].strip('"'),  # U=Urbano, R=Rural
                "latitud": safe_float(row['LAT_DECIMAL']),
                "longitud": safe_float(row['LON_DECIMAL']),
                "altitud": safe_int(row['ALTITUD']),
                "poblacion_total": poblacion_total,
                "poblacion_masculina": safe_int(row['POB_MASCULINA']),
                "poblacion_femenina": safe_int(row['POB_FEMENINA']),
                "viviendas_habitadas": safe_int(row['TOTAL DE VIVIENDAS HABITADAS'])
            }
            
            localidades.append(loc_data)
            
            if len(localidades) % 1000 == 0:
                print(f"   Aceptadas {len(localidades):,} localidades (de {total_procesados:,} procesadas)...")
    
    print(f"✅ Total procesadas: {total_procesados:,} localidades")
    print(f"✅ Total aceptadas: {len(localidades):,} localidades (>= {min_poblacion:,} hab)")
    return localidades


def save_to_catalogmx_format(localidades, output_path, min_poblacion):
    """Save localities to catalogmx JSON format."""
    
    # Get statistics
    estados = {}
    poblacion_total = 0
    urbanas = 0
    rurales = 0
    
    for loc in localidades:
        estado = loc['nom_entidad']
        estados[estado] = estados.get(estado, 0) + 1
        poblacion_total += loc['poblacion_total']
        if loc['ambito'] == 'U':
            urbanas += 1
        else:
            rurales += 1
    
    # Create catalog structure
    catalog = {
        "metadata": {
            "catalog": "INEGI_Localidades",
            "version": "2025-10",
            "source": "INEGI - Marco Geoestadístico Nacional (AGEEML)",
            "description": f"Catálogo de localidades de México con {min_poblacion:,}+ habitantes",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "total_records": len(localidades),
            "total_states": len(estados),
            "total_population": poblacion_total,
            "min_population_filter": min_poblacion,
            "localidades_urbanas": urbanas,
            "localidades_rurales": rurales,
            "notes": f"Catálogo filtrado del INEGI con localidades >= {min_poblacion:,} habitantes. Incluye coordenadas GPS, población y vivienda del Censo 2020.",
            "download_url": "https://www.inegi.org.mx/app/ageeml/"
        },
        "localidades": localidades
    }
    
    print(f"💾 Guardando en formato catalogmx...")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
    
    # Get file size
    size_mb = output_path.stat().st_size / (1024 * 1024)
    
    print(f"✅ Guardado exitosamente")
    print(f"   📁 Archivo: {output_path}")
    print(f"   📊 Tamaño: {size_mb:.2f} MB")
    print(f"   🏘️  Localidades: {len(localidades):,}")
    print(f"   🏙️  Urbanas: {urbanas:,}")
    print(f"   🏡 Rurales: {rurales:,}")
    print(f"   🗺️  Estados: {len(estados)}")
    print(f"   👥 Población total: {poblacion_total:,}")
    
    # Show top 10 states by localities
    print(f"\n📊 Distribución por estado (top 10):")
    sorted_estados = sorted(estados.items(), key=lambda x: x[1], reverse=True)[:10]
    for estado, count in sorted_estados:
        print(f"   {estado}: {count:,} localidades")


def main():
    """Main function."""
    
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Procesar localidades INEGI con filtro de población'
    )
    parser.add_argument(
        '--min-poblacion',
        type=int,
        default=1000,
        help='Población mínima para incluir localidad (default: 1000)'
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🇲🇽 Procesador de Localidades INEGI (AGEEML)")
    print("=" * 70)
    print()
    
    # Input file
    script_dir = Path(__file__).parent
    input_file = script_dir.parent / 'tmp' / 'AGEEML_2025101415820_utf.txt'
    
    if not input_file.exists():
        print(f"❌ Error: No se encontró el archivo {input_file}")
        print("   Descomprime min_sin_acento.zip en el directorio tmp/")
        return 1
    
    # Output file
    output_dir = script_dir.parent / 'packages' / 'shared-data' / 'inegi'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    suffix = f"_{args.min_poblacion}hab" if args.min_poblacion != 1000 else ""
    output_file = output_dir / f'localidades{suffix}.json'
    
    # Process file
    localidades = parse_inegi_localidades(input_file, args.min_poblacion)
    
    if not localidades:
        print("❌ Error: No se procesaron localidades")
        return 1
    
    print()
    
    # Save to catalogmx format
    save_to_catalogmx_format(localidades, output_file, args.min_poblacion)
    
    print()
    print("=" * 70)
    print("✅ Conversión completada!")
    print("=" * 70)
    print()
    print("💡 Uso del catálogo:")
    print("   from catalogmx.catalogs.inegi import LocalidadesCatalog")
    print("   localidades = LocalidadesCatalog.get_all()")
    print()
    print("🔗 Vinculación con códigos postales:")
    print("   Ver VINCULACION_CP_LOCALIDAD.md para estrategias")
    
    return 0


if __name__ == '__main__':
    exit(main())

