"""Catálogo c_Banco"""
import json
from pathlib import Path
from typing import Dict, List, Optional

class BancoCatalog:
    _data: Optional[List[Dict]] = None
    _by_code: Optional[Dict[str, Dict]] = None
    _by_name: Optional[Dict[str, Dict]] = None

    @classmethod
    def _load_data(cls):
        if cls._data is None:
            path = Path(__file__).parent.parent.parent.parent.parent.parent / 'shared-data' / 'sat' / 'nomina_1.2' / 'banco.json'
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['bancos']
            cls._by_code = {item['code']: item for item in cls._data}
            cls._by_name = {item['name']: item for item in cls._data}

    @classmethod
    def get_banco(cls, code: str) -> Optional[Dict]:
        """Obtiene banco por código"""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def get_by_name(cls, name: str) -> Optional[Dict]:
        """Obtiene banco por nombre corto"""
        cls._load_data()
        return cls._by_name.get(name)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de banco es válido"""
        return cls.get_banco(code) is not None

    @classmethod
    def get_all(cls) -> List[Dict]:
        """Obtiene todos los bancos"""
        cls._load_data()
        return cls._data.copy()
