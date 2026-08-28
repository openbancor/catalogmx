"""Catálogo c_Moneda - monedas reutilizadas de CFDI 4.0."""

from catalogmx.catalogs.sat.comercio_exterior._cfdi_views import moneda_rows


class MonedaCatalog:
    """Catálogo de monedas para operaciones de comercio exterior."""

    _data: list[dict] | None = None
    _moneda_by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga el catálogo CFDI compartido mediante DatasetResolver."""
        if cls._data is None:
            cls._data = moneda_rows()
            cls._moneda_by_code = {item["codigo"]: item for item in cls._data}

    @classmethod
    def get_moneda(cls, code: str) -> dict | None:
        """Obtiene una moneda por su código ISO 4217/SAT."""
        cls._load_data()
        return cls._moneda_by_code.get(code.upper())

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de moneda es válido."""
        return cls.get_moneda(code) is not None

    @classmethod
    def validate_conversion_usd(cls, cfdi_data: dict) -> dict:
        """Valida la conversión a USD según las reglas históricas de CatalogMX."""
        errors = []
        moneda = cfdi_data.get("moneda", "").upper()
        tipo_cambio = cfdi_data.get("tipo_cambio_usd")
        total = cfdi_data.get("total")
        total_usd = cfdi_data.get("total_usd")

        if not cls.is_valid(moneda):
            errors.append(f"Moneda {moneda} no válida")
            return {"valid": False, "errors": errors}

        if moneda == "USD":
            if tipo_cambio and tipo_cambio != 1:
                errors.append("Para USD, TipoCambioUSD debe ser 1")
            if total != total_usd:
                errors.append("Para USD, Total debe ser igual a TotalUSD")
        else:
            if not tipo_cambio:
                errors.append("TipoCambioUSD es obligatorio cuando Moneda != USD")
            if tipo_cambio and total and total_usd:
                expected_total_usd = round(total * tipo_cambio, 2)
                if abs(total_usd - expected_total_usd) > 0.01:
                    errors.append(f"TotalUSD incorrecto. Esperado: {expected_total_usd}")

        return {"valid": len(errors) == 0, "errors": errors}

    @classmethod
    def get_all(cls) -> list[dict]:
        """Retorna las monedas publicadas en el catálogo compartido CFDI 4.0."""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def search(cls, query: str) -> list[dict]:
        """Busca monedas por código o nombre SAT.

        El antiguo país de conveniencia no es un campo autoritativo de
        ``cfdi_40_monedas`` y ya no participa en la búsqueda runtime.
        """
        cls._load_data()
        query_lower = query.lower()
        return [
            item
            for item in cls._data
            if query_lower in item["codigo"].lower() or query_lower in item["nombre"].lower()
        ]
