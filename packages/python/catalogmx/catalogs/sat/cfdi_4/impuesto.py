"""Catálogo c_Impuesto"""

import json
from pathlib import Path


class ImpuestoCatalog:
    """Catálogo de Impuestos del SAT (c_Impuesto)"""

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
                / "impuesto.json"
            )
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
                cls._data = data["impuestos"]
            cls._by_code = {item["code"]: item for item in cls._data}

    @classmethod
    def get_impuesto(cls, code: str) -> dict | None:
        """Obtiene un impuesto por su código"""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Valida si un código de impuesto es válido"""
        return cls.get_impuesto(code) is not None

    @classmethod
    def supports_retention(cls, code: str) -> bool:
        """Valida si un impuesto soporta retención"""
        impuesto = cls.get_impuesto(code)
        return impuesto.get("retention", False) if impuesto else False

    @classmethod
    def supports_transfer(cls, code: str) -> bool:
        """Valida si un impuesto soporta traslado"""
        impuesto = cls.get_impuesto(code)
        return impuesto.get("transfer", False) if impuesto else False

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todos los impuestos"""
        cls._load_data()
        return cls._data.copy()
