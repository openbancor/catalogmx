#!/usr/bin/env python3
"""Synchronize Banxico CEP institution reference data.

Banco de México publishes a live CEP-SCL institution list with the institution
key used by its payment systems and the current short name. CatalogMX stores
that current source snapshot separately from ``banks.json``: the latter is a
compatibility/enrichment view that also carries manually curated fields such as
RFC, legal name and institution type.

The updater is deliberately fail-closed. It validates the source shape and a
minimum plausible row count before writing anything, preserves historical
entries and manual enrichments, and never treats an empty/partial response as a
successful update.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parent.parent
CEP_LIST_URL = "https://www.banxico.org.mx/cep-scl/listaInstituciones.do"
BANKS_PATH = REPO_ROOT / "packages" / "shared-data" / "banxico" / "banks.json"
SNAPSHOT_PATH = (
    REPO_ROOT
    / "packages"
    / "shared-data"
    / "banxico"
    / "spei_institutions.json"
)
MIN_EXPECTED_INSTITUTIONS = 50


class InstitutionTableParser(HTMLParser):
    """Extract ``(Banxico key, short name)`` pairs from the CEP-SCL table."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._in_row = False
        self._in_cell = False
        self._cell_parts: list[str] = []
        self._row_cells: list[str] = []
        self.institutions: list[tuple[str, str]] = []

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        del attrs
        if tag == "tr":
            self._in_row = True
            self._row_cells = []
        elif self._in_row and tag in {"td", "th"}:
            self._in_cell = True
            self._cell_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_cell:
            self._cell_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self._in_cell and tag in {"td", "th"}:
            value = " ".join("".join(self._cell_parts).split())
            self._row_cells.append(value)
            self._in_cell = False
            self._cell_parts = []
            return

        if self._in_row and tag == "tr":
            if len(self._row_cells) >= 2:
                key = self._row_cells[0].strip()
                name = self._row_cells[1].strip()
                if key.isdigit() and name:
                    self.institutions.append((key, name))
            self._in_row = False
            self._row_cells = []


@dataclass(frozen=True)
class SyncSummary:
    current: int
    added: int
    renamed: int
    historical: int


def normalize_institution_key(raw_key: str) -> str:
    """Map Banxico's payment-system key to the 3-digit institution code."""
    key = raw_key.strip()
    if not key.isdigit() or len(key) not in {4, 5}:
        raise ValueError(f"invalid Banxico institution key: {raw_key!r}")
    return key[-3:].zfill(3)


def validate_institutions(
    institutions: Sequence[tuple[str, str]],
) -> list[tuple[str, str]]:
    """Validate source completeness and code uniqueness before mutation."""
    if len(institutions) < MIN_EXPECTED_INSTITUTIONS:
        raise RuntimeError(
            "Banxico CEP institution list looks incomplete: "
            f"expected at least {MIN_EXPECTED_INSTITUTIONS}, got {len(institutions)}"
        )

    raw_keys: set[str] = set()
    normalized_codes: set[str] = set()
    validated: list[tuple[str, str]] = []
    for raw_key, raw_name in institutions:
        key = raw_key.strip()
        name = " ".join(raw_name.split())
        if not name:
            raise RuntimeError(f"empty institution name for key {key!r}")
        if key in raw_keys:
            raise RuntimeError(f"duplicate Banxico institution key: {key}")
        raw_keys.add(key)

        code = normalize_institution_key(key)
        if code in normalized_codes:
            raise RuntimeError(
                "multiple Banxico institution keys collapse to compatibility "
                f"code {code}; source contract requires review"
            )
        normalized_codes.add(code)
        validated.append((key, name))

    return validated


def parse_institutions_html(payload: str) -> list[tuple[str, str]]:
    """Parse and validate the live Banxico CEP-SCL institution table."""
    parser = InstitutionTableParser()
    parser.feed(payload)
    parser.close()
    return validate_institutions(parser.institutions)


