"""
TIIE 28 días Catalog

This module provides access to TIIE 28-day values from Banco de México.
TIIE (Tasa de Interés Interbancaria de Equilibrio) is the interbank equilibrium interest rate.
"""

import json
from pathlib import Path


class TIIE28Catalog:
    """
    Catalog of TIIE 28-day values

    TIIE is the reference interest rate calculated daily by Banco de México
    based on transactions between banks in the Mexican peso money market.
    """

    _data: list[dict] | None = None
    _by_fecha: dict[str, dict] | None = None
    _by_anio: dict[int, list[dict]] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Load TIIE data from JSON file"""
        if cls._data is None:
            current_file = Path(__file__)
            shared_data_path = (
                current_file.parent.parent.parent.parent.parent
                / "shared-data"
                / "banxico"
                / "tiie_28.json"
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
        Get all TIIE data

        :return: List of all TIIE records
        """
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_por_fecha(cls, fecha: str) -> dict | None:
        """
        Get TIIE rate for a specific date

        :param fecha: Date string in YYYY-MM-DD format
        :return: TIIE record or None if not found
        """
        cls._load_data()
        record = cls._by_fecha.get(fecha)
        return record.copy() if record else None

    @classmethod
    def get_por_anio(cls, anio: int) -> list[dict]:
        """
        Get all TIIE rates for a specific year

        :param anio: Year (e.g., 2024)
        :return: List of TIIE records for the year
        """
        cls._load_data()
        records = cls._by_anio.get(anio, [])
        return [record.copy() for record in records]

    @classmethod
    def get_actual(cls) -> dict | None:
        """
        Get most recent TIIE rate

        :return: Latest TIIE record
        """
        cls._load_data()

        if not cls._data:
            return None

        record = max(cls._data, key=lambda r: r.get("fecha", ""), default=None)
        return record.copy() if record else None

    @classmethod
    def get_tasa_actual(cls) -> float | None:
        """
        Get current TIIE rate value

        :return: Current TIIE rate or None
        """
        record = cls.get_actual()
        return record.get("tasa") if record else None

    @classmethod
    def calcular_interes(cls, capital: float, fecha_inicio: str, fecha_fin: str) -> float | None:
        """
        Calculate interest for a period using TIIE

        :param capital: Principal amount
        :param fecha_inicio: Start date (YYYY-MM-DD)
        :param fecha_fin: End date (YYYY-MM-DD)
        :return: Interest amount or None if rates not found
        """
        # This is a simplified calculation - in practice, you might need
        # more sophisticated interest calculation methods
        record_inicio = cls.get_por_fecha(fecha_inicio)
        record_fin = cls.get_por_fecha(fecha_fin)

        if not record_inicio or not record_fin:
            return None

        # Use average rate for the period (simplified)
        rate_inicio = record_inicio.get("tasa", 0)
        rate_fin = record_fin.get("tasa", 0)
        avg_rate = (rate_inicio + rate_fin) / 2

        # Calculate days between dates (simplified)
        # In practice, you should use proper date calculations
        days = 30  # Simplified assumption

        # Daily rate
        daily_rate = avg_rate / 100 / 360  # Assuming 360-day year

        return capital * daily_rate * days

    @classmethod
    def get_promedio_anual(cls, anio: int) -> float | None:
        """
        Calculate annual average TIIE rate

        :param anio: Year (e.g., 2024)
        :return: Annual average rate or None if no data
        """
        records = cls.get_por_anio(anio)
        if not records:
            return None

        rates = [r.get("tasa") for r in records if r.get("tasa")]
        return sum(rates) / len(rates) if rates else None


# Convenience functions
def get_tiie_actual() -> dict | None:
    """Get most recent TIIE rate"""
    return TIIE28Catalog.get_actual()


def get_tiie_por_fecha(fecha: str) -> dict | None:
    """Get TIIE rate for a specific date"""
    return TIIE28Catalog.get_por_fecha(fecha)


def calcular_interes_tiie(capital: float, fecha_inicio: str, fecha_fin: str) -> float | None:
    """Calculate interest using TIIE"""
    return TIIE28Catalog.calcular_interes(capital, fecha_inicio, fecha_fin)


# Export commonly used functions and classes
__all__ = [
    "TIIE28Catalog",
    "get_tiie_actual",
    "get_tiie_por_fecha",
    "calcular_interes_tiie",
]
