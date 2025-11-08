"""Catálogo c_TipoPermiso - Tipos de Permiso"""
import json
from pathlib import Path
from typing import Dict, List, Optional

class TipoPermisoCatalog:
    _data: Optional[List[Dict]] = None
    _by_code: Optional[Dict[str, Dict]] = None

    @classmethod
    def _load_data(cls):
        if cls._data is None:
            path = Path(__file__).parent.parent.parent.parent.parent.parent / 'shared-data' / 'sat' / 'carta_porte_3' / 'tipo_permiso.json'
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['permisos']
            cls._by_code = {item['code']: item for item in cls._data}

    @classmethod
    def get_permiso(cls, code: str) -> Optional[Dict]:
        """Obtiene permiso por código"""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de permiso es válido"""
        return cls.get_permiso(code) is not None

    @classmethod
    def get_all(cls) -> List[Dict]:
        """Obtiene todos los permisos"""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_by_type(cls, tipo: str) -> List[Dict]:
        """Obtiene permisos por tipo (Carga, Pasajeros)"""
        cls._load_data()
        return [p for p in cls._data if p['type'] == tipo]

    @classmethod
    def is_carga_permit(cls, code: str) -> bool:
        """Verifica si es un permiso de carga"""
        permiso = cls.get_permiso(code)
        return permiso.get('type') == 'Carga' if permiso else False
