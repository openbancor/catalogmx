"""Catálogo de Códigos Postales SEPOMEX - Versión Completa

Provides access to all ~150,000 Mexican postal codes with enhanced data.
Includes settlement type (tipo_asentamiento), zone (zona), and state/municipality codes.

WARNING: This catalog is very large (~42MB). Use with caution and consider
using pagination or filters when displaying results.
"""

import json
from pathlib import Path

from catalogmx.utils.text import normalize_text


class CodigosPostalesCompleto:
    """Catálogo completo de códigos postales con datos extendidos"""

    _data: list[dict] | None = None
    _by_cp: dict[str, list[dict]] | None = None
    _by_estado: dict[str, list[dict]] | None = None
    _by_estado_normalized: dict[str, list[dict]] | None = None
    _by_municipio_normalized: dict[str, list[dict]] | None = None
    _by_zona: dict[str, list[dict]] | None = None

    @classmethod
    def _load_data(cls) -> None:
        if cls._data is None:
            path = (
                Path(__file__).parent.parent.parent.parent.parent
                / "shared-data"
                / "sepomex"
                / "codigos_postales_completo.json"
            )
            with open(path, encoding="utf-8") as f:
                cls._data = json.load(f)

            # Index by CP (can have multiple settlements)
            cls._by_cp = {}
            for item in cls._data:
                cp = item.get("cp") or item.get("codigo_postal")
                if cp:
                    if cp not in cls._by_cp:
                        cls._by_cp[cp] = []
                    cls._by_cp[cp].append(item)

            # Index by estado
            cls._by_estado = {}
            for item in cls._data:
                estado = item.get("estado")
                if estado:
                    if estado not in cls._by_estado:
                        cls._by_estado[estado] = []
                    cls._by_estado[estado].append(item)

            # Index by estado normalized (accent-insensitive)
            cls._by_estado_normalized = {}
            for item in cls._data:
                estado = item.get("estado")
                if estado:
                    estado_norm = normalize_text(estado)
                    if estado_norm not in cls._by_estado_normalized:
                        cls._by_estado_normalized[estado_norm] = []
                    cls._by_estado_normalized[estado_norm].append(item)

            # Index by municipio normalized (accent-insensitive)
            cls._by_municipio_normalized = {}
            for item in cls._data:
                municipio = item.get("municipio")
                if municipio:
                    municipio_norm = normalize_text(municipio)
                    if municipio_norm not in cls._by_municipio_normalized:
                        cls._by_municipio_normalized[municipio_norm] = []
                    cls._by_municipio_normalized[municipio_norm].append(item)

            # Index by zona (Urbano/Rural)
            cls._by_zona = {}
            for item in cls._data:
                zona = item.get("zona")
                if zona:
                    if zona not in cls._by_zona:
                        cls._by_zona[zona] = []
                    cls._by_zona[zona].append(item)

    @classmethod
    def get_by_cp(cls, cp: str) -> list[dict]:
        """Obtiene todos los asentamientos de un código postal"""
        cls._load_data()
        return cls._by_cp.get(cp, [])

    @classmethod
    def is_valid(cls, cp: str) -> bool:
        """Verifica si un código postal existe"""
        cls._load_data()
        return cp in cls._by_cp

    @classmethod
    def get_by_estado(cls, estado: str) -> list[dict]:
        """Obtiene todos los códigos postales de un estado (insensible a acentos)"""
        cls._load_data()
        estado_normalized = normalize_text(estado)
        return cls._by_estado_normalized.get(estado_normalized, [])

    @classmethod
    def get_by_municipio(cls, municipio: str) -> list[dict]:
        """Obtiene todos los códigos postales de un municipio (insensible a acentos)"""
        cls._load_data()
        municipio_normalized = normalize_text(municipio)
        return cls._by_municipio_normalized.get(municipio_normalized, [])

    @classmethod
    def get_by_zona(cls, zona: str) -> list[dict]:
        """Obtiene códigos postales por zona (Urbano o Rural)"""
        cls._load_data()
        return cls._by_zona.get(zona, [])

    @classmethod
    def search_by_asentamiento(
        cls, query: str, *, codigo_postal: str | None = None, estado: str | None = None
    ) -> list[dict]:
        """Busca códigos postales por nombre de asentamiento (insensible a acentos)"""
        cls._load_data()
        query_normalized = normalize_text(query)

        search_list = cls._data
        if codigo_postal:
            search_list = cls.get_by_cp(codigo_postal)
        elif estado:
            search_list = cls.get_by_estado(estado)

        return [
            item
            for item in search_list
            if query_normalized in normalize_text(item.get("asentamiento", ""))
        ]

    @classmethod
    def search_by_colonia(cls, colonia: str) -> list[dict]:
        """Alias for search_by_asentamiento for backwards compatibility"""
        return cls.search_by_asentamiento(colonia)

    @classmethod
    def get_by_tipo_asentamiento(cls, tipo: str) -> list[dict]:
        """Obtiene códigos postales por tipo de asentamiento (Colonia, Fraccionamiento, etc.)"""
        cls._load_data()
        tipo_normalized = normalize_text(tipo)
        return [
            item
            for item in cls._data
            if tipo_normalized in normalize_text(item.get("tipo_asentamiento", ""))
        ]

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todos los códigos postales (WARNING: dataset muy grande)"""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_municipio(cls, cp: str) -> str | None:
        """Obtiene el municipio de un código postal"""
        settlements = cls.get_by_cp(cp)
        return settlements[0]["municipio"] if settlements else None

    @classmethod
    def get_estado(cls, cp: str) -> str | None:
        """Obtiene el estado de un código postal"""
        settlements = cls.get_by_cp(cp)
        return settlements[0]["estado"] if settlements else None

    @classmethod
    def get_total_count(cls) -> int:
        """Obtiene el conteo total de códigos postales"""
        cls._load_data()
        return len(cls._data)

    @classmethod
    def get_unique_cps(cls) -> list[str]:
        """Obtiene todos los códigos postales únicos"""
        cls._load_data()
        return sorted(set(cls._by_cp.keys()))

    @classmethod
    def get_count_by_estado(cls, estado: str) -> int:
        """Obtiene el conteo de códigos postales por estado"""
        return len(cls.get_by_estado(estado))

    @classmethod
    def get_asentamientos(cls, cp: str) -> list[str]:
        """Obtiene todos los asentamientos de un código postal"""
        settlements = cls.get_by_cp(cp)
        return [s.get("asentamiento", "") for s in settlements]

    @classmethod
    def search(
        cls,
        *,
        cp: str | None = None,
        estado: str | None = None,
        municipio: str | None = None,
        asentamiento: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """Busca con múltiples criterios (con paginación)"""
        cls._load_data()
        results = cls._data

        if cp:
            results = [r for r in results if r.get("cp") == cp or r.get("codigo_postal") == cp]
        if estado:
            estado_norm = normalize_text(estado)
            results = [r for r in results if normalize_text(r.get("estado", "")) == estado_norm]
        if municipio:
            municipio_norm = normalize_text(municipio)
            results = [
                r for r in results if municipio_norm in normalize_text(r.get("municipio", ""))
            ]
        if asentamiento:
            asentamiento_norm = normalize_text(asentamiento)
            results = [
                r for r in results if asentamiento_norm in normalize_text(r.get("asentamiento", ""))
            ]

        return results[:limit]

    @classmethod
    def get_statistics(cls) -> dict:
        """Obtiene estadísticas del catálogo"""
        cls._load_data()
        unique_cps = set()
        unique_states = set()
        unique_municipalities = set()

        for item in cls._data:
            cp = item.get("cp") or item.get("codigo_postal")
            if cp:
                unique_cps.add(cp)
            estado = item.get("estado")
            if estado:
                unique_states.add(estado)
            municipio = item.get("municipio")
            estado = item.get("estado")
            if municipio and estado:
                unique_municipalities.add(f"{estado}:{municipio}")

        return {
            "total_postal_codes": len(cls._data),
            "unique_postal_codes": len(unique_cps),
            "states": len(unique_states),
            "municipalities": len(unique_municipalities),
        }

    @classmethod
    def clear_cache(cls) -> None:
        """Limpia los datos en caché para liberar memoria"""
        cls._data = None
        cls._by_cp = None
        cls._by_estado = None
        cls._by_estado_normalized = None
        cls._by_municipio_normalized = None
        cls._by_zona = None
