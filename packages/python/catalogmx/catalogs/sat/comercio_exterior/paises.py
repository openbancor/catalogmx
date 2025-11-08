"""Catálogo c_Pais - Códigos de Países ISO 3166-1"""

import json
from pathlib import Path
from typing import Dict, List, Optional

class PaisCatalog:
    """Catálogo de países para identificar origen/destino en comercio exterior"""

    _data: Optional[List[Dict]] = None
    _pais_by_code: Optional[Dict[str, Dict]] = None
    _pais_by_iso2: Optional[Dict[str, Dict]] = None

    @classmethod
    def _load_data(cls):
        if cls._data is None:
            current_file = Path(__file__)
            shared_data_path = (current_file.parent.parent.parent.parent.parent.parent
                              / 'shared-data' / 'sat' / 'comercio_exterior' / 'paises.json')

            with open(shared_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['paises']

            cls._pais_by_code = {item['codigo']: item for item in cls._data}
            cls._pais_by_iso2 = {item['iso2']: item for item in cls._data}

    @classmethod
    def get_pais(cls, code: str) -> Optional[Dict]:
        """Obtiene un país por su código ISO 3166-1 Alpha-3"""
        cls._load_data()
        code_upper = code.upper()

        # Intentar primero con Alpha-3
        pais = cls._pais_by_code.get(code_upper)
        if pais:
            return pais

        # Intentar con Alpha-2
        return cls._pais_by_iso2.get(code_upper)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de país es válido"""
        return cls.get_pais(code) is not None

    @classmethod
    def requires_subdivision(cls, code: str) -> bool:
        """
        Verifica si el país requiere subdivisión (estado/provincia)

        Args:
            code: Código del país (USA, CAN, etc.)

        Returns:
            True si requiere estado/provincia
        """
        pais = cls.get_pais(code)
        return pais.get('requiere_subdivision', False) if pais else False

    @classmethod
    def get_all(cls) -> List[Dict]:
        """Retorna todos los países"""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def search(cls, query: str) -> List[Dict]:
        """Busca países por código o nombre"""
        cls._load_data()
        query_lower = query.lower()

        return [
            item for item in cls._data
            if (query_lower in item['codigo'].lower() or
                query_lower in item['nombre'].lower() or
                query_lower in item.get('iso2', '').lower())
        ]
