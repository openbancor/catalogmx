#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fetch SAT Official Catalogs from XSD

This script downloads the official catCFDI.xsd from the SAT website,
parses it, and extracts all the enumeration-based catalogs into
separate JSON files.
"""

import argparse
import json
import sys
from pathlib import Path
import requests
from datetime import datetime
import xml.etree.ElementTree as ET
import pandas as pd

# SAT Catalog XSD URL
SAT_XSD_URL = "http://www.sat.gob.mx/sitio_internet/cfd/catalogos/catCFDI.xsd"
SAT_EXCEL_URL = "http://omawww.sat.gob.mx/tramitesyservicios/Paginas/documentos/catCFDI_V_4_20251023.xls"

# Catalogs to be extracted from the XSD file
XSD_CATALOGS = {
    'c_FormaPago': 'c_FormaPago',
    'c_Impuesto': 'c_Impuesto',
    'c_MetodoPago': 'c_MetodoPago',
    'c_Moneda': 'c_Moneda',
    'c_Pais': 'c_Pais',
    'c_RegimenFiscal': 'c_RegimenFiscal',
    'c_TipoDeComprobante': 'c_TipoDeComprobante',
    'c_TipoFactor': 'c_TipoFactor',
    'c_TipoRelacion': 'c_TipoRelacion',
    'c_UsoCFDI': 'c_UsoCFDI',
    'c_Meses': 'c_Meses',
    'c_Periodicidad': 'c_Periodicidad',
    'c_Exportacion': 'c_Exportacion',
    'c_ObjetoImp': 'c_ObjetoImp',
}

# Catalogs that must be extracted from the Excel file
EXCEL_CATALOGS = {
    'c_TasaOCuota': 'c_TasaOCuota',
    # Add other Excel-only catalogs here if needed
}


def download_and_parse_xsd(output_dir, force=False):
    """
    Downloads the main XSD file and processes all catalogs.
    """
    print(f"📥 Downloading XSD from {SAT_XSD_URL}...")
    try:
        response = requests.get(SAT_XSD_URL)
        response.raise_for_status()
        print("✅ XSD file downloaded successfully.")
        
        root = ET.fromstring(response.content)
        
        # Define the XML namespace
        ns = {'xs': 'http://www.w3.org/2001/XMLSchema'}
        
        all_success = True
        for xsd_name, json_name in XSD_CATALOGS.items():
            output_path = output_dir / 'cfdi_4.0' / f"{json_name}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists() and not force:
                print(f"⏭️  {json_name}: Already exists, skipping.")
                continue

            print(f"   - Processing catalog: {xsd_name} -> {json_name}.json")

    try:
                # Find the simpleType element for the catalog
                st_element = root.find(f".//xs:simpleType[@name='{xsd_name}']", ns)
                if st_element is None:
                    # Some names might have the namespace prefix in the XSD itself
                    st_element = root.find(f".//xs:simpleType[@name='catCFDI:{xsd_name}']", ns)

                if st_element is None:
                    raise ValueError(f"Could not find simpleType '{xsd_name}' in XSD.")

                # Find all enumeration values
                enumerations = st_element.findall('.//xs:enumeration', ns)
                records = []
                for enum in enumerations:
                    record = {'valor': enum.get('value')}
                    # Try to get documentation/description if it exists
                    annotation = enum.find('xs:annotation/xs:documentation', ns)
                    if annotation is not None:
                        record['descripcion'] = annotation.text
                    records.append(record)

                final_data = {
            '_meta': {
                        'catalog': json_name,
                        'source': SAT_XSD_URL,
                        'xsd_name': xsd_name,
                'downloaded': datetime.now().isoformat(),
            },
                    'data': records
        }

        with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(final_data, f, ensure_ascii=False, indent=2)

                print(f"     ✅ Saved {len(records)} records to {output_path.name}")

            except Exception as e:
                print(f"     ❌ Failed to process catalog {xsd_name}: {e}")
                all_success = False
        
        return all_success

    except Exception as e:
        print(f"❌ Failed to download or parse the main XSD file: {e}")
        return False


def download_and_process_excel(output_dir, force=False):
    """
    Downloads the main Excel file and processes catalogs that are only available there.
    """
    print(f"📥 Downloading Excel file from {SAT_EXCEL_URL}...")
    try:
        excel_file = pd.ExcelFile(SAT_EXCEL_URL)
        print("✅ Excel file downloaded successfully.")
    except Exception as e:
        print(f"❌ Failed to download the Excel file: {e}")
        return False

    all_success = True
    for catalog_name, sheet_name in EXCEL_CATALOGS.items():
        output_path = output_dir / 'cfdi_4.0' / f"{catalog_name}.json"
        if output_path.exists() and not force:
            print(f"⏭️  {catalog_name} (from Excel): Already exists, skipping.")
            continue

        print(f"   - Processing Excel sheet: {sheet_name} -> {catalog_name}.json")
        try:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            df.columns = [str(col).strip().replace(' ', '_').lower() for col in df.columns]
            
            for col in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    df[col] = df[col].dt.strftime('%Y-%m-%d')
            
            records = df.to_dict('records')
            
            final_data = {
                '_meta': { 'catalog': catalog_name, 'source': SAT_EXCEL_URL, 'sheet': sheet_name, 'downloaded': datetime.now().isoformat() },
                'data': records
            }

            def json_converter(o):
                if isinstance(o, datetime):
                    return o.isoformat()

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(final_data, f, ensure_ascii=False, indent=2, default=json_converter)
            
            print(f"     ✅ Saved {len(records)} records to {output_path.name}")
        except Exception as e:
            print(f"     ❌ Failed to process sheet {sheet_name}: {e}")
            all_success = False
    return all_success


def main():
    parser = argparse.ArgumentParser(
        description='Download official SAT catalogs for CFDI 4.0 from the main XSD file.',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force download and process even if JSON files exist'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path(__file__).parent.parent / 'packages' / 'shared-data' / 'sat',
        help='Output directory (default: packages/shared-data/sat/)'
    )
    args = parser.parse_args()

    print("=" * 70)
    print("🇲🇽 SAT Catalog Downloader (from XSD)")
    print("=" * 70)
    print(f"📁 Output directory: {args.output}")
    print()

    print("--- Processing XSD Catalogs ---")
    xsd_success = download_and_parse_xsd(args.output, args.force)
    
    print("\n--- Processing Excel Catalogs ---")
    excel_success = download_and_process_excel(args.output, args.force)

    print("=" * 70)
    if xsd_success and excel_success:
        print("✅ All catalogs processed successfully!")
    else:
        print("❌ Some catalogs failed to process.")
    print("=" * 70)

    return 0 if xsd_success and excel_success else 1


if __name__ == '__main__':
    sys.exit(main())
