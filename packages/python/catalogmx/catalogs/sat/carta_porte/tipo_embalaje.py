"""Catálogo c_TipoEmbalaje - Tipos de Embalaje"""
import json
from pathlib import Path


class TipoEmbalajeCatalog:
    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        if cls._data is None:
            path = Path(__file__).parent.parent.parent.parent.parent.parent / 'shared-data' / 'sat' / 'carta_porte_3' / 'tipo_embalaje.json'
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['embalajes']
            cls._by_code = {item['code']: item for item in cls._data}

    @classmethod
    def get_embalaje(cls, code: str) -> dict | None:
        """Obtiene embalaje por código"""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de embalaje es válido"""
        return cls.get_embalaje(code) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todos los embalajes"""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_by_material(cls, material: str) -> list[dict]:
        """Obtiene embalajes por material (Acero, Plástico, Madera, etc.)"""
        cls._load_data()
        return [e for e in cls._data if e['material'] == material]
