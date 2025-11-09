"""
Mexican License Plates Formats Catalog

This module provides validation patterns and formats for Mexican vehicle license plates
according to NOM-001-SCT-2-2016.
"""
import json
import re
from pathlib import Path
from typing import List, Dict, Optional


class PlacasFormatosCatalog:
    """
    Catalog of Mexican license plate formats

    Provides validation and detection for 35 official vehicle plate formats
    defined by NOM-001-SCT-2-2016.
    """

    _data: Optional[List[Dict]] = None

    @classmethod
    def _load_data(cls) -> None:
        """Load license plate formats from JSON file"""
        if cls._data is None:
            # Path: catalogmx/packages/python/catalogmx/catalogs/mexico/placas_formatos.py
            # Target: catalogmx/packages/shared-data/mexico/placas_formatos.json
            current_file = Path(__file__)
            shared_data_path = current_file.parent.parent.parent.parent.parent / 'shared-data' / 'mexico' / 'placas_formatos.json'

            with open(shared_data_path, 'r', encoding='utf-8') as f:
                cls._data = json.load(f)

    @classmethod
    def get_data(cls) -> List[Dict]:
        """
        Get all license plate formats

        :return: List of all plate format dictionaries
        """
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def validate_placa(cls, placa: str) -> bool:
        """
        Validate a license plate against all known active formats

        :param placa: License plate string to validate
        :return: True if valid, False otherwise
        """
        cls._load_data()
        normalized_placa = placa.upper().strip()

        for formato in cls._data:
            if formato.get('activo', True):
                pattern = formato['pattern']
                if re.match(pattern, normalized_placa):
                    return True

        return False

    @classmethod
    def get_formatos_por_estado(cls, estado: str) -> List[Dict]:
        """
        Get all formats for a specific state

        :param estado: State name (e.g., 'Jalisco', 'Nacional')
        :return: List of formats for the state
        """
        cls._load_data()
        estado_lower = estado.lower()

        return [
            f for f in cls._data
            if estado_lower in f['estado'].lower() or estado_lower == 'nacional'
        ]

    @classmethod
    def get_formatos_por_tipo(cls, tipo: str) -> List[Dict]:
        """
        Get all active formats by type

        :param tipo: Plate type (e.g., 'particular', 'diplomatico', 'militar_ejercito')
        :return: List of formats of the specified type
        """
        cls._load_data()

        return [
            f for f in cls._data
            if f.get('tipo') == tipo and f.get('activo', True)
        ]

    @classmethod
    def detect_formato(cls, placa: str) -> Optional[Dict]:
        """
        Detect the format of a given license plate

        :param placa: License plate string
        :return: Format dictionary if detected, None otherwise
        """
        cls._load_data()
        normalized_placa = placa.upper().strip()

        for formato in cls._data:
            pattern = formato['pattern']
            if re.match(pattern, normalized_placa):
                return formato.copy()

        return None

    @classmethod
    def get_formatos_activos(cls) -> List[Dict]:
        """
        Get all active formats

        :return: List of active plate formats
        """
        cls._load_data()

        return [f for f in cls._data if f.get('activo', True)]

    @classmethod
    def is_diplomatica(cls, placa: str) -> bool:
        """
        Check if a plate is diplomatic

        :param placa: License plate string
        :return: True if diplomatic, False otherwise
        """
        formato = cls.detect_formato(placa)
        return formato.get('tipo') == 'diplomatico' if formato else False

    @classmethod
    def is_federal(cls, placa: str) -> bool:
        """
        Check if a plate is federal (government, military, or federal service)

        :param placa: License plate string
        :return: True if federal, False otherwise
        """
        formato = cls.detect_formato(placa)
        if not formato:
            return False

        tipo = formato.get('tipo')
        federal_types = [
            'gobierno_federal',
            'servicio_publico_federal',
            'carga_federal',
            'policia_federal',
            'remolque_federal'
        ]

        return tipo in federal_types


# Convenience functions for direct access
def validate_placa(placa: str) -> bool:
    """Validate a license plate"""
    return PlacasFormatosCatalog.validate_placa(placa)


def detect_formato(placa: str) -> Optional[Dict]:
    """Detect the format of a license plate"""
    return PlacasFormatosCatalog.detect_formato(placa)


def get_formatos_activos() -> List[Dict]:
    """Get all active plate formats"""
    return PlacasFormatosCatalog.get_formatos_activos()


# Export commonly used functions and classes
__all__ = [
    'PlacasFormatosCatalog',
    'validate_placa',
    'detect_formato',
    'get_formatos_activos',
]
