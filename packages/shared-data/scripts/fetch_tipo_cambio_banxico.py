#!/usr/bin/env python3
"""
Fetch USD/MXN exchange rate from Banxico API

Serie: SF43718 - Tipo de cambio FIX (USD/MXN)
Periodicidad: Diaria
Inicio: 1991-11-08
"""

import argparse
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_ROOT = SCRIPT_DIR.parent
OUTPUT_FILE = DATA_ROOT / "banxico" / "tipo_cambio_usd.json"

BANXICO_API = "https://www.banxico.org.mx/SieAPIRest/service/v1"
EXCHANGE_RATE_SERIES = "SF43718"  # Serie: Tipo de cambio FIX USD/MXN

RATE_LIMIT_DELAY = 0.7
_last_request_time = 0.0


def rate_limit():
    """Ensure we don't exceed Banxico's rate limit (100 req/min)"""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < RATE_LIMIT_DELAY:
        time.sleep(RATE_LIMIT_DELAY - elapsed)
    _last_request_time = time.time()


def fetch_chunk(token: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
    """Fetch exchange rate data for a specific date range"""
    url = f"{BANXICO_API}/series/{EXCHANGE_RATE_SERIES}/datos/{start_date}/{end_date}"
    
    headers = {
        "Bmx-Token": token,
        "Accept": "application/json",
    }
    
    rate_limit()
    
    request = Request(url, headers=headers)
    with urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode('utf-8'))
        
        if 'bmx' not in data or 'series' not in data['bmx']:
            raise ValueError(f"Unexpected API response format")
        
        series = data['bmx']['series'][0]
        if 'datos' not in series or not series['datos']:
            return []
        
        series_data = series['datos']
        
        records = []
        for item in series_data:
            fecha = item['fecha']
            valor = float(item['dato']) if item['dato'] else None
            
            if valor is None:
                continue
            
            date_obj = datetime.strptime(fecha, '%d/%m/%Y')
            
            records.append({
                "fecha": date_obj.strftime('%Y-%m-%d'),
                "tipo_cambio": valor,
                "moneda_origen": "USD",
                "moneda_destino": "MXN",
                "tipo": "oficial_banxico_fix",
                "año": date_obj.year,
                "mes": date_obj.month,
                "fuente": "Banco de México - Tipo de cambio FIX"
            })
        
        return records


def get_last_date_in_file(filepath: Path) -> str | None:
    """Get the last date in the existing file"""
    if not filepath.exists():
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not data:
                return None
            last_record = max(data, key=lambda x: x['fecha'])
            return last_record['fecha']
    except Exception:
        return None


def fetch_data(token: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
    """Fetch exchange rate data in chunks"""
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    all_records = []
    current = start
    
    print(f"[fetch] Fetching USD/MXN from {start_date} to {end_date}...")
    print(f"[fetch] Using rate limit: {RATE_LIMIT_DELAY}s between requests")
    
    try:
        while current <= end:
            chunk_end = min(current + timedelta(days=365), end)
            
            chunk_start_str = current.strftime('%Y-%m-%d')
            chunk_end_str = chunk_end.strftime('%Y-%m-%d')
            
            print(f"[fetch] {chunk_start_str} to {chunk_end_str}...", end=' ')
            
            records = fetch_chunk(token, chunk_start_str, chunk_end_str)
            all_records.extend(records)
            
            print(f"✓ {len(records)} records")
            
            current = chunk_end + timedelta(days=1)
        
        print(f"[fetch] ✓ Total: {len(all_records)} records")
        return all_records
            
    except HTTPError as e:
        if e.code == 401:
            raise ValueError("Invalid Banxico token")
        elif e.code == 429:
            raise ValueError("Rate limit exceeded")
        raise ValueError(f"HTTP Error {e.code}: {e.reason}")
    except Exception as e:
        raise ValueError(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token", default=os.environ.get("BANXICO_TOKEN"))
    parser.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", default=datetime.now().strftime('%Y-%m-%d'))
    parser.add_argument("--output", type=Path, default=OUTPUT_FILE)
    parser.add_argument("--full", action="store_true")
    
    args = parser.parse_args()
    
    if not args.token:
        print("ERROR: BANXICO_TOKEN required")
        return 1
    
    # Determine start date
    start_date = args.start_date
    if not start_date:
        if args.full:
            start_date = "1991-11-08"
            print("[fetch] Full download: starting from 1991-11-08")
        else:
            last_date = get_last_date_in_file(args.output)
            if last_date:
                start_date_obj = datetime.strptime(last_date, '%Y-%m-%d') + timedelta(days=1)
                start_date = start_date_obj.strftime('%Y-%m-%d')
                print(f"[fetch] Incremental: last={last_date}, fetching from {start_date}")
            else:
                start_date = "1991-11-08"
                print("[fetch] No data found, starting from 1991-11-08")
    
    # Check if up to date
    if start_date > args.end_date:
        print(f"[fetch] ✓ Already up to date (last: {get_last_date_in_file(args.output)})")
        return 0
    
    try:
        new_records = fetch_data(args.token, start_date, args.end_date)
        
        if not new_records:
            print("[fetch] No new records")
            return 1
        
        # Merge with existing
        all_records = new_records
        if not args.full and args.output.exists():
            try:
                with open(args.output, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                    if existing:
                        print(f"[fetch] Merging with {len(existing)} existing...")
                        all_records = existing + new_records
            except Exception as e:
                print(f"[fetch] Warning: {e}")
        
        # Deduplicate and sort
        unique = {r['fecha']: r for r in all_records}
        records = sorted(unique.values(), key=lambda x: x['fecha'])
        
        # Write
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        
        print(f"[fetch] ✓ Saved {len(records)} total records")
        print(f"[fetch] Range: {records[0]['fecha']} to {records[-1]['fecha']}")
        print(f"[fetch] Latest: {records[-1]['tipo_cambio']} MXN per USD")
        print(f"[fetch] New: {len(new_records)}")
        
        return 0
        
    except ValueError as e:
        print(f"[fetch] ERROR: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

