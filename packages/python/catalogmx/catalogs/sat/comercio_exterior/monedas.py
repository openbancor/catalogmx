"""Catálogo c_Moneda - Códigos de Monedas ISO 4217"""

import json
from pathlib import Path


class MonedaCatalog:
    """Catálogo de monedas para operaciones de comercio exterior"""

    _data: list[dict] | None = None
    _moneda_by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga los datos del catálogo desde el archivo JSON compartido"""
        if cls._data is None:
            current_file = Path(__file__)
            shared_data_path = (
                current_file.parent.parent.parent.parent.parent.parent
                / "shared-data"
                / "sat"
                / "comercio_exterior"
                / "monedas.json"
            )

            with open(shared_data_path, encoding="utf-8") as f:
                data = json.load(f)
                # Handle both list and dict formats
                cls._data = data if isinstance(data, list) else data.get("monedas", data)

            cls._moneda_by_code = {item["codigo"]: item for item in cls._data}

    @classmethod
    def get_moneda(cls, code: str) -> dict | None:
        """Obtiene una moneda por su código ISO 4217"""
        cls._load_data()
        return cls._moneda_by_code.get(code.upper())

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de moneda es válido"""
        return cls.get_moneda(code) is not None

    @classmethod
    def validate_conversion_usd(cls, cfdi_data: dict) -> dict:
        """
        Valida la conversión a USD según reglas SAT

        Args:
            cfdi_data: dict con 'moneda', 'total', 'tipo_cambio_usd', 'total_usd'

        Returns:
            dict con 'valid' (bool) y 'errors' (list)
        """
        errors = []
        moneda = cfdi_data.get("moneda", "").upper()
        tipo_cambio = cfdi_data.get("tipo_cambio_usd")
        total = cfdi_data.get("total")
        total_usd = cfdi_data.get("total_usd")

        # Validar que la moneda existe
        if not cls.is_valid(moneda):
            errors.append(f"Moneda {moneda} no válida")
            return {"valid": False, "errors": errors}

        # Si es USD, tipo_cambio debe ser 1
        if moneda == "USD":
            if tipo_cambio and tipo_cambio != 1:
                errors.append("Para USD, TipoCambioUSD debe ser 1")

            if total != total_usd:
                errors.append("Para USD, Total debe ser igual a TotalUSD")

        # Si NO es USD, tipo_cambio es obligatorio
        else:
            if not tipo_cambio:
                errors.append("TipoCambioUSD es obligatorio cuando Moneda != USD")

            # Validar cálculo de TotalUSD
            if tipo_cambio and total and total_usd:
                expected_total_usd = round(total * tipo_cambio, 2)
                if abs(total_usd - expected_total_usd) > 0.01:
                    errors.append(f"TotalUSD incorrecto. Esperado: {expected_total_usd}")

        return {"valid": len(errors) == 0, "errors": errors}

    @classmethod
    def get_all(cls) -> list[dict]:
        """Retorna todas las monedas"""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def search(cls, query: str) -> list[dict]:
        """Busca monedas por código, nombre o país"""
        cls._load_data()
        query_lower = query.lower()

        return [
            item
            for item in cls._data
            if (
                query_lower in item["codigo"].lower()
                or query_lower in item["nombre"].lower()
                or query_lower in item.get("pais", "").lower()
            )
        ]
