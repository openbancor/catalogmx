#!/usr/bin/env python3
"""
Explore Banxico API catalog to find useful series

API Catalog endpoint: 
https://www.banxico.org.mx/SieAPIRest/service/v1/catalogo/series

This script downloads the full series catalog from Banxico
and helps identify useful series for catalogmx.
"""

import argparse
import json
import os
from urllib.request import Request, urlopen
from pathlib import Path

BANXICO_API = "https://www.banxico.org.mx/SieAPIRest/service/v1"


def fetch_catalog(token: str) -> list[dict]:
    """Fetch the complete series catalog from Banxico"""
    url = f"{BANXICO_API}/catalogo/series"
    
    headers = {
        "Bmx-Token": token,
        "Accept": "application/json",
    }
    
    print("[catalog] Fetching series catalog from Banxico...")
    
    request = Request(url, headers=headers)
    with urlopen(request, timeout=60) as response:
        data = json.loads(response.read().decode('utf-8'))
        
        if 'catalogo' not in data or 'series' not in data['catalogo']:
            raise ValueError("Unexpected API response format")
        
        series = data['catalogo']['series']
        print(f"[catalog] ✓ Retrieved {len(series)} series")
        return series


def search_series(catalog: list[dict], keywords: list[str]) -> list[dict]:
    """Search series by keywords in title"""
    keywords_lower = [k.lower() for k in keywords]
    
    results = []
    for serie in catalog:
        titulo = serie.get('titulo', '').lower()
        if any(keyword in titulo for keyword in keywords_lower):
            results.append(serie)
    
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token", default=os.environ.get("BANXICO_TOKEN"), help="Banxico API token")
    parser.add_argument("--search", nargs='+', help="Keywords to search (e.g., --search UDI TIIE CETES)")
    parser.add_argument("--output", type=Path, help="Save catalog to JSON file")
    
    args = parser.parse_args()
    
    if not args.token:
        print("ERROR: BANXICO_TOKEN required")
        print("Get one at: https://www.banxico.org.mx/SieAPIRest/service/v1/token")
        return 1
    
    try:
        catalog = fetch_catalog(args.token)
        
        # Save full catalog if requested
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(catalog, f, indent=2, ensure_ascii=False)
            print(f"[catalog] ✓ Saved {len(catalog)} series to {args.output}")
        
        # Search if keywords provided
        if args.search:
            results = search_series(catalog, args.search)
            print(f"\n[search] Found {len(results)} series matching: {', '.join(args.search)}\n")
            
            for serie in results[:20]:  # Limit to first 20
                print(f"📊 {serie.get('titulo', 'N/A')}")
                print(f"   ID: {serie.get('idSerie', 'N/A')}")
                print(f"   Periodicidad: {serie.get('periodicidad', 'N/A')}")
                if serie.get('fechaInicio'):
                    print(f"   Desde: {serie.get('fechaInicio')}")
                print()
            
            if len(results) > 20:
                print(f"... y {len(results) - 20} más")
        
        # Show useful categories
        else:
            print("\n=== SERIES ÚTILES PARA CATALOGMX ===\n")
            
            categories = {
                "Tasas de Interés": ["TIIE", "CETES", "TASA", "OBJETIVO"],
                "Tipo de Cambio": ["DOLAR", "EURO", "FIX", "CAMBIO"],
                "Inflación": ["INPC", "INFLACION", "PRECIOS"],
                "Reservas": ["RESERVAS", "INTERNACIONALES"],
            }
            
            for category, keywords in categories.items():
                results = search_series(catalog, keywords)
                print(f"📁 {category}: {len(results)} series encontradas")
                print(f"   Busca con: --search {' '.join(keywords[:2])}")
                print()
        
        return 0
        
    except Exception as e:
        print(f"[catalog] ERROR: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

