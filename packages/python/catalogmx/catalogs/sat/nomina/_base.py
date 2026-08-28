"""Shared resolver-backed loader for SAT Nómina 1.2 catalog APIs."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar

from catalogmx.catalogs.sat._sqlite import read_dataset_table

DATASET_ID = "sat.nomina_1_2"
DATABASE_NAME = "sat_nomina_12.sqlite3"

_TABLE_BY_FILENAME = {
    "banco.json": "nomina_bancos",
    "origen_recurso.json": "nomina_origenes_recursos",
    "periodicidad_pago.json": "nomina_periodicidades_pagos",
    "riesgo_puesto.json": "nomina_riesgos_puestos",
    "tipo_contrato.json": "nomina_tipos_contratos",
    "tipo_deduccion.json": "nomina_tipos_deducciones",
    "tipo_horas.json": "nomina_tipos_horas",
    "tipo_incapacidad.json": "nomina_tipos_incapacidades",
    "tipo_jornada.json": "nomina_tipos_jornadas",
    "tipo_nomina.json": "nomina_tipos_nominas",
    "tipo_otro_pago.json": "nomina_tipos_otros_pagos",
    "tipo_percepcion.json": "nomina_tipos_percepciones",
    "tipo_regimen.json": "nomina_tipos_regimenes",
}

# CatalogMX-owned convenience metadata. These values are not columns from
# catNomina and therefore intentionally remain code-versioned while every
# SAT-owned code/description/vigencia field comes from the canonical artifact.
_EXTENSION_BY_FILENAME: dict[str, dict[str, dict[str, Any]]] = {
    "periodicidad_pago.json": {
        "01": {"days": 1},
        "02": {"days": 7},
        "03": {"days": 14},
        "04": {"days": 15},
        "05": {"days": 30},
        "06": {"days": 60},
        "07": {"days": 0},
        "08": {"days": 0},
        "09": {"days": 0},
        "10": {"days": 10},
        "99": {"days": 0},
    },
    "riesgo_puesto.json": {
        "1": {"prima_minima": 0.5, "prima_media": 0.54355, "prima_maxima": 0.625},
        "2": {"prima_minima": 0.625, "prima_media": 1.13065, "prima_maxima": 1.63},
        "3": {"prima_minima": 1.63, "prima_media": 2.59645, "prima_maxima": 3.06},
        "4": {"prima_minima": 3.06, "prima_media": 4.65325, "prima_maxima": 5.77},
        "5": {"prima_minima": 5.77, "prima_media": 6.71, "prima_maxima": 8.7},
    },
}


class NominaJsonCatalog:
    """Lazy compatibility API backed by canonical Nómina 1.2 SQLite data.

    The class name is retained for source compatibility. JSON files are no
    longer the runtime source of SAT-owned fields.
    """

    filename: ClassVar[str]
    _data: ClassVar[list[dict[str, Any]] | None] = None
    _by_code: ClassVar[dict[str, dict[str, Any]] | None] = None

    @classmethod
    def _normalize(cls, item: Mapping[str, Any]) -> dict[str, Any]:
        normalized = dict(item)
        code = normalized.get("code", normalized.get("clave", normalized.get("id")))
        if code is None:
            raise ValueError(f"{cls.filename}: catalog row has no code")
        code = str(code)
        normalized["code"] = code
        normalized.setdefault("clave", code)

        description = normalized.get(
            "description", normalized.get("descripcion", normalized.get("texto"))
        )
        if description is not None:
            normalized["description"] = str(description)
            normalized.setdefault("descripcion", str(description))

        name = normalized.get("name", normalized.get("nombre"))
        if name is not None:
            normalized["name"] = str(name)
            normalized.setdefault("nombre", str(name))

        legal_name = normalized.get("razon_social", normalized.get("full_name"))
        if legal_name is not None:
            normalized["razon_social"] = str(legal_name)
            normalized.setdefault("full_name", str(legal_name))
        return normalized

    @classmethod
    def _compatibility_item(cls, row: Mapping[str, Any]) -> dict[str, Any]:
        code = str(row["id"])
        text = str(row["texto"])
        if cls.filename == "banco.json":
            legal_name = str(row.get("razon_social") or "")
            item: dict[str, Any] = {
                "code": code,
                "name": text,
                "full_name": legal_name,
                "razon_social": legal_name,
            }
        else:
            item = {
                "code": code,
                "description": text,
                "descripcion": text,
            }

        if "vigencia_desde" in row:
            item["valid_from"] = row.get("vigencia_desde") or None
        if "vigencia_hasta" in row:
            item["valid_to"] = row.get("vigencia_hasta") or None

        item.update(_EXTENSION_BY_FILENAME.get(cls.filename, {}).get(code, {}))
        return item

    @classmethod
    def _load(cls) -> list[dict[str, Any]]:
        if cls._data is None:
            table = _TABLE_BY_FILENAME.get(cls.filename)
            if table is None:
                raise ValueError(f"unsupported Nómina compatibility catalog: {cls.filename}")
            rows = read_dataset_table(DATASET_ID, DATABASE_NAME, table)
            cls._data = [cls._normalize(cls._compatibility_item(row)) for row in rows]
            cls._by_code = {item["code"]: item for item in cls._data}
        return cls._data

    @classmethod
    def reload(cls) -> None:
        cls._data = None
        cls._by_code = None

    @classmethod
    def get_all(cls) -> list[dict[str, Any]]:
        # Existing Nómina APIs returned a shallow list copy. Preserve that
        # contract so callers cannot mutate the catalog cache by appending.
        return cls._load().copy()

    @classmethod
    def get_by_code(cls, code: str) -> dict[str, Any] | None:
        cls._load()
        assert cls._by_code is not None
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        return cls.get_by_code(code) is not None

    @classmethod
    def search(cls, text: str) -> list[dict[str, Any]]:
        query = text.casefold()
        return [
            item
            for item in cls._load()
            if query
            in str(
                item.get("description") or item.get("name") or item.get("full_name") or ""
            ).casefold()
        ]
