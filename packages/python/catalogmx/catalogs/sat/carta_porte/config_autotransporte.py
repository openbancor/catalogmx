"""Catálogo c_ConfigAutotransporte - Configuraciones Vehiculares"""
import json
from pathlib import Path
from typing import Dict, List, Optional

class ConfigAutotransporteCatalog:
    _data: Optional[List[Dict]] = None
    _by_code: Optional[Dict[str, Dict]] = None

    @classmethod
    def _load_data(cls):
        if cls._data is None:
            path = Path(__file__).parent.parent.parent.parent.parent.parent / 'shared-data' / 'sat' / 'carta_porte_3' / 'config_autotransporte.json'
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['configuraciones']
            cls._by_code = {item['code']: item for item in cls._data}

    @classmethod
    def get_config(cls, code: str) -> Optional[Dict]:
        """Obtiene configuración por código"""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de configuración es válido"""
        return cls.get_config(code) is not None

    @classmethod
    def get_all(cls) -> List[Dict]:
        """Obtiene todas las configuraciones"""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_by_type(cls, tipo: str) -> List[Dict]:
        """Obtiene configuraciones por tipo (Unitario, Articulado)"""
        cls._load_data()
        return [c for c in cls._data if c['type'] == tipo]

    @classmethod
    def get_axes_count(cls, code: str) -> Optional[int]:
        """Obtiene el número de ejes de una configuración"""
        config = cls.get_config(code)
        return config.get('axes') if config else None
