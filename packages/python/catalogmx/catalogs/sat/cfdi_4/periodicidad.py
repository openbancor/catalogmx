"""Catálogo de Periodicidad (SAT)"""

from catalogmx.catalogs.sat.cfdi_4._resolver_views import value_rows


class Periodicidad:
    _data = None

    @classmethod
    def _load_data(cls):
        if cls._data is None:
            rows = value_rows("cfdi_40_periodicidades")
            cls._data = {item["valor"]: item for item in rows}
        return cls._data

    @classmethod
    def get_data(cls):
        return cls._load_data()

    @classmethod
    def get_by_id(cls, periodicidad_id):
        """Busca una periodicidad por su ID."""
        data = cls.get_data()
        return data.get(periodicidad_id)

    @classmethod
    def is_valid(cls, periodicidad_id):
        """Verifica si un ID de periodicidad es válido."""
        return periodicidad_id in cls.get_data()
