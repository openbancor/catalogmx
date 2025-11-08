"""Catálogo c_UsoCFDI"""
import json
from pathlib import Path

class UsoCFDICatalog:
    """Catálogo de Usos del CFDI del SAT (c_UsoCFDI)"""

    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga los datos del catálogo si aún no han sido cargados"""
        if cls._data is None:
            path = Path(__file__).parent.parent.parent.parent.parent.parent / 'shared-data' / 'sat' / 'cfdi_4.0' / 'uso_cfdi.json'
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['usos']
            cls._by_code = {item['code']: item for item in cls._data}

    @classmethod
    def get_uso(cls, code: str) -> dict | None:
        """Obtiene un uso del CFDI por su código"""
        cls._load_data()
        return cls._by_code.get(code.upper())

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Valida si un código de uso del CFDI es válido"""
        return cls.get_uso(code) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todos los usos del CFDI"""
        cls._load_data()
        return cls._data.copy()
