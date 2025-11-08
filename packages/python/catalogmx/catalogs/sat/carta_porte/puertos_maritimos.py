"""Catálogo c_NumAutorizacionNaviero - Puertos Marítimos"""
import json
from pathlib import Path
from typing import Dict, List, Optional

class PuertosMaritimos:
    _data: Optional[List[Dict]] = None
    _by_code: Optional[Dict[str, Dict]] = None

    @classmethod
    def _load_data(cls):
        if cls._data is None:
            path = Path(__file__).parent.parent.parent.parent.parent.parent / 'shared-data' / 'sat' / 'carta_porte_3' / 'puertos_maritimos.json'
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['puertos']
            cls._by_code = {item['code']: item for item in cls._data}

    @classmethod
    def get_puerto(cls, code: str) -> Optional[Dict]:
        """Obtiene puerto por código"""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de puerto es válido"""
        return cls.get_puerto(code) is not None

    @classmethod
    def get_all(cls) -> List[Dict]:
        """Obtiene todos los puertos"""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_by_coast(cls, coast: str) -> List[Dict]:
        """Obtiene puertos por costa (Pacífico, Golfo de México, Golfo de California, Caribe)"""
        cls._load_data()
        return [p for p in cls._data if p['coast'] == coast]

    @classmethod
    def get_by_state(cls, state: str) -> List[Dict]:
        """Obtiene puertos por estado"""
        cls._load_data()
        return [p for p in cls._data if p['state'] == state]
