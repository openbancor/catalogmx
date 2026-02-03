"""Catálogo de Tipos de Factor (SAT)"""

import json

from catalogmx.utils.shared_data import get_shared_data_path


class TipoFactor:
    _data = None

    @classmethod
    def _load_data(cls):
        if cls._data is None:
            path = get_shared_data_path("sat", "cfdi_4.0", "c_TipoFactor.json")
            with open(path, encoding="utf-8") as f:
                json_data = json.load(f)
                cls._data = {item["valor"]: item for item in json_data["data"]}
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
