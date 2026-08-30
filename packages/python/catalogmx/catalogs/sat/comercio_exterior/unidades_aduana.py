"""Catálogo c_UnidadAduana - Unidades de Medida Aduanera."""

from catalogmx.catalogs.sat.comercio_exterior._resolver_views import (
    unidad_aduana_rows,
)


class UnidadAduanaCatalog:
    """Catálogo de unidades de medida aduanera de Comercio Exterior 2.0."""

    _data: list[dict] | None = None
    _unidad_by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga las unidades del artifact canónico CCE 2.0."""
        if cls._data is None:
            cls._data = unidad_aduana_rows()
            cls._unidad_by_code = {item["code"]: item for item in cls._data}

    @classmethod
    def get_unidad(cls, code: str) -> dict | None:
        """Obtiene una unidad de medida por su código."""
        cls._load_data()
        return cls._unidad_by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de unidad es válido."""
        return cls.get_unidad(code) is not None

    @classmethod
    def get_by_type(cls, unit_type: str) -> list[dict]:
        """Obtiene unidades por clasificación de conveniencia CatalogMX."""
        cls._load_data()
        return [item for item in cls._data if item.get("type") == unit_type]

    @classmethod
    def get_all(cls) -> list[dict]:
        """Retorna todas las unidades de medida publicadas por CCE 2.0."""
        cls._load_data()
        return cls._data.copy()
