"""Catálogo c_TipoRegimen"""

import json
from pathlib import Path


class TipoRegimenCatalog:
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
                / "tipo_regimen.json"
            )
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
                cls._data = data["regimenes"]
            cls._by_code = {item["code"]: item for item in cls._data}

    @classmethod
    def get_regimen(cls, code: str) -> dict | None:
        """Obtiene tipo de régimen por código"""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de régimen es válido"""
        return cls.get_regimen(code) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todos los tipos de régimen"""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def is_asimilado(cls, code: str) -> bool:
        """Verifica si es régimen asimilado a salarios"""
        return code in ["05", "06", "07", "08", "09", "10", "11", "12", "13"]
