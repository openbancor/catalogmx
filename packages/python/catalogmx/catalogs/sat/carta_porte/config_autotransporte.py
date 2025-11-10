"""Catálogo c_ConfigAutotransporte - Configuraciones Vehiculares"""
import json
from pathlib import Path


class ConfigAutotransporteCatalog:
    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        if cls._data is None:
            path = Path(__file__).parent.parent.parent.parent.parent.parent / 'shared-data' / 'sat' / 'carta_porte_3' / 'config_autotransporte.json'
            with open(path, encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['configuraciones']
            cls._by_code = {item['code']: item for item in cls._data}

    @classmethod
    def get_config(cls, code: str) -> dict | None:
        """Obtiene configuración por código"""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de configuración es válido"""
        return cls.get_config(code) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todas las configuraciones"""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_by_type(cls, tipo: str) -> list[dict]:
        """Obtiene configuraciones por tipo (Unitario, Articulado)"""
        cls._load_data()
        return [c for c in cls._data if c['type'] == tipo]

    @classmethod
    def get_axes_count(cls, code: str) -> int | None:
        """Obtiene el número de ejes de una configuración"""
        config = cls.get_config(code)
        return config.get('axes') if config else None
