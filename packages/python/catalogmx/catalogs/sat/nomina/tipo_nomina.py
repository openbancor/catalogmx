"""SAT Nómina 1.2 c_TipoNomina catalog."""

from __future__ import annotations

from ._base import NominaJsonCatalog


class TipoNominaCatalog(NominaJsonCatalog):
    filename = "tipo_nomina.json"

    @classmethod
    def get_tipo(cls, code: str):
        return cls.get_by_code(code)

    @classmethod
    def is_ordinaria(cls, code: str) -> bool:
        return code == "O" and cls.is_valid(code)

    @classmethod
    def is_extraordinaria(cls, code: str) -> bool:
        return code == "E" and cls.is_valid(code)
