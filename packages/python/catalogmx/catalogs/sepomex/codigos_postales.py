"""Catálogo de Códigos Postales SEPOMEX"""
import json
from pathlib import Path
from typing import Dict, List, Optional

class CodigosPostales:
    _data: Optional[List[Dict]] = None
    _by_cp: Optional[Dict[str, List[Dict]]] = None
    _by_estado: Optional[Dict[str, List[Dict]]] = None

    @classmethod
    def _load_data(cls):
        if cls._data is None:
            path = Path(__file__).parent.parent.parent.parent.parent.parent / 'shared-data' / 'sepomex' / 'codigos_postales.json'
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['codigos_postales']

            # Index by CP (can have multiple settlements)
            cls._by_cp = {}
            for item in cls._data:
                cp = item['cp']
                if cp not in cls._by_cp:
                    cls._by_cp[cp] = []
                cls._by_cp[cp].append(item)

            # Index by estado
            cls._by_estado = {}
            for item in cls._data:
                estado = item['estado']
                if estado not in cls._by_estado:
                    cls._by_estado[estado] = []
                cls._by_estado[estado].append(item)

    @classmethod
    def get_by_cp(cls, cp: str) -> List[Dict]:
        """Obtiene todos los asentamientos de un código postal"""
        cls._load_data()
        return cls._by_cp.get(cp, [])

    @classmethod
    def is_valid(cls, cp: str) -> bool:
        """Verifica si un código postal existe"""
        cls._load_data()
        return cp in cls._by_cp

    @classmethod
    def get_by_estado(cls, estado: str) -> List[Dict]:
        """Obtiene todos los códigos postales de un estado"""
        cls._load_data()
        return cls._by_estado.get(estado, [])

    @classmethod
    def get_all(cls) -> List[Dict]:
        """Obtiene todos los códigos postales"""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_municipio(cls, cp: str) -> Optional[str]:
        """Obtiene el municipio de un código postal"""
        settlements = cls.get_by_cp(cp)
        return settlements[0]['municipio'] if settlements else None

    @classmethod
    def get_estado(cls, cp: str) -> Optional[str]:
        """Obtiene el estado de un código postal"""
        settlements = cls.get_by_cp(cp)
        return settlements[0]['estado'] if settlements else None
