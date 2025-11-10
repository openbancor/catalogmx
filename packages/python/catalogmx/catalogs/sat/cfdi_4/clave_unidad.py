"""
SAT CFDI 4.0 - Clave de Unidad (c_ClaveUnidad)

Catálogo de unidades de medida para productos y servicios.
Contiene ~2,400 unidades oficiales del SAT basadas en las
recomendaciones 20 y 21 de UN/ECE.
"""

import json
from pathlib import Path
from typing import TypedDict


class ClaveUnidad(TypedDict):
    """Estructura de una unidad de medida"""
    id: str
    nombre: str
    descripcion: str
    nota: str
    fechaDeInicioDeVigencia: str
    fechaDeFinDeVigencia: str
    simbolo: str


class ClaveUnidadCatalog:
    """
    Catálogo de claves de unidad SAT CFDI 4.0.

    Características:
    - ~2,400 unidades de medida oficiales
    - Basado en UN/ECE Recommendation 20 y 21
    - Incluye peso, longitud, volumen, tiempo, piezas, etc.
    - Distingue entre unidades vigentes y obsoletas
    - Búsqueda por ID, nombre, símbolo y categoría

    Ejemplo:
        >>> from catalogmx.catalogs.sat.cfdi_4 import ClaveUnidadCatalog
        >>>
        >>> # Obtener unidad por ID
        >>> metro = ClaveUnidadCatalog.get_unidad("MTR")
        >>> print(metro['nombre'])  # "Metro"
        >>>
        >>> # Buscar por nombre
        >>> kilos = ClaveUnidadCatalog.search_by_name("kilogramo")
        >>> for unidad in kilos:
        ...     print(f"{unidad['id']}: {unidad['nombre']}")
        >>>
        >>> # Validar unidad
        >>> if ClaveUnidadCatalog.is_valid("KGM"):
        ...     print("Unidad válida")
    """

    _data: list[ClaveUnidad] | None = None
    _by_id: dict[str, ClaveUnidad] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy de datos desde JSON"""
        if cls._data is not None:
            return

        # Path: catalogmx/packages/python/catalogmx/catalogs/sat/cfdi_4/clave_unidad.py
        # Target: catalogmx/packages/shared-data/sat/cfdi_4.0/clave_unidad.json
        data_path = (
            Path(__file__).parent.parent.parent.parent.parent.parent
            / 'shared-data' / 'sat' / 'cfdi_4.0' / 'clave_unidad.json'
        )

        with open(data_path, 'r', encoding='utf-8') as f:
            cls._data = json.load(f)

        # Crear índice por ID
        cls._by_id = {item['id']: item for item in cls._data}

    @classmethod
    def get_all(cls) -> list[ClaveUnidad]:
        """
        Obtiene todas las unidades.

        WARNING: Retorna ~2,400 unidades. Considere usar búsqueda o paginación.

        Returns:
            Lista completa de unidades

        Ejemplo:
            >>> unidades = ClaveUnidadCatalog.get_all()
            >>> print(f"Total unidades: {len(unidades)}")
        """
        cls._load_data()
        return cls._data.copy()  # type: ignore

    @classmethod
    def get_unidad(cls, id: str) -> ClaveUnidad | None:
        """
        Obtiene una unidad por su ID/clave.

        Args:
            id: Clave de la unidad (ej: "MTR", "KGM", "H87")

        Returns:
            Unidad o None si no existe

        Ejemplo:
            >>> metro = ClaveUnidadCatalog.get_unidad("MTR")
            >>> print(metro['nombre'])  # "Metro"
            >>> print(metro['simbolo'])  # "m"
        """
        cls._load_data()
        return cls._by_id.get(id)  # type: ignore

    @classmethod
    def is_valid(cls, id: str) -> bool:
        """
        Verifica si una clave de unidad existe.

        Args:
            id: Clave de la unidad

        Returns:
            True si existe, False en caso contrario

        Ejemplo:
            >>> ClaveUnidadCatalog.is_valid("KGM")  # True
            >>> ClaveUnidadCatalog.is_valid("INVALID")  # False
        """
        return cls.get_unidad(id) is not None

    @classmethod
    def search_by_name(cls, keyword: str) -> list[ClaveUnidad]:
        """
        Busca unidades por nombre (búsqueda parcial, case-insensitive).

        Args:
            keyword: Palabra clave a buscar en el nombre

        Returns:
            Lista de unidades que coinciden

        Ejemplo:
            >>> unidades = ClaveUnidadCatalog.search_by_name("kilogramo")
            >>> for u in unidades:
            ...     print(f"{u['id']}: {u['nombre']}")
        """
        cls._load_data()
        keyword_lower = keyword.lower()
        return [
            u for u in cls._data  # type: ignore
            if keyword_lower in u['nombre'].lower()
        ]

    @classmethod
    def search_by_symbol(cls, simbolo: str) -> list[ClaveUnidad]:
        """
        Busca unidades por símbolo (ej: "kg", "m", "l").

        Args:
            simbolo: Símbolo a buscar

        Returns:
            Lista de unidades con ese símbolo

        Ejemplo:
            >>> metros = ClaveUnidadCatalog.search_by_symbol("m")
            >>> for u in metros:
            ...     print(f"{u['id']}: {u['nombre']} ({u['simbolo']})")
        """
        cls._load_data()
        simbolo_lower = simbolo.lower()
        return [
            u for u in cls._data  # type: ignore
            if u['simbolo'].lower() == simbolo_lower
        ]

    @classmethod
    def get_vigentes(cls) -> list[ClaveUnidad]:
        """
        Obtiene unidades vigentes (sin fecha de fin de vigencia).

        Returns:
            Lista de unidades vigentes

        Ejemplo:
            >>> vigentes = ClaveUnidadCatalog.get_vigentes()
            >>> print(f"Unidades vigentes: {len(vigentes)}")
        """
        cls._load_data()
        return [
            u for u in cls._data  # type: ignore
            if not u['fechaDeFinDeVigencia'] or u['fechaDeFinDeVigencia'] == ''
        ]

    @classmethod
    def get_obsoletas(cls) -> list[ClaveUnidad]:
        """
        Obtiene unidades obsoletas (con fecha de fin de vigencia).

        Returns:
            Lista de unidades obsoletas

        Ejemplo:
            >>> obsoletas = ClaveUnidadCatalog.get_obsoletas()
            >>> print(f"Unidades obsoletas: {len(obsoletas)}")
        """
        cls._load_data()
        return [
            u for u in cls._data  # type: ignore
            if u['fechaDeFinDeVigencia'] and u['fechaDeFinDeVigencia'] != ''
        ]

    @classmethod
    def search_by_category(cls, categoria: str) -> list[ClaveUnidad]:
        """
        Busca unidades por categoría (en el nombre).

        Categorías soportadas: peso, longitud, volumen, tiempo, pieza

        Args:
            categoria: Categoría a buscar

        Returns:
            Lista de unidades en esa categoría

        Ejemplo:
            >>> pesos = ClaveUnidadCatalog.search_by_category("peso")
            >>> for u in pesos:
            ...     print(f"{u['id']}: {u['nombre']}")
        """
        cls._load_data()
        cat_lower = categoria.lower()

        keywords: dict[str, list[str]] = {
            'peso': ['kilogramo', 'gramo', 'tonelada', 'libra', 'onza'],
            'longitud': ['metro', 'centímetro', 'milímetro', 'kilómetro', 'pulgada', 'pie', 'yarda'],
            'volumen': ['litro', 'mililitro', 'metro cúbico', 'galón', 'barril'],
            'tiempo': ['hora', 'minuto', 'segundo', 'día', 'semana', 'mes', 'año'],
            'pieza': ['pieza', 'unidad', 'paquete', 'caja', 'docena']
        }

        search_words = keywords.get(cat_lower, [cat_lower])

        results = []
        for u in cls._data:  # type: ignore
            nombre_lower = u['nombre'].lower()
            if any(word in nombre_lower for word in search_words):
                results.append(u)

        return results

    @classmethod
    def get_total_count(cls) -> int:
        """
        Obtiene el total de unidades en el catálogo.

        Returns:
            Número total de unidades

        Ejemplo:
            >>> total = ClaveUnidadCatalog.get_total_count()
            >>> print(f"Total: {total} unidades")
        """
        cls._load_data()
        return len(cls._data)  # type: ignore

    @classmethod
    def get_statistics(cls) -> dict[str, int]:
        """
        Obtiene estadísticas del catálogo.

        Returns:
            Diccionario con estadísticas de unidades

        Ejemplo:
            >>> stats = ClaveUnidadCatalog.get_statistics()
            >>> print(f"Total: {stats['total']}")
            >>> print(f"Vigentes: {stats['vigentes']}")
            >>> print(f"Obsoletas: {stats['obsoletas']}")
        """
        cls._load_data()

        con_simbolo = sum(
            1 for u in cls._data  # type: ignore
            if u['simbolo'] and u['simbolo'] != ''
        )

        return {
            'total': len(cls._data),  # type: ignore
            'vigentes': len(cls.get_vigentes()),
            'obsoletas': len(cls.get_obsoletas()),
            'con_simbolo': con_simbolo,
            'sin_simbolo': len(cls._data) - con_simbolo  # type: ignore
        }
