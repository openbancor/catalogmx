"""Catálogo c_TipoEmbalaje - Tipos de Embalaje."""

from catalogmx.catalogs.sat.carta_porte._resolver_views import tipo_embalaje_rows


class TipoEmbalajeCatalog:
    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        if cls._data is None:
            cls._data = tipo_embalaje_rows()
            cls._by_code = {item["code"]: item for item in cls._data}

    @classmethod
    def get_embalaje(cls, code: str) -> dict | None:
        """Obtiene embalaje por código."""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de embalaje es válido."""
        return cls.get_embalaje(code) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene los tipos de embalaje publicados por SAT Carta Porte 3.1."""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_by_material(cls, material: str) -> list[dict]:
        """Busca por la etiqueta de material derivada del texto oficial."""
        cls._load_data()
        return [item for item in cls._data if item["material"] == material]
