"""Catálogo c_RegimenFiscal"""
import json
from pathlib import Path
from typing import Dict, List, Optional

class RegimenFiscalCatalog:
    _data: Optional[List[Dict]] = None
    _by_code: Optional[Dict[str, Dict]] = None

    @classmethod
    def _load_data(cls):
        if cls._data is None:
            path = Path(__file__).parent.parent.parent.parent.parent.parent / 'shared-data' / 'sat' / 'cfdi_4.0' / 'regimen_fiscal.json'
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['regimenes']
            cls._by_code = {item['code']: item for item in cls._data}

    @classmethod
    def get_regimen(cls, code: str) -> Optional[Dict]:
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        return cls.get_regimen(code) is not None

    @classmethod
    def is_valid_for_persona_fisica(cls, code: str) -> bool:
        regimen = cls.get_regimen(code)
        return regimen.get('fisica', False) if regimen else False

    @classmethod
    def is_valid_for_persona_moral(cls, code: str) -> bool:
        regimen = cls.get_regimen(code)
        return regimen.get('moral', False) if regimen else False

    @classmethod
    def get_all(cls) -> List[Dict]:
        cls._load_data()
        return cls._data.copy()
