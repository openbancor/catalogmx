"""
Catálogo de Sectores CNBV - Entidades reguladas por la Comisión Nacional Bancaria y de Valores.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict


class SectorCNBV(TypedDict, total=False):
    """Estructura de un sector CNBV."""

    id: str
    nombre: str
    nombre_corto: str
    descripcion: str
    ley_aplicable: str
    regulador_principal: str
    supervisores_adicionales: list[str]
    ejemplos: list[str]
    subtipos: list[dict]
    caracteristicas: str
    nota: str


class Regulador(TypedDict):
    """Estructura de un regulador financiero."""

    id: str
    nombre: str
    siglas: str
    funcion: str


class SectoresCNBV:
    """Catálogo de sectores financieros regulados por la CNBV."""

    _data: dict | None = None
    _sectores: list[SectorCNBV] | None = None
    _by_id: dict[str, SectorCNBV] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy de los datos del catálogo."""
        if cls._data is not None:
            return

        data_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "shared-data"
            / "cnbv"
            / "sectores.json"
        )

        with open(data_path, encoding="utf-8") as f:
            cls._data = json.load(f)

        cls._sectores = cls._data.get("sectores", [])
        cls._by_id = {s["id"]: s for s in cls._sectores}

    @classmethod
    def get_all(cls) -> list[SectorCNBV]:
        """Obtiene todos los sectores CNBV."""
        cls._load_data()
        return cls._sectores.copy() if cls._sectores else []

    @classmethod
    def get_by_id(cls, sector_id: str) -> SectorCNBV | None:
        """Obtiene un sector por su ID."""
        cls._load_data()
        return cls._by_id.get(sector_id) if cls._by_id else None

    @classmethod
    def is_valid(cls, sector_id: str) -> bool:
        """Valida si un ID de sector existe."""
        return cls.get_by_id(sector_id) is not None

    @classmethod
    def search(cls, query: str) -> list[SectorCNBV]:
        """Busca sectores por nombre o descripción."""
        cls._load_data()
        if not cls._sectores:
            return []

        query_lower = query.lower()
        results = []

        for sector in cls._sectores:
            if (
                query_lower in sector.get("nombre", "").lower()
                or query_lower in sector.get("nombre_corto", "").lower()
                or query_lower in sector.get("descripcion", "").lower()
            ):
                results.append(sector)

        return results

    @classmethod
    def get_by_regulador(cls, regulador: str) -> list[SectorCNBV]:
        """Obtiene sectores por regulador principal."""
        cls._load_data()
        if not cls._sectores:
            return []

        regulador_upper = regulador.upper()
        return [
            s
            for s in cls._sectores
            if s.get("regulador_principal", "").upper() == regulador_upper
        ]

    @classmethod
    def count(cls) -> int:
        """Retorna el número total de sectores."""
        cls._load_data()
        return len(cls._sectores) if cls._sectores else 0


class ReguladorFinanciero:
    """Catálogo de reguladores del sistema financiero mexicano."""

    _reguladores: list[Regulador] | None = None
    _by_id: dict[str, Regulador] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy de los datos del catálogo."""
        if cls._reguladores is not None:
            return

        data_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "shared-data"
            / "cnbv"
            / "sectores.json"
        )

        with open(data_path, encoding="utf-8") as f:
            data = json.load(f)

        cls._reguladores = data.get("reguladores", [])
        cls._by_id = {r["id"]: r for r in cls._reguladores}

    @classmethod
    def get_all(cls) -> list[Regulador]:
        """Obtiene todos los reguladores."""
        cls._load_data()
        return cls._reguladores.copy() if cls._reguladores else []

    @classmethod
    def get_by_id(cls, regulador_id: str) -> Regulador | None:
        """Obtiene un regulador por su ID."""
        cls._load_data()
        return cls._by_id.get(regulador_id) if cls._by_id else None

    @classmethod
    def get_by_siglas(cls, siglas: str) -> Regulador | None:
        """Obtiene un regulador por sus siglas."""
        cls._load_data()
        if not cls._reguladores:
            return None

        siglas_upper = siglas.upper()
        for reg in cls._reguladores:
            if reg.get("siglas", "").upper() == siglas_upper:
                return reg
        return None

    @classmethod
    def count(cls) -> int:
        """Retorna el número total de reguladores."""
        cls._load_data()
        return len(cls._reguladores) if cls._reguladores else 0
