"""Catálogo c_MotivoTraslado - Motivos de Traslado para CFDI tipo T"""

import json
from pathlib import Path

class MotivoTrasladoCatalog:
    """Catálogo de motivos de traslado para CFDI con comercio exterior"""

    _data: list[dict] | None = None
    _motivo_by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga los datos del catálogo desde el archivo JSON compartido"""
        if cls._data is None:
            current_file = Path(__file__)
            shared_data_path = (current_file.parent.parent.parent.parent.parent.parent
                              / 'shared-data' / 'sat' / 'comercio_exterior' / 'motivos_traslado.json')

            with open(shared_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['motivos']

            cls._motivo_by_code = {item['code']: item for item in cls._data}

    @classmethod
    def get_motivo(cls, code: str) -> dict | None:
        """Obtiene un motivo de traslado por su código"""
        cls._load_data()
        return cls._motivo_by_code.get(code)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de motivo es válido"""
        return cls.get_motivo(code) is not None

    @classmethod
    def requires_propietario(cls, code: str) -> bool:
        """Verifica si el motivo requiere nodo <Propietario>"""
        motivo = cls.get_motivo(code)
        return motivo.get('requires_propietario', False) if motivo else False

    @classmethod
    def get_all(cls) -> list[dict]:
        """Retorna todos los motivos de traslado"""
        cls._load_data()
        return cls._data.copy()
