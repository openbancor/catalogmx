"""Catálogo c_RegistroIdentTribReceptor - Tipos de Registro de Identificación Tributaria"""

import json
import re
from pathlib import Path


class RegistroIdentTribCatalog:
    """Catálogo de tipos de registro tributario del receptor extranjero"""

    _data: list[dict] | None = None
    _tipo_by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga los datos del catálogo desde el archivo JSON compartido"""
        if cls._data is None:
            current_file = Path(__file__)
            shared_data_path = (current_file.parent.parent.parent.parent.parent.parent
                              / 'shared-data' / 'sat' / 'comercio_exterior' / 'registro_ident_trib.json')

            with open(shared_data_path, encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['tipos_registro']

            cls._tipo_by_code = {item['code']: item for item in cls._data}

    @classmethod
    def get_tipo(cls, code: str) -> dict | None:
        """Obtiene un tipo de registro por su código"""
        cls._load_data()
        return cls._tipo_by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de tipo es válido"""
        return cls.get_tipo(code) is not None

    @classmethod
    def validate_tax_id(cls, tipo_registro: str, num_reg_id_trib: str) -> dict:
        """
        Valida un número de identificación tributaria según su tipo

        Args:
            tipo_registro: Código del tipo de registro
            num_reg_id_trib: Número de identificación tributaria

        Returns:
            dict con 'valid' (bool) y 'errors' (list)
        """
        tipo = cls.get_tipo(tipo_registro)
        if not tipo:
            return {'valid': False, 'errors': ['Tipo de registro no válido']}

        errors = []

        # Validar formato si está definido
        format_pattern = tipo.get('format_pattern')
        if format_pattern:
            if not re.match(format_pattern, num_reg_id_trib):
                format_desc = tipo.get('format_description', 'formato no válido')
                errors.append(f'Formato incorrecto. Esperado: {format_desc}')

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    @classmethod
    def get_all(cls) -> list[dict]:
        """Retorna todos los tipos de registro tributario"""
        cls._load_data()
        return cls._data.copy()
