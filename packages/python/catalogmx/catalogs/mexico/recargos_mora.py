"""Effective Mexican federal tax late-payment surcharge rates."""

import json
from decimal import Decimal
from pathlib import Path


class RecargosMoraCatalog:
    """Versioned annual rates published for federal tax late payment."""

    _data: list[dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        if cls._data is None:
            shared_data_path = (
                Path(__file__).parent.parent.parent.parent.parent
                / "shared-data"
                / "mexico"
                / "recargos_mora.json"
            )
            with shared_data_path.open(encoding="utf-8") as file:
                cls._data = json.load(file)

    @classmethod
    def get_data(cls) -> list[dict]:
        """Return defensive copies of all versioned records."""
        cls._load_data()
        return [record.copy() for record in cls._data or []]

    @classmethod
    def get_por_anio(cls, anio: int) -> dict | None:
        """Return the record whose fiscal vigency covers ``anio``."""
        cls._load_data()
        for record in cls._data or []:
            if record["ejercicio"] == anio:
                return record.copy()
        return None

    @classmethod
    def get_tasa_mensual(cls, anio: int) -> Decimal | None:
        """Return the effective mora rate as a decimal fraction."""
        record = cls.get_por_anio(anio)
        return Decimal(record["tasa_mora_mensual"]) if record else None

    @classmethod
    def get_actual(cls) -> dict | None:
        """Return the record with the latest fiscal year in the dataset."""
        records = cls.get_data()
        return max(records, key=lambda record: record["ejercicio"], default=None)


def get_recargos_mora_por_anio(anio: int) -> dict | None:
    """Return the source-backed late-payment surcharge record for a year."""
    return RecargosMoraCatalog.get_por_anio(anio)


def get_tasa_recargos_mora(anio: int) -> Decimal | None:
    """Return the effective monthly late-payment rate for a year."""
    return RecargosMoraCatalog.get_tasa_mensual(anio)


__all__ = [
    "RecargosMoraCatalog",
    "get_recargos_mora_por_anio",
    "get_tasa_recargos_mora",
]
