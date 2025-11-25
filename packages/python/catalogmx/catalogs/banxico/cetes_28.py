"""
CETES 28 días Catalog

This module provides access to CETES 28-day values from Banco de México.
CETES (Certificados de la Tesorería) are short-term government securities.
"""

import json
from pathlib import Path


class CETES28Catalog:
    """
    Catalog of CETES 28-day values

    CETES are short-term government securities issued by the Mexican Treasury
    and are considered the benchmark for risk-free interest rates in Mexico.
    """

    _data: list[dict] | None = None
    _by_fecha: dict[str, dict] | None = None
    _by_anio: dict[int, list[dict]] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Load CETES data from JSON file"""
        if cls._data is None:
            current_file = Path(__file__)
            shared_data_path = (
                current_file.parent.parent.parent.parent.parent
                / "shared-data"
                / "banxico"
                / "cetes_28.json"
            )

            with open(shared_data_path, encoding="utf-8") as f:
                cls._data = json.load(f)

        if cls._by_fecha is not None:
            return

        cls._by_fecha = {}
        cls._by_anio = {}

        for record in cls._data:
            fecha = record.get("fecha")
            if not fecha:
                continue

            cls._by_fecha[fecha] = record

            anio = record.get("año")
            if anio:
                if anio not in cls._by_anio:
                    cls._by_anio[anio] = []
                cls._by_anio[anio].append(record)

        # Sort by date within each year
        for anio in cls._by_anio:
            cls._by_anio[anio].sort(key=lambda r: r["fecha"])

    @classmethod
    def get_data(cls) -> list[dict]:
        """
        Get all CETES data

        :return: List of all CETES records
        """
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_por_fecha(cls, fecha: str) -> dict | None:
        """
        Get CETES rate for a specific date

        :param fecha: Date string in YYYY-MM-DD format
        :return: CETES record or None if not found
        """
        cls._load_data()
        record = cls._by_fecha.get(fecha)
        return record.copy() if record else None

    @classmethod
    def get_por_anio(cls, anio: int) -> list[dict]:
        """
        Get all CETES rates for a specific year

        :param anio: Year (e.g., 2024)
        :return: List of CETES records for the year
        """
        cls._load_data()
        records = cls._by_anio.get(anio, [])
        return [record.copy() for record in records]

    @classmethod
    def get_actual(cls) -> dict | None:
        """
        Get most recent CETES rate

        :return: Latest CETES record
        """
        cls._load_data()

        if not cls._data:
            return None

        record = max(cls._data, key=lambda r: r.get("fecha", ""), default=None)
        return record.copy() if record else None

    @classmethod
    def get_tasa_actual(cls) -> float | None:
        """
        Get current CETES rate value

        :return: Current CETES rate or None
        """
        record = cls.get_actual()
        return record.get("tasa") if record else None

    @classmethod
    def calcular_rendimiento(
        cls, inversion: float, fecha_inicio: str, fecha_fin: str
    ) -> float | None:
        """
        Calculate return on CETES investment

        :param inversion: Investment amount
        :param fecha_inicio: Start date (YYYY-MM-DD)
        :param fecha_fin: End date (YYYY-MM-DD)
        :return: Final amount or None if rates not found
        """
        # CETES are discounted securities, so the calculation is different
        # This is a simplified version
        record = cls.get_por_fecha(fecha_inicio)

        if not record:
            return None

        rate = record.get("tasa", 0) / 100  # Convert to decimal

        # CETES are typically 28-day securities
        # Simplified calculation: final value = investment / (1 - rate * days/360)
        days = 28  # Standard CETES term
        discount_factor = 1 - (rate * days / 360)

        if discount_factor <= 0:
            return None

        face_value = inversion / discount_factor
        return face_value

    @classmethod
    def get_promedio_anual(cls, anio: int) -> float | None:
        """
        Calculate annual average CETES rate

        :param anio: Year (e.g., 2024)
        :return: Annual average rate or None if no data
        """
        records = cls.get_por_anio(anio)
        if not records:
            return None

        rates = [r.get("tasa") for r in records if r.get("tasa")]
        return sum(rates) / len(rates) if rates else None


# Convenience functions
def get_cetes_actual() -> dict | None:
    """Get most recent CETES rate"""
    return CETES28Catalog.get_actual()


def get_cetes_por_fecha(fecha: str) -> dict | None:
    """Get CETES rate for a specific date"""
    return CETES28Catalog.get_por_fecha(fecha)


def calcular_rendimiento_cetes(
    inversion: float, fecha_inicio: str, fecha_fin: str
) -> float | None:
    """Calculate CETES investment return"""
    return CETES28Catalog.calcular_rendimiento(inversion, fecha_inicio, fecha_fin)


# Export commonly used functions and classes
__all__ = [
    "CETES28Catalog",
    "get_cetes_actual",
    "get_cetes_por_fecha",
    "calcular_rendimiento_cetes",
]
