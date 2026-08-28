"""Compatibility projections over canonical Comercio Exterior 2.0 data.

The SAT-owned catalog rows live in the independently versioned
``sat.comercio_exterior`` SQLite artifact.  This module projects those rows to
historical Python dictionary shapes and keeps non-SAT convenience metadata
explicitly in code instead of mixing it into the authority dataset.
"""

from __future__ import annotations

from typing import Any

from catalogmx.catalogs.sat._sqlite import read_dataset_table

DATASET_ID = "sat.comercio_exterior"
DATABASE_NAME = "sat_comercio_exterior_20.sqlite3"

_INCOTERM_NAMES = {
    "CFR": ("Cost and Freight", "Costo y flete"),
    "CIF": ("Cost, Insurance and Freight", "Costo, seguro y flete"),
    "CIP": ("Carriage and Insurance Paid To", "Transporte y seguro pagados hasta"),
    "CPT": ("Carriage Paid To", "Transporte pagado hasta"),
    "DAP": ("Delivered at Place", "Entregado en lugar"),
    "DDP": ("Delivered Duty Paid", "Entregado con derechos pagados"),
    "DPU": ("Delivered at Place Unloaded", "Entregado en lugar descargado"),
    "EXW": ("Ex Works", "En fábrica"),
    "FAS": ("Free Alongside Ship", "Franco al costado del buque"),
    "FCA": ("Free Carrier", "Franco transportista"),
    "FOB": ("Free On Board", "Franco a bordo"),
}
_MARITIME_INCOTERMS = {"CFR", "CIF", "FAS", "FOB"}
_SELLER_PAYS_FREIGHT = {"CFR", "CIF", "CIP", "CPT", "DAP", "DDP", "DPU"}
_SELLER_PAYS_INSURANCE = {"CIF", "CIP"}
_SELLER_RESPONSIBILITY = {
    "EXW": "minimal",
    "FCA": "medium",
    "CPT": "medium",
    "CIP": "medium",
    "DAP": "high",
    "DPU": "high",
    "DDP": "maximum",
    "FAS": "medium",
    "FOB": "medium",
    "CFR": "medium",
    "CIF": "medium",
}
_RISK_TRANSFER_POINT = {
    "EXW": "seller_premises",
    "FCA": "carrier_custody",
    "CPT": "carrier_custody",
    "CIP": "carrier_custody",
    "DAP": "destination_ready_unload",
    "DPU": "destination_unloaded",
    "DDP": "destination_ready_unload",
    "FAS": "alongside_ship",
    "FOB": "on_board_ship",
    "CFR": "on_board_ship",
    "CIF": "on_board_ship",
}

_UNIT_TYPES = {
    "01": "weight",
    "02": "weight",
    "03": "length",
    "04": "area",
    "05": "volume",
    "06": "unit",
    "07": "unit",
    "08": "volume",
    "09": "unit",
    "10": "unit",
    "11": "unit",
    "12": "unit",
    "13": "unit",
    "14": "weight",
    "15": "volume",
    "16": "weight",
    "17": "unit",
    "18": "unit",
    "19": "unit",
    "20": "container",
    "21": "container",
    "22": "weight",
    "99": "service",
}


def _rows(table: str, *, order_by: str | tuple[str, ...] = "id") -> list[dict[str, Any]]:
    return read_dataset_table(DATASET_ID, DATABASE_NAME, table, order_by=order_by)


def _optional_text(value: object) -> str | None:
    text = str(value or "")
    return text or None


def estado_rows() -> list[dict[str, Any]]:
    """Return current USA/Canada state rows from the CCE 2.0 catalog."""
    result: list[dict[str, Any]] = []
    for row in _rows("cce_20_estados", order_by=("pais", "estado")):
        country = str(row["pais"])
        if country not in {"USA", "CAN"}:
            continue
        result.append(
            {
                "code": str(row["estado"]),
                "name": str(row.get("texto") or ""),
                "country": country,
                "valid_from": _optional_text(row.get("vigencia_desde")),
                "valid_to": _optional_text(row.get("vigencia_hasta")),
            }
        )
    return result


def incoterm_rows() -> list[dict[str, Any]]:
    """Return SAT INCOTERM rows plus explicit CatalogMX convenience rules."""
    result: list[dict[str, Any]] = []
    for row in _rows("cce_20_incoterms"):
        code = str(row["id"])
        name, name_es = _INCOTERM_NAMES[code]
        maritime = code in _MARITIME_INCOTERMS
        item: dict[str, Any] = {
            "code": code,
            "name": name,
            "name_es": name_es,
            "description": str(row.get("texto") or ""),
            "transport_mode": "maritime" if maritime else "any",
            "seller_responsibility": _SELLER_RESPONSIBILITY[code],
            "seller_pays_freight": code in _SELLER_PAYS_FREIGHT,
            "seller_pays_insurance": code in _SELLER_PAYS_INSURANCE,
            "risk_transfer_point": _RISK_TRANSFER_POINT[code],
            "suitable_for": ["sea"] if maritime else ["land", "sea", "air", "multimodal"],
            "valid_from": _optional_text(row.get("vigencia_desde")),
            "valid_to": _optional_text(row.get("vigencia_hasta")),
        }
        if code == "CIP":
            item["insurance_coverage"] = "110% of contract value (Institute Cargo Clauses A)"
        elif code == "CIF":
            item["insurance_coverage"] = (
                "110% of contract value (Institute Cargo Clauses C - minimum)"
            )
        if code == "DAP":
            item["seller_unloads"] = False
        elif code == "DPU":
            item["seller_unloads"] = True
            item["notes"] = "Reemplazó a DAT (Delivered at Terminal) en Incoterms 2020"
        elif code == "DDP":
            item["seller_pays_import_duties"] = True
            item["seller_clears_import"] = True
        elif maritime:
            item["notes"] = "Solo para transporte marítimo y vías navegables interiores"
        result.append(item)
    return result


def motivo_traslado_rows() -> list[dict[str, Any]]:
    """Return current CCE transfer-reason rows."""
    return [
        {
            "code": str(row["id"]),
            "descripcion": str(row.get("texto") or ""),
            "requires_propietario": str(row["id"]) == "05",
        }
        for row in _rows("cce_20_motivos_traslado")
    ]


def unidad_aduana_rows() -> list[dict[str, Any]]:
    """Return current customs-unit rows plus a search-only unit classification."""
    result: list[dict[str, Any]] = []
    for row in _rows("cce_20_unidades_medida"):
        code = str(row["id"])
        result.append(
            {
                "code": code,
                "descripcion": str(row.get("texto") or ""),
                "type": _UNIT_TYPES.get(code),
                "valid_from": _optional_text(row.get("vigencia_desde")),
                "valid_to": _optional_text(row.get("vigencia_hasta")),
            }
        )
    return result


__all__ = [
    "estado_rows",
    "incoterm_rows",
    "motivo_traslado_rows",
    "unidad_aduana_rows",
]
