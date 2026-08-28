"""Catálogo de Tasa o Cuota (SAT CFDI 4.0)."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from catalogmx.catalogs.sat.cfdi_4._resolver_views import tasa_o_cuota_rows

_IMPUESTO_ALIASES = {
    "001": "ISR",
    "002": "IVA",
    "003": "IEPS",
}


class TasaOCuota:
    """Consulta reglas SAT de tasa o cuota desde el dataset canónico CFDI 4.0."""

    _data: list[dict[str, Any]] | None = None

    @classmethod
    def _load_data(cls) -> list[dict[str, Any]]:
        if cls._data is None:
            cls._data = tasa_o_cuota_rows()
        return cls._data

    @classmethod
    def get_data(cls) -> list[dict[str, Any]]:
        """Return normalized fixed/range tax-rate rules.

        Decimal values remain exact strings from the canonical SQLite artifact.
        For ``Fijo`` rows, ``valor_mínimo`` is ``None`` and
        ``valor_máximo`` is the fixed value. For ``Rango`` rows, both limits
        are populated.
        """
        return cls._load_data()

    @staticmethod
    def _decimal_matches(actual: object, expected: object) -> bool:
        if expected is None:
            return True
        if actual is None:
            return False
        try:
            return Decimal(str(actual)) == Decimal(str(expected))
        except InvalidOperation:
            return str(actual) == str(expected)

    @staticmethod
    def _impuesto_matches(actual: object, expected: object) -> bool:
        if expected is None:
            return True
        actual_text = str(actual or "").upper()
        expected_text = str(expected or "").upper()
        expected_text = _IMPUESTO_ALIASES.get(expected_text, expected_text)
        return actual_text == expected_text

    @staticmethod
    def _factor_matches(actual: object, expected: object) -> bool:
        if expected is None:
            return True
        return str(actual or "").casefold() == str(expected or "").casefold()

    @classmethod
    def get_by_range_and_tax(
        cls,
        valor_min: object,
        valor_max: object,
        impuesto: object,
        factor: object,
        trasladado: bool | None,
        retenido: bool | None,
    ) -> list[dict[str, Any]]:
        """Filter tax-rate rules by the provided criteria.

        ``None`` means that criterion is not filtered. Decimal criteria accept
        strings, ints, floats or ``Decimal`` values and are compared through
        ``Decimal`` rather than binary floating point. ``impuesto`` accepts the
        canonical names (``ISR``, ``IVA``, ``IEPS``) or SAT codes
        (``001``, ``002``, ``003``).
        """
        return [
            item
            for item in cls.get_data()
            if cls._decimal_matches(item.get("valor_mínimo"), valor_min)
            and cls._decimal_matches(item.get("valor_máximo"), valor_max)
            and cls._impuesto_matches(item.get("impuesto"), impuesto)
            and cls._factor_matches(item.get("factor"), factor)
            and (trasladado is None or bool(item.get("trasladado")) is bool(trasladado))
            and (retenido is None or bool(item.get("retenido")) is bool(retenido))
        ]
