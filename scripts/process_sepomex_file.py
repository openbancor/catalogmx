#!/usr/bin/env python3
"""
Process SEPOMEX postal codes file to catalogmx format.

This script processes the CPdescarga.txt file from SEPOMEX and converts it
to the catalogmx JSON format.
"""

import json
import csv
from pathlib import Path
from datetime import datetime

def parse_sepomex_file(file_path):
    """Parse SEPOMEX pipe-delimited file."""
    
    codigos_postales = []
    
    print(f"📖 Leyendo archivo: {file_path}")
    
    with open(file_path, 'r', encoding='latin-1') as f:
        # Skip first line (copyright notice)
        next(f)
        
        # Read CSV with pipe delimiter
        reader = csv.DictReader(f, delimiter='|')
        
        count = 0
        for row in reader:
            cp_data = {
                "cp": row.get('d_codigo', '').strip(),
                "asentamiento": row.get('d_asenta', '').strip(),
                "tipo_asentamiento": row.get('d_tipo_asenta', '').strip(),
                "municipio": row.get('D_mnpio', '').strip(),
                "estado": row.get('d_estado', '').strip(),
                "ciudad": row.get('d_ciudad', '').strip() if row.get('d_ciudad', '').strip() else '',
                "codigo_estado": row.get('c_estado', '').strip().zfill(2),
                "codigo_municipio": row.get('c_mnpio', '').strip().zfill(3),
                "zona": row.get('d_zona', '').strip() if row.get('d_zona', '').strip() else ''
            }
            
            # Only include valid postal codes
            if cp_data['cp'] and cp_data['cp'] != '00000' and len(cp_data['cp']) == 5:
                codigos_postales.append(cp_data)
                count += 1
                
                if count % 10000 == 0:
                    print(f"   Procesados {count:,} códigos postales...")
    
    print(f"✅ Total procesados: {len(codigos_postales):,} códigos postales")
    return codigos_postales


def save_to_catalogmx_format(codigos_postales, output_path):
    """Save postal codes to catalogmx JSON format."""
    
    # Get statistics
    estados = {}
    for cp in codigos_postales:
        estado = cp['estado']
        estados[estado] = estados.get(estado, 0) + 1
    
    # Create catalog structure
    catalog = {
        "metadata": {
            "catalog": "SEPOMEX",
            "version": "2025-11",
            "source": "Servicio Postal Mexicano (SEPOMEX)",
            "description": "Catálogo completo de códigos postales de México",
            "last_updated": datetime.now().strftime("%Y-%m-%d"),
            "total_records": len(codigos_postales),
            "total_states": len(estados),
            "notes": "Catálogo completo descargado de SEPOMEX. Incluye todos los códigos postales de México con asentamientos, municipios y estados.",
            "download_url": "https://www.correosdemexico.gob.mx/SSLServicios/ConsultaCP/CodigoPostal_Exportar.aspx"
        },
        "codigos_postales": codigos_postales
    }
    
    print(f"💾 Guardando en formato catalogmx...")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
    
    # Get file size
    size_mb = output_path.stat().st_size / (1024 * 1024)
    
    print(f"✅ Guardado exitosamente")
    print(f"   📁 Archivo: {output_path}")
    print(f"   📊 Tamaño: {size_mb:.2f} MB")
    print(f"   📮 Códigos postales: {len(codigos_postales):,}")
    print(f"   🏛️  Estados: {len(estados)}")
    
    # Show top 10 states by postal codes
    print(f"\n📊 Distribución por estado (top 10):")
    sorted_estados = sorted(estados.items(), key=lambda x: x[1], reverse=True)[:10]
    for estado, count in sorted_estados:
        print(f"   {estado}: {count:,}")


def main():
    """Main function."""
    
    print("=" * 70)
    print("🇲🇽 Procesador de Códigos Postales SEPOMEX")
    print("=" * 70)
    print()
    
    # Input file
    script_dir = Path(__file__).parent
    input_file = script_dir.parent / 'tmp' / 'CPdescarga.txt'
    
    if not input_file.exists():
        print(f"❌ Error: No se encontró el archivo {input_file}")
        print("   Coloca el archivo CPdescarga.txt en el directorio tmp/")
        return 1
    
    # Output file
    output_dir = script_dir.parent / 'packages' / 'shared-data' / 'sepomex'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'codigos_postales_completo.json'
    
    # Process file
    codigos_postales = parse_sepomex_file(input_file)
    
    if not codigos_postales:
        print("❌ Error: No se procesaron códigos postales")
        return 1
    
    print()
    
    # Save to catalogmx format
    save_to_catalogmx_format(codigos_postales, output_file)
    
    print()
    print("=" * 70)
    print("✅ Conversión completada!")
    print("=" * 70)
    
    return 0


if __name__ == '__main__':
    exit(main())

