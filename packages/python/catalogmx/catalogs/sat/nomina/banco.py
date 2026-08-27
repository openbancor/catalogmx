"""SAT Nómina 1.2 c_Banco catalog."""

from __future__ import annotations

from ._base import NominaJsonCatalog


class BancoCatalog(NominaJsonCatalog):
    filename = "banco.json"

    @classmethod
    def get_banco(cls, code: str):
        return cls.get_by_code(code)

    @classmethod
    def get_by_name(cls, name: str):
        query = name.casefold()
        return [
            item
            for item in cls.get_all()
            if query in str(item.get("name", "")).casefold()
            or query in str(item.get("full_name", "")).casefold()
        ]
