"""
Salarios Mínimos Catalog

This module provides access to minimum wage data from Banco de México.
Includes different zones: general and northern border area.
"""

import json
from pathlib import Path


class SalariosMinimosCatalog:
    """
    Catalog of minimum wage values

    Minimum wages are established by the Mexican government and vary by zone.
    The northern border area has higher minimum wages.
    """

    _data: list[dict] | None = None
    _by_fecha_zona: dict[str, dict] | None = None
    _by_anio_zona: dict[str, list[dict]] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Load minimum wage data from JSON file"""
        if cls._data is None:
            current_file = Path(__file__)
            shared_data_path = (
                current_file.parent.parent.parent.parent.parent
                / "shared-data"
                / "banxico"
                / "salarios_minimos.json"
            )

            with open(shared_data_path, encoding="utf-8") as f:
                cls._data = json.load(f)

        if cls._by_fecha_zona is not None:
            return

        cls._by_fecha_zona = {}
        cls._by_anio_zona = {}

        for record in cls._data:
            fecha = record.get("fecha")
            zona = record.get("zona", "general")

            if fecha:
                key = f"{fecha}_{zona}"
                cls._by_fecha_zona[key] = record

            anio = record.get("año")
            if anio:
                key_anio = f"{anio}_{zona}"
                if key_anio not in cls._by_anio_zona:
                    cls._by_anio_zona[key_anio] = []
                cls._by_anio_zona[key_anio].append(record)

        # Sort by date within each year/zone
        for key in cls._by_anio_zona:
            cls._by_anio_zona[key].sort(key=lambda r: r["fecha"])

    @classmethod
    def get_data(cls) -> list[dict]:
        """
        Get all minimum wage data

        :return: List of all minimum wage records
        """
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_por_fecha_zona(cls, fecha: str, zona: str = "general") -> dict | None:
        """
        Get minimum wage for a specific date and zone

        :param fecha: Date string in YYYY-MM-DD format
        :param zona: Zone ('general' or 'frontera_norte')
        :return: Minimum wage record or None if not found
        """
        cls._load_data()
        key = f"{fecha}_{zona}"
        record = cls._by_fecha_zona.get(key)
        return record.copy() if record else None

    @classmethod
    def get_por_anio_zona(cls, anio: int, zona: str = "general") -> list[dict]:
        """
        Get all minimum wages for a specific year and zone

        :param anio: Year (e.g., 2024)
        :param zona: Zone ('general' or 'frontera_norte')
        :return: List of minimum wage records for the year and zone
        """
        cls._load_data()
        key = f"{anio}_{zona}"
        records = cls._by_anio_zona.get(key, [])
        return [record.copy() for record in records]

    @classmethod
    def get_actual_zona(cls, zona: str = "general") -> dict | None:
        """
        Get most recent minimum wage for a zone

        :param zona: Zone ('general' or 'frontera_norte')
        :return: Latest minimum wage record for the zone
        """
        cls._load_data()

        if not cls._data:
            return None

        # Filter by zone and get the most recent
        zone_records = [r for r in cls._data if r.get("zona") == zona]
        if not zone_records:
            return None

        record = max(zone_records, key=lambda r: r.get("fecha", ""), default=None)
        return record.copy() if record else None

    @classmethod
    def get_actual_general(cls) -> dict | None:
        """Get most recent minimum wage for general zone"""
        return cls.get_actual_zona("general")

    @classmethod
    def get_actual_frontera(cls) -> dict | None:
        """Get most recent minimum wage for northern border zone"""
        return cls.get_actual_zona("frontera_norte")

    @classmethod
    def get_salario_actual_zona(cls, zona: str = "general") -> float | None:
        """
        Get current minimum wage value for a zone

        :param zona: Zone ('general' or 'frontera_norte')
        :return: Current minimum wage or None
        """
        record = cls.get_actual_zona(zona)
        return record.get("salario_minimo") if record else None

    @classmethod
    def calcular_incremento(
        cls, fecha_inicio: str, fecha_fin: str, zona: str = "general"
    ) -> float | None:
        """
        Calculate wage increase percentage between two dates

        :param fecha_inicio: Start date (YYYY-MM-DD)
        :param fecha_fin: End date (YYYY-MM-DD)
        :param zona: Zone ('general' or 'frontera_norte')
        :return: Percentage increase or None if values not found
        """
        record_inicio = cls.get_por_fecha_zona(fecha_inicio, zona)
        record_fin = cls.get_por_fecha_zona(fecha_fin, zona)

        if not record_inicio or not record_fin:
            return None

        salario_inicio = record_inicio.get("salario_minimo")
        salario_fin = record_fin.get("salario_minimo")

        if not salario_inicio or not salario_fin:
            return None

        return ((salario_fin - salario_inicio) / salario_inicio) * 100

    @classmethod
    def get_promedio_anual_zona(cls, anio: int, zona: str = "general") -> float | None:
        """
        Calculate annual average minimum wage for a zone

        :param anio: Year (e.g., 2024)
        :param zona: Zone ('general' or 'frontera_norte')
        :return: Annual average minimum wage or None if no data
        """
        records = cls.get_por_anio_zona(anio, zona)
        if not records:
            return None

        salaries = [r.get("salario_minimo") for r in records if r.get("salario_minimo")]
        return sum(salaries) / len(salaries) if salaries else None


# Convenience functions
def get_salario_minimo_actual_general() -> dict | None:
    """Get most recent minimum wage for general zone"""
    return SalariosMinimosCatalog.get_actual_general()


def get_salario_minimo_actual_frontera() -> dict | None:
    """Get most recent minimum wage for northern border zone"""
    return SalariosMinimosCatalog.get_actual_frontera()


def get_salario_minimo_por_fecha_zona(fecha: str, zona: str = "general") -> dict | None:
    """Get minimum wage for a specific date and zone"""
    return SalariosMinimosCatalog.get_por_fecha_zona(fecha, zona)


# Export commonly used functions and classes
__all__ = [
    "SalariosMinimosCatalog",
    "get_salario_minimo_actual_general",
    "get_salario_minimo_actual_frontera",
    "get_salario_minimo_por_fecha_zona",
]
