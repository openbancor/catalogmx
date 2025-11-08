"""Catálogo c_Estado - Estados de USA y Provincias de Canadá"""

import json
from pathlib import Path

class EstadoCatalog:
    """Catálogo de estados/provincias de USA y Canadá para comercio exterior"""

    _estados_usa: list[dict] | None = None
    _provincias_canada: list[dict] | None = None
    _estado_by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga los datos del catálogo desde el archivo JSON compartido"""
        if cls._estados_usa is None:
            current_file = Path(__file__)
            shared_data_path = (current_file.parent.parent.parent.parent.parent.parent
                              / 'shared-data' / 'sat' / 'comercio_exterior' / 'estados_usa_canada.json')

            with open(shared_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._estados_usa = data['estados_usa']
                cls._provincias_canada = data['provincias_canada']

            # Crear índice unificado por código
            cls._estado_by_code = {}
            for estado in cls._estados_usa:
                cls._estado_by_code[estado['code']] = estado
            for provincia in cls._provincias_canada:
                cls._estado_by_code[provincia['code']] = provincia

    @classmethod
    def get_estado(cls, code: str, country: str | None = None) -> dict | None:
        """
        Obtiene un estado/provincia por su código

        Args:
            code: Código del estado (TX, CA, ON, etc.)
            country: Opcional - 'USA' o 'CAN' para filtrar

        Returns:
            dict con información del estado/provincia
        """
        cls._load_data()
        code_upper = code.upper()
        estado = cls._estado_by_code.get(code_upper)

        if estado and country:
            if estado['country'] != country.upper():
                return None

        return estado

    @classmethod
    def get_estado_usa(cls, code: str) -> dict | None:
        """Obtiene un estado de USA por su código"""
        return cls.get_estado(code, 'USA')

    @classmethod
    def get_provincia_canada(cls, code: str) -> dict | None:
        """Obtiene una provincia de Canadá por su código"""
        return cls.get_estado(code, 'CAN')

    @classmethod
    def is_valid(cls, code: str, country: str | None = None) -> bool:
        """Verifica si un código de estado/provincia es válido"""
        return cls.get_estado(code, country) is not None

    @classmethod
    def get_all_usa(cls) -> list[dict]:
        """Retorna todos los estados de USA"""
        cls._load_data()
        return cls._estados_usa.copy()

    @classmethod
    def get_all_canada(cls) -> list[dict]:
        """Retorna todas las provincias de Canadá"""
        cls._load_data()
        return cls._provincias_canada.copy()

    @classmethod
    def get_all(cls) -> list[dict]:
        """Retorna todos los estados y provincias"""
        cls._load_data()
        return cls._estados_usa + cls._provincias_canada

    @classmethod
    def validate_foreign_address(cls, address_data: dict) -> dict:
        """
        Valida dirección extranjera para comercio exterior

        Args:
            address_data: dict con 'pais', 'estado', 'num_reg_id_trib'

        Returns:
            dict con 'valid' (bool) y 'errors' (list)
        """
        errors = []
        pais = address_data.get('pais', '').upper()
        estado = address_data.get('estado', '').upper()

        # Validar que USA/CAN tengan estado
        if pais in ['USA', 'CAN']:
            if not estado:
                errors.append(f'Campo Estado es obligatorio para país {pais}')
            elif not cls.is_valid(estado, pais):
                errors.append(f'Estado {estado} no válido para país {pais}')

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
