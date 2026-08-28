"""Catálogo c_Impuesto"""

from catalogmx.catalogs.sat.cfdi_4._resolver_views import impuesto_rows


class ImpuestoCatalog:
    """Catálogo de Impuestos del SAT (c_Impuesto)"""

    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy desde el artefacto canónico CFDI 4.0."""
        if cls._data is None:
            cls._data = impuesto_rows()
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
