"""
UDI (Unidades de Inversión) Catalog - SQLite Backend

This module provides access to UDI values from Banco de México using a SQLite database
that can be automatically updated without requiring library releases.

UDIs are inflation-indexed investment units used in Mexico.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

from catalogmx.data.updater import get_database_path


class UDICatalog:
    """
    Catalog of UDI (Unidades de Inversión) values

    UDIs are inflation-indexed investment units maintained by Banco de México.
    They are commonly used for mortgage loans and other long-term financial obligations.

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
            "valor": row["valor"],
            "año": row["anio"],
            "mes": row["mes"],
            "tipo": row["tipo"],
            "moneda": row["moneda"] if "moneda" in row.keys() else "MXN",
            "notas": row["notas"] if "notas" in row.keys() else None,
        }

    @classmethod
    def get_data(cls) -> list[dict]:
        """
        Get all UDI data

        :return: List of all UDI records
        """
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row
        cursor = db.execute(
            "SELECT fecha, valor, anio, mes, tipo, moneda, notas FROM udis ORDER BY fecha"
        )
        results = [cls._row_to_dict(row) for row in cursor.fetchall()]
        db.close()
        return results

    @classmethod
    def get_por_fecha(cls, fecha: str) -> dict | None:
        """
        Get UDI value for a specific date

        :param fecha: Date string in YYYY-MM-DD format
        :return: UDI record or None if not found
        """
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row

        # Try exact match first
        cursor = db.execute(
            """
            SELECT fecha, valor, anio, mes, tipo, moneda, notas
            FROM udis
            WHERE fecha = ? AND tipo IN ('diario', 'oficial_banxico')
            LIMIT 1
            """,
            (fecha,),
        )
        row = cursor.fetchone()

        # If not found, try monthly average
        if not row:
            try:
                anio, mes, _dia = fecha.split("-")
                cursor = db.execute(
                    """
                    SELECT fecha, valor, anio, mes, tipo, moneda, notas
                    FROM udis
                    WHERE anio = ? AND mes = ? AND tipo = 'promedio_mensual'
                    LIMIT 1
                    """,
                    (int(anio), int(mes)),
                )
                row = cursor.fetchone()
            except ValueError:
                pass

        db.close()

        if row:
            return cls._row_to_dict(row)
        return None

    @classmethod
    def get_por_mes(cls, anio: int, mes: int) -> dict | None:
        """
        Get monthly average UDI value

        :param anio: Year (e.g., 2024)
        :param mes: Month (1-12)
        :return: UDI record with monthly average or None if not found
        """
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row

        cursor = db.execute(
            """
            SELECT fecha, valor, anio, mes, tipo, moneda, notas
            FROM udis
            WHERE anio = ? AND mes = ? AND tipo = 'promedio_mensual'
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
    def get_promedio_anual(cls, anio: int) -> dict | None:
        """
        Get annual average UDI value

        :param anio: Year (e.g., 2024)
        :return: UDI record with annual average or None if not found
        """
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row

        cursor = db.execute(
            """
            SELECT fecha, valor, anio, mes, tipo, moneda, notas
            FROM udis
            WHERE anio = ? AND tipo = 'promedio_anual'
            LIMIT 1
            """,
            (anio,),
        )
        row = cursor.fetchone()
        db.close()

        if row:
            return cls._row_to_dict(row)
        return None

    @classmethod
    def get_por_anio(cls, anio: int) -> list[dict]:
        """
        Return the daily UDI series for a given year

        :param anio: Year (e.g., 2024)
        :return: List of UDI records for the year
        """
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row

        cursor = db.execute(
            """
            SELECT fecha, valor, anio, mes, tipo, moneda, notas
            FROM udis
            WHERE anio = ? AND tipo IN ('diario', 'oficial_banxico')
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
        Get most recent UDI value

        :return: Latest UDI record
        """
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row

        cursor = db.execute(
            """
            SELECT fecha, valor, anio, mes, tipo, moneda, notas
            FROM udis
            WHERE tipo IN ('diario', 'oficial_banxico')
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
    def _get_valor_cercano(cls, fecha: str) -> dict | None:
        """Get UDI value closest to given date"""
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row

        # Get closest date (before or after)
        cursor = db.execute(
            """
            SELECT fecha, valor, anio, mes, tipo, moneda, notas,
                   ABS(julianday(fecha) - julianday(?)) as diff
            FROM udis
            WHERE tipo IN ('diario', 'oficial_banxico')
            ORDER BY diff
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
    def pesos_a_udis(cls, pesos: float, fecha: str) -> float | None:
        """
        Convert Mexican pesos to UDIs

        :param pesos: Amount in Mexican pesos
        :param fecha: Date string in YYYY-MM-DD format
        :return: Amount in UDIs or None if UDI value not found
        """
        record = cls.get_por_fecha(fecha)
        if not record:
            record = cls._get_valor_cercano(fecha)
        if not record:
            return None

        valor_udi = record.get("valor")
        if not valor_udi:
            return None

        return pesos / valor_udi

    @classmethod
    def udis_a_pesos(cls, udis: float, fecha: str) -> float | None:
        """
        Convert UDIs to Mexican pesos

        :param udis: Amount in UDIs
        :param fecha: Date string in YYYY-MM-DD format
        :return: Amount in Mexican pesos or None if UDI value not found
        """
        record = cls.get_por_fecha(fecha)
        if not record:
            record = cls._get_valor_cercano(fecha)
        if not record:
            return None

        valor_udi = record.get("valor")
        if not valor_udi:
            return None

        return udis * valor_udi

    @classmethod
    def calcular_variacion(cls, fecha_inicio: str, fecha_fin: str) -> float | None:
        """
        Calculate percentage variation between two dates

        :param fecha_inicio: Start date (YYYY-MM-DD)
        :param fecha_fin: End date (YYYY-MM-DD)
        :return: Percentage variation or None if values not found
        """
        record_inicio = cls.get_por_fecha(fecha_inicio) or cls._get_valor_cercano(
            fecha_inicio
        )
        record_fin = cls.get_por_fecha(fecha_fin) or cls._get_valor_cercano(fecha_fin)

        if not record_inicio or not record_fin:
            return None

        valor_inicio = record_inicio.get("valor")
        valor_fin = record_fin.get("valor")

        if not valor_inicio or not valor_fin:
            return None

        return ((valor_fin - valor_inicio) / valor_inicio) * 100


# Convenience functions
def get_udi_actual() -> dict | None:
    """Get most recent UDI value"""
    return UDICatalog.get_actual()


def get_udi_por_fecha(fecha: str) -> dict | None:
    """Get UDI value for a specific date"""
    return UDICatalog.get_por_fecha(fecha)


def pesos_a_udis(pesos: float, fecha: str) -> float | None:
    """Convert pesos to UDIs"""
    return UDICatalog.pesos_a_udis(pesos, fecha)


def udis_a_pesos(udis: float, fecha: str) -> float | None:
    """Convert UDIs to pesos"""
    return UDICatalog.udis_a_pesos(udis, fecha)


# Export commonly used functions and classes
__all__ = [
    "UDICatalog",
    "get_udi_actual",
    "get_udi_por_fecha",
    "pesos_a_udis",
    "udis_a_pesos",
]
