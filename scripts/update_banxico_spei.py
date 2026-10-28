#!/usr/bin/env python3
"""Regenerate the SPEI participant catalog (5-digit + 3-digit codes) from Banxico.

Source: ``https://www.banxico.org.mx/cep/instituciones.do?fecha=<dd-mm-aaaa>``,
the open CEP service (no credentials). It returns the participant list valid on
the requested date as ``{"instituciones": [[code5, name], ...]}``. The date is
mandatory and explicit so a run is reproducible and auditable.

The script reuses the fail-closed machinery of ``update_banxico_banks.py``
(shape/size/continuity validation, atomic two-file transaction) and then:

* writes ``spei_code`` (5-digit key; the official 4-digit ``2001`` for BANXICO)
  and ``status`` (``active``/``historical``) on every ``banks.json`` row;
* stamps provenance (``spei_source``, ``spei_verified_at``) on every row;
* marks the participants the project owner declared disaffiliated from SPEI
  (143, 608, 630) as historical, keeping their 3-digit code, with an unknown
  disaffiliation date (never invented).

Usage: ``python scripts/update_banxico_spei.py --fecha 2026-10-27``
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections.abc import Sequence
from datetime import date
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

_BASE_PATH = Path(__file__).resolve().parent / "update_banxico_banks.py"
_spec = importlib.util.spec_from_file_location("_update_banxico_banks_base", _BASE_PATH)
assert _spec is not None and _spec.loader is not None
_base = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _base
_spec.loader.exec_module(_base)

SPEI_URL = "https://www.banxico.org.mx/cep/instituciones.do"
SOURCE_LABEL = "Banxico CEP https://www.banxico.org.mx/cep/instituciones.do"
BANKS_PATH = _base.BANKS_PATH
SNAPSHOT_PATH = _base.SNAPSHOT_PATH
OWNER_DISAFFILIATED = frozenset({"143", "608", "630"})
OWNER_STATUS_SOURCE = (
    "Indicación del dueño del proyecto (2026-10-28): desafiliado de SPEI; "
    "la lista vigente de Banxico confirma su ausencia. Fecha de desafiliación desconocida."
)


def build_url(fecha_iso: str) -> str:
    """Build the service URL from an explicit ISO date (``aaaa-mm-dd``)."""
    try:
        parsed = date.fromisoformat(fecha_iso)
    except ValueError as exc:
        raise ValueError(f"fecha inválida {fecha_iso!r}: use aaaa-mm-dd") from exc
    return f"{SPEI_URL}?fecha={parsed.strftime('%d-%m-%Y')}"


def parse_payload(text: str) -> list[tuple[str, str]]:
    """Parse the service JSON into validated ``(code5, name)`` pairs."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise RuntimeError("Banxico SPEI response is not valid JSON") from exc
    rows = data.get("instituciones") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        raise RuntimeError("Banxico SPEI response has no 'instituciones' list")
    pairs: list[tuple[str, str]] = []
    for row in rows:
        if not (
            isinstance(row, list)
            and len(row) == 2
            and all(isinstance(v, str) for v in row)
        ):
            raise RuntimeError("Banxico SPEI row must be [code, name]")
        pairs.append((row[0], row[1]))
    return _base.validate_institutions(pairs)


def fetch_institutions(fecha_iso: str) -> list[tuple[str, str]]:
    request = Request(
        build_url(fecha_iso),
        headers={
            "Accept": "application/json",
            "User-Agent": "catalogmx-banxico-spei-maintenance",
        },
    )
    with urlopen(request, timeout=30) as response:  # noqa: S310
        charset = response.headers.get_content_charset() or "utf-8"
        payload = response.read().decode(charset, errors="strict")
    return parse_payload(payload)


def check_consistency(banks: Sequence[dict[str, Any]]) -> None:
    """Every ``spei_code`` must end with the row's 3-digit code and be unique per code."""
    seen: set[str] = set()
    for bank in banks:
        if bank["code"] in seen:
            raise RuntimeError(f"duplicate code {bank['code']}")
        seen.add(bank["code"])
        spei_code = bank.get("spei_code")
        if spei_code is not None and spei_code[-3:] != bank["code"]:
            raise RuntimeError(f"spei_code suffix mismatch for code {bank['code']}")


def build_catalog(
    existing: Sequence[dict[str, Any]],
    institutions: Sequence[tuple[str, str]],
    verified_at: str,
):
    """Merge the source into ``banks.json`` rows and stamp the SPEI fields."""
    merged, summary = _base.sync_banks(existing, institutions)
    for bank in merged:
        bank["spei_source"] = SOURCE_LABEL
        bank["spei_verified_at"] = verified_at
        if bank["code"] in OWNER_DISAFFILIATED and bank["status"] == "historical":
            bank["spei"] = False
            bank["spei_disaffiliated"] = True
            bank["spei_disaffiliation_date"] = None
            bank["status_source"] = OWNER_STATUS_SOURCE
    check_consistency(merged)
    return merged, summary


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fecha", required=True, help="Fecha de consulta aaaa-mm-dd")
    parser.add_argument("--banks-path", type=Path, default=BANKS_PATH)
    parser.add_argument("--snapshot-path", type=Path, default=SNAPSHOT_PATH)
    args = parser.parse_args(argv)
    try:
        institutions = fetch_institutions(args.fecha)
        _base.validate_snapshot_transition(
            _base.load_snapshot(args.snapshot_path), institutions
        )
        merged, summary = build_catalog(
            _base.load_banks(args.banks_path), institutions, args.fecha
        )
        _base.write_json_transaction(
            [
                (args.snapshot_path, _base.render_current_snapshot(institutions)),
                (args.banks_path, merged),
            ]
        )
    except (
        HTTPError,
        URLError,
        TimeoutError,
        OSError,
        ValueError,
        RuntimeError,
    ) as exc:
        print(f"Banxico SPEI maintenance failed: {exc}")
        return 1
    print(
        f"Banxico SPEI synchronized ({args.fecha}): current={summary.current}, "
        f"added={summary.added}, renamed={summary.renamed}, historical={summary.historical}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
