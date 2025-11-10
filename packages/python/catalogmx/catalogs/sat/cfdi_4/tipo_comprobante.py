"""Catálogo c_TipoComprobante"""
import json
from pathlib import Path


class TipoComprobanteCatalog:
    """Catálogo de Tipos de Comprobante del SAT (c_TipoComprobante)"""

    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga los datos del catálogo si aún no han sido cargados"""
        if cls._data is None:
            path = Path(__file__).parent.parent.parent.parent.parent.parent / 'shared-data' / 'sat' / 'cfdi_4.0' / 'tipo_comprobante.json'
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['tipos']
            cls._by_code = {item['code']: item for item in cls._data}

    @classmethod
    def get_tipo(cls, code: str) -> dict | None:
        """Obtiene un tipo de comprobante por su código"""
        cls._load_data()
        return cls._by_code.get(code.upper())

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Valida si un código de tipo de comprobante es válido"""
        return cls.get_tipo(code) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todos los tipos de comprobante"""
        cls._load_data()
        return cls._data.copy()
