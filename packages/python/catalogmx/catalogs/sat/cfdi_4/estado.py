"""Catálogo c_Estado compartido por CFDI y Nómina 1.2."""

from catalogmx.catalogs.sat.cfdi_4._resolver_views import code_description_rows


class EstadoCfdiCatalog:
    """Estados y provincias publicados por SAT como c_Estado."""

    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        if cls._data is None:
            cls._data = code_description_rows("cfdi_40_estados")
            cls._by_code = {item["code"]: item for item in cls._data}

    @classmethod
    def get_estado(cls, code: str) -> dict | None:
        cls._load_data()
        return cls._by_code.get(code.upper())

    @classmethod
    def is_valid(cls, code: str) -> bool:
        return cls.get_estado(code) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        cls._load_data()
        return cls._data.copy()
