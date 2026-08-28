#!/usr/bin/env python3
"""
Fetch USD/MXN exchange rate historical series from Banxico API and write to SQLite

Serie: SF63528 - Tipo de cambio peso dólar desde 1954 (serie histórica)
Periodicidad: Diaria
Inicio: 1954-01-01
Descripción: Serie histórica completa del tipo de cambio USD/MXN
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
from banxico_sqlite_helper import (
    DB_FILE,
    EXIT_ERROR,
    EXIT_NO_OBSERVATION,
    EXIT_SUCCESS,
    ensure_database_exists,
    get_last_date,
    save_to_db,
    get_table_stats,
)

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_ROOT = SCRIPT_DIR.parent

BANXICO_API = "https://www.banxico.org.mx/SieAPIRest/service/v1"
EXCHANGE_RATE_SERIES = "SF63528"  # Serie histórica completa

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
            raise ValueError("Unexpected API response format")

        series = data['bmx']['series'][0]
        if 'datos' not in series or not series['datos']:
            return []

        records = []
        for item in series['datos']:
            fecha = item['fecha']
            valor = float(item['dato']) if item['dato'] else None

            if valor is None:
                continue

            date_obj = datetime.strptime(fecha, '%d/%m/%Y')

            records.append({
                "fecha": date_obj.strftime('%Y-%m-%d'),
                "tipo_cambio": valor,
                "fuente": "historico",
                "anio": date_obj.year,
                "mes": date_obj.month,
                "moneda_origen": "USD",
                "moneda_destino": "MXN"
            })

        return records


def fetch_data(token: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
    """Fetch exchange rate data in chunks"""
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')

    all_records = []
    current = start

    print(f"[fetch] Fetching USD/MXN Historical from {start_date} to {end_date}...")
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
    parser.add_argument("--database", type=Path, default=DB_FILE)
    parser.add_argument("--full", action="store_true")

    args = parser.parse_args()

    if not args.token:
        print("ERROR: BANXICO_TOKEN required")
        return EXIT_ERROR

    ensure_database_exists(args.database)

    start_date = args.start_date
    if not start_date:
        if args.full:
            start_date = "1954-01-01"
            print("[fetch] Full download: starting from 1954-01-01")
        else:
            last_date = get_last_date(args.database, "tipo_cambio", where_clause="fuente = 'historico'")
            if last_date:
                start_date_obj = datetime.strptime(last_date, '%Y-%m-%d') + timedelta(days=1)
                start_date = start_date_obj.strftime('%Y-%m-%d')
                print(f"[fetch] Incremental: last={last_date}, fetching from {start_date}")
            else:
                start_date = "1954-01-01"
                print("[fetch] No data found, starting from 1954-01-01")

    if start_date > args.end_date:
        last_date = get_last_date(args.database, "tipo_cambio", where_clause="fuente = 'historico'")
        print(f"[fetch] ✓ Already up to date (last: {last_date})")
        return EXIT_SUCCESS

    try:
        new_records = fetch_data(args.token, start_date, args.end_date)

        if not new_records:
            print("[fetch] No new records")
            return EXIT_NO_OBSERVATION

        inserted_count = save_to_db(args.database, "tipo_cambio", new_records)

        print(f"[fetch] ✓ Saved {inserted_count} records to database")
        print(f"[fetch] Latest: {new_records[-1]['tipo_cambio']} MXN per USD ({new_records[-1]['fecha']})")

        stats = get_table_stats(args.database, "tipo_cambio")
        print(f"[fetch] Total records in database: {stats['count']:,}")
        if stats['min_date'] and stats['max_date']:
            print(f"[fetch] Database date range: {stats['min_date']} to {stats['max_date']}")

        return EXIT_SUCCESS

    except ValueError as e:
        print(f"[fetch] ERROR: {e}")
        return EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
