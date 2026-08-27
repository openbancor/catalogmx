"""SAT Nómina 1.2 c_PeriodicidadPago catalog."""

from __future__ import annotations

from ._base import NominaJsonCatalog


class PeriodicidadPagoCatalog(NominaJsonCatalog):
    filename = "periodicidad_pago.json"

    @classmethod
    def get_periodicidad(cls, code: str):
        return cls.get_by_code(code)

    @classmethod
    def get_days(cls, code: str):
        item = cls.get_by_code(code)
        return item.get("days") if item else None
