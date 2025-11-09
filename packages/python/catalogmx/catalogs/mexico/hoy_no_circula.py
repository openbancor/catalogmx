"""
Hoy No Circula CDMX Catalog

This module provides access to the Hoy No Circula traffic restriction program
for Mexico City (CDMX) and Estado de México.
"""
import json
from pathlib import Path
from typing import List, Dict, Optional


class HoyNoCirculaCatalog:
    """
    Catalog for Hoy No Circula traffic restriction program

    The Hoy No Circula program restricts vehicle circulation in Mexico City
    and Estado de México based on the last digit of the license plate number
    and the vehicle's verification hologram.
    """

    _data: Optional[Dict] = None

    @classmethod
    def _load_data(cls) -> None:
        """Load Hoy No Circula data from JSON file"""
        if cls._data is None:
            # Path: catalogmx/packages/python/catalogmx/catalogs/mexico/hoy_no_circula.py
            # Target: catalogmx/packages/shared-data/mexico/hoy_no_circula_cdmx.json
            current_file = Path(__file__)
            shared_data_path = current_file.parent.parent.parent.parent.parent / 'shared-data' / 'mexico' / 'hoy_no_circula_cdmx.json'

            with open(shared_data_path, 'r', encoding='utf-8') as f:
                cls._data = json.load(f)

    @classmethod
    def get_data(cls) -> Dict:
        """
        Get all Hoy No Circula data

        :return: Complete Hoy No Circula data dictionary
        """
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_restricciones(cls) -> List[Dict]:
        """
        Get all restrictions by day of week

        :return: List of restriction dictionaries
        """
        cls._load_data()
        return cls._data.get('restricciones_por_dia', []).copy()

    @classmethod
    def get_restriccion_por_dia(cls, dia: str) -> Optional[Dict]:
        """
        Get restriction for a specific day of week

        :param dia: Day of week (e.g., 'lunes', 'martes')
        :return: Restriction dictionary or None if not found
        """
        cls._load_data()
        restricciones = cls._data.get('restricciones_por_dia', [])

        for restriccion in restricciones:
            if restriccion.get('dia', '').lower() == dia.lower():
                return restriccion.copy()

        return None

    @classmethod
    def get_exenciones(cls) -> List[Dict]:
        """
        Get all exemptions by hologram type

        :return: List of exemption dictionaries
        """
        cls._load_data()
        return cls._data.get('exenciones_por_holograma', []).copy()

    @classmethod
    def get_exencion_por_holograma(cls, holograma: str) -> Optional[Dict]:
        """
        Get exemption information for a specific hologram

        :param holograma: Hologram type (e.g., '00', '0', '1', '2')
        :return: Exemption dictionary or None if not found
        """
        cls._load_data()
        exenciones = cls._data.get('exenciones_por_holograma', [])

        for exencion in exenciones:
            if exencion.get('holograma') == holograma:
                return exencion.copy()

        return None

    @classmethod
    def puede_circular(cls, terminacion: str, dia: str, holograma: str = '2') -> bool:
        """
        Check if a vehicle can circulate on a given day

        :param terminacion: Last digit of license plate (0-9)
        :param dia: Day of week ('lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado')
        :param holograma: Verification hologram ('00', '0', '1', '2')
        :return: True if can circulate, False otherwise
        """
        cls._load_data()

        # Check exemption by hologram first
        exencion = cls.get_exencion_por_holograma(holograma)
        if exencion:
            # Hologram 00 and 0 can circulate all days (except Saturdays for 0)
            if holograma == '00':
                return True
            elif holograma == '0':
                return dia.lower() != 'sábado'

        # Check restriction for the day
        restriccion = cls.get_restriccion_por_dia(dia)
        if not restriccion:
            # No restriction for this day (e.g., Sunday)
            return True

        # Check if the termination is restricted
        terminaciones_restringidas = restriccion.get('terminacion_placa', [])
        return str(terminacion) not in [str(t) for t in terminaciones_restringidas]

    @classmethod
    def get_dia_restriccion(cls, terminacion: str) -> Optional[str]:
        """
        Get the day of week when a vehicle is restricted (for hologram 2)

        :param terminacion: Last digit of license plate (0-9)
        :return: Day of week when restricted or None if not restricted
        """
        cls._load_data()

        restricciones = cls._data.get('restricciones_por_dia', [])
        for restriccion in restricciones:
            terminaciones = restriccion.get('terminacion_placa', [])
            if str(terminacion) in [str(t) for t in terminaciones]:
                return restriccion.get('dia')

        return None

    @classmethod
    def get_engomado(cls, terminacion: str) -> Optional[str]:
        """
        Get the engomado (sticker color) for a license plate termination

        :param terminacion: Last digit of license plate (0-9)
        :return: Engomado color or None if not found
        """
        cls._load_data()

        restricciones = cls._data.get('restricciones_por_dia', [])
        for restriccion in restricciones:
            terminaciones = restriccion.get('terminacion_placa', [])
            if str(terminacion) in [str(t) for t in terminaciones]:
                engomados = restriccion.get('engomado', [])
                return engomados[0] if engomados else None

        return None

    @classmethod
    def get_contingencias(cls) -> Dict:
        """
        Get contingency program information

        :return: Dictionary with environmental contingency rules
        """
        cls._load_data()
        return cls._data.get('contingencias_ambientales', {}).copy()

    @classmethod
    def get_sabatinos(cls) -> Dict:
        """
        Get Saturday restriction information

        :return: Dictionary with Saturday restriction rules
        """
        cls._load_data()
        return cls._data.get('sabatinos', {}).copy()


# Convenience functions
def puede_circular(terminacion: str, dia: str, holograma: str = '2') -> bool:
    """Check if a vehicle can circulate on a given day"""
    return HoyNoCirculaCatalog.puede_circular(terminacion, dia, holograma)


def get_dia_restriccion(terminacion: str) -> Optional[str]:
    """Get the day when a vehicle is restricted"""
    return HoyNoCirculaCatalog.get_dia_restriccion(terminacion)


def get_engomado(terminacion: str) -> Optional[str]:
    """Get the engomado color for a license plate termination"""
    return HoyNoCirculaCatalog.get_engomado(terminacion)


# Export commonly used functions and classes
__all__ = [
    'HoyNoCirculaCatalog',
    'puede_circular',
    'get_dia_restriccion',
    'get_engomado',
]
