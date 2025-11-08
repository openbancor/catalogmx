"""Catálogo c_Impuesto"""
import json
from pathlib import Path
from typing import Dict, List, Optional

class ImpuestoCatalog:
    _data: Optional[List[Dict]] = None
    _by_code: Optional[Dict[str, Dict]] = None

    @classmethod
    def _load_data(cls):
        if cls._data is None:
            path = Path(__file__).parent.parent.parent.parent.parent.parent / 'shared-data' / 'sat' / 'cfdi_4.0' / 'impuesto.json'
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['impuestos']
            cls._by_code = {item['code']: item for item in cls._data}

    @classmethod
    def get_impuesto(cls, code: str) -> Optional[Dict]:
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        return cls.get_impuesto(code) is not None

    @classmethod
    def supports_retention(cls, code: str) -> bool:
        impuesto = cls.get_impuesto(code)
        return impuesto.get('retention', False) if impuesto else False

    @classmethod
    def supports_transfer(cls, code: str) -> bool:
        impuesto = cls.get_impuesto(code)
        return impuesto.get('transfer', False) if impuesto else False

    @classmethod
    def get_all(cls) -> List[Dict]:
        cls._load_data()
        return cls._data.copy()
