"""Compatibility projections over canonical Carta Porte 3.1 SQLite data."""

from __future__ import annotations

import re
from typing import Any

from catalogmx.catalogs.sat._sqlite import read_dataset_table

DATASET_ID = "sat.carta_porte"
DATABASE_NAME = "sat_carta_porte_31.sqlite3"


def _rows(table: str) -> list[dict[str, Any]]:
    return read_dataset_table(DATASET_ID, DATABASE_NAME, table)


def _nullable_text(value: object) -> str | None:
    text = str(value or "")
    return text or None


def _config_type(code: str, text: str) -> str:
    normalized = text.casefold()
    if "unitario" in normalized:
        return "Unitario"
    if code == "VL" or "vehículo ligero" in normalized or "vehiculo ligero" in normalized:
        return "Ligero"
    return "Articulado"


def config_autotransporte_rows() -> list[dict[str, Any]]:
    """Project current SAT vehicle configurations to the historical Python shape."""
    result: list[dict[str, Any]] = []
    for row in _rows("ccp_31_configuraciones_autotransporte"):
        code = str(row["id"])
        name = str(row.get("texto") or "")
        result.append(
            {
                "code": code,
                "name": name,
                "type": _config_type(code, name),
                "axes": row.get("numero_de_ejes"),
                "wheels": row.get("numero_de_llantas"),
                "trailer": str(row.get("remolque") or ""),
                "valid_from": _nullable_text(row.get("vigencia_desde")),
                "valid_to": _nullable_text(row.get("vigencia_hasta")),
            }
        )
    return result


def _hazard_class(value: object) -> str:
    text = str(value or "")
    match = re.match(r"\s*(\d+)", text)
    return match.group(1) if match else ""


def material_peligroso_rows() -> list[dict[str, Any]]:
    """Project the complete current dangerous-material catalog.

    Carta Porte 3.1 does not publish a packing-group column. The historical
    compatibility JSON did, but that small snapshot is not authoritative; the
    compatibility fields therefore remain explicitly unknown instead of being
    fabricated.
    """
    result: list[dict[str, Any]] = []
    for row in _rows("ccp_31_materiales_peligrosos"):
        division = str(row.get("clase_o_div") or "")
        result.append(
            {
                "code": str(row["id"]),
                "descripcion": str(row.get("texto") or ""),
                "class": _hazard_class(division),
                "clase_riesgo": _hazard_class(division),
                "clase_division": division,
                "peligro_secundario": str(row.get("peligro_secundario") or ""),
                "nombre_tecnico": str(row.get("nombre_tecnico") or ""),
                "packing_group": None,
                "grupo_embalaje": None,
                "valid_from": _nullable_text(row.get("vigencia_desde")),
                "valid_to": _nullable_text(row.get("vigencia_hasta")),
            }
        )
    return result


_MATERIAL_PATTERNS = (
    ("acero", "Acero"),
    ("aluminio", "Aluminio"),
    ("plástico", "Plástico"),
    ("plastico", "Plástico"),
    ("madera", "Madera"),
    ("fibra", "Fibra"),
    ("papel", "Papel"),
    ("textil", "Textil"),
    ("tela", "Textil"),
    ("metal", "Metal"),
    ("vidrio", "Vidrio"),
)


def _packaging_material(text: str) -> str:
    normalized = text.casefold()
    for needle, label in _MATERIAL_PATTERNS:
        if needle in normalized:
            return label
    return "Otro"


def tipo_embalaje_rows() -> list[dict[str, Any]]:
    """Project current SAT packaging types and derive a search material label."""
    result: list[dict[str, Any]] = []
    for row in _rows("ccp_31_tipos_embalaje"):
        description = str(row.get("texto") or "")
        result.append(
            {
                "code": str(row["id"]),
                "descripcion": description,
                "material": _packaging_material(description),
                "categoria_onu": None,
                "valid_from": _nullable_text(row.get("vigencia_desde")),
                "valid_to": _nullable_text(row.get("vigencia_hasta")),
            }
        )
    return result


def _permit_type(text: str) -> str:
    normalized = text.casefold()
    if "carga" in normalized:
        return "Carga"
    if any(token in normalized for token in ("pasaje", "pasajero", "turismo")):
        return "Pasajeros"
    return "Otro"


def tipo_permiso_rows() -> list[dict[str, Any]]:
    """Project current permits and derive the legacy high-level type label."""
    result: list[dict[str, Any]] = []
    for row in _rows("ccp_31_tipos_permiso"):
        name = str(row.get("texto") or "").rstrip(".")
        transport = str(row.get("clave_transporte") or "")
        result.append(
            {
                "code": str(row["id"]),
                "name": name,
                "type": _permit_type(name),
                "transport": transport,
                "clave_transporte": transport,
                "valid_from": _nullable_text(row.get("vigencia_desde")),
                "valid_to": _nullable_text(row.get("vigencia_hasta")),
            }
        )
    return result


__all__ = [
    "config_autotransporte_rows",
    "material_peligroso_rows",
    "tipo_embalaje_rows",
    "tipo_permiso_rows",
]
