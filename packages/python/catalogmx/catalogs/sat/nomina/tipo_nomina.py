"""Catálogo c_TipoNomina"""
import json
from pathlib import Path
from typing import Dict, List, Optional

class TipoNominaCatalog:
    _data: Optional[List[Dict]] = None
    _by_code: Optional[Dict[str, Dict]] = None

    @classmethod
    def _load_data(cls):
        if cls._data is None:
            path = Path(__file__).parent.parent.parent.parent.parent.parent / 'shared-data' / 'sat' / 'nomina_1.2' / 'tipo_nomina.json'
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['tipos']
            cls._by_code = {item['code']: item for item in cls._data}

    @classmethod
    def get_tipo(cls, code: str) -> Optional[Dict]:
        """Obtiene tipo de nómina por código"""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de tipo de nómina es válido"""
        return cls.get_tipo(code) is not None

    @classmethod
    def get_all(cls) -> List[Dict]:
        """Obtiene todos los tipos de nómina"""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def is_ordinaria(cls, code: str) -> bool:
        """Verifica si es nómina ordinaria"""
        return code == 'O'

    @classmethod
    def is_extraordinaria(cls, code: str) -> bool:
        """Verifica si es nómina extraordinaria"""
        return code == 'E'
