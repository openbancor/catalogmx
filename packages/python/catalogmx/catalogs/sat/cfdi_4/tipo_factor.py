"""Catálogo de Tipos de Factor (SAT)"""

from catalogmx.catalogs.sat.cfdi_4._resolver_views import value_rows


class TipoFactor:
    _data = None

    @classmethod
    def _load_data(cls):
        if cls._data is None:
            rows = value_rows("cfdi_40_tipos_factores")
            cls._data = {item["valor"]: item for item in rows}
        return cls._data

    @classmethod
    def get_data(cls):
        return cls._load_data()

    @classmethod
    def get_by_id(cls, tipo_factor_id):
        """Busca un tipo de factor por su ID."""
        data = cls.get_data()
        return data.get(tipo_factor_id)

    @classmethod
    def is_valid(cls, tipo_factor_id):
        """Verifica si un ID de tipo de factor es válido."""
        return tipo_factor_id in cls.get_data()
