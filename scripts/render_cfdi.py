#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Render a simple printable representation of a CFDI XML (HTML)."""

from __future__ import annotations

import argparse
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import xml.etree.ElementTree as ET

from catalogmx.utils.shared_data import get_shared_data_path


def _local(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _find_first(root: ET.Element, name: str) -> ET.Element | None:
    for elem in root.iter():
        if _local(elem.tag) == name:
            return elem
    return None


def _find_all(root: ET.Element, name: str) -> list[ET.Element]:
    return [elem for elem in root.iter() if _local(elem.tag) == name]


def _fmt_money(value: str | None) -> str:
    if not value:
        return "$0.00"
    try:
        return f"${Decimal(value):,.2f}"
    except Exception:
        return value


def _fmt_date(value: str | None) -> str:
    if not value:
        return "-"
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
        try:
            dt = datetime.strptime(value, fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    return value


def _load_catalog(path_parts: list[str], key: str = "code", value: str = "description") -> dict[str, str]:
    try:
        data_path = get_shared_data_path(*path_parts)
        import json

        with open(data_path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = data.get("data", data)
        if not isinstance(data, list):
            return {}
        return {str(item.get(key)): str(item.get(value, "")) for item in data if item.get(key)}
    except Exception:
        return {}


def render_cfdi_html(xml_path: Path) -> str:
    xml_bytes = xml_path.read_bytes()
    root = ET.fromstring(xml_bytes)

    comprobante = _find_first(root, "Comprobante")
    emisor = _find_first(root, "Emisor")
    receptor = _find_first(root, "Receptor")
    timbre = _find_first(root, "TimbreFiscalDigital")

    conceptos = _find_all(root, "Concepto")

    cat_tipo = _load_catalog(["sat", "cfdi_4.0", "tipo_comprobante.json"])
    cat_metodo = _load_catalog(["sat", "cfdi_4.0", "metodo_pago.json"])
    cat_forma = _load_catalog(["sat", "cfdi_4.0", "forma_pago.json"])
    cat_uso = _load_catalog(["sat", "cfdi_4.0", "uso_cfdi.json"])
    cat_regimen = _load_catalog(["sat", "cfdi_4.0", "regimen_fiscal.json"])

    def label(value: str | None, catalog: dict[str, str]) -> str:
        if not value:
            return "-"
        desc = catalog.get(value)
        return f"{value} - {desc}" if desc else value

    html = [
        "<!DOCTYPE html>",
        "<html lang='es'>",
        "<head>",
        "<meta charset='utf-8' />",
        "<style>",
        "body{font-family:Arial,Helvetica,sans-serif;color:#0f172a;margin:24px}",
        "h1{font-size:18px;margin:0 0 8px}",
        ".grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}",
        ".card{border:1px solid #e2e8f0;border-radius:8px;padding:10px}",
        ".kv{display:grid;grid-template-columns:120px 1fr;gap:6px;font-size:12px}",
        "table{width:100%;border-collapse:collapse;font-size:12px;margin-top:12px}",
        "th,td{border-bottom:1px solid #e2e8f0;padding:6px;text-align:left}",
        "th{background:#f1f5f9}",
        ".num{text-align:right}",
        "</style>",
        "</head>",
        "<body>",
        f"<h1>CFDI {comprobante.get('Version','') if comprobante is not None else ''}</h1>",
        f"<div>UUID: {timbre.get('UUID','-') if timbre is not None else '-'}</div>",
        f"<div>Fecha timbrado: {_fmt_date(timbre.get('FechaTimbrado')) if timbre is not None else '-'}</div>",
        "<div class='grid' style='margin-top:12px'>",
        "<div class='card'>",
        "<strong>Emisor</strong>",
        "<div class='kv'>",
        f"<div>RFC</div><div>{emisor.get('Rfc','-') if emisor is not None else '-'}</div>",
        f"<div>Nombre</div><div>{emisor.get('Nombre','-') if emisor is not None else '-'}</div>",
        f"<div>Régimen</div><div>{label(emisor.get('RegimenFiscal') if emisor is not None else None, cat_regimen)}</div>",
        "</div></div>",
        "<div class='card'>",
        "<strong>Receptor</strong>",
        "<div class='kv'>",
        f"<div>RFC</div><div>{receptor.get('Rfc','-') if receptor is not None else '-'}</div>",
        f"<div>Nombre</div><div>{receptor.get('Nombre','-') if receptor is not None else '-'}</div>",
        f"<div>Uso CFDI</div><div>{label(receptor.get('UsoCFDI') if receptor is not None else None, cat_uso)}</div>",
        f"<div>Régimen</div><div>{label(receptor.get('RegimenFiscalReceptor') if receptor is not None else None, cat_regimen)}</div>",
        "</div></div>",
        "</div>",
        "<div class='grid' style='margin-top:12px'>",
        "<div class='card'>",
        "<strong>Comprobante</strong>",
        "<div class='kv'>",
        f"<div>Serie/Folio</div><div>{(comprobante.get('Serie','') + ' ' + comprobante.get('Folio','')).strip() if comprobante is not None else '-'}</div>",
        f"<div>Fecha</div><div>{_fmt_date(comprobante.get('Fecha')) if comprobante is not None else '-'}</div>",
        f"<div>Tipo</div><div>{label(comprobante.get('TipoDeComprobante') if comprobante is not None else None, cat_tipo)}</div>",
        f"<div>Moneda</div><div>{comprobante.get('Moneda','-') if comprobante is not None else '-'}</div>",
        f"<div>Método</div><div>{label(comprobante.get('MetodoPago') if comprobante is not None else None, cat_metodo)}</div>",
        f"<div>Forma</div><div>{label(comprobante.get('FormaPago') if comprobante is not None else None, cat_forma)}</div>",
        "</div></div>",
        "<div class='card'>",
        "<strong>Totales</strong>",
        "<div class='kv'>",
        f"<div>Subtotal</div><div>{_fmt_money(comprobante.get('SubTotal') if comprobante is not None else None)}</div>",
        f"<div>Descuento</div><div>{_fmt_money(comprobante.get('Descuento') if comprobante is not None else None)}</div>",
        f"<div>Total</div><div>{_fmt_money(comprobante.get('Total') if comprobante is not None else None)}</div>",
        "</div></div>",
        "</div>",
        "<table>",
        "<thead><tr><th>Clave</th><th>Descripción</th><th class='num'>Cant.</th><th>Unidad</th><th class='num'>V. Unitario</th><th class='num'>Importe</th></tr></thead>",
        "<tbody>",
    ]

    for c in conceptos:
        html.append(
            "<tr>"
            f"<td>{c.get('ClaveProdServ','')}</td>"
            f"<td>{c.get('Descripcion','')}</td>"
            f"<td class='num'>{c.get('Cantidad','')}</td>"
            f"<td>{c.get('ClaveUnidad','')}</td>"
            f"<td class='num'>{_fmt_money(c.get('ValorUnitario'))}</td>"
            f"<td class='num'>{_fmt_money(c.get('Importe'))}</td>"
            "</tr>"
        )

    html += ["</tbody>", "</table>", "</body>", "</html>"]
    return "\n".join(html)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render CFDI XML to HTML")
    parser.add_argument("xml", type=Path, help="Path to CFDI XML")
    parser.add_argument("--output", "-o", type=Path, help="Output HTML path")
    args = parser.parse_args()

    html = render_cfdi_html(args.xml)
    if args.output:
        args.output.write_text(html, encoding="utf-8")
    else:
        print(html)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
