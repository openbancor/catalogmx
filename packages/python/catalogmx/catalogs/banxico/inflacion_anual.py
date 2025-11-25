"""
Inflación Anual Catalog

This module provides access to annual inflation data (INPC) from Banco de México.
Inflation is measured using the National Consumer Price Index.
"""

import json
from pathlib import Path


class InflacionAnualCatalog:
    """
    Catalog of annual inflation data (INPC)

    The National Consumer Price Index (INPC) measures the evolution of prices
    of a basket of goods and services representative of household consumption.
    """

    _data: list[dict] | None = None
    _by_fecha: dict[str, dict] | None = None
    _by_anio: dict[int, list[dict]] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Load inflation data from JSON file"""
        if cls._data is None:
            current_file = Path(__file__)
            shared_data_path = (
                current_file.parent.parent.parent.parent.parent
                / "shared-data"
                / "banxico"
                / "inflacion_anual.json"
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
        Get all inflation data

        :return: List of all inflation records
        """
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_por_fecha(cls, fecha: str) -> dict | None:
        """
        Get inflation rate for a specific date

        :param fecha: Date string in YYYY-MM-DD format
        :return: Inflation record or None if not found
        """
        cls._load_data()
        record = cls._by_fecha.get(fecha)
        return record.copy() if record else None

    @classmethod
    def get_por_anio(cls, anio: int) -> list[dict]:
        """
        Get all inflation rates for a specific year

        :param anio: Year (e.g., 2024)
        :return: List of inflation records for the year
        """
        cls._load_data()
        records = cls._by_anio.get(anio, [])
        return [record.copy() for record in records]

    @classmethod
    def get_actual(cls) -> dict | None:
        """
        Get most recent inflation rate

        :return: Latest inflation record
        """
        cls._load_data()

        if not cls._data:
            return None

        record = max(cls._data, key=lambda r: r.get("fecha", ""), default=None)
        return record.copy() if record else None

    @classmethod
    def get_tasa_actual(cls) -> float | None:
        """
        Get current inflation rate

        :return: Current annual inflation rate or None
        """
        record = cls.get_actual()
        return record.get("inflacion_anual") if record else None

    @classmethod
    def ajustar_por_inflacion(
        cls, monto: float, fecha_original: str, fecha_actual: str
    ) -> float | None:
        """
        Adjust amount for inflation between two dates

        :param monto: Original amount
        :param fecha_original: Original date (YYYY-MM-DD)
        :param fecha_actual: Current date (YYYY-MM-DD)
        :return: Adjusted amount or None if rates not found
        """
        record_original = cls.get_por_fecha(fecha_original)
        record_actual = cls.get_por_fecha(fecha_actual)

        if not record_original or not record_actual:
            return None

        inflacion_original = record_original.get("inflacion_anual", 0) / 100
        inflacion_actual = record_actual.get("inflacion_anual", 0) / 100

        # Simplified adjustment: multiply by ratio of inflation rates
        # More sophisticated methods exist for inflation adjustment
        adjustment_factor = (1 + inflacion_actual) / (1 + inflacion_original)

        return monto * adjustment_factor

    @classmethod
    def calcular_variacion(cls, fecha_inicio: str, fecha_fin: str) -> float | None:
        """
        Calculate inflation variation between two dates

        :param fecha_inicio: Start date (YYYY-MM-DD)
        :param fecha_fin: End date (YYYY-MM-DD)
        :return: Percentage variation or None if rates not found
        """
        record_inicio = cls.get_por_fecha(fecha_inicio)
        record_fin = cls.get_por_fecha(fecha_fin)

        if not record_inicio or not record_fin:
            return None

        inflacion_inicio = record_inicio.get("inflacion_anual", 0)
        inflacion_fin = record_fin.get("inflacion_anual", 0)

        return inflacion_fin - inflacion_inicio

    @classmethod
    def get_promedio_anual(cls, anio: int) -> float | None:
        """
        Calculate annual average inflation rate

        :param anio: Year (e.g., 2024)
        :return: Annual average inflation rate or None if no data
        """
        records = cls.get_por_anio(anio)
        if not records:
            return None

        rates = [r.get("inflacion_anual") for r in records if r.get("inflacion_anual")]
        return sum(rates) / len(rates) if rates else None


# Convenience functions
def get_inflacion_actual() -> dict | None:
    """Get most recent inflation rate"""
    return InflacionAnualCatalog.get_actual()


def get_inflacion_por_fecha(fecha: str) -> dict | None:
    """Get inflation rate for a specific date"""
    return InflacionAnualCatalog.get_por_fecha(fecha)


def ajustar_por_inflacion(monto: float, fecha_original: str, fecha_actual: str) -> float | None:
    """Adjust amount for inflation"""
    return InflacionAnualCatalog.ajustar_por_inflacion(monto, fecha_original, fecha_actual)


# Export commonly used functions and classes
__all__ = [
    "InflacionAnualCatalog",
    "get_inflacion_actual",
    "get_inflacion_por_fecha",
    "ajustar_por_inflacion",
]
