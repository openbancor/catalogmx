"""
Actualizar el catálogo de bancos (Banxico) desde el endpoint público del CEP.

Uso:
    python scripts/update_banxico_banks.py [--fecha dd-mm-aaaa]

Por defecto usa la fecha actual (formato requerido por el CEP).
Solo añade bancos nuevos; no elimina ni sobreescribe los existentes
para no perder campos (RFC, full_name) ya capturados a mano.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen


CEP_URL = "https://www.banxico.org.mx/cep/instituciones.do?fecha={fecha}"
BANKS_PATH = Path(__file__).resolve().parent.parent / "packages" / "shared-data" / "banxico" / "banks.json"


def fetch_instituciones(fecha: str) -> list[tuple[str, str]]:
    """Descarga instituciones del CEP (código, nombre)."""
    url = CEP_URL.format(fecha=fecha)
    with urlopen(url, timeout=15) as resp:  # nosec: B310 - endpoint oficial público
        payload = resp.read().decode("utf-8")
    data = json.loads(payload)
    instituciones = data.get("instituciones", [])
    return [(item[0], item[1]) for item in instituciones if len(item) >= 2]


def load_banks() -> list[dict[str, Any]]:
    with BANKS_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def save_banks(banks: list[dict[str, Any]]) -> None:
    banks_sorted = sorted(banks, key=lambda b: int(b["code"]))
    with BANKS_PATH.open("w", encoding="utf-8") as f:
        json.dump(banks_sorted, f, ensure_ascii=False, indent=2)
        f.write("\n")


def merge_instituciones(existing: list[dict[str, Any]], nuevas: list[tuple[str, str]]) -> list[dict[str, Any]]:
    by_code = {b["code"]: b for b in existing}
    added = 0
    for raw_code, name in nuevas:
        code3 = raw_code[-3:].zfill(3)
        if code3 in by_code:
            continue
        by_code[code3] = {
            "code": code3,
            "name": name,
            "full_name": name,
            "rfc": None,
            "spei": True,
        }
        added += 1
    if added:
        print(f"Añadidos {added} bancos nuevos desde CEP.")
    else:
        print("Sin cambios: no se encontraron bancos nuevos en CEP.")
    return list(by_code.values())


def main() -> int:
    parser = argparse.ArgumentParser(description="Actualiza packages/shared-data/banxico/banks.json desde CEP Banxico.")
    parser.add_argument("--fecha", help="Fecha dd-mm-aaaa (por defecto hoy)", default=None)
    args = parser.parse_args()

    fecha = args.fecha
    if not fecha:
        hoy = datetime.now(timezone.utc)
        fecha = hoy.strftime("%d-%m-%Y")

    try:
        instituciones = fetch_instituciones(fecha)
    except URLError as exc:  # pragma: no cover - red fallida
        print(f"Error al descargar instituciones CEP: {exc}")
        return 1

    if not instituciones:
        print("CEP no devolvió instituciones; no se realizan cambios.")
        return 0

    banks = load_banks()
    merged = merge_instituciones(banks, instituciones)
    save_banks(merged)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
