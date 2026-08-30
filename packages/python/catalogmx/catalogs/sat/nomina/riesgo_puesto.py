"""SAT Nómina 1.2 c_RiesgoPuesto catalog."""

from __future__ import annotations

from ._base import NominaJsonCatalog


class RiesgoPuestoCatalog(NominaJsonCatalog):
    filename = "riesgo_puesto.json"

    @classmethod
    def get_riesgo(cls, code: str):
        return cls.get_by_code(code)

    @classmethod
    def get_prima_media(cls, code: str):
        item = cls.get_by_code(code)
        return item.get("prima_media") if item else None

    @classmethod
    def validate_prima(cls, code: str, prima: float) -> bool:
        item = cls.get_by_code(code)
        if not item:
            return False
        minimum = item.get("prima_minima")
        maximum = item.get("prima_maxima")
        if minimum is None or maximum is None:
            return False
        return float(minimum) <= prima <= float(maximum)
