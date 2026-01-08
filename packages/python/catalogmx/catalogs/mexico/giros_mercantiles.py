"""
Catálogo de Giros Mercantiles - Clasificación de negocios en México.

Catálogo de actividades comerciales comunes para licencias de funcionamiento.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict


class GiroMercantil(TypedDict):
    """Estructura de un giro mercantil."""

    id: str
    nombre: str
    categoria: str
    requiere_licencia_alcohol: bool


class CategoriaMercantil(TypedDict):
    """Estructura de una categoría de giros."""

    id: str
    nombre: str
    descripcion: str


class GirosMercantilesCatalog:
    """Catálogo de giros mercantiles comunes en México."""

    _data: dict | None = None
    _giros: list[GiroMercantil] | None = None
    _categorias: list[CategoriaMercantil] | None = None
    _by_id: dict[str, GiroMercantil] | None = None
    _by_categoria: dict[str, list[GiroMercantil]] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy de los datos del catálogo."""
        if cls._data is not None:
            return

        data_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "shared-data"
            / "mexico"
            / "giros_mercantiles.json"
        )

        with open(data_path, encoding="utf-8") as f:
            cls._data = json.load(f)

        cls._giros = cls._data.get("giros", [])
        cls._categorias = cls._data.get("categorias", [])
        cls._by_id = {g["id"]: g for g in cls._giros}

        # Agrupar por categoría
        cls._by_categoria = {}
        for giro in cls._giros:
            cat = giro.get("categoria", "otro")
            if cat not in cls._by_categoria:
                cls._by_categoria[cat] = []
            cls._by_categoria[cat].append(giro)

    @classmethod
    def get_all(cls) -> list[GiroMercantil]:
        """Obtiene todos los giros mercantiles."""
        cls._load_data()
        return cls._giros.copy() if cls._giros else []

    @classmethod
    def get_by_id(cls, giro_id: str) -> GiroMercantil | None:
        """Obtiene un giro por su ID."""
        cls._load_data()
        return cls._by_id.get(giro_id) if cls._by_id else None

    @classmethod
    def is_valid(cls, giro_id: str) -> bool:
        """Valida si un ID de giro existe."""
        return cls.get_by_id(giro_id) is not None

    @classmethod
    def get_categorias(cls) -> list[CategoriaMercantil]:
        """Obtiene todas las categorías."""
        cls._load_data()
        return cls._categorias.copy() if cls._categorias else []

    @classmethod
    def get_by_categoria(cls, categoria: str) -> list[GiroMercantil]:
        """Obtiene giros por categoría."""
        cls._load_data()
        return cls._by_categoria.get(categoria, []).copy() if cls._by_categoria else []

    @classmethod
    def get_requieren_licencia_alcohol(cls) -> list[GiroMercantil]:
        """Obtiene giros que requieren licencia de alcohol."""
        cls._load_data()
        if not cls._giros:
            return []
        return [g for g in cls._giros if g.get("requiere_licencia_alcohol")]

    @classmethod
    def search(cls, query: str) -> list[GiroMercantil]:
        """Busca giros por nombre."""
        cls._load_data()
        if not cls._giros:
            return []

        query_lower = query.lower()
        return [g for g in cls._giros if query_lower in g.get("nombre", "").lower()]

    @classmethod
    def count(cls) -> int:
        """Retorna el número total de giros."""
        cls._load_data()
        return len(cls._giros) if cls._giros else 0
