"""Catálogo c_RiesgoPuesto"""
import json
from pathlib import Path
from typing import Dict, List, Optional

class RiesgoPuestoCatalog:
    _data: Optional[List[Dict]] = None
    _by_code: Optional[Dict[str, Dict]] = None

    @classmethod
    def _load_data(cls):
        if cls._data is None:
            path = Path(__file__).parent.parent.parent.parent.parent.parent / 'shared-data' / 'sat' / 'nomina_1.2' / 'riesgo_puesto.json'
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['riesgos']
            cls._by_code = {item['code']: item for item in cls._data}

    @classmethod
    def get_riesgo(cls, code: str) -> Optional[Dict]:
        """Obtiene nivel de riesgo por código"""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de riesgo es válido"""
        return cls.get_riesgo(code) is not None

    @classmethod
    def get_all(cls) -> List[Dict]:
        """Obtiene todos los niveles de riesgo"""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_prima_media(cls, code: str) -> Optional[float]:
        """Obtiene la prima media del nivel de riesgo"""
        riesgo = cls.get_riesgo(code)
        return riesgo.get('prima_media') if riesgo else None

    @classmethod
    def validate_prima(cls, code: str, prima: float) -> bool:
        """Valida que la prima esté en el rango permitido"""
        riesgo = cls.get_riesgo(code)
        if not riesgo:
            return False
        return riesgo['prima_min'] <= prima <= riesgo['prima_max']
