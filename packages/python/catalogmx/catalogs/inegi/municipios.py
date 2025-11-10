"""Catálogo de Municipios INEGI"""
import json
from pathlib import Path

from catalogmx.utils.text import normalize_text


class MunicipiosCatalog:
    _data: list[dict] | None = None
    _by_cve_completa: dict[str, dict] | None = None
    _by_entidad: dict[str, list[dict]] | None = None

    @classmethod
    def _load_data(cls) -> None:
        if cls._data is None:
            # Path: catalogmx/packages/python/catalogmx/catalogs/inegi/municipios.py
            # Target: catalogmx/packages/shared-data/inegi/municipios_completo.json
            path = Path(__file__).parent.parent.parent.parent.parent / 'shared-data' / 'inegi' / 'municipios_completo.json'
            with open(path, encoding='utf-8') as f:
                cls._data = json.load(f)

            cls._by_cve_completa = {item['cve_completa']: item for item in cls._data}

            # Index by entidad
            cls._by_entidad = {}
            for item in cls._data:
                entidad = item['cve_entidad']
                if entidad not in cls._by_entidad:
                    cls._by_entidad[entidad] = []
                cls._by_entidad[entidad].append(item)

    @classmethod
    def get_municipio(cls, cve_completa: str) -> dict | None:
        """Obtiene municipio por clave completa (5 dígitos)"""
        cls._load_data()
        return cls._by_cve_completa.get(cve_completa)

    @classmethod
    def get_by_entidad(cls, cve_entidad: str) -> list[dict]:
        """Obtiene todos los municipios de una entidad"""
        cls._load_data()
        return cls._by_entidad.get(cve_entidad, [])

    @classmethod
    def is_valid(cls, cve_completa: str) -> bool:
        """Verifica si una clave de municipio es válida"""
        return cls.get_municipio(cve_completa) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todos los municipios"""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def search_by_name(cls, nombre: str) -> list[dict]:
        """
        Busca municipios por nombre (búsqueda parcial, insensible a acentos).

        Ejemplo:
            >>> # Ambas búsquedas funcionan igual
            >>> munis = MunicipiosCatalog.search_by_name("leon")
            >>> munis = MunicipiosCatalog.search_by_name("león")  # mismo resultado
        """
        cls._load_data()
        nombre_normalized = normalize_text(nombre)
        return [m for m in cls._data if nombre_normalized in normalize_text(m['nom_municipio'])]
