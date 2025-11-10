"""Catálogo c_MetodoPago"""

import json
from pathlib import Path


class MetodoPagoCatalog:
    """Catálogo de Métodos de Pago del SAT (c_MetodoPago)"""

    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga los datos del catálogo si aún no han sido cargados"""
        if cls._data is None:
            path = (
                Path(__file__).parent.parent.parent.parent.parent.parent
                / "shared-data"
                / "sat"
                / "cfdi_4.0"
                / "metodo_pago.json"
            )
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
                # Handle both list and dict formats
                cls._data = data if isinstance(data, list) else data.get("metodos", data)
            cls._by_code = {item["code"]: item for item in cls._data}

    @classmethod
    def get_metodo(cls, code: str) -> dict | None:
        """Obtiene un método de pago por su código"""
        cls._load_data()
        return cls._by_code.get(code.upper())

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Valida si un código de método de pago es válido"""
        return cls.get_metodo(code) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todos los métodos de pago"""
        cls._load_data()
        return cls._data.copy()
