"""Catálogo c_PeriodicidadPago"""
import json
from pathlib import Path

class PeriodicidadPagoCatalog:
    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        if cls._data is None:
            path = Path(__file__).parent.parent.parent.parent.parent.parent / 'shared-data' / 'sat' / 'nomina_1.2' / 'periodicidad_pago.json'
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['periodicidades']
            cls._by_code = {item['code']: item for item in cls._data}

    @classmethod
    def get_periodicidad(cls, code: str) -> dict | None:
        """Obtiene periodicidad de pago por código"""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de periodicidad es válido"""
        return cls.get_periodicidad(code) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todas las periodicidades"""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_days(cls, code: str) -> int | None:
        """Obtiene el número de días de la periodicidad"""
        periodicidad = cls.get_periodicidad(code)
        return periodicidad.get('days') if periodicidad else None
