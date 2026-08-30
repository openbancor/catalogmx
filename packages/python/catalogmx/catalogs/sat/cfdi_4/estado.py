"""Catálogo c_Estado compartido por CFDI y Nómina 1.2."""

import json
from importlib.resources import files


class EstadoCfdiCatalog:
    """Estados y provincias publicados por SAT como c_Estado."""

    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        if cls._data is None:
            # SAT defines c_Estado in catCFDI.xsd as an identifier set.  The
            # technical-mirror SQLite release is missing the DIF identifier,
            # so this catalog intentionally consumes the reviewed XSD-derived
            # package artifact also used to generate the TypeScript view.
            path = files("catalogmx.data").joinpath("cfdi-estado.json")
            with path.open(encoding="utf-8") as handle:
                document = json.load(handle)
            cls._data = [{"code": str(item["code"])} for item in document["data"]]
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
