"""Catálogo c_Exportacion"""

from catalogmx.catalogs.sat.cfdi_4._resolver_views import code_description_rows


class ExportacionCatalog:
    """Catálogo de Exportaciones del SAT (c_Exportacion)"""

    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy desde el artefacto canónico CFDI 4.0."""
        if cls._data is None:
            cls._data = code_description_rows("cfdi_40_exportaciones")
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
