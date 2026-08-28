"""Catálogo c_MetodoPago"""

from catalogmx.catalogs.sat.cfdi_4._resolver_views import code_description_rows


class MetodoPagoCatalog:
    """Catálogo de Métodos de Pago del SAT (c_MetodoPago)"""

    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy desde el artefacto canónico CFDI 4.0."""
        if cls._data is None:
            cls._data = code_description_rows("cfdi_40_metodos_pago")
            cls._by_code = {item["code"]: item for item in cls._data}

    @classmethod
    def get_metodo(cls, code: str) -> dict | None:
        """Obtiene un método de pago por su código"""
        cls._load_data()
        return cls._by_code.get(code.upper())

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Valida si un código de método de pago es válido"""
        return cls.get_metodo(code) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todos los métodos de pago"""
        cls._load_data()
        return cls._data.copy()
