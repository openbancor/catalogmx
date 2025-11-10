"""
UMA (Unidad de Medida y Actualización) Catalog

This module provides access to UMA values, which are used as reference
units for fines, taxes, and other obligations in Mexico.
"""

import json
from pathlib import Path

from .salarios_minimos import SalariosMinimos


class UMACatalog:
    """
    Catalog of UMA (Unidad de Medida y Actualización) values

    UMA is a reference economic unit used in Mexico for calculating
    fines, taxes, social security contributions, and other obligations.
    It was introduced in 2016 to replace the minimum wage as a reference unit.
    """

    _data: list[dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Load UMA data from JSON file"""
        if cls._data is None:
            # Path: catalogmx/packages/python/catalogmx/catalogs/mexico/uma.py
            # Target: catalogmx/packages/shared-data/mexico/uma.json
            current_file = Path(__file__)
            shared_data_path = (
                current_file.parent.parent.parent.parent.parent
                / "shared-data"
                / "mexico"
                / "uma.json"
            )

            with open(shared_data_path, encoding="utf-8") as f:
                cls._data = json.load(f)

    @classmethod
    def get_data(cls) -> list[dict]:
        """
        Get all UMA data

        :return: List of all UMA records
        """
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_por_anio(cls, anio: int) -> dict | None:
        """
        Get UMA values for a specific year

        :param anio: Year (e.g., 2024)
        :return: UMA record or None if not found
        """
        cls._load_data()

        for record in cls._data:
            if record["año"] == anio:
                return record.copy()

        # Fallback to salary minimum equivalence for pre-2017 years
        salario = SalariosMinimos.get_por_anio(anio)
        if not salario:
            return None

        diario = salario.get("uma_equivalente_diario") or salario.get("resto_pais")
        if diario is None:
            return None

        mensual = salario.get("uma_equivalente_mensual")
        if mensual is None:
            mensual = round(diario * 30.4, 2)

        anual = salario.get("uma_equivalente_anual")
        if anual is None:
            anual = round(diario * 365, 2)

        return {
            "año": anio,
            "vigencia_inicio": salario.get("vigencia_inicio", f"{anio}-01-01"),
            "vigencia_fin": f"{anio}-12-31",
            "valor_diario": round(diario, 2),
            "valor_mensual": mensual,
            "valor_anual": anual,
            "moneda": salario.get("moneda", "MXN"),
            "publicacion_dof": salario.get("vigencia_inicio", f"{anio}-01-01"),
            "incremento_porcentual": None,
            "notas": "Equivalencia de UMA derivada del salario mínimo vigente antes de 2017",
        }

    @classmethod
    def get_actual(cls) -> dict | None:
        """
        Get current UMA values (latest year in data)

        :return: Latest UMA record
        """
        cls._load_data()

        if not cls._data:
            return None

        # Data is sorted by year descending, so first element is most recent
        return cls._data[0].copy()

    @classmethod
    def get_valor(cls, anio: int, tipo: str = "diario") -> float | None:
        """
        Get UMA value for specific year and type

        :param anio: Year
        :param tipo: Type of value ('diario', 'mensual', 'anual')
        :return: UMA value or None if not found
        """
        record = cls.get_por_anio(anio)
        if not record:
            return None

        tipo_map = {"diario": "valor_diario", "mensual": "valor_mensual", "anual": "valor_anual"}

        field = tipo_map.get(tipo.lower())
        if not field:
            return None

        return record.get(field)

    @classmethod
    def calcular_umas(cls, monto: float, anio: int, tipo: str = "diario") -> float | None:
        """
        Calculate how many UMAs a given amount represents

        :param monto: Amount in Mexican pesos
        :param anio: Year for UMA value
        :param tipo: Type of UMA ('diario', 'mensual', 'anual')
        :return: Number of UMAs or None if UMA value not found
        """
        valor_uma = cls.get_valor(anio, tipo)
        if not valor_uma:
            return None

        return monto / valor_uma

    @classmethod
    def calcular_monto(cls, umas: float, anio: int, tipo: str = "diario") -> float | None:
        """
        Calculate the peso amount for a given number of UMAs

        :param umas: Number of UMAs
        :param anio: Year for UMA value
        :param tipo: Type of UMA ('diario', 'mensual', 'anual')
        :return: Amount in Mexican pesos or None if UMA value not found
        """
        valor_uma = cls.get_valor(anio, tipo)
        if not valor_uma:
            return None

        return umas * valor_uma

    @classmethod
    def get_incremento(cls, anio: int) -> float | None:
        """
        Get percentage increment for a specific year

        :param anio: Year
        :return: Percentage increment or None if not found
        """
        record = cls.get_por_anio(anio)
        if not record:
            return None

        return record.get("incremento_porcentual")


# Convenience functions
def get_uma_actual() -> dict | None:
    """Get current UMA values"""
    return UMACatalog.get_actual()


def get_uma_por_anio(anio: int) -> dict | None:
    """Get UMA values for a specific year"""
    return UMACatalog.get_por_anio(anio)


def calcular_umas(monto: float, anio: int, tipo: str = "diario") -> float | None:
    """Calculate how many UMAs a given amount represents"""
    return UMACatalog.calcular_umas(monto, anio, tipo)


def calcular_monto(umas: float, anio: int, tipo: str = "diario") -> float | None:
    """Calculate peso amount for a given number of UMAs"""
    return UMACatalog.calcular_monto(umas, anio, tipo)


# Export commonly used functions and classes
__all__ = [
    "UMACatalog",
    "get_uma_actual",
    "get_uma_por_anio",
    "calcular_umas",
    "calcular_monto",
]
