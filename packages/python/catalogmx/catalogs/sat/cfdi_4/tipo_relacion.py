"""Catálogo c_TipoRelacion"""

from catalogmx.catalogs.sat.cfdi_4._resolver_views import code_description_rows


class TipoRelacionCatalog:
    """Catálogo de Tipos de Relación del SAT (c_TipoRelacion)"""

    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy desde el artefacto canónico CFDI 4.0."""
        if cls._data is None:
            cls._data = code_description_rows("cfdi_40_tipos_relaciones")
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
