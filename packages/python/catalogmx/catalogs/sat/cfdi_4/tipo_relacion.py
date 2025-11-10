"""Catálogo c_TipoRelacion"""

import json
from pathlib import Path


class TipoRelacionCatalog:
    """Catálogo de Tipos de Relación del SAT (c_TipoRelacion)"""

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
                / "tipo_relacion.json"
            )
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
                # Handle both list and dict formats
                cls._data = data if isinstance(data, list) else data.get("tipos", data)
            cls._by_code = {item["code"]: item for item in cls._data}

    @classmethod
    def get_tipo(cls, code: str) -> dict | None:
        """Obtiene un tipo de relación por su código"""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Valida si un código de tipo de relación es válido"""
        return cls.get_tipo(code) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todos los tipos de relación"""
        cls._load_data()
        return cls._data.copy()
