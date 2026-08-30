"""Catálogo de Meses (SAT)"""

from catalogmx.catalogs.sat.cfdi_4._resolver_views import value_rows


class Meses:
    _data = None

    @classmethod
    def _load_data(cls):
        if cls._data is None:
            rows = value_rows("cfdi_40_meses")
            cls._data = {item["valor"]: item for item in rows}
        return cls._data

    @classmethod
    def get_data(cls):
        return cls._load_data()

    @classmethod
    def get_by_id(cls, mes_id):
        """Busca un mes por su ID (e.g., '01', '02')."""
        data = cls.get_data()
        return data.get(mes_id)

    @classmethod
    def is_valid(cls, mes_id):
        """Verifica si un ID de mes es válido."""
        return mes_id in cls.get_data()
