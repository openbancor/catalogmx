"""Catálogo c_TipoJornada"""
import json
from pathlib import Path
from typing import Dict, List, Optional

class TipoJornadaCatalog:
    _data: Optional[List[Dict]] = None
    _by_code: Optional[Dict[str, Dict]] = None

    @classmethod
    def _load_data(cls):
        if cls._data is None:
            path = Path(__file__).parent.parent.parent.parent.parent.parent / 'shared-data' / 'sat' / 'nomina_1.2' / 'tipo_jornada.json'
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['jornadas']
            cls._by_code = {item['code']: item for item in cls._data}

    @classmethod
    def get_jornada(cls, code: str) -> Optional[Dict]:
        """Obtiene tipo de jornada por código"""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de jornada es válido"""
        return cls.get_jornada(code) is not None

    @classmethod
    def get_all(cls) -> List[Dict]:
        """Obtiene todos los tipos de jornada"""
        cls._load_data()
        return cls._data.copy()
