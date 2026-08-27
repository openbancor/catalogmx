"""SAT Nómina 1.2 c_TipoJornada catalog."""

from __future__ import annotations

from ._base import NominaJsonCatalog


class TipoJornadaCatalog(NominaJsonCatalog):
    filename = "tipo_jornada.json"

    @classmethod
    def get_jornada(cls, code: str):
        return cls.get_by_code(code)
