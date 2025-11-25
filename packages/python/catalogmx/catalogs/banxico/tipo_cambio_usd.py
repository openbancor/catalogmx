"""
Tipo de Cambio USD/MXN (FIX) Catalog

This module provides access to USD/MXN exchange rate FIX values from Banco de México.
The FIX rate is the official exchange rate determined daily by Banco de México.
"""

import json
from pathlib import Path


class TipoCambioUSDCatalog:
    """
    Catalog of USD/MXN exchange rate FIX values

    The FIX exchange rate is the official reference rate published daily by
    Banco de México for transactions in foreign currency.
    """

    _data: list[dict] | None = None
    _by_fecha: dict[str, dict] | None = None
    _by_anio: dict[int, list[dict]] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Load exchange rate data from JSON file"""
        if cls._data is None:
            # Path: catalogmx/packages/python/catalogmx/catalogs/banxico/tipo_cambio_usd.py
            # Target: catalogmx/packages/shared-data/banxico/tipo_cambio_usd.json
            current_file = Path(__file__)
            shared_data_path = (
                current_file.parent.parent.parent.parent.parent
                / "shared-data"
                / "banxico"
                / "tipo_cambio_usd.json"
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
        Get all exchange rate data

        :return: List of all exchange rate records
        """
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_por_fecha(cls, fecha: str) -> dict | None:
        """
        Get exchange rate for a specific date

        :param fecha: Date string in YYYY-MM-DD format
        :return: Exchange rate record or None if not found
        """
        cls._load_data()
        record = cls._by_fecha.get(fecha)
        return record.copy() if record else None

    @classmethod
    def get_por_anio(cls, anio: int) -> list[dict]:
        """
        Get all exchange rates for a specific year

        :param anio: Year (e.g., 2024)
        :return: List of exchange rate records for the year
        """
        cls._load_data()
        records = cls._by_anio.get(anio, [])
        return [record.copy() for record in records]

    @classmethod
    def get_actual(cls) -> dict | None:
        """
        Get most recent exchange rate

        :return: Latest exchange rate record
        """
        cls._load_data()

        if not cls._data:
            return None

        # Get the most recent record
        record = max(cls._data, key=lambda r: r.get("fecha", ""), default=None)
        return record.copy() if record else None

    @classmethod
    def get_valor_actual(cls) -> float | None:
        """
        Get current exchange rate value

        :return: Current USD/MXN rate or None
        """
        record = cls.get_actual()
        return record.get("tipo_cambio") if record else None

    @classmethod
    def usd_a_mxn(cls, usd: float, fecha: str | None = None) -> float | None:
        """
        Convert USD to MXN

        :param usd: Amount in USD
        :param fecha: Date string in YYYY-MM-DD format, or None for latest rate
        :return: Amount in MXN or None if rate not found
        """
        if fecha:
            record = cls.get_por_fecha(fecha)
        else:
            record = cls.get_actual()

        if not record:
            return None

        rate = record.get("tipo_cambio")
        return usd * rate if rate else None

    @classmethod
    def mxn_a_usd(cls, mxn: float, fecha: str | None = None) -> float | None:
        """
        Convert MXN to USD

        :param mxn: Amount in MXN
        :param fecha: Date string in YYYY-MM-DD format, or None for latest rate
        :return: Amount in USD or None if rate not found
        """
        if fecha:
            record = cls.get_por_fecha(fecha)
        else:
            record = cls.get_actual()

        if not record:
            return None

        rate = record.get("tipo_cambio")
        return mxn / rate if rate else None

    @classmethod
    def calcular_variacion(cls, fecha_inicio: str, fecha_fin: str) -> float | None:
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

        rate_inicio = record_inicio.get("tipo_cambio")
        rate_fin = record_fin.get("tipo_cambio")

        if not rate_inicio or not rate_fin:
            return None

        return ((rate_fin - rate_inicio) / rate_inicio) * 100

    @classmethod
    def get_promedio_anual(cls, anio: int) -> float | None:
        """
        Calculate annual average exchange rate

        :param anio: Year (e.g., 2024)
        :return: Annual average rate or None if no data
        """
        records = cls.get_por_anio(anio)
        if not records:
            return None

        rates = [r.get("tipo_cambio") for r in records if r.get("tipo_cambio")]
        return sum(rates) / len(rates) if rates else None


# Convenience functions
def get_tipo_cambio_actual() -> dict | None:
    """Get most recent exchange rate"""
    return TipoCambioUSDCatalog.get_actual()


def get_tipo_cambio_por_fecha(fecha: str) -> dict | None:
    """Get exchange rate for a specific date"""
    return TipoCambioUSDCatalog.get_por_fecha(fecha)


def usd_a_mxn(usd: float, fecha: str | None = None) -> float | None:
    """Convert USD to MXN"""
    return TipoCambioUSDCatalog.usd_a_mxn(usd, fecha)


def mxn_a_usd(mxn: float, fecha: str | None = None) -> float | None:
    """Convert MXN to USD"""
    return TipoCambioUSDCatalog.mxn_a_usd(mxn, fecha)


# Export commonly used functions and classes
__all__ = [
    "TipoCambioUSDCatalog",
    "get_tipo_cambio_actual",
    "get_tipo_cambio_por_fecha",
    "usd_a_mxn",
    "mxn_a_usd",
]
