"""Catálogo de Meses (SAT)"""

import json

from ....helpers import get_project_root


class Meses:
    _data = None

    @classmethod
    def _load_data(cls):
        if cls._data is None:
            root = get_project_root()
            path = root / "packages" / "shared-data" / "sat" / "cfdi_4.0" / "c_Meses.json"
            with open(path, encoding="utf-8") as f:
                json_data = json.load(f)
                cls._data = {item["valor"]: item for item in json_data["data"]}
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
