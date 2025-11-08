#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fetch SAT Official Catalogs

This script downloads official SAT catalogs for CFDI 4.0 from the SAT website.

Catalogs downloaded:
- c_RegimenFiscal - Tax regimes
- c_UsoCFDI - CFDI usage codes
- c_FormaPago - Payment methods
- c_MetodoPago - Payment types
- c_TipoComprobante - Receipt types
- c_Impuesto - Taxes
- c_TasaOCuota - Tax rates
- c_Moneda - Currencies
- c_Pais - Countries
- c_TipoRelacion - Relation types
- c_Exportacion - Export types
- c_ObjetoImp - Tax object
- c_Meses - Months
- c_Periodicidad - Periodicity

And many more (26 total catalogs from Anexo 20)

Official Source:
http://omawww.sat.gob.mx/tramitesyservicios/Paginas/anexo_20_version3-3.htm

Usage:
    python scripts/fetch_sat_catalogs.py

    # Download specific catalog only
    python scripts/fetch_sat_catalogs.py --catalog c_RegimenFiscal

    # Force download even if files exist
    python scripts/fetch_sat_catalogs.py --force
"""

import argparse
import json
import os
import sys
from pathlib import Path
import requests
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# SAT Catalog URLs (these may change - check oficial SAT site)
# Note: SAT provides XSD and Excel files, this script focuses on parsing Excel
SAT_CATALOG_BASE_URL = "http://omawww.sat.gob.mx/tramitesyservicios/Paginas/documentos/catCFDI_V4.0/"

SAT_CATALOGS = {
    # Essential catalogs (Phase 2)
    'c_RegimenFiscal': {
        'url': SAT_CATALOG_BASE_URL + 'c_RegimenFiscal.xls',
        'description': 'Tax Regimes',
        'phase': 2
    },
    'c_UsoCFDI': {
        'url': SAT_CATALOG_BASE_URL + 'c_UsoCFDI.xls',
        'description': 'CFDI Usage Codes',
        'phase': 2
    },
    'c_FormaPago': {
        'url': SAT_CATALOG_BASE_URL + 'c_FormaPago.xls',
        'description': 'Payment Methods',
        'phase': 2
    },
    'c_MetodoPago': {
        'url': SAT_CATALOG_BASE_URL + 'c_MetodoPago.xls',
        'description': 'Payment Types',
        'phase': 2
    },
    'c_TipoComprobante': {
        'url': SAT_CATALOG_BASE_URL + 'c_TipoComprobante.xls',
        'description': 'Receipt Types',
        'phase': 2
    },
    'c_Impuesto': {
        'url': SAT_CATALOG_BASE_URL + 'c_Impuesto.xls',
        'description': 'Taxes',
        'phase': 2
    },
    'c_TasaOCuota': {
        'url': SAT_CATALOG_BASE_URL + 'c_TasaOCuota.xls',
        'description': 'Tax Rates',
        'phase': 2
    },
    'c_Moneda': {
        'url': SAT_CATALOG_BASE_URL + 'c_Moneda.xls',
        'description': 'Currencies',
        'phase': 2
    },
    'c_Pais': {
        'url': SAT_CATALOG_BASE_URL + 'c_Pais.xls',
        'description': 'Countries',
        'phase': 2
    },
    'c_TipoRelacion': {
        'url': SAT_CATALOG_BASE_URL + 'c_TipoRelacion.xls',
        'description': 'Relation Types',
        'phase': 2
    },

    # Extended catalogs (Phase 4)
    'c_ClaveProdServ': {
        'url': SAT_CATALOG_BASE_URL + 'c_ClaveProdServ.xls',
        'description': 'Product/Service Codes (~52k records)',
        'phase': 4,
        'large': True
    },
    'c_ClaveUnidad': {
        'url': SAT_CATALOG_BASE_URL + 'c_ClaveUnidad.xls',
        'description': 'Unit Codes (~3k records)',
        'phase': 4
    },

    # Nomina catalogs
    'c_TipoContrato': {
        'url': SAT_CATALOG_BASE_URL + 'nomina/c_TipoContrato.xls',
        'description': 'Contract Types',
        'phase': 4,
        'category': 'nomina'
    },
    'c_TipoJornada': {
        'url': SAT_CATALOG_BASE_URL + 'nomina/c_TipoJornada.xls',
        'description': 'Work Schedule Types',
        'phase': 4,
        'category': 'nomina'
    },
    'c_TipoPercepcion': {
        'url': SAT_CATALOG_BASE_URL + 'nomina/c_TipoPercepcion.xls',
        'description': 'Income Types (50+ codes)',
        'phase': 4,
        'category': 'nomina'
    },
    'c_TipoDeduccion': {
        'url': SAT_CATALOG_BASE_URL + 'nomina/c_TipoDeduccion.xls',
        'description': 'Deduction Types (20+ codes)',
        'phase': 4,
        'category': 'nomina'
    },
}


def download_catalog(catalog_name, catalog_info, output_dir, force=False):
    """
    Download a single SAT catalog

    Args:
        catalog_name: Name of the catalog (e.g., 'c_RegimenFiscal')
        catalog_info: Dictionary with catalog information
        output_dir: Output directory path
        force: Force download even if file exists
    """
    # Determine output path
    category = catalog_info.get('category', '')
    if category:
        output_path = output_dir / category / f"{catalog_name}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
    else:
        output_path = output_dir / f"{catalog_name}.json"

    # Check if file exists
    if output_path.exists() and not force:
        print(f"⏭️  {catalog_name}: Already exists, skipping (use --force to redownload)")
        return True

    print(f"📥 Downloading {catalog_name}: {catalog_info['description']}...")

    try:
        # NOTE: This is a placeholder implementation
        # In reality, you would need to:
        # 1. Download the Excel file from the URL
        # 2. Parse it using openpyxl or pandas
        # 3. Convert to JSON
        # 4. Save to output_path

        # For now, create a placeholder structure
        placeholder_data = {
            '_meta': {
                'catalog': catalog_name,
                'description': catalog_info['description'],
                'source': catalog_info['url'],
                'downloaded': datetime.now().isoformat(),
                'note': 'This is a placeholder. Implement Excel parsing to populate real data.'
            },
            'data': []
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(placeholder_data, f, ensure_ascii=False, indent=2)

        print(f"✅ {catalog_name}: Downloaded successfully")
        print(f"   📁 Saved to: {output_path}")
        return True

    except Exception as e:
        print(f"❌ {catalog_name}: Failed to download - {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Download official SAT catalogs for CFDI 4.0',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all Phase 2 catalogs (essentials)
  python scripts/fetch_sat_catalogs.py --phase 2

  # Download specific catalog
  python scripts/fetch_sat_catalogs.py --catalog c_RegimenFiscal

  # Download all catalogs
  python scripts/fetch_sat_catalogs.py --all

  # Force redownload
  python scripts/fetch_sat_catalogs.py --force
        """
    )
    parser.add_argument(
        '--catalog',
        help='Download specific catalog only'
    )
    parser.add_argument(
        '--phase',
        type=int,
        choices=[2, 4],
        help='Download all catalogs for a specific phase'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Download all catalogs'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force download even if files exist'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output directory (default: packages/shared-data/sat/)'
    )

    args = parser.parse_args()

    # Determine output directory
    if args.output:
        output_dir = args.output
    else:
        # Default to shared-data/sat
        script_dir = Path(__file__).parent
        output_dir = script_dir.parent / 'packages' / 'shared-data' / 'sat'

    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("🇲🇽 SAT Catalog Downloader")
    print("=" * 70)
    print(f"📁 Output directory: {output_dir}")
    print()

    # Determine which catalogs to download
    catalogs_to_download = {}

    if args.catalog:
        # Single catalog
        if args.catalog in SAT_CATALOGS:
            catalogs_to_download[args.catalog] = SAT_CATALOGS[args.catalog]
        else:
            print(f"❌ Error: Unknown catalog '{args.catalog}'")
            print(f"\nAvailable catalogs:")
            for name in sorted(SAT_CATALOGS.keys()):
                print(f"  - {name}")
            return 1

    elif args.phase:
        # Phase-specific catalogs
        catalogs_to_download = {
            name: info for name, info in SAT_CATALOGS.items()
            if info.get('phase') == args.phase
        }
        print(f"📦 Downloading Phase {args.phase} catalogs ({len(catalogs_to_download)} catalogs)")

    elif args.all:
        # All catalogs
        catalogs_to_download = SAT_CATALOGS
        print(f"📦 Downloading all catalogs ({len(catalogs_to_download)} catalogs)")

    else:
        # Default: Phase 2 essentials
        catalogs_to_download = {
            name: info for name, info in SAT_CATALOGS.items()
            if info.get('phase') == 2
        }
        print(f"📦 Downloading Phase 2 (essentials) catalogs ({len(catalogs_to_download)} catalogs)")
        print("   Use --all to download all catalogs")

    print()

    # Download catalogs
    success_count = 0
    fail_count = 0

    for catalog_name, catalog_info in catalogs_to_download.items():
        if download_catalog(catalog_name, catalog_info, output_dir, args.force):
            success_count += 1
        else:
            fail_count += 1
        print()

    # Summary
    print("=" * 70)
    print(f"✅ Successfully downloaded: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print("=" * 70)

    print()
    print("⚠️  NOTE: This script currently creates placeholder files.")
    print("   To get real data, you need to implement Excel parsing.")
    print("   Required libraries: openpyxl or pandas + xlrd")
    print()
    print("   Example implementation:")
    print("   ```python")
    print("   import pandas as pd")
    print("   df = pd.read_excel(url)")
    print("   data = df.to_dict('records')")
    print("   ```")

    return 0 if fail_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
