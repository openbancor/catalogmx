"""Catálogo c_UnidadAduana - Unidades de Medida Aduanera"""

import json
from pathlib import Path


class UnidadAduanaCatalog:
    """Catálogo de unidades de medida reconocidas por aduanas"""

    _data: list[dict] | None = None
    _unidad_by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga los datos del catálogo desde el archivo JSON compartido"""
        if cls._data is None:
            current_file = Path(__file__)
            shared_data_path = (
                current_file.parent.parent.parent.parent.parent.parent
                / "shared-data"
                / "sat"
                / "comercio_exterior"
                / "unidades_aduana.json"
            )

            with open(shared_data_path, encoding="utf-8") as f:
                data = json.load(f)
                # Handle both list and dict formats
                cls._data = data if isinstance(data, list) else data.get("unidades", data)

            cls._unidad_by_code = {item["code"]: item for item in cls._data}

    @classmethod
    def get_unidad(cls, code: str) -> dict | None:
        """Obtiene una unidad de medida por su código"""
        cls._load_data()
        return cls._unidad_by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de unidad es válido"""
        return cls.get_unidad(code) is not None

    @classmethod
    def get_by_type(cls, unit_type: str) -> list[dict]:
        """Obtiene unidades por tipo (weight, volume, length, area, unit, container)"""
        cls._load_data()
        return [item for item in cls._data if item.get("type") == unit_type]

    @classmethod
    def get_all(cls) -> list[dict]:
        """Retorna todas las unidades de medida aduanera"""
        cls._load_data()
        return cls._data.copy()
