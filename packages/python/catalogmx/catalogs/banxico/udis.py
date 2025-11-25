"""
UDI (Unidades de Inversión) Catalog

This module provides access to UDI values from Banco de México.
UDIs are inflation-indexed investment units used in Mexico.
"""

import json
from datetime import datetime
from pathlib import Path


class UDICatalog:
    """
    Catalog of UDI (Unidades de Inversión) values

    UDIs are inflation-indexed investment units maintained by Banco de México.
    They are commonly used for mortgage loans and other long-term financial obligations.
    """

    _data: list[dict] | None = None
    _by_fecha: dict[str, dict] | None = None
    _mensual: dict[str, dict] | None = None
    _anual: dict[int, dict] | None = None
    _daily: list[dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Load UDI data from JSON file"""
        if cls._data is None:
            # Path: catalogmx/packages/python/catalogmx/catalogs/banxico/udis.py
            # Target: catalogmx/packages/shared-data/banxico/udis.json
            current_file = Path(__file__)
            shared_data_path = (
                current_file.parent.parent.parent.parent.parent
                / "shared-data"
                / "banxico"
                / "udis.json"
            )

            with open(shared_data_path, encoding="utf-8") as f:
                cls._data = json.load(f)

        if cls._by_fecha is not None:
            return

        cls._by_fecha = {}
        cls._mensual = {}
        cls._anual = {}
        daily: list[dict] = []

        for record in cls._data:
            fecha = record.get("fecha")
            if not fecha:
                continue

            tipo = record.get("tipo", "")

            existing = cls._by_fecha.get(fecha)
            if existing is None or (
                tipo in ("diario", "oficial_banxico")
                and existing.get("tipo") not in ("diario", "oficial_banxico")
            ):
                cls._by_fecha[fecha] = record

            # Treat "oficial_banxico" as daily data (it is)
            if tipo in ("diario", "oficial_banxico"):
                daily.append(record)
            elif tipo == "promedio_mensual":
                key = f"{record.get('año')}-{int(record.get('mes', 0)):02d}"
                cls._mensual[key] = record
            elif tipo == "promedio_anual":
                cls._anual[int(record.get("año"))] = record

        daily.sort(key=lambda r: r["fecha"])
        cls._daily = daily

    @classmethod
    def get_data(cls) -> list[dict]:
        """
        Get all UDI data

        :return: List of all UDI records
        """
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def _get_by_fecha(cls, fecha: str) -> dict | None:
        cls._load_data()
        record = cls._by_fecha.get(fecha)
        if record:
            return record

        try:
            anio, mes, _dia = fecha.split("-")
            mensual = cls._mensual.get(f"{int(anio)}-{int(mes):02d}") if cls._mensual else None
            return mensual
        except ValueError:
            return None

    @classmethod
    def get_por_fecha(cls, fecha: str) -> dict | None:
        """
        Get UDI value for a specific date

        :param fecha: Date string in YYYY-MM-DD format
        :return: UDI record or None if not found
        """
        record = cls._get_by_fecha(fecha)
        return record.copy() if record else None

    @classmethod
    def get_por_mes(cls, anio: int, mes: int) -> dict | None:
        """
        Get monthly average UDI value

        :param anio: Year (e.g., 2024)
        :param mes: Month (1-12)
        :return: UDI record with monthly average or None if not found
        """
        cls._load_data()
        key = f"{anio}-{mes:02d}"
        record = cls._mensual.get(key) if cls._mensual else None
        return record.copy() if record else None

    @classmethod
    def get_promedio_anual(cls, anio: int) -> dict | None:
        """
        Get annual average UDI value

        :param anio: Year (e.g., 2024)
        :return: UDI record with annual average or None if not found
        """
        cls._load_data()

        record = cls._anual.get(anio) if cls._anual else None
        return record.copy() if record else None

    @classmethod
    def get_por_anio(cls, anio: int) -> list[dict]:
        """Return the daily UDI series for a given year."""
        cls._load_data()

        source = (
            cls._daily
            if cls._daily
            else [r for r in cls._data if r.get("tipo") == "promedio_mensual"]
        )
        return [record.copy() for record in source if record.get("año") == anio]

    @classmethod
    def get_actual(cls) -> dict | None:
        """
        Get most recent UDI value

        :return: Latest UDI record
        """
        cls._load_data()

        if cls._daily:
            return cls._daily[-1].copy()

        if not cls._data:
            return None

        record = max(cls._data, key=lambda r: r.get("fecha", ""), default=None)
        return record.copy() if record else None

    @classmethod
    def _get_valor_cercano(cls, fecha: str) -> dict | None:
        cls._load_data()
        objetivo = datetime.fromisoformat(fecha)

        candidatos = (
            cls._daily
            if cls._daily
            else [r for r in cls._data if r.get("tipo") == "promedio_mensual"]
        )
        if not candidatos:
            return None

        def _diff(record: dict) -> float:
            return abs((datetime.fromisoformat(record["fecha"]) - objetivo).total_seconds())

        return min(candidatos, key=_diff)

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
        record_inicio = cls.get_por_fecha(fecha_inicio) or cls._get_valor_cercano(fecha_inicio)
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
    record = UDICatalog.get_actual()
    return record.copy() if record else None


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
