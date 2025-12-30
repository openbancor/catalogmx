#!/usr/bin/env python3
"""
Fetch Salarios Mínimos from Banxico API and write to SQLite

Series:
- SL2538: Salarios Mínimos General (hasta nov-2012)
- SL2542: Índices Reales (1994=100) General (hasta nov-2012)
- SL11126: Salarios Mínimos General (dic-2012 a dic-2018)
- SL11127: Índices Reales (Dic2012=100) General (dic-2012 a dic-2018)
- SL11298: Salarios Mínimos General (desde dic-2018)
- SL11295: Zona Libre de la Frontera Norte (desde dic-2018)
- SL11297: Índices Reales General (Dic2018=100) (desde dic-2018)
- SL11296: Índices Reales Zona Libre (Dic2018=100) (desde dic-2018)
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
from banxico_sqlite_helper import ensure_database_exists, get_last_date, save_to_db, get_table_stats, DB_FILE

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_ROOT = SCRIPT_DIR.parent

BANXICO_API = "https://www.banxico.org.mx/SieAPIRest/service/v1"

# Series de salarios mínimos
SALARY_SERIES = {
    # Histórico hasta 2012
    "SL2538": {
        "name": "Salarios Mínimos General",
        "period": "hasta_nov_2012",
        "start_date": "1976-01-01",
        "type": "nominal",
        "zone": "general"
    },
    "SL2542": {
        "name": "Índices Reales (1994=100) General",
        "period": "hasta_nov_2012",
        "start_date": "1976-01-01",
        "type": "real",
        "zone": "general",
        "base_year": 1994
    },
    # Período 2012-2018
    "SL11126": {
        "name": "Salarios Mínimos General",
        "period": "dic_2012_dic_2018",
        "start_date": "2012-12-01",
        "type": "nominal",
        "zone": "general"
    },
    "SL11127": {
        "name": "Índices Reales (Dic2012=100) General",
        "period": "dic_2012_dic_2018",
        "start_date": "2012-12-01",
        "type": "real",
        "zone": "general",
        "base_year": 2012
    },
    # Desde 2018
    "SL11298": {
        "name": "Salarios Mínimos General",
        "period": "desde_dic_2018",
        "start_date": "2018-12-01",
        "type": "nominal",
        "zone": "general"
    },
    "SL11295": {
        "name": "Zona Libre de la Frontera Norte",
        "period": "desde_dic_2018",
        "start_date": "2018-12-01",
        "type": "nominal",
        "zone": "frontera_norte"
    },
    "SL11297": {
        "name": "Índices Reales General (Dic2018=100)",
        "period": "desde_dic_2018",
        "start_date": "2018-12-01",
        "type": "real",
        "zone": "general",
        "base_year": 2018
    },
    "SL11296": {
        "name": "Índices Reales Zona Libre (Dic2018=100)",
        "period": "desde_dic_2018",
        "start_date": "2018-12-01",
        "type": "real",
        "zone": "frontera_norte",
        "base_year": 2018
    }
}

RATE_LIMIT_DELAY = 0.7
_last_request_time = 0.0


def rate_limit():
    """Ensure we don't exceed Banxico's rate limit (100 req/min)"""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < RATE_LIMIT_DELAY:
        time.sleep(RATE_LIMIT_DELAY - elapsed)
    _last_request_time = time.time()


def fetch_series_chunk(token: str, series_id: str, series_info: dict, start_date: str, end_date: str) -> list[dict[str, Any]]:
    """Fetch salary data for a specific series and date range"""
    url = f"{BANXICO_API}/series/{series_id}/datos/{start_date}/{end_date}"

    headers = {
        "Bmx-Token": token,
        "Accept": "application/json",
    }

    rate_limit()

    request = Request(url, headers=headers)
    with urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode('utf-8'))

        if 'bmx' not in data or 'series' not in data['bmx']:
            raise ValueError(f"Unexpected API response format for {series_id}")

        series_data = data['bmx']['series'][0]
        if 'datos' not in series_data or not series_data['datos']:
            return []

        records = []
        for item in series_data['datos']:
            fecha = item['fecha']
            valor = float(item['dato']) if item['dato'] else None

            if valor is None:
                continue

            # Banxico returns data in format "01/MM/YYYY"
            date_obj = datetime.strptime(fecha, '%d/%m/%Y')

            record = {
                "fecha": date_obj.strftime('%Y-%m-%d'),
                "salario_minimo": valor,
                "tipo": series_info["type"],
                "zona": series_info["zone"],
                "periodo": series_info["period"],
                "serie": series_id,
                "año": date_obj.year,
                "mes": date_obj.month,
                "fuente": "Banco de México - Salarios Mínimos"
            }

            if "base_year" in series_info:
                record["base_year"] = series_info["base_year"]

            records.append(record)

        return records


def fetch_all_series(token: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
    """Fetch salary data from all relevant series"""
    all_records = []

    print(f"[fetch] Fetching Salarios Mínimos from {start_date} to {end_date}...")
    print(f"[fetch] Using rate limit: {RATE_LIMIT_DELAY}s between requests")

    for series_id, series_info in SALARY_SERIES.items():
        print(f"[fetch] Series {series_id}: {series_info['name']}")

        try:
            # Only fetch if the series period overlaps with our date range
            series_start = series_info["start_date"]
            if series_start > end_date:
                print(f"[fetch]   Skipping {series_id} (starts after end date)")
                continue

            effective_start = max(start_date, series_start)
            effective_end = end_date

            if effective_start > effective_end:
                print(f"[fetch]   Skipping {series_id} (no overlap)")
                continue

            records = fetch_series_chunk(token, series_id, series_info, effective_start, effective_end)
            all_records.extend(records)
            print(f"[fetch]   ✓ {len(records)} records")

        except Exception as e:
            print(f"[fetch]   ⚠️ Error with {series_id}: {e}")
            continue

    print(f"[fetch] ✓ Total records from all series: {len(all_records)}")
    return all_records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token", default=os.environ.get("BANXICO_TOKEN"))
    parser.add_argument("--start-date", help="Start date (YYYY-MM-DD)")
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
            start_date = "1976-01-01"
            print("[fetch] Full download: starting from 1976-01-01")
        else:
            last_date = get_last_date(args.database, "salarios_minimos", where_clause="zona = 'general'")
            if last_date:
                start_date_obj = datetime.strptime(last_date, '%Y-%m-%d') + timedelta(days=32)  # Next month
                start_date = start_date_obj.strftime('%Y-%m-01')
                print(f"[fetch] Incremental: last={last_date}, fetching from {start_date}")
            else:
                start_date = "1976-01-01"
                print("[fetch] No data found, starting from 1976-01-01")

    # Check if up to date
    if start_date > args.end_date:
        last_date = get_last_date(args.database, "salarios_minimos", where_clause="zona = 'general'")
        print(f"[fetch] ✓ Already up to date (last: {last_date})")
        return 0

    try:
        new_records = fetch_all_series(args.token, start_date, args.end_date)

        if not new_records:
            print("[fetch] No new records")
            return 1

        # Save to database
        inserted_count = save_to_db(args.database, "salarios_minimos", new_records)

        print(f"[fetch] ✓ Saved {inserted_count} records to database")
        if new_records:
            print(f"[fetch] Latest: ${new_records[-1]['salario_minimo']:.2f} ({new_records[-1]['zona']}, {new_records[-1]['fecha']})")

        # Get total count from database
        stats = get_table_stats(args.database, "salarios_minimos")
        print(f"[fetch] Total records in database: {stats['count']:,}")
        if stats['min_date'] and stats['max_date']:
            print(f"[fetch] Database date range: {stats['min_date']} to {stats['max_date']}")

        return 0

    except ValueError as e:
        print(f"[fetch] ERROR: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
