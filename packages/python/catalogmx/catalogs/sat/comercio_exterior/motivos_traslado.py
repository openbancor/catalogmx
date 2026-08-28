"""Catálogo c_MotivoTraslado para CFDI tipo T con Comercio Exterior."""

from catalogmx.catalogs.sat.comercio_exterior._resolver_views import (
    motivo_traslado_rows,
)


class MotivoTrasladoCatalog:
    """Catálogo de motivos de traslado para Comercio Exterior 2.0."""

    _data: list[dict] | None = None
    _motivo_by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga los motivos vigentes del artifact canónico CCE 2.0."""
        if cls._data is None:
            cls._data = motivo_traslado_rows()
            cls._motivo_by_code = {item["code"]: item for item in cls._data}

    @classmethod
    def get_motivo(cls, code: str) -> dict | None:
        """Obtiene un motivo de traslado por su código."""
        cls._load_data()
        return cls._motivo_by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de motivo es válido."""
        return cls.get_motivo(code) is not None

    @classmethod
    def requires_propietario(cls, code: str) -> bool:
        """Indica si la regla de aplicación requiere nodo Propietario."""
        motivo = cls.get_motivo(code)
        return motivo.get("requires_propietario", False) if motivo else False

    @classmethod
    def get_all(cls) -> list[dict]:
        """Retorna todos los motivos de traslado publicados por CCE 2.0."""
        cls._load_data()
        return cls._data.copy()
