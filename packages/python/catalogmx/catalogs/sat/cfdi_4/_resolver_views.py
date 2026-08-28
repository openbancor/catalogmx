"""Compatibility projections over the canonical CFDI 4.0 SQLite artifact.

Public Python catalog classes historically exposed small JSON-shaped dictionaries.
These helpers preserve those shapes while sourcing authority-owned fields from the
independently versioned ``sat.cfdi_4`` dataset through ``DatasetResolver``.
"""

from __future__ import annotations

from typing import Any

from catalogmx.catalogs.sat._sqlite import read_dataset_table

DATASET_ID = "sat.cfdi_4"
DATABASE_NAME = "sat_cfdi_40.sqlite3"

_IMPUESTO_NAMES = {
    "001": "Impuesto Sobre la Renta",
    "002": "Impuesto al Valor Agregado",
    "003": "Impuesto Especial sobre Producción y Servicios",
}


def _rows(table: str) -> list[dict[str, Any]]:
    return read_dataset_table(DATASET_ID, DATABASE_NAME, table)


def _description(value: object, *, strip_terminal_period: bool = False) -> str:
    text = str(value or "")
    return text.rstrip(".") if strip_terminal_period else text


def code_description_rows(
    table: str, *, strip_terminal_period: bool = False
) -> list[dict[str, Any]]:
    """Project canonical ``id``/``texto`` rows to legacy code/description rows."""
    return [
        {
            "code": str(row["id"]),
            "description": _description(
                row.get("texto"), strip_terminal_period=strip_terminal_period
            ),
        }
        for row in _rows(table)
    ]


def value_rows(table: str) -> list[dict[str, str]]:
    """Project a canonical identifier table to the historical ``valor`` shape."""
    return [{"valor": str(row["id"])} for row in _rows(table)]


def impuesto_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in _rows("cfdi_40_impuestos"):
        code = str(row["id"])
        rows.append(
            {
                "code": code,
                "description": str(row.get("texto") or ""),
                "name": _IMPUESTO_NAMES.get(code, str(row.get("texto") or "")),
                "retention": bool(row.get("retencion")),
                "transfer": bool(row.get("traslado")),
            }
        )
    return rows


def regimen_fiscal_rows() -> list[dict[str, Any]]:
    return [
        {
            "code": str(row["id"]),
            "description": str(row.get("texto") or ""),
            "fisica": bool(row.get("aplica_fisica")),
            "moral": bool(row.get("aplica_moral")),
        }
        for row in _rows("cfdi_40_regimenes_fiscales")
    ]


def uso_cfdi_rows() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for row in _rows("cfdi_40_usos_cfdi"):
        fisica = bool(row.get("aplica_fisica"))
        moral = bool(row.get("aplica_moral"))
        applies_to = (
            "both"
            if fisica and moral
            else "fisica"
            if fisica
            else "moral"
            if moral
            else "none"
        )
        result.append(
            {
                "code": str(row["id"]),
                "description": _description(
                    row.get("texto"), strip_terminal_period=True
                ),
                "fisica": fisica,
                "moral": moral,
                "applies_to": applies_to,
            }
        )
    return result


def _legacy_date(value: object) -> str:
    """Preserve ClaveUnidad's historical DD-MM-YYYY presentation."""
    text = str(value or "")
    if not text:
        return ""
    parts = text.split("-")
    if len(parts) == 3 and all(parts):
        year, month, day = parts
        if len(year) == 4:
            return f"{day}-{month}-{year}"
    return text


def clave_unidad_rows() -> list[dict[str, str]]:
    return [
        {
            "id": str(row["id"]),
            "nombre": str(row.get("texto") or ""),
            "descripcion": str(row.get("descripcion") or ""),
            "nota": str(row.get("notas") or ""),
            "fechaDeInicioDeVigencia": _legacy_date(row.get("vigencia_desde")),
            "fechaDeFinDeVigencia": _legacy_date(row.get("vigencia_hasta")),
            "simbolo": str(row.get("simbolo") or ""),
        }
        for row in _rows("cfdi_40_claves_unidades")
    ]


__all__ = [
    "clave_unidad_rows",
    "code_description_rows",
    "impuesto_rows",
    "regimen_fiscal_rows",
    "uso_cfdi_rows",
    "value_rows",
]
