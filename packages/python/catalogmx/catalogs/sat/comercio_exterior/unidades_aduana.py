"""Catálogo c_UnidadAduana - Unidades de Medida Aduanera"""

import json
from pathlib import Path
from typing import Dict, List, Optional

class UnidadAduanaCatalog:
    """Catálogo de unidades de medida reconocidas por aduanas"""

    _data: Optional[List[Dict]] = None
    _unidad_by_code: Optional[Dict[str, Dict]] = None

    @classmethod
    def _load_data(cls):
        if cls._data is None:
            current_file = Path(__file__)
            shared_data_path = (current_file.parent.parent.parent.parent.parent.parent
                              / 'shared-data' / 'sat' / 'comercio_exterior' / 'unidades_aduana.json')

            with open(shared_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['unidades']

            cls._unidad_by_code = {item['code']: item for item in cls._data}

    @classmethod
    def get_unidad(cls, code: str) -> Optional[Dict]:
        """Obtiene una unidad de medida por su código"""
        cls._load_data()
        return cls._unidad_by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de unidad es válido"""
        return cls.get_unidad(code) is not None

    @classmethod
    def get_by_type(cls, unit_type: str) -> List[Dict]:
        """Obtiene unidades por tipo (weight, volume, length, area, unit, container)"""
        cls._load_data()
        return [item for item in cls._data if item.get('type') == unit_type]

    @classmethod
    def get_all(cls) -> List[Dict]:
        """Retorna todas las unidades de medida aduanera"""
        cls._load_data()
        return cls._data.copy()
