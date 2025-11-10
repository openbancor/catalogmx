"""Catálogo c_Banco"""

import json
from pathlib import Path


class BancoCatalog:
    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None
    _by_name: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        if cls._data is None:
            path = (
                Path(__file__).parent.parent.parent.parent.parent.parent
                / "shared-data"
                / "sat"
                / "nomina_1.2"
                / "banco.json"
            )
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
                # Handle both list and dict formats
                cls._data = data if isinstance(data, list) else data.get("bancos", data)
            cls._by_code = {item["code"]: item for item in cls._data}
            cls._by_name = {item["name"]: item for item in cls._data}

    @classmethod
    def get_banco(cls, code: str) -> dict | None:
        """Obtiene banco por código"""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def get_by_name(cls, name: str) -> dict | None:
        """Obtiene banco por nombre corto"""
        cls._load_data()
        return cls._by_name.get(name)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de banco es válido"""
        return cls.get_banco(code) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todos los bancos"""
        cls._load_data()
        return cls._data.copy()
