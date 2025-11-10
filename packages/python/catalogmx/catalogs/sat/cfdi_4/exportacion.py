"""Catálogo c_Exportacion"""

import json
from pathlib import Path


class ExportacionCatalog:
    """Catálogo de Exportaciones del SAT (c_Exportacion)"""

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
                / "exportacion.json"
            )
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
                cls._data = data["exportaciones"]
            cls._by_code = {item["code"]: item for item in cls._data}

    @classmethod
    def get_exportacion(cls, code: str) -> dict | None:
        """Obtiene una exportación por su código"""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Valida si un código de exportación es válido"""
        return cls.get_exportacion(code) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todas las exportaciones"""
        cls._load_data()
        return cls._data.copy()
