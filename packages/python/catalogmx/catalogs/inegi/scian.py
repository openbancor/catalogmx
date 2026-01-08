"""
Catálogo SCIAN - Sistema de Clasificación Industrial de América del Norte.

INEGI - Clasificación de actividades económicas para México, EE.UU. y Canadá.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict


class SectorSCIAN(TypedDict):
    """Estructura de un sector SCIAN."""

    codigo: str
    nombre: str
    nombre_corto: str
    subsectores: int
    ramas: int
    descripcion: str


class SCIANCatalog:
    """Catálogo de sectores SCIAN (Sistema de Clasificación Industrial de América del Norte)."""

    _data: dict | None = None
    _sectores: list[SectorSCIAN] | None = None
    _by_codigo: dict[str, SectorSCIAN] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy de los datos del catálogo."""
        if cls._data is not None:
            return

        data_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "shared-data"
            / "inegi"
            / "scian"
            / "sectores.json"
        )

        with open(data_path, encoding="utf-8") as f:
            cls._data = json.load(f)

        cls._sectores = cls._data.get("sectores", [])
        cls._by_codigo = {s["codigo"]: s for s in cls._sectores}

    @classmethod
    def get_all_sectores(cls) -> list[SectorSCIAN]:
        """Obtiene todos los sectores SCIAN (20 sectores)."""
        cls._load_data()
        return cls._sectores.copy() if cls._sectores else []

    @classmethod
    def get_sector_by_codigo(cls, codigo: str) -> SectorSCIAN | None:
        """Obtiene un sector por su código (2 dígitos)."""
        cls._load_data()
        return cls._by_codigo.get(codigo) if cls._by_codigo else None

    @classmethod
    def is_valid_sector(cls, codigo: str) -> bool:
        """Valida si un código de sector existe."""
        return cls.get_sector_by_codigo(codigo) is not None

    @classmethod
    def search(cls, query: str) -> list[SectorSCIAN]:
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
    def get_sector_for_code(cls, codigo: str) -> SectorSCIAN | None:
        """
        Obtiene el sector al que pertenece un código SCIAN de cualquier nivel.

        Por ejemplo: para código "311811" (Panaderías) retorna sector "31-33" (Manufactura).
        """
        cls._load_data()
        if not cls._sectores:
            return None

        # Obtener los primeros 2 dígitos
        codigo_2 = codigo[:2] if len(codigo) >= 2 else codigo

        # Buscar coincidencia directa o en rangos
        for sector in cls._sectores:
            sector_codigo = sector["codigo"]

            # Manejar rangos como "31-33" o "48-49"
            if "-" in sector_codigo:
                inicio, fin = sector_codigo.split("-")
                if inicio <= codigo_2 <= fin:
                    return sector
            elif sector_codigo == codigo_2:
                return sector

        return None

    @classmethod
    def get_totales(cls) -> dict[str, int]:
        """Retorna los totales de la estructura SCIAN."""
        cls._load_data()
        return cls._data.get("totales", {}) if cls._data else {}

    @classmethod
    def count_sectores(cls) -> int:
        """Retorna el número total de sectores."""
        cls._load_data()
        return len(cls._sectores) if cls._sectores else 0
