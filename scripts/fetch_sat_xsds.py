#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Download SAT XSDs recursively for CFDI 4.0."""

from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urljoin, urlparse
import xml.etree.ElementTree as ET

import requests

DEFAULT_ENTRY_URLS = [
    "http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd",
    "http://www.sat.gob.mx/sitio_internet/cfd/catalogos/catCFDI.xsd",
    "http://www.sat.gob.mx/sitio_internet/cfd/TimbreFiscalDigital/TimbreFiscalDigital.xsd",
    "http://www.sat.gob.mx/sitio_internet/cfd/Pagos/Pagos20.xsd",
    "http://www.sat.gob.mx/sitio_internet/cfd/nomina/nomina12.xsd",
    "http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte30.xsd",
    "http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte31.xsd",
    "http://www.sat.gob.mx/sitio_internet/cfd/ComercioExterior11/ComercioExterior11.xsd",
]

DEFAULT_XSLT_URLS = [
    "http://www.sat.gob.mx/sitio_internet/cfd/2/cadenaoriginal_2_0/cadenaoriginal_2_0.xslt",
    "http://www.sat.gob.mx/sitio_internet/cfd/2/cadenaoriginal_2_0/utilerias.xslt",
    "http://www.sat.gob.mx/sitio_internet/cfd/3/cadenaoriginal_3_0/cadenaoriginal_3_0.xslt",
    "http://www.sat.gob.mx/sitio_internet/cfd/3/cadenaoriginal_3_2/cadenaoriginal_3_2.xslt",
    "http://www.sat.gob.mx/sitio_internet/cfd/3/cadenaoriginal_3_3/cadenaoriginal_3_3.xslt",
    "http://www.sat.gob.mx/sitio_internet/cfd/4/cadenaoriginal_4_0/cadenaoriginal_4_0.xslt",
    "http://www.sat.gob.mx/sitio_internet/cfd/TimbreFiscalDigital/cadenaoriginal_TFD_1_1.xslt",
    "http://www.sat.gob.mx/sitio_internet/timbrefiscaldigital/cadenaoriginal_TFD_1_0.xslt",
    "http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte20.xslt",
    "http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte30.xslt",
    "http://www.sat.gob.mx/sitio_internet/cfd/CartaPorte/CartaPorte31.xslt",
    "http://www.sat.gob.mx/sitio_internet/cfd/Pagos/Pagos10.xslt",
    "http://www.sat.gob.mx/sitio_internet/cfd/Pagos/Pagos20.xslt",
    "http://www.sat.gob.mx/sitio_internet/cfd/ComercioExterior11/ComercioExterior11.xslt",
]


def _url_to_path(url: str, output_dir: Path) -> Path:
    parsed = urlparse(url)
    rel = Path(parsed.netloc) / parsed.path.lstrip("/")
    return output_dir / rel


def _extract_schema_locations(content: bytes, base_url: str) -> list[str]:
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return []

    ns = {"xs": "http://www.w3.org/2001/XMLSchema"}
    urls: list[str] = []
    for elem in root.findall(".//xs:import", ns) + root.findall(".//xs:include", ns):
        schema_location = elem.get("schemaLocation")
        if not schema_location:
            continue
        urls.append(urljoin(base_url, schema_location))
    return urls


def _fetch_url(url: str) -> bytes:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; catalogmx/1.0)",
        "Accept": "*/*",
    }
    response = requests.get(url, timeout=60, headers=headers)
    if response.status_code == 403 and url.startswith("http://"):
        https_url = "https://" + url[len("http://") :]
        response = requests.get(https_url, timeout=60, headers=headers)
    if response.status_code in {403, 404}:
        parsed = urlparse(url)
        mirror = (
            "https://raw.githubusercontent.com/phpcfdi/resources-sat-xml/master/resources"
            f"/{parsed.netloc}{parsed.path}"
        )
        response = requests.get(mirror, timeout=60, headers=headers)
    response.raise_for_status()
    return response.content


def download_recursive(url: str, output_dir: Path, visited: set[str]) -> None:
    if url in visited:
        return
    visited.add(url)

    content = _fetch_url(url)

    target = _url_to_path(url, output_dir)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)

    for child_url in _extract_schema_locations(content, url):
        try:
            download_recursive(child_url, output_dir, visited)
        except Exception as exc:
            print(f"⚠️  Failed to download {child_url}: {exc}")


def _download_from_mirror(path: str, output_dir: Path) -> None:
    url = (
        "https://raw.githubusercontent.com/phpcfdi/resources-sat-xml/master/"
        + path.lstrip("/")
    )
    content = _fetch_url(url)
    target = output_dir / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)


def download_all_from_mirror(output_dir: Path, extensions: set[str]) -> int:
    tree_url = "https://api.github.com/repos/phpcfdi/resources-sat-xml/git/trees/master?recursive=1"
    response = requests.get(tree_url, timeout=60)
    response.raise_for_status()
    data = response.json()

    total = 0
    for item in data.get("tree", []):
        if item.get("type") != "blob":
            continue
        path = item.get("path", "")
        if not any(path.lower().endswith(ext) for ext in extensions):
            continue
        _download_from_mirror(path, output_dir)
        total += 1
    return total

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download SAT XSDs recursively for CFDI 4.0",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent.parent / "packages" / "shared-data" / "sat" / "cfdi_4.0" / "xsd",
        help="Output directory for XSD files",
    )
    parser.add_argument(
        "--entry",
        action="append",
        default=[],
        help="Additional entry-point XSD URLs (repeatable)",
    )
    parser.add_argument(
        "--xslt",
        action="append",
        default=[],
        help="Additional XSLT URLs to download (repeatable)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Download all XSD/XSLT files from the phpcfdi/resources-sat-xml mirror",
    )
    args = parser.parse_args()

    output_dir = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.all:
        total = download_all_from_mirror(output_dir, {".xsd", ".xslt"})
        print(f"\nTotal files (mirror): {total}")
        return 0

    urls = DEFAULT_ENTRY_URLS + args.entry
    visited: set[str] = set()

    for url in urls:
        try:
            download_recursive(url, output_dir, visited)
            print(f"✅ Downloaded: {url}")
        except Exception as exc:
            print(f"❌ Failed: {url}: {exc}")

    xslt_dir = output_dir / "xslt"
    xslt_dir.mkdir(parents=True, exist_ok=True)
    xslt_urls = DEFAULT_XSLT_URLS + args.xslt
    for url in xslt_urls:
        try:
            content = _fetch_url(url)
            target = _url_to_path(url, xslt_dir)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            print(f"✅ Downloaded XSLT: {url}")
        except Exception as exc:
            print(f"❌ Failed XSLT: {url}: {exc}")

    print(f"\nTotal XSD files: {len(visited)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
