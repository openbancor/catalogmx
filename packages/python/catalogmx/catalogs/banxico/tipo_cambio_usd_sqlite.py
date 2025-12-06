"""
Tipo de Cambio USD/MXN Catalog - SQLite Backend

This module provides access to USD/MXN exchange rate values using a SQLite database
that can be automatically updated without requiring library releases.
"""

import sqlite3
from pathlib import Path

from catalogmx.data.updater import get_database_path


class TipoCambioUSDCatalog:
    """
    Catalog of USD/MXN exchange rate values

    The FIX exchange rate is the official reference rate published daily by
    Banco de México. This catalog uses an auto-updating SQLite database backend.
    """

    _db_path: Path | None = None

    @classmethod
    def _get_db_path(cls) -> Path:
        """Get path to database with auto-update"""
        if cls._db_path is None:
            cls._db_path = get_database_path(auto_update=True, max_age_hours=24)
        return cls._db_path

    @classmethod
    def _row_to_dict(cls, row: sqlite3.Row) -> dict:
        """Convert SQLite row to dictionary"""
        return {
            "fecha": row["fecha"],
            "tipo_cambio": row["tipo_cambio"],
            "año": row["anio"],
            "mes": row["mes"],
            "fuente": row["fuente"],
            "moneda_origen": row["moneda_origen"],
            "moneda_destino": row["moneda_destino"],
        }

    @classmethod
    def get_data(cls) -> list[dict]:
        """
        Get all exchange rate data

        :return: List of all exchange rate records
        """
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row
        cursor = db.execute(
            """
            SELECT fecha, tipo_cambio, anio, mes, fuente, moneda_origen, moneda_destino
            FROM tipo_cambio
            WHERE fuente = 'FIX'
            ORDER BY fecha
            """
        )
        results = [cls._row_to_dict(row) for row in cursor.fetchall()]
        db.close()
        return results

    @classmethod
    def get_por_fecha(cls, fecha: str) -> dict | None:
        """
        Get exchange rate for a specific date

        :param fecha: Date string in YYYY-MM-DD format
        :return: Exchange rate record or None if not found
        """
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row

        cursor = db.execute(
            """
            SELECT fecha, tipo_cambio, anio, mes, fuente, moneda_origen, moneda_destino
            FROM tipo_cambio
            WHERE fecha = ? AND fuente = 'FIX'
            LIMIT 1
            """,
            (fecha,),
        )
        row = cursor.fetchone()
        db.close()

        if row:
            return cls._row_to_dict(row)
        return None

    @classmethod
    def get_por_anio(cls, anio: int) -> list[dict]:
        """
        Get all exchange rates for a specific year

        :param anio: Year (e.g., 2024)
        :return: List of exchange rate records for the year
        """
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row

        cursor = db.execute(
            """
            SELECT fecha, tipo_cambio, anio, mes, fuente, moneda_origen, moneda_destino
            FROM tipo_cambio
            WHERE anio = ? AND fuente = 'FIX'
            ORDER BY fecha
            """,
            (anio,),
        )
        results = [cls._row_to_dict(row) for row in cursor.fetchall()]
        db.close()
        return results

    @classmethod
    def get_actual(cls) -> dict | None:
        """
        Get most recent exchange rate

        :return: Latest exchange rate record
        """
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row

        cursor = db.execute(
            """
            SELECT fecha, tipo_cambio, anio, mes, fuente, moneda_origen, moneda_destino
            FROM tipo_cambio
            WHERE fuente = 'FIX'
            ORDER BY fecha DESC
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        db.close()

        if row:
            return cls._row_to_dict(row)
        return None

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
