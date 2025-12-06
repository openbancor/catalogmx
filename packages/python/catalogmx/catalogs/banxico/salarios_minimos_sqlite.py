"""
Salarios Mínimos Catalog - SQLite Backend

This module provides access to minimum wage values from Banco de México using a SQLite
database that can be automatically updated without requiring library releases.
"""

import sqlite3
from pathlib import Path

from catalogmx.data.updater import get_database_path


class SalariosMinimosCatalog:
    """
    Catalog of minimum wage values in Mexico

    Provides access to historical minimum wage data for both general zone and
    northern border free zone (zona libre de la frontera norte).

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
            "zona": row["zona"],
            "salario_diario": row["salario_diario"],
            "año": row["anio"],
            "mes": row["mes"],
        }

    @classmethod
    def get_data(cls) -> list[dict]:
        """
        Get all minimum wage data

        :return: List of all minimum wage records
        """
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row
        cursor = db.execute(
            """
            SELECT fecha, zona, salario_diario, anio, mes
            FROM salarios_minimos
            ORDER BY fecha, zona
            """
        )
        results = [cls._row_to_dict(row) for row in cursor.fetchall()]
        db.close()
        return results

    @classmethod
    def get_por_fecha(cls, fecha: str, zona: str = "general") -> dict | None:
        """
        Get minimum wage for a specific date and zone

        :param fecha: Date string in YYYY-MM-DD format
        :param zona: Zone ('general' or 'frontera_norte')
        :return: Minimum wage record or None if not found
        """
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row

        cursor = db.execute(
            """
            SELECT fecha, zona, salario_diario, anio, mes
            FROM salarios_minimos
            WHERE fecha <= ? AND zona = ?
            ORDER BY fecha DESC
            LIMIT 1
            """,
            (fecha, zona),
        )
        row = cursor.fetchone()
        db.close()

        if row:
            return cls._row_to_dict(row)
        return None

    @classmethod
    def get_actual(cls, zona: str = "general") -> dict | None:
        """
        Get current minimum wage

        :param zona: Zone ('general' or 'frontera_norte')
        :return: Latest minimum wage record
        """
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row

        cursor = db.execute(
            """
            SELECT fecha, zona, salario_diario, anio, mes
            FROM salarios_minimos
            WHERE zona = ?
            ORDER BY fecha DESC
            LIMIT 1
            """,
            (zona,),
        )
        row = cursor.fetchone()
        db.close()

        if row:
            return cls._row_to_dict(row)
        return None

    @classmethod
    def get_valor_actual(cls, zona: str = "general") -> float | None:
        """
        Get current minimum wage value

        :param zona: Zone ('general' or 'frontera_norte')
        :return: Current daily minimum wage or None
        """
        record = cls.get_actual(zona)
        return record.get("salario_diario") if record else None

    @classmethod
    def get_por_anio(cls, anio: int) -> list[dict]:
        """
        Get all minimum wage records for a specific year

        :param anio: Year (e.g., 2024)
        :return: List of minimum wage records for the year
        """
        db = sqlite3.connect(cls._get_db_path())
        db.row_factory = sqlite3.Row

        cursor = db.execute(
            """
            SELECT fecha, zona, salario_diario, anio, mes
            FROM salarios_minimos
            WHERE anio = ?
            ORDER BY fecha, zona
            """,
            (anio,),
        )
        results = [cls._row_to_dict(row) for row in cursor.fetchall()]
        db.close()
        return results

    @classmethod
    def calcular_variacion(
        cls, fecha_inicio: str, fecha_fin: str, zona: str = "general"
    ) -> float | None:
        """
        Calculate percentage variation between two dates

        :param fecha_inicio: Start date (YYYY-MM-DD)
        :param fecha_fin: End date (YYYY-MM-DD)
        :param zona: Zone ('general' or 'frontera_norte')
        :return: Percentage variation or None if values not found
        """
        record_inicio = cls.get_por_fecha(fecha_inicio, zona)
        record_fin = cls.get_por_fecha(fecha_fin, zona)

        if not record_inicio or not record_fin:
            return None

        salario_inicio = record_inicio.get("salario_diario")
        salario_fin = record_fin.get("salario_diario")

        if not salario_inicio or not salario_fin:
            return None

        return ((salario_fin - salario_inicio) / salario_inicio) * 100

    @classmethod
    def salario_mensual(cls, zona: str = "general", fecha: str | None = None) -> float | None:
        """
        Calculate monthly minimum wage (daily * 30.4)

        :param zona: Zone ('general' or 'frontera_norte')
        :param fecha: Date string or None for current
        :return: Monthly minimum wage or None
        """
        if fecha:
            record = cls.get_por_fecha(fecha, zona)
        else:
            record = cls.get_actual(zona)

        if not record:
            return None

        salario_diario = record.get("salario_diario")
        return salario_diario * 30.4 if salario_diario else None

    @classmethod
    def salario_anual(cls, zona: str = "general", fecha: str | None = None) -> float | None:
        """
        Calculate annual minimum wage (daily * 365)

        :param zona: Zone ('general' or 'frontera_norte')
        :param fecha: Date string or None for current
        :return: Annual minimum wage or None
        """
        if fecha:
            record = cls.get_por_fecha(fecha, zona)
        else:
            record = cls.get_actual(zona)

        if not record:
            return None

        salario_diario = record.get("salario_diario")
        return salario_diario * 365 if salario_diario else None


# Convenience functions
def get_salario_minimo_actual(zona: str = "general") -> dict | None:
    """Get current minimum wage"""
    return SalariosMinimosCatalog.get_actual(zona)


def get_salario_minimo_por_fecha(fecha: str, zona: str = "general") -> dict | None:
    """Get minimum wage for a specific date"""
    return SalariosMinimosCatalog.get_por_fecha(fecha, zona)


def get_valor_actual(zona: str = "general") -> float | None:
    """Get current minimum wage value"""
    return SalariosMinimosCatalog.get_valor_actual(zona)


def salario_mensual(zona: str = "general") -> float | None:
    """Get current monthly minimum wage"""
    return SalariosMinimosCatalog.salario_mensual(zona)


def salario_anual(zona: str = "general") -> float | None:
    """Get current annual minimum wage"""
    return SalariosMinimosCatalog.salario_anual(zona)


# Export commonly used functions and classes
__all__ = [
    "SalariosMinimosCatalog",
    "get_salario_minimo_actual",
    "get_salario_minimo_por_fecha",
    "get_valor_actual",
    "salario_mensual",
    "salario_anual",
]
