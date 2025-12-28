"""
Inflación (Inflation) Catalog - SQLite Backend

This module provides access to inflation data from Banco de México using a SQLite
database that can be automatically updated without requiring library releases.
"""

import sqlite3
from pathlib import Path

from catalogmx.data.updater import get_database_path


class InflacionCatalog:
    """
    Catalog of Mexican inflation data

    Provides access to INPC (National Consumer Price Index) and
    inflation rates (monthly and annual) from Banco de México.

    This catalog uses an auto-updating SQLite database backend.
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
            "año": row["anio"],
            "mes": row["mes"],
            "inpc": row["inpc"] if row["inpc"] is not None else None,
            "inflacion_mensual": (
                row["inflacion_mensual"] if row["inflacion_mensual"] is not None else None
            ),
            "inflacion_anual": (
                row["inflacion_anual"] if row["inflacion_anual"] is not None else None
            ),
        }

    @classmethod
    def get_data(cls) -> list[dict]:
        """
        Get all inflation data

        :return: List of all inflation records
        """
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row
        cursor = db.execute(
            """
            SELECT fecha, anio, mes, inpc, inflacion_mensual, inflacion_anual
            FROM inflacion
            ORDER BY fecha
            """
        )
        results = [cls._row_to_dict(row) for row in cursor.fetchall()]
        db.close()
        return results

    @classmethod
    def get_por_fecha(cls, fecha: str) -> dict | None:
        """
        Get inflation data for a specific date

        :param fecha: Date string in YYYY-MM-DD format
        :return: Inflation record or None if not found
        """
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row

        cursor = db.execute(
            """
            SELECT fecha, anio, mes, inpc, inflacion_mensual, inflacion_anual
            FROM inflacion
            WHERE fecha = ?
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
    def get_por_mes(cls, anio: int, mes: int) -> dict | None:
        """
        Get inflation data for a specific month

        :param anio: Year (e.g., 2024)
        :param mes: Month (1-12)
        :return: Inflation record or None if not found
        """
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row

        cursor = db.execute(
            """
            SELECT fecha, anio, mes, inpc, inflacion_mensual, inflacion_anual
            FROM inflacion
            WHERE anio = ? AND mes = ?
            LIMIT 1
            """,
            (anio, mes),
        )
        row = cursor.fetchone()
        db.close()

        if row:
            return cls._row_to_dict(row)
        return None

    @classmethod
    def get_actual(cls) -> dict | None:
        """
        Get most recent inflation data

        :return: Latest inflation record
        """
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row

        cursor = db.execute(
            """
            SELECT fecha, anio, mes, inpc, inflacion_mensual, inflacion_anual
            FROM inflacion
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
    def get_inflacion_anual_actual(cls) -> float | None:
        """
        Get current annual inflation rate

        :return: Current annual inflation rate or None
        """
        record = cls.get_actual()
        return record.get("inflacion_anual") if record else None

    @classmethod
    def get_inflacion_mensual_actual(cls) -> float | None:
        """
        Get current monthly inflation rate

        :return: Current monthly inflation rate or None
        """
        record = cls.get_actual()
        return record.get("inflacion_mensual") if record else None

    @classmethod
    def get_inpc_actual(cls) -> float | None:
        """
        Get current INPC value

        :return: Current INPC value or None
        """
        record = cls.get_actual()
        return record.get("inpc") if record else None

    @classmethod
    def get_por_anio(cls, anio: int) -> list[dict]:
        """
        Get all inflation data for a specific year

        :param anio: Year (e.g., 2024)
        :return: List of inflation records for the year
        """
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row

        cursor = db.execute(
            """
            SELECT fecha, anio, mes, inpc, inflacion_mensual, inflacion_anual
            FROM inflacion
            WHERE anio = ?
            ORDER BY fecha
            """,
            (anio,),
        )
        results = [cls._row_to_dict(row) for row in cursor.fetchall()]
        db.close()
        return results

    @classmethod
    def calcular_inflacion_acumulada(cls, fecha_inicio: str, fecha_fin: str) -> float | None:
        """
        Calculate accumulated inflation between two dates

        :param fecha_inicio: Start date (YYYY-MM-DD)
        :param fecha_fin: End date (YYYY-MM-DD)
        :return: Accumulated inflation percentage or None
        """
        record_inicio = cls.get_por_fecha(fecha_inicio)
        record_fin = cls.get_por_fecha(fecha_fin)

        if not record_inicio or not record_fin:
            return None

        inpc_inicio = record_inicio.get("inpc")
        inpc_fin = record_fin.get("inpc")

        if inpc_inicio is None or inpc_fin is None:
            return None

        return ((inpc_fin - inpc_inicio) / inpc_inicio) * 100

    @classmethod
    def get_promedio_anual(cls, anio: int) -> float | None:
        """
        Calculate average annual inflation for a year

        :param anio: Year (e.g., 2024)
        :return: Average annual inflation or None if no data
        """
        records = cls.get_por_anio(anio)
        if not records:
            return None

        inflaciones = [
            r.get("inflacion_anual") for r in records if r.get("inflacion_anual") is not None
        ]
        return sum(inflaciones) / len(inflaciones) if inflaciones else None

    @classmethod
    def get_tasa_actual(cls) -> float | None:
        """
        Get current inflation rate (alias for get_inflacion_anual_actual)

        :return: Current annual inflation rate or None
        """
        return cls.get_inflacion_anual_actual()

    @classmethod
    def ajustar_por_inflacion(cls, monto: float, fecha_inicio: str, fecha_fin: str) -> float | None:
        """
        Adjust an amount for inflation between two dates

        :param monto: Original amount
        :param fecha_inicio: Start date (YYYY-MM-DD)
        :param fecha_fin: End date (YYYY-MM-DD)
        :return: Inflation-adjusted amount or None if data not available
        """
        record_inicio = cls.get_por_fecha(fecha_inicio)
        record_fin = cls.get_por_fecha(fecha_fin)

        if not record_inicio or not record_fin:
            return None

        inpc_inicio = record_inicio.get("inpc")
        inpc_fin = record_fin.get("inpc")

        if inpc_inicio is None or inpc_fin is None or inpc_inicio == 0:
            return None

        # Adjust amount using INPC ratio
        return round(monto * (inpc_fin / inpc_inicio), 2)


# Convenience functions
def get_inflacion_actual() -> dict | None:
    """Get most recent inflation data"""
    return InflacionCatalog.get_actual()


def get_inflacion_anual_actual() -> float | None:
    """Get current annual inflation rate"""
    return InflacionCatalog.get_inflacion_anual_actual()


def get_inflacion_mensual_actual() -> float | None:
    """Get current monthly inflation rate"""
    return InflacionCatalog.get_inflacion_mensual_actual()


def get_inpc_actual() -> float | None:
    """Get current INPC value"""
    return InflacionCatalog.get_inpc_actual()


# Export commonly used functions and classes
__all__ = [
    "InflacionCatalog",
    "get_inflacion_actual",
    "get_inflacion_anual_actual",
    "get_inflacion_mensual_actual",
    "get_inpc_actual",
]
