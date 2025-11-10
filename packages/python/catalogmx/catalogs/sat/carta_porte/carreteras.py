"""Catálogo c_Carreteras - Carreteras Federales"""
import json
from pathlib import Path

from catalogmx.utils.text import normalize_text


class CarreterasCatalog:
    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        if cls._data is None:
            path = Path(__file__).parent.parent.parent.parent.parent.parent / 'shared-data' / 'sat' / 'carta_porte_3' / 'carreteras.json'
            with open(path, encoding='utf-8') as f:
                cls._data = json.load(f)
            cls._by_code = {item['code']: item for item in cls._data}

    @classmethod
    def get_carretera(cls, code: str) -> dict | None:
        """Obtiene carretera por código"""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de carretera es válido"""
        return cls.get_carretera(code) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todas las carreteras"""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_by_type(cls, tipo: str) -> list[dict]:
        """Obtiene carreteras por tipo (Cuota, Libre)"""
        cls._load_data()
        return [c for c in cls._data if c['type'] == tipo]

    @classmethod
    def search_by_name(cls, name: str) -> list[dict]:
        """Busca carreteras por nombre (insensible a acentos)"""
        cls._load_data()
        name_normalized = normalize_text(name)
        return [
            c for c in cls._data
            if name_normalized in normalize_text(c.get('nombre', c.get('name', '')))
        ]
