"""Catálogo c_NumAutorizacionNaviero - Puertos Marítimos"""

import json
from pathlib import Path

from catalogmx.utils.text import normalize_text


class PuertosMaritimos:
    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        if cls._data is None:
            path = (
                Path(__file__).parent.parent.parent.parent.parent.parent
                / "shared-data"
                / "sat"
                / "carta_porte_3"
                / "puertos_maritimos.json"
            )
            with open(path, encoding="utf-8") as f:
                cls._data = json.load(f)
            cls._by_code = {item["code"]: item for item in cls._data}

    @classmethod
    def get_puerto(cls, code: str) -> dict | None:
        """Obtiene puerto por código"""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de puerto es válido"""
        return cls.get_puerto(code) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todos los puertos"""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_by_coast(cls, coast: str) -> list[dict]:
        """Obtiene puertos por costa (insensible a acentos)"""
        cls._load_data()
        coast_normalized = normalize_text(coast)
        return [p for p in cls._data if normalize_text(p["coast"]) == coast_normalized]

    @classmethod
    def get_by_state(cls, state: str) -> list[dict]:
        """Obtiene puertos por estado (insensible a acentos)"""
        cls._load_data()
        state_normalized = normalize_text(state)
        return [p for p in cls._data if normalize_text(p["state"]) == state_normalized]

    @classmethod
    def search_by_name(cls, name: str) -> list[dict]:
        """Busca puertos por nombre (insensible a acentos)"""
        cls._load_data()
        name_normalized = normalize_text(name)
        return [p for p in cls._data if name_normalized in normalize_text(p["name"])]
