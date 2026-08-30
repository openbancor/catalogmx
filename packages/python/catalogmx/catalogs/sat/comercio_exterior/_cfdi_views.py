"""Compatibility projections over CFDI datasets reused by Comercio Exterior.

The Comercio Exterior profile intentionally reuses shared CFDI 4.0 catalogs
instead of duplicating them into ``sat.comercio_exterior``.  This module keeps
that ownership boundary explicit for Python consumers that live under the
Comercio Exterior package.
"""

from __future__ import annotations

from typing import Any

from catalogmx.catalogs.sat._sqlite import read_dataset_table

DATASET_ID = "sat.cfdi_4"
DATABASE_NAME = "sat_cfdi_40.sqlite3"


def _optional_text(value: object) -> str | None:
    text = str(value or "")
    return text or None


def moneda_rows() -> list[dict[str, Any]]:
    """Return current SAT currency rows in the historical Python shape.

    The legacy ``pais`` field was an enrichment from the tracked compatibility
    snapshot, not a column of ``cfdi_40_monedas`` and not a sound one-to-one
    property for every ISO 4217 currency.  It is retained as ``None`` to keep
    dictionary shape stable without fabricating authority data.
    """
    return [
        {
            "codigo": str(row["id"]),
            "nombre": str(row.get("texto") or ""),
            "pais": None,
            "decimales": int(row.get("decimales") or 0),
            "porcentaje_variacion": row.get("porcentaje_variacion"),
            "valid_from": _optional_text(row.get("vigencia_desde")),
            "valid_to": _optional_text(row.get("vigencia_hasta")),
        }
        for row in read_dataset_table(DATASET_ID, DATABASE_NAME, "cfdi_40_monedas")
    ]


def country_tax_identity_rows() -> list[dict[str, Any]]:
    """Return SAT country-scoped tax-identity validation metadata.

    ``cfdi_40_paises`` is the actual SAT owner of the foreign tax identity
    pattern used by Comercio Exterior. Most countries intentionally publish no
    local pattern. Mexico additionally marks identity validation as
    ``Lista del SAT``; callers must not reinterpret that marker as a regex-only
    validation rule.
    """
    return [
        {
            "country": str(row["id"]),
            "country_name": str(row.get("texto") or ""),
            "format_pattern": _optional_text(row.get("patron_identidad_tributaria")),
            "validation_mode": _optional_text(row.get("validacion_identidad_tributaria")),
            "postal_code_pattern": _optional_text(row.get("patron_codigo_postal")),
            "groups": _optional_text(row.get("agrupaciones")),
        }
        for row in read_dataset_table(DATASET_ID, DATABASE_NAME, "cfdi_40_paises")
    ]


__all__ = ["country_tax_identity_rows", "moneda_rows"]
