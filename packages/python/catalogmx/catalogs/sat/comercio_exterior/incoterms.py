"""
Catálogo c_INCOTERM - Términos Internacionales de Comercio (INCOTERMS 2020)

Los INCOTERMS definen las responsabilidades entre comprador y vendedor
en operaciones de comercio internacional.

Fuente: ICC - International Chamber of Commerce / SAT México
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

class IncotermsValidator:
    """Validador y catálogo de INCOTERMS 2020 para Comercio Exterior"""

    _data: Optional[List[Dict]] = None
    _incoterm_by_code: Optional[Dict[str, Dict]] = None

    @classmethod
    def _load_data(cls):
        """Carga los datos del catálogo desde el archivo JSON compartido"""
        if cls._data is None:
            current_file = Path(__file__)
            # Navegar a shared-data desde packages/python/catalogmx/catalogs/sat/comercio_exterior
            shared_data_path = (current_file.parent.parent.parent.parent.parent.parent
                              / 'shared-data' / 'sat' / 'comercio_exterior' / 'incoterms.json')

            with open(shared_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['incoterms']

            # Crear índice por código
            cls._incoterm_by_code = {item['code']: item for item in cls._data}

    @classmethod
    def get_incoterm(cls, code: str) -> Optional[Dict]:
        """
        Obtiene un INCOTERM por su código

        Args:
            code: Código INCOTERM (EXW, FCA, FOB, CIF, etc.)

        Returns:
            Dict con información del INCOTERM o None si no existe

        Example:
            >>> incoterm = IncotermsValidator.get_incoterm('CIF')
            >>> print(incoterm['name'])
            Cost, Insurance and Freight
        """
        cls._load_data()
        return cls._incoterm_by_code.get(code.upper())

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """
        Verifica si un código INCOTERM es válido

        Args:
            code: Código INCOTERM a validar

        Returns:
            True si el código es válido

        Example:
            >>> IncotermsValidator.is_valid('FOB')
            True
            >>> IncotermsValidator.is_valid('XXX')
            False
        """
        return cls.get_incoterm(code) is not None

    @classmethod
    def is_valid_for_transport(cls, code: str, transport_type: str) -> bool:
        """
        Verifica si un INCOTERM es válido para un tipo de transporte

        Args:
            code: Código INCOTERM
            transport_type: Tipo de transporte ('sea', 'land', 'air', 'multimodal', 'any')

        Returns:
            True si el INCOTERM es válido para ese transporte

        Example:
            >>> IncotermsValidator.is_valid_for_transport('CIF', 'sea')
            True
            >>> IncotermsValidator.is_valid_for_transport('CIF', 'land')
            False
            >>> IncotermsValidator.is_valid_for_transport('FCA', 'land')
            True
        """
        incoterm = cls.get_incoterm(code)
        if not incoterm:
            return False

        suitable_for = incoterm.get('suitable_for', [])

        if transport_type == 'any' or incoterm['transport_mode'] == 'any':
            return True

        return transport_type in suitable_for

    @classmethod
    def get_multimodal_incoterms(cls) -> List[str]:
        """
        Retorna lista de INCOTERMS válidos para cualquier modo de transporte

        Returns:
            Lista de códigos INCOTERM multimodales

        Example:
            >>> multimodal = IncotermsValidator.get_multimodal_incoterms()
            >>> print(multimodal)
            ['EXW', 'FCA', 'CPT', 'CIP', 'DAP', 'DPU', 'DDP']
        """
        cls._load_data()
        return [
            item['code']
            for item in cls._data
            if item['transport_mode'] == 'any'
        ]

    @classmethod
    def get_maritime_incoterms(cls) -> List[str]:
        """
        Retorna lista de INCOTERMS válidos solo para transporte marítimo

        Returns:
            Lista de códigos INCOTERM marítimos

        Example:
            >>> maritime = IncotermsValidator.get_maritime_incoterms()
            >>> print(maritime)
            ['FAS', 'FOB', 'CFR', 'CIF']
        """
        cls._load_data()
        return [
            item['code']
            for item in cls._data
            if item['transport_mode'] == 'maritime'
        ]

    @classmethod
    def seller_pays_freight(cls, code: str) -> bool:
        """
        Verifica si el vendedor paga el flete en este INCOTERM

        Args:
            code: Código INCOTERM

        Returns:
            True si el vendedor paga flete

        Example:
            >>> IncotermsValidator.seller_pays_freight('CIF')
            True
            >>> IncotermsValidator.seller_pays_freight('EXW')
            False
        """
        incoterm = cls.get_incoterm(code)
        return incoterm.get('seller_pays_freight', False) if incoterm else False

    @classmethod
    def seller_pays_insurance(cls, code: str) -> bool:
        """
        Verifica si el vendedor paga el seguro en este INCOTERM

        Args:
            code: Código INCOTERM

        Returns:
            True si el vendedor paga seguro

        Example:
            >>> IncotermsValidator.seller_pays_insurance('CIF')
            True
            >>> IncotermsValidator.seller_pays_insurance('CFR')
            False
        """
        incoterm = cls.get_incoterm(code)
        return incoterm.get('seller_pays_insurance', False) if incoterm else False

    @classmethod
    def get_all(cls) -> List[Dict]:
        """
        Retorna todos los INCOTERMS disponibles

        Returns:
            Lista completa de INCOTERMS

        Example:
            >>> all_incoterms = IncotermsValidator.get_all()
            >>> print(len(all_incoterms))
            11
        """
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def search(cls, query: str) -> List[Dict]:
        """
        Busca INCOTERMS por nombre o descripción

        Args:
            query: Texto a buscar

        Returns:
            Lista de INCOTERMS que coinciden

        Example:
            >>> results = IncotermsValidator.search('insurance')
            >>> print([r['code'] for r in results])
            ['CIP', 'CIF']
        """
        cls._load_data()
        query_lower = query.lower()

        return [
            item for item in cls._data
            if (query_lower in item['name'].lower() or
                query_lower in item['name_es'].lower() or
                query_lower in item['description'].lower())
        ]
