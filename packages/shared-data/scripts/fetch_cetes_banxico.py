#!/usr/bin/env python3
"""
Fetch CETES 28 days from Banxico API and write to SQLite

Serie: SF43936 - CETES 28 días
Periodicidad: Semanal (publicación en subastas)
Inicio: 1978-01-05
Descripción: Tasa de rendimiento de Certificados de la Tesorería (CETES) a 28 días
"""

import argparse
import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from banxico_sqlite_helper import ensure_database_exists, get_last_date, save_to_db, get_table_stats, DB_FILE

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_ROOT = SCRIPT_DIR.parent

BANXICO_API = "https://www.banxico.org.mx/SieAPIRest/service/v1"
CETES_SERIES = "SF43936"

RATE_LIMIT_DELAY = 0.7
_last_request_time = 0.0


def rate_limit():
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < RATE_LIMIT_DELAY:
        time.sleep(RATE_LIMIT_DELAY - elapsed)
    _last_request_time = time.time()


def fetch_chunk(token: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
    url = f"{BANXICO_API}/series/{CETES_SERIES}/datos/{start_date}/{end_date}"
    headers = {"Bmx-Token": token, "Accept": "application/json"}
    
    rate_limit()
    
    request = Request(url, headers=headers)
    with urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode('utf-8'))
        
        series = data['bmx']['series'][0]
        if 'datos' not in series or not series['datos']:
            return []
        
        records = []
        for item in series['datos']:
            dato = item['dato']
            if not dato or dato == 'N/E':
                continue
            try:
                valor = float(dato)
            except (ValueError, TypeError):
                continue
            
            date_obj = datetime.strptime(item['fecha'], '%d/%m/%Y')
            
            records.append({
                "fecha": date_obj.strftime('%Y-%m-%d'),
                "plazo": 28,
                "tasa": valor,
                "anio": date_obj.year,
                "mes": date_obj.month
            })
        
        return records


def fetch_data(token: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    all_records = []
    current = start
    
    print(f"[fetch] Fetching CETES 28d from {start_date} to {end_date}...")
    
    while current <= end:
        chunk_end = min(current + timedelta(days=365), end)
        print(f"[fetch] {current.strftime('%Y-%m-%d')} to {chunk_end.strftime('%Y-%m-%d')}...", end=' ')
        
        records = fetch_chunk(token, current.strftime('%Y-%m-%d'), chunk_end.strftime('%Y-%m-%d'))
        all_records.extend(records)
        print(f"✓ {len(records)}")
        
        current = chunk_end + timedelta(days=1)
    
    print(f"[fetch] ✓ Total: {len(all_records)}")
    return all_records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token", default=os.environ.get("BANXICO_TOKEN"))
    parser.add_argument("--start-date")
    parser.add_argument("--end-date", default=datetime.now().strftime('%Y-%m-%d'))
    parser.add_argument("--database", type=Path, default=DB_FILE)
    parser.add_argument("--full", action="store_true")
    
    args = parser.parse_args()
    
    if not args.token:
        print("ERROR: BANXICO_TOKEN required")
        return 1

    # Ensure database exists
    ensure_database_exists(args.database)

    # Determine start date
    start_date = args.start_date
    if not start_date:
        if args.full:
            start_date = "1978-01-05"
            print("[fetch] Full download: starting from 1978-01-05")
        else:
            last_date = get_last_date(args.database, "cetes", where_clause="plazo = 28")
            if last_date:
                start_date_obj = datetime.strptime(last_date, '%Y-%m-%d') + timedelta(days=1)
                start_date = start_date_obj.strftime('%Y-%m-%d')
                print(f"[fetch] Incremental: last={last_date}, fetching from {start_date}")
            else:
                start_date = "1978-01-05"
                print("[fetch] No data found, starting from 1978-01-05")

    # Check if up to date
    if start_date > args.end_date:
        last_date = get_last_date(args.database, "cetes", where_clause="plazo = 28")
        print(f"[fetch] ✓ Already up to date (last: {last_date})")
        return 0

    try:
        new_records = fetch_data(args.token, start_date, args.end_date)

        if not new_records:
            print("[fetch] No new records")
            return 1

        # Save to database
        inserted_count = save_to_db(args.database, "cetes", new_records)

        print(f"[fetch] ✓ Saved {inserted_count} records to database")
        print(f"[fetch] Latest: {new_records[-1]['tasa']}% ({new_records[-1]['fecha']})")

        # Get total count from database
        stats = get_table_stats(args.database, "cetes")
        print(f"[fetch] Total records in database: {stats['count']:,}")
        if stats['min_date'] and stats['max_date']:
            print(f"[fetch] Database date range: {stats['min_date']} to {stats['max_date']}")

        return 0
    except ValueError as e:
        print(f"[fetch] ERROR: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

