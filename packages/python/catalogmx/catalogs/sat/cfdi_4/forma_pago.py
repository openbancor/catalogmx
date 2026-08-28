"""Catálogo c_FormaPago"""

from catalogmx.catalogs.sat.cfdi_4._resolver_views import code_description_rows


class FormaPagoCatalog:
    """Catálogo de Formas de Pago del SAT (c_FormaPago)"""

    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy desde el artefacto canónico CFDI 4.0."""
        if cls._data is None:
            cls._data = code_description_rows("cfdi_40_formas_pago")
            cls._by_code = {item["code"]: item for item in cls._data}

    @classmethod
    def get_forma_pago(cls, code: str) -> dict | None:
        """Obtiene una forma de pago por su código"""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Valida si un código de forma de pago es válido"""
        return cls.get_forma_pago(code) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todas las formas de pago"""
        cls._load_data()
        return cls._data.copy()
