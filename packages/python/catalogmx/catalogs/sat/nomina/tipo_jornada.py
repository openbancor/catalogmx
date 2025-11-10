"""Catálogo c_TipoJornada"""

import json
from pathlib import Path


class TipoJornadaCatalog:
    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        if cls._data is None:
            path = (
                Path(__file__).parent.parent.parent.parent.parent.parent
                / "shared-data"
                / "sat"
                / "nomina_1.2"
                / "tipo_jornada.json"
            )
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
                # Handle both list and dict formats
                cls._data = data if isinstance(data, list) else data.get("jornadas", data)
            cls._by_code = {item["code"]: item for item in cls._data}

    @classmethod
    def get_jornada(cls, code: str) -> dict | None:
        """Obtiene tipo de jornada por código"""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de jornada es válido"""
        return cls.get_jornada(code) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todos los tipos de jornada"""
        cls._load_data()
        return cls._data.copy()
