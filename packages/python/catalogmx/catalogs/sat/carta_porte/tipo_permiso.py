"""Catálogo c_TipoPermiso - Tipos de Permiso."""

from catalogmx.catalogs.sat.carta_porte._resolver_views import tipo_permiso_rows


class TipoPermisoCatalog:
    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        if cls._data is None:
            cls._data = tipo_permiso_rows()
            cls._by_code = {item["code"]: item for item in cls._data}

    @classmethod
    def get_permiso(cls, code: str) -> dict | None:
        """Obtiene permiso por código."""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de permiso es válido."""
        return cls.get_permiso(code) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene los tipos de permiso publicados por SAT Carta Porte 3.1."""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_by_type(cls, tipo: str) -> list[dict]:
        """Busca por la clasificación de conveniencia derivada del texto SAT."""
        cls._load_data()
        return [item for item in cls._data if item["type"] == tipo]

    @classmethod
    def get_by_transport(cls, transport: str) -> list[dict]:
        """Obtiene permisos por clave de transporte publicada por SAT."""
        cls._load_data()
        return [item for item in cls._data if item["transport"] == transport]

    @classmethod
    def is_carga_permit(cls, code: str) -> bool:
        """Verifica si el texto oficial describe un permiso de carga."""
        permiso = cls.get_permiso(code)
        return permiso.get("type") == "Carga" if permiso else False
