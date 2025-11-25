#!/usr/bin/env python3
"""
Fetch historical UDI data from Banxico API and update udis.json

API Documentation: https://www.banxico.org.mx/SieAPIRest/service/v1/
Series: SF43718 (UDI)
Rate Limit: 100 requests per minute per token

Requires: BANXICO_TOKEN environment variable or pass as --token argument
Get your token at: https://www.banxico.org.mx/SieAPIRest/service/v1/token
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
UDIS_FILE = DATA_ROOT / "banxico" / "udis.json"

# Banxico API configuration
BANXICO_API = "https://www.banxico.org.mx/SieAPIRest/service/v1"
UDI_SERIES = "SF43718"  # Serie de UDI

# Rate limiting
RATE_LIMIT_DELAY = 0.7  # seconds between requests (allows ~85 req/min, under 100 limit)
_last_request_time = 0.0


def rate_limit():
    """Ensure we don't exceed Banxico's rate limit (100 req/min)"""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < RATE_LIMIT_DELAY:
        time.sleep(RATE_LIMIT_DELAY - elapsed)
    _last_request_time = time.time()


def fetch_udi_chunk(token: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
    """
    Fetch UDI data for a specific date range
    """
    url = f"{BANXICO_API}/series/{UDI_SERIES}/datos/{start_date}/{end_date}"
    
    headers = {
        "Bmx-Token": token,
        "Accept": "application/json",
    }
    
    # Apply rate limiting
    rate_limit()
    
    request = Request(url, headers=headers)
    with urlopen(request, timeout=30) as response:
        data = json.loads(response.read().decode('utf-8'))
        
        if 'bmx' not in data or 'series' not in data['bmx']:
            raise ValueError(f"Unexpected API response format")
        
        # Handle case where no data is available yet for the requested dates
        series = data['bmx']['series'][0]
        if 'datos' not in series or not series['datos']:
            return []  # No data available for this date range yet
        
        series_data = series['datos']
        
        # Transform to our format
        records = []
        for item in series_data:
            fecha = item['fecha']
            valor = float(item['dato']) if item['dato'] else None
            
            if valor is None:
                continue
            
            # Parse date (Banxico format: DD/MM/YYYY)
            date_obj = datetime.strptime(fecha, '%d/%m/%Y')
            
            records.append({
                "fecha": date_obj.strftime('%Y-%m-%d'),
                "valor": valor,
                "moneda": "MXN",
                "tipo": "oficial_banxico",
                "año": date_obj.year,
                "mes": date_obj.month,
                "notas": "Valor oficial publicado por Banco de México"
            })
        
        return records


def fetch_udi_data(token: str, start_date: str, end_date: str) -> list[dict[str, Any]]:
    """
    Fetch UDI data from Banxico API in chunks to respect rate limits
    
    Args:
        token: Banxico API token
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        List of UDI records
    """
    # Parse dates
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Fetch in 1-year chunks to avoid overwhelming the API
    all_records = []
    current = start
    
    print(f"[fetch] Fetching UDI data from {start_date} to {end_date}...")
    print(f"[fetch] Using rate limit: {RATE_LIMIT_DELAY}s between requests (~85 req/min)")
    
    try:
        while current <= end:
            chunk_end = min(current + timedelta(days=365), end)
            
            chunk_start_str = current.strftime('%Y-%m-%d')
            chunk_end_str = chunk_end.strftime('%Y-%m-%d')
            
            print(f"[fetch] Requesting {chunk_start_str} to {chunk_end_str}...", end=' ')
            
            records = fetch_udi_chunk(token, chunk_start_str, chunk_end_str)
            all_records.extend(records)
            
            print(f"✓ {len(records)} records")
            
            current = chunk_end + timedelta(days=1)
        
        print(f"[fetch] ✓ Total retrieved: {len(all_records)} UDI records")
        return all_records
            
    except HTTPError as e:
        if e.code == 401:
            raise ValueError("Invalid Banxico API token. Get one at https://www.banxico.org.mx/SieAPIRest/service/v1/token")
        elif e.code == 429:
            raise ValueError("Rate limit exceeded. The script already implements delays, but Banxico may have additional limits.")
        raise ValueError(f"HTTP Error {e.code}: {e.reason}")
    except URLError as e:
        raise ValueError(f"Failed to connect to Banxico API: {e.reason}")
    except Exception as e:
        raise ValueError(f"Error fetching UDI data: {e}")


def get_last_date_in_file(filepath: Path) -> str | None:
    """Get the last date in the existing file"""
    if not filepath.exists():
        return None
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not data:
                return None
            # Assuming data is sorted by date
            last_record = max(data, key=lambda x: x['fecha'])
            return last_record['fecha']
    except Exception as e:
        print(f"[fetch] Warning: Could not read existing file: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--token",
        help="Banxico API token (or set BANXICO_TOKEN env var)",
        default=os.environ.get("BANXICO_TOKEN"),
    )
    parser.add_argument(
        "--start-date",
        help="Start date (YYYY-MM-DD). Default: auto-detect from existing file or 1995-04-04",
    )
    parser.add_argument(
        "--end-date",
        default=datetime.now().strftime('%Y-%m-%d'),
        help="End date (YYYY-MM-DD). Default: today",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=UDIS_FILE,
        help=f"Output file. Default: {UDIS_FILE}",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Force full download from 1995 (ignores existing data)",
    )
    
    args = parser.parse_args()
    
    if not args.token:
        print("ERROR: Banxico API token required.")
        print("")
        print("Get your FREE token at:")
        print("https://www.banxico.org.mx/SieAPIRest/service/v1/token")
        print("")
        print("Then set it in your environment:")
        print(f"  export BANXICO_TOKEN='your_token_here'")
        print(f"  ./scripts/full_check.sh")
        print("")
        print("Or pass directly:")
        print(f"  python {Path(__file__).name} --token your_token_here")
        return 1
    
    # Determine start date
    start_date = args.start_date
    if not start_date:
        if args.full:
            start_date = "1995-04-04"
            print("[fetch] Full download mode: starting from UDI inception (1995-04-04)")
        else:
            last_date = get_last_date_in_file(args.output)
            if last_date:
                # Start from day after last record
                last_date_obj = datetime.strptime(last_date, '%Y-%m-%d')
                start_date_obj = last_date_obj + timedelta(days=1)
                start_date = start_date_obj.strftime('%Y-%m-%d')
                print(f"[fetch] Incremental mode: last record is {last_date}, fetching from {start_date}")
            else:
                start_date = "1995-04-04"
                print("[fetch] No existing data found, starting from UDI inception (1995-04-04)")
    
    # Banxico publishes with 1-2 day delay, adjust end date if needed
    today = datetime.now().date()
    requested_end = datetime.strptime(args.end_date, '%Y-%m-%d').date()
    
    # Calculate the expected last available date (2 days ago to be safe)
    expected_last_date = today - timedelta(days=2)
    expected_last_date_str = expected_last_date.strftime('%Y-%m-%d')
    
    if requested_end >= today:
        # Request until 2 days ago to account for publication delay
        args.end_date = expected_last_date_str
        print(f"[fetch] Adjusted end date to {args.end_date} (Banxico publishes with 1-2 day delay)")
    
    # Parse dates for comparison
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date_obj = datetime.strptime(args.end_date, '%Y-%m-%d').date()
    
    # Check if start date is already beyond what Banxico would have
    if start_date_obj > expected_last_date:
        last_date = get_last_date_in_file(args.output)
        print(f"[fetch] ✓ Data is already up to date")
        print(f"[fetch]   Last record: {last_date}")
        print(f"[fetch]   Expected Banxico latest: {expected_last_date_str}")
        print(f"[fetch]   Next fetch will be possible after: {(expected_last_date + timedelta(days=1)).strftime('%Y-%m-%d')}")
        return 0
    
    # Check if we need to fetch anything
    if start_date_obj > end_date_obj:
        last_date = get_last_date_in_file(args.output)
        print(f"[fetch] ✓ Data is already up to date (last: {last_date})")
        return 0
    
    try:
        new_records = fetch_udi_data(args.token, start_date, args.end_date)
        
        if not new_records:
            print("[fetch] No new records retrieved")
            return 1
        
        # Merge with existing data
        all_records = new_records
        if not args.full and args.output.exists():
            try:
                with open(args.output, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                    if existing:
                        print(f"[fetch] Merging with {len(existing)} existing records...")
                        all_records = existing + new_records
            except Exception as e:
                print(f"[fetch] Warning: Could not merge with existing data: {e}")
        
        # Remove duplicates and sort
        unique_records = {r['fecha']: r for r in all_records}
        records = sorted(unique_records.values(), key=lambda x: x['fecha'])
        
        # Write to file
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(records, f, indent=2, ensure_ascii=False)
        
        print(f"[fetch] ✓ Saved {len(records)} total UDI records to {args.output}")
        print(f"[fetch] Date range: {records[0]['fecha']} to {records[-1]['fecha']}")
        print(f"[fetch] Latest UDI: {records[-1]['valor']} MXN ({records[-1]['fecha']})")
        print(f"[fetch] New records added: {len(new_records)}")
        
        return 0
        
    except ValueError as e:
        print(f"[fetch] ERROR: {e}")
        return 1
    except Exception as e:
        print(f"[fetch] Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())

