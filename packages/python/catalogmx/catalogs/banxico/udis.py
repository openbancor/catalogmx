"""
UDI (Unidades de Inversión) Catalog

This module provides access to UDI values from Banco de México.
UDIs are inflation-indexed investment units used in Mexico.
"""
import json
from datetime import date, datetime
from pathlib import Path
from typing import List, Dict, Optional


class UDICatalog:
    """
    Catalog of UDI (Unidades de Inversión) values

    UDIs are inflation-indexed investment units maintained by Banco de México.
    They are commonly used for mortgage loans and other long-term financial obligations.
    """

    _data: Optional[List[Dict]] = None

    @classmethod
    def _load_data(cls) -> None:
        """Load UDI data from JSON file"""
        if cls._data is None:
            # Path: catalogmx/packages/python/catalogmx/catalogs/banxico/udis.py
            # Target: catalogmx/packages/shared-data/banxico/udis.json
            current_file = Path(__file__)
            shared_data_path = current_file.parent.parent.parent.parent.parent / 'shared-data' / 'banxico' / 'udis.json'

            with open(shared_data_path, 'r', encoding='utf-8') as f:
                cls._data = json.load(f)

    @classmethod
    def get_data(cls) -> List[Dict]:
        """
        Get all UDI data

        :return: List of all UDI records
        """
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_por_fecha(cls, fecha: str) -> Optional[Dict]:
        """
        Get UDI value for a specific date

        :param fecha: Date string in YYYY-MM-DD format
        :return: UDI record or None if not found
        """
        cls._load_data()

        for record in cls._data:
            if record.get('fecha') == fecha:
                return record.copy()

        return None

    @classmethod
    def get_por_mes(cls, anio: int, mes: int) -> Optional[Dict]:
        """
        Get monthly average UDI value

        :param anio: Year (e.g., 2024)
        :param mes: Month (1-12)
        :return: UDI record with monthly average or None if not found
        """
        cls._load_data()

        # Format as YYYY-MM
        fecha_str = f"{anio}-{mes:02d}"

        for record in cls._data:
            if record.get('tipo') == 'promedio_mensual' and record.get('fecha', '').startswith(fecha_str):
                return record.copy()

        return None

    @classmethod
    def get_por_anio(cls, anio: int) -> Optional[Dict]:
        """
        Get annual average UDI value

        :param anio: Year (e.g., 2024)
        :return: UDI record with annual average or None if not found
        """
        cls._load_data()

        for record in cls._data:
            if record.get('tipo') == 'promedio_anual' and record.get('fecha', '').startswith(str(anio)):
                return record.copy()

        return None

    @classmethod
    def get_actual(cls) -> Optional[Dict]:
        """
        Get most recent UDI value

        :return: Latest UDI record
        """
        cls._load_data()

        if not cls._data:
            return None

        # Find the most recent value (daily, monthly average, or annual average)
        # Data should be sorted by date descending, so first element is most recent
        return cls._data[0].copy()

    @classmethod
    def pesos_a_udis(cls, pesos: float, fecha: str) -> Optional[float]:
        """
        Convert Mexican pesos to UDIs

        :param pesos: Amount in Mexican pesos
        :param fecha: Date string in YYYY-MM-DD format
        :return: Amount in UDIs or None if UDI value not found
        """
        record = cls.get_por_fecha(fecha)
        if not record:
            return None

        valor_udi = record.get('valor')
        if not valor_udi:
            return None

        return pesos / valor_udi

    @classmethod
    def udis_a_pesos(cls, udis: float, fecha: str) -> Optional[float]:
        """
        Convert UDIs to Mexican pesos

        :param udis: Amount in UDIs
        :param fecha: Date string in YYYY-MM-DD format
        :return: Amount in Mexican pesos or None if UDI value not found
        """
        record = cls.get_por_fecha(fecha)
        if not record:
            return None

        valor_udi = record.get('valor')
        if not valor_udi:
            return None

        return udis * valor_udi

    @classmethod
    def calcular_variacion(cls, fecha_inicio: str, fecha_fin: str) -> Optional[float]:
        """
        Calculate percentage variation between two dates

        :param fecha_inicio: Start date (YYYY-MM-DD)
        :param fecha_fin: End date (YYYY-MM-DD)
        :return: Percentage variation or None if values not found
        """
        record_inicio = cls.get_por_fecha(fecha_inicio)
        record_fin = cls.get_por_fecha(fecha_fin)

        if not record_inicio or not record_fin:
            return None

        valor_inicio = record_inicio.get('valor')
        valor_fin = record_fin.get('valor')

        if not valor_inicio or not valor_fin:
            return None

        return ((valor_fin - valor_inicio) / valor_inicio) * 100


# Convenience functions
def get_udi_actual() -> Optional[Dict]:
    """Get most recent UDI value"""
    return UDICatalog.get_actual()


def get_udi_por_fecha(fecha: str) -> Optional[Dict]:
    """Get UDI value for a specific date"""
    return UDICatalog.get_por_fecha(fecha)


def pesos_a_udis(pesos: float, fecha: str) -> Optional[float]:
    """Convert pesos to UDIs"""
    return UDICatalog.pesos_a_udis(pesos, fecha)


def udis_a_pesos(udis: float, fecha: str) -> Optional[float]:
    """Convert UDIs to pesos"""
    return UDICatalog.udis_a_pesos(udis, fecha)


# Export commonly used functions and classes
__all__ = [
    'UDICatalog',
    'get_udi_actual',
    'get_udi_por_fecha',
    'pesos_a_udis',
    'udis_a_pesos',
]
