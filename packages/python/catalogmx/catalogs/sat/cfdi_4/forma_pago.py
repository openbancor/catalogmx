"""Catálogo c_FormaPago"""
import json
from pathlib import Path
from typing import Dict, List, Optional

class FormaPagoCatalog:
    _data: Optional[List[Dict]] = None
    _by_code: Optional[Dict[str, Dict]] = None

    @classmethod
    def _load_data(cls):
        if cls._data is None:
            path = Path(__file__).parent.parent.parent.parent.parent.parent / 'shared-data' / 'sat' / 'cfdi_4.0' / 'forma_pago.json'
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['formas_pago']
            cls._by_code = {item['code']: item for item in cls._data}

    @classmethod
    def get_forma_pago(cls, code: str) -> Optional[Dict]:
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        return cls.get_forma_pago(code) is not None

    @classmethod
    def get_all(cls) -> List[Dict]:
        cls._load_data()
        return cls._data.copy()
