"""SAT Nómina 1.2 c_TipoRegimen catalog."""

from __future__ import annotations

from ._base import NominaJsonCatalog


class TipoRegimenCatalog(NominaJsonCatalog):
    filename = "tipo_regimen.json"

    @classmethod
    def get_regimen(cls, code: str):
        return cls.get_by_code(code)

    @classmethod
    def is_asimilado(cls, code: str) -> bool:
        return code in {"05", "06", "07", "08", "09", "10", "11"} and cls.is_valid(code)