def fetch_institutions(url: str = CEP_LIST_URL) -> list[tuple[str, str]]:
    """Fetch the current authoritative CEP-SCL institution list."""
    request = Request(
        url,
        headers={
            "Accept": "text/html,application/xhtml+xml",
            "User-Agent": "catalogmx-banxico-reference-maintenance",
        },
    )
    with urlopen(request, timeout=30) as response:  # noqa: S310
        charset = response.headers.get_content_charset() or "utf-8"
        payload = response.read().decode(charset, errors="strict")
    return parse_institutions_html(payload)


def load_banks(path: Path = BANKS_PATH) -> list[dict[str, Any]]:
    """Load the enriched compatibility bank catalog."""
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        raise ValueError("banks catalog must be a JSON array")
    return data


def write_json(path: Path, payload: Any) -> None:
    """Write deterministic UTF-8 JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def render_current_snapshot(
    institutions: Sequence[tuple[str, str]],
) -> list[dict[str, str]]:
    """Render a source-faithful snapshot without manual enrichments."""
    return [
        {
            "banxico_key": key,
            "code": normalize_institution_key(key),
            "name": name,
        }
        for key, name in sorted(institutions, key=lambda item: int(item[0]))
    ]


def sync_banks(
    existing: Sequence[dict[str, Any]],
    institutions: Sequence[tuple[str, str]],
) -> tuple[list[dict[str, Any]], SyncSummary]:
    """Merge current Banxico source fields into the enriched compatibility view.

    Historical rows and manual enrichment fields are retained. Source-owned
    ``name``, ``banxico_key`` and ``cep_current`` are refreshed. ``spei`` is not
    inferred from absence in the CEP consultation list because that field has a
    broader compatibility meaning in existing CatalogMX APIs.
    """
    by_code: dict[str, dict[str, Any]] = {}
    for source_item in existing:
        item = dict(source_item)
        code = str(item.get("code", ""))
        if not code or code in by_code:
            raise ValueError(f"invalid or duplicate compatibility bank code: {code!r}")
        by_code[code] = item

    current_by_code: dict[str, tuple[str, str]] = {}
    for key, name in validate_institutions(institutions):
        code = normalize_institution_key(key)
        current_by_code[code] = (key, name)

    added = 0
    renamed = 0
    for code, item in by_code.items():
        current = current_by_code.get(code)
        if current is None:
            item["cep_current"] = False
            continue
        key, name = current
        if item.get("name") != name:
            item["name"] = name
            renamed += 1
        item["banxico_key"] = key
        item["cep_current"] = True

    for code, (key, name) in current_by_code.items():
        if code in by_code:
            continue
        by_code[code] = {
            "code": code,
            "name": name,
            "full_name": name,
            "rfc": None,
            "spei": True,
            "banxico_key": key,
            "cep_current": True,
        }
        added += 1

    merged = sorted(by_code.values(), key=lambda item: int(str(item["code"])))
    historical = sum(1 for item in merged if item.get("cep_current") is False)
    summary = SyncSummary(
        current=len(current_by_code),
        added=added,
        renamed=renamed,
        historical=historical,
    )
    return merged, summary


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-url", default=CEP_LIST_URL)
    parser.add_argument("--banks-path", type=Path, default=BANKS_PATH)
    parser.add_argument("--snapshot-path", type=Path, default=SNAPSHOT_PATH)
    args = parser.parse_args(argv)

    try:
        institutions = fetch_institutions(args.source_url)
        existing = load_banks(args.banks_path)
        merged, summary = sync_banks(existing, institutions)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, RuntimeError) as exc:
        print(f"Banxico reference maintenance failed: {exc}")
        return 1

    write_json(args.snapshot_path, render_current_snapshot(institutions))
    write_json(args.banks_path, merged)
    print(
        "Banxico reference synchronized: "
        f"current={summary.current}, added={summary.added}, "
        f"renamed={summary.renamed}, historical={summary.historical}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
