"""SAT Nómina 1.2 c_TipoContrato catalog."""

from __future__ import annotations

from ._base import NominaJsonCatalog


class TipoContratoCatalog(NominaJsonCatalog):
    filename = "tipo_contrato.json"

    @classmethod
    def get_contrato(cls, code: str):
        return cls.get_by_code(code)

    @classmethod
    def is_indeterminado(cls, code: str) -> bool:
        return code == "01" and cls.is_valid(code)
