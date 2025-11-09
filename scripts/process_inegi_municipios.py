#!/usr/bin/env python3
"""
Process INEGI municipalities file to catalogmx format.

This script processes the INEGI AGEEML municipios file and converts it
to the catalogmx JSON format.
"""

import json
import csv
from pathlib import Path
from datetime import datetime

def parse_inegi_municipios(file_path):
    """Parse INEGI tab-delimited municipios file."""
    
    municipios = []
    
    print(f"📖 Leyendo archivo: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        # Read tab-separated file
        reader = csv.DictReader(f, delimiter='\t')
        
        count = 0
        for row in reader:
            # Remove quotes from values and handle missing data
            def safe_int(value):
                """Convert to int, handle '-' and empty values"""
                val = value.strip('"').strip()
                if not val or val == '-':
                    return 0
                try:
                    return int(val)
                except ValueError:
                    return 0
            
            mun_data = {
                "cve_entidad": row['CVE_ENT'].strip('"').zfill(2),
                "nom_entidad": row['NOM_ENT'].strip('"'),
                "nom_abr_entidad": row['NOM_ABR'].strip('"'),
                "cve_municipio": row['CVE_MUN'].strip('"').zfill(3),
                "nom_municipio": row['NOM_MUN'].strip('"'),
                "cve_completa": row['CVEGEO'].strip('"'),
                "cve_cabecera": row['CVE_CAB'].strip('"'),
                "nom_cabecera": row['NOM_CAB'].strip('"'),
                "poblacion_total": safe_int(row['POB_TOTAL']),
                "poblacion_masculina": safe_int(row['POB_MASCULINA']),
                "poblacion_femenina": safe_int(row['POB_FEMENINA']),
                "viviendas_habitadas": safe_int(row['TOTAL DE VIVIENDAS HABITADAS'])
            }
            
            municipios.append(mun_data)
            count += 1
            
            if count % 500 == 0:
                print(f"   Procesados {count:,} municipios...")
    
    print(f"✅ Total procesados: {len(municipios):,} municipios")
    return municipios


def save_to_catalogmx_format(municipios, output_path):
    """Save municipalities to catalogmx JSON format."""
    
    # Get statistics
    estados = {}
    poblacion_total = 0
    for mun in municipios:
        estado = mun['nom_entidad']
        estados[estado] = estados.get(estado, 0) + 1
        poblacion_total += mun['poblacion_total']
    
    # Create catalog structure
    catalog = {
        "metadata": {
            "catalog": "INEGI_Municipios",
            "version": "2025-10",
            "source": "INEGI - Marco Geoestadístico Nacional (AGEEML)",
            "description": "Catálogo completo de municipios y demarcaciones territoriales de México",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "total_records": len(municipios),
            "total_states": len(estados),
            "total_population": poblacion_total,
            "notes": "Catálogo completo del INEGI con todos los municipios de México. Incluye datos de población y vivienda del Censo 2020.",
            "download_url": "https://www.inegi.org.mx/app/ageeml/"
        },
        "municipios": municipios
    }
    
    print(f"💾 Guardando en formato catalogmx...")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
    
    # Get file size
    size_mb = output_path.stat().st_size / (1024 * 1024)
    
    print(f"✅ Guardado exitosamente")
    print(f"   📁 Archivo: {output_path}")
    print(f"   📊 Tamaño: {size_mb:.2f} MB")
    print(f"   🏛️  Municipios: {len(municipios):,}")
    print(f"   🗺️  Estados: {len(estados)}")
    print(f"   👥 Población total: {poblacion_total:,}")
    
    # Show top 10 states by municipalities
    print(f"\n📊 Distribución por estado (top 10):")
    sorted_estados = sorted(estados.items(), key=lambda x: x[1], reverse=True)[:10]
    for estado, count in sorted_estados:
        print(f"   {estado}: {count:,} municipios")


def main():
    """Main function."""
    
    print("=" * 70)
    print("🇲🇽 Procesador de Municipios INEGI (AGEEML)")
    print("=" * 70)
    print()
    
    # Input file
    script_dir = Path(__file__).parent
    input_file = script_dir.parent / 'tmp' / 'AGEEML_20251021630614.txt'
    
    if not input_file.exists():
        print(f"❌ Error: No se encontró el archivo {input_file}")
        print("   Descomprime catun_municipio.zip en el directorio tmp/")
        return 1
    
    # Output file
    output_dir = script_dir.parent / 'packages' / 'shared-data' / 'inegi'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'municipios_completo.json'
    
    # Process file
    municipios = parse_inegi_municipios(input_file)
    
    if not municipios:
        print("❌ Error: No se procesaron municipios")
        return 1
    
    print()
    
    # Save to catalogmx format
    save_to_catalogmx_format(municipios, output_file)
    
    print()
    print("=" * 70)
    print("✅ Conversión completada!")
    print("=" * 70)
    
    return 0


if __name__ == '__main__':
    exit(main())

