"""Effective Mexican federal tax late-payment surcharge rates."""

import json
from decimal import Decimal
from typing import TypedDict

from catalogmx.utils.shared_data import get_shared_data_path


class RecargosMoraRecord(TypedDict):
    """Versioned effective mora-rate record and its normative provenance."""

    ejercicio: int
    vigencia_inicio: str
    vigencia_fin: str
    tasa_base_lif: str
    tasa_mora_mensual: str
    unidad: str
    fuente_normativa: str
    fecha_publicacion: str
    url_fuente: str
    nota: str


class RecargosMoraCatalog:
    """Versioned annual rates published for federal tax late payment."""

    _data: list[RecargosMoraRecord] | None = None

    @classmethod
    def _load_data(cls) -> None:
        if cls._data is None:
            shared_data_path = get_shared_data_path("mexico", "recargos_mora.json")
            with shared_data_path.open(encoding="utf-8") as file:
                data = json.load(file)
            records = (
                data
                if isinstance(data, list)
                else data.get("items") if isinstance(data, dict) else None
            )
            if not isinstance(records, list):
                raise ValueError("recargos_mora.json must contain a list or an items list")
            cls._data = records

    @classmethod
    def get_data(cls) -> list[RecargosMoraRecord]:
        """Return defensive copies of all versioned records."""
        cls._load_data()
        return [record.copy() for record in cls._data or []]

    @classmethod
    def get_por_anio(cls, anio: int) -> RecargosMoraRecord | None:
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
    def get_actual(cls) -> RecargosMoraRecord | None:
        """Return the record with the latest fiscal year in the dataset."""
        records = cls.get_data()
        return max(records, key=lambda record: record["ejercicio"], default=None)


def get_recargos_mora_por_anio(anio: int) -> RecargosMoraRecord | None:
    """Return the source-backed late-payment surcharge record for a year."""
    return RecargosMoraCatalog.get_por_anio(anio)


def get_tasa_recargos_mora(anio: int) -> Decimal | None:
    """Return the effective monthly late-payment rate for a year."""
    return RecargosMoraCatalog.get_tasa_mensual(anio)


__all__ = [
    "RecargosMoraRecord",
    "RecargosMoraCatalog",
    "get_recargos_mora_por_anio",
    "get_tasa_recargos_mora",
]
