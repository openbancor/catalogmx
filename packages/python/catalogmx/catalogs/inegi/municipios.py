"""Catálogo de Municipios INEGI"""
import json
from pathlib import Path
from typing import Dict, List, Optional

class MunicipiosCatalog:
    _data: Optional[List[Dict]] = None
    _by_cve_completa: Optional[Dict[str, Dict]] = None
    _by_entidad: Optional[Dict[str, List[Dict]]] = None

    @classmethod
    def _load_data(cls):
        if cls._data is None:
            path = Path(__file__).parent.parent.parent.parent.parent.parent / 'shared-data' / 'inegi' / 'municipios_completo.json'
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['municipios']

            cls._by_cve_completa = {item['cve_completa']: item for item in cls._data}

            # Index by entidad
            cls._by_entidad = {}
            for item in cls._data:
                entidad = item['cve_entidad']
                if entidad not in cls._by_entidad:
                    cls._by_entidad[entidad] = []
                cls._by_entidad[entidad].append(item)

    @classmethod
    def get_municipio(cls, cve_completa: str) -> Optional[Dict]:
        """Obtiene municipio por clave completa (5 dígitos)"""
        cls._load_data()
        return cls._by_cve_completa.get(cve_completa)

    @classmethod
    def get_by_entidad(cls, cve_entidad: str) -> List[Dict]:
        """Obtiene todos los municipios de una entidad"""
        cls._load_data()
        return cls._by_entidad.get(cve_entidad, [])

    @classmethod
    def is_valid(cls, cve_completa: str) -> bool:
        """Verifica si una clave de municipio es válida"""
        return cls.get_municipio(cve_completa) is not None

    @classmethod
    def get_all(cls) -> List[Dict]:
        """Obtiene todos los municipios"""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def search_by_name(cls, nombre: str) -> List[Dict]:
        """Busca municipios por nombre (búsqueda parcial, insensible a mayúsculas)"""
        cls._load_data()
        nombre_lower = nombre.lower()
        return [m for m in cls._data if nombre_lower in m['nom_municipio'].lower()]
