"""Catálogo c_TipoComprobante"""

from catalogmx.catalogs.sat.cfdi_4._resolver_views import code_description_rows


class TipoComprobanteCatalog:
    """Catálogo de Tipos de Comprobante del SAT (c_TipoComprobante)"""

    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy desde el artefacto canónico CFDI 4.0."""
        if cls._data is None:
            cls._data = code_description_rows("cfdi_40_tipos_comprobantes")
            cls._by_code = {item["code"]: item for item in cls._data}

    @classmethod
    def get_tipo(cls, code: str) -> dict | None:
        """Obtiene un tipo de comprobante por su código"""
        cls._load_data()
        return cls._by_code.get(code.upper())

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Valida si un código de tipo de comprobante es válido"""
        return cls.get_tipo(code) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todos los tipos de comprobante"""
        cls._load_data()
        return cls._data.copy()
