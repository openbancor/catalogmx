"""
CETES (Certificados de la Tesorería) Catalog - SQLite Backend

This module provides access to CETES rates from Banco de México using a SQLite
database that can be automatically updated without requiring library releases.
"""

import sqlite3
from pathlib import Path

from catalogmx.data.updater import get_database_path


class CETESCatalog:
    """
    Catalog of CETES (Certificados de la Tesorería) rates

    CETES are short-term Mexican treasury bills and serve as the
    risk-free rate benchmark for the Mexican market.

    This catalog uses an auto-updating SQLite database backend.
    """

    _db_path: Path | None = None

    @classmethod
    def _get_db_path(cls) -> Path:
        """Get path to database with auto-update"""
        if cls._db_path is None:
            cls._db_path = get_database_path(auto_update=True)
        return cls._db_path

    @classmethod
    def _row_to_dict(cls, row: sqlite3.Row) -> dict:
        """Convert SQLite row to dictionary"""
        return {
            "fecha": row["fecha"],
            "plazo": row["plazo"],
            "tasa": row["tasa"],
            "año": row["anio"],
            "mes": row["mes"],
            "instrumento": "CETES",  # Add instrumento field for compatibility
        }

    @classmethod
    def get_data(cls, plazo: int = 28) -> list[dict]:
        """
        Get all CETES data for a specific term

        :param plazo: Term in days (28, 91, 182, or 364)
        :return: List of all CETES records
        """
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row
        cursor = db.execute(
            """
            SELECT fecha, plazo, tasa, anio, mes
            FROM cetes
            WHERE plazo = ?
            ORDER BY fecha
            """,
            (plazo,),
        )
        results = [cls._row_to_dict(row) for row in cursor.fetchall()]
        db.close()
        return results

    @classmethod
    def get_por_fecha(cls, fecha: str, plazo: int = 28) -> dict | None:
        """
        Get CETES rate for a specific date and term

        :param fecha: Date string in YYYY-MM-DD format
        :param plazo: Term in days (28, 91, 182, or 364)
        :return: CETES record or None if not found
        """
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row

        cursor = db.execute(
            """
            SELECT fecha, plazo, tasa, anio, mes
            FROM cetes
            WHERE fecha = ? AND plazo = ?
            LIMIT 1
            """,
            (fecha, plazo),
        )
        row = cursor.fetchone()
        db.close()

        if row:
            return cls._row_to_dict(row)
        return None

    @classmethod
    def get_actual(cls, plazo: int = 28) -> dict | None:
        """
        Get most recent CETES rate

        :param plazo: Term in days (28, 91, 182, or 364)
        :return: Latest CETES record
        """
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row

        cursor = db.execute(
            """
            SELECT fecha, plazo, tasa, anio, mes
            FROM cetes
            WHERE plazo = ?
            ORDER BY fecha DESC
            LIMIT 1
            """,
            (plazo,),
        )
        row = cursor.fetchone()
        db.close()

        if row:
            return cls._row_to_dict(row)
        return None

    @classmethod
    def get_valor_actual(cls, plazo: int = 28) -> float | None:
        """
        Get current CETES rate value

        :param plazo: Term in days (28, 91, 182, or 364)
        :return: Current CETES rate or None
        """
        record = cls.get_actual(plazo)
        return record.get("tasa") if record else None

    @classmethod
    def get_por_anio(cls, anio: int, plazo: int = 28) -> list[dict]:
        """
        Get all CETES rates for a specific year and term

        :param anio: Year (e.g., 2024)
        :param plazo: Term in days (28, 91, 182, or 364)
        :return: List of CETES records for the year
        """
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row

        cursor = db.execute(
            """
            SELECT fecha, plazo, tasa, anio, mes
            FROM cetes
            WHERE anio = ? AND plazo = ?
            ORDER BY fecha
            """,
            (anio, plazo),
        )
        results = [cls._row_to_dict(row) for row in cursor.fetchall()]
        db.close()
        return results

    @classmethod
    def calcular_variacion(cls, fecha_inicio: str, fecha_fin: str, plazo: int = 28) -> float | None:
        """
        Calculate variation between two dates

        :param fecha_inicio: Start date (YYYY-MM-DD)
        :param fecha_fin: End date (YYYY-MM-DD)
        :param plazo: Term in days (28, 91, 182, or 364)
        :return: Variation in percentage points or None
        """
        record_inicio = cls.get_por_fecha(fecha_inicio, plazo)
        record_fin = cls.get_por_fecha(fecha_fin, plazo)

        if not record_inicio or not record_fin:
            return None

        tasa_inicio = record_inicio.get("tasa")
        tasa_fin = record_fin.get("tasa")

        if tasa_inicio is None or tasa_fin is None:
            return None

        # Return difference in percentage points (not percentage change)
        return tasa_fin - tasa_inicio

    @classmethod
    def get_promedio_anual(cls, anio: int, plazo: int = 28) -> float | None:
        """
        Calculate annual average CETES rate

        :param anio: Year (e.g., 2024)
        :param plazo: Term in days (28, 91, 182, or 364)
        :return: Annual average rate or None if no data
        """
        records = cls.get_por_anio(anio, plazo)
        if not records:
            return None

        tasas = [r.get("tasa") for r in records if r.get("tasa") is not None]
        return sum(tasas) / len(tasas) if tasas else None

    @classmethod
    def get_tasa_actual(cls, plazo: int = 28) -> float | None:
        """
        Get current CETES rate value (alias for get_valor_actual)

        :param plazo: Term in days (28, 91, 182, or 364)
        :return: Current CETES rate or None
        """
        return cls.get_valor_actual(plazo)

    @classmethod
    def calcular_rendimiento(
        cls, monto: float, fecha_inicio: str, fecha_fin: str, plazo: int = 28
    ) -> float | None:
        """
        Calculate CETES return (principal + interest)

        :param monto: Initial investment amount
        :param fecha_inicio: Start date (YYYY-MM-DD)
        :param fecha_fin: End date (YYYY-MM-DD)
        :param plazo: Term in days (28, 91, 182, or 364)
        :return: Total return (principal + interest) or None if data not available
        """
        from datetime import datetime

        record_inicio = cls.get_por_fecha(fecha_inicio, plazo)
        record_fin = cls.get_por_fecha(fecha_fin, plazo)

        if not record_inicio and not record_fin:
            return None

        # Use available rate (start or end, or average if both)
        tasa = None
        if record_inicio and record_fin:
            tasa = (record_inicio.get("tasa", 0) + record_fin.get("tasa", 0)) / 2
        elif record_inicio:
            tasa = record_inicio.get("tasa")
        elif record_fin:
            tasa = record_fin.get("tasa")

        if tasa is None:
            return None

        # Calculate days between dates
        date_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        date_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
        dias = (date_fin - date_inicio).days

        if dias <= 0:
            return monto

        # Calculate simple interest return
        interes = monto * (tasa / 100) * (dias / 365)
        return round(monto + interes, 2)


# Convenience functions for CETES 28 (most commonly used)
def get_cetes_actual(plazo: int = 28) -> dict | None:
    """Get most recent CETES rate"""
    return CETESCatalog.get_actual(plazo)


def get_cetes_por_fecha(fecha: str, plazo: int = 28) -> dict | None:
    """Get CETES rate for a specific date"""
    return CETESCatalog.get_por_fecha(fecha, plazo)


def get_cetes_valor_actual(plazo: int = 28) -> float | None:
    """Get current CETES rate value"""
    return CETESCatalog.get_valor_actual(plazo)


# Export commonly used functions and classes
__all__ = [
    "CETESCatalog",
    "get_cetes_actual",
    "get_cetes_por_fecha",
    "get_cetes_valor_actual",
]
