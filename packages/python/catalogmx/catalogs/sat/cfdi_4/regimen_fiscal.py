"""Catálogo c_RegimenFiscal"""

from catalogmx.catalogs.sat.cfdi_4._resolver_views import regimen_fiscal_rows


class RegimenFiscalCatalog:
    """Catálogo de Regímenes Fiscales del SAT (c_RegimenFiscal)"""

    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy desde el artefacto canónico CFDI 4.0."""
        if cls._data is None:
            cls._data = regimen_fiscal_rows()
            cls._by_code = {item["code"]: item for item in cls._data}

    @classmethod
    def get_regimen(cls, code: str) -> dict | None:
        """Obtiene un régimen fiscal por su código"""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Valida si un código de régimen fiscal es válido"""
        return cls.get_regimen(code) is not None

    @classmethod
    def is_valid_for_persona_fisica(cls, code: str) -> bool:
        """Valida si un régimen es válido para persona física"""
        regimen = cls.get_regimen(code)
        return regimen.get("fisica", False) if regimen else False

    @classmethod
    def is_valid_for_persona_moral(cls, code: str) -> bool:
        """Valida si un régimen es válido para persona moral"""
        regimen = cls.get_regimen(code)
        return regimen.get("moral", False) if regimen else False

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todos los regímenes fiscales"""
        cls._load_data()
        return cls._data.copy()
