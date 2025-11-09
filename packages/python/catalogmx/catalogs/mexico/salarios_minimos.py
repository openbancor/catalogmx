"""
Mexican Minimum Wage Catalog

This module provides access to historical minimum wage data for Mexico.
"""
import json
from datetime import date
from pathlib import Path
from typing import List, Dict, Optional


class SalariosMinimos:
    """
    Catalog of Mexican minimum wages

    Provides historical minimum wage data from 2010 to present,
    with separate values for border zone and rest of country.
    """

    _data: Optional[List[Dict]] = None

    @classmethod
    def _load_data(cls) -> None:
        """Load minimum wage data from JSON file"""
        if cls._data is None:
            # Path: catalogmx/packages/python/catalogmx/catalogs/mexico/salarios_minimos.py
            # Target: catalogmx/packages/shared-data/mexico/salarios_minimos.json
            current_file = Path(__file__)
            shared_data_path = current_file.parent.parent.parent.parent.parent / 'shared-data' / 'mexico' / 'salarios_minimos.json'

            with open(shared_data_path, 'r', encoding='utf-8') as f:
                cls._data = json.load(f)

    @classmethod
    def get_data(cls) -> List[Dict]:
        """
        Get all minimum wage data

        :return: List of all minimum wage records
        """
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_por_anio(cls, anio: int) -> Optional[Dict]:
        """
        Get minimum wage for a specific year

        :param anio: Year (e.g., 2024)
        :return: Minimum wage record or None if not found
        """
        cls._load_data()

        for record in cls._data:
            if record['año'] == anio:
                return record.copy()

        return None

    @classmethod
    def get_actual(cls) -> Optional[Dict]:
        """
        Get current minimum wage (latest year in data)

        :return: Latest minimum wage record
        """
        cls._load_data()

        if not cls._data:
            return None

        # Data is sorted by year descending, so first element is most recent
        return cls._data[0].copy()

    @classmethod
    def calcular_mensual(cls, diario: float, dias: int = 30) -> float:
        """
        Calculate monthly wage from daily wage

        :param diario: Daily wage amount
        :param dias: Number of days (default 30)
        :return: Monthly wage
        """
        return diario * dias

    @classmethod
    def calcular_anual(cls, diario: float, dias: int = 365) -> float:
        """
        Calculate annual wage from daily wage

        :param diario: Daily wage amount
        :param dias: Number of days (default 365)
        :return: Annual wage
        """
        return diario * dias

    @classmethod
    def get_por_zona(cls, anio: int, zona_frontera: bool = False) -> Optional[float]:
        """
        Get minimum wage for specific zone and year

        :param anio: Year
        :param zona_frontera: True for border zone, False for rest of country
        :return: Daily wage amount or None if not found
        """
        record = cls.get_por_anio(anio)
        if not record:
            return None

        if zona_frontera:
            return record.get('zona_frontera_norte')
        else:
            return record.get('resto_pais')

    @classmethod
    def get_incremento(cls, anio: int) -> Optional[float]:
        """
        Get percentage increment for a specific year

        :param anio: Year
        :return: Percentage increment or None if not found
        """
        record = cls.get_por_anio(anio)
        if not record:
            return None

        return record.get('incremento_porcentual')


# Convenience functions
def get_salario_actual() -> Optional[Dict]:
    """Get current minimum wage"""
    return SalariosMinimos.get_actual()


def get_salario_por_anio(anio: int) -> Optional[Dict]:
    """Get minimum wage for a specific year"""
    return SalariosMinimos.get_por_anio(anio)


def calcular_mensual(diario: float, dias: int = 30) -> float:
    """Calculate monthly wage from daily wage"""
    return SalariosMinimos.calcular_mensual(diario, dias)


# Export commonly used functions and classes
__all__ = [
    'SalariosMinimos',
    'get_salario_actual',
    'get_salario_por_anio',
    'calcular_mensual',
]
