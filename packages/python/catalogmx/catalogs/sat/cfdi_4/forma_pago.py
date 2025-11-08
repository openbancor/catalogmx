"""Catálogo c_FormaPago"""
import json
from pathlib import Path

class FormaPagoCatalog:
    """Catálogo de Formas de Pago del SAT (c_FormaPago)"""

    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga los datos del catálogo si aún no han sido cargados"""
        if cls._data is None:
            path = Path(__file__).parent.parent.parent.parent.parent.parent / 'shared-data' / 'sat' / 'cfdi_4.0' / 'forma_pago.json'
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['formas_pago']
            cls._by_code = {item['code']: item for item in cls._data}

    @classmethod
    def get_forma_pago(cls, code: str) -> dict | None:
        """Obtiene una forma de pago por su código"""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Valida si un código de forma de pago es válido"""
        return cls.get_forma_pago(code) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todas las formas de pago"""
        cls._load_data()
        return cls._data.copy()
