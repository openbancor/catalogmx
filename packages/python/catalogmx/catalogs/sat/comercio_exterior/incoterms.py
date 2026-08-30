"""Catálogo c_INCOTERM para Comercio Exterior 2.0."""

from catalogmx.catalogs.sat.comercio_exterior._resolver_views import incoterm_rows


class IncotermsValidator:
    """Validador y catálogo de INCOTERMS para Comercio Exterior."""

    _data: list[dict] | None = None
    _incoterm_by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga códigos/textos SAT y metadata de conveniencia CatalogMX."""
        if cls._data is None:
            cls._data = incoterm_rows()
            cls._incoterm_by_code = {item["code"]: item for item in cls._data}

    @classmethod
    def get_incoterm(cls, code: str) -> dict | None:
        """Obtiene un INCOTERM por su código."""
        cls._load_data()
        return cls._incoterm_by_code.get(code.upper())

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código INCOTERM es válido."""
        return cls.get_incoterm(code) is not None

    @classmethod
    def is_valid_for_transport(cls, code: str, transport_type: str) -> bool:
        """Verifica si un INCOTERM aplica al tipo de transporte indicado."""
        incoterm = cls.get_incoterm(code)
        if not incoterm:
            return False
        if transport_type == "any" or incoterm["transport_mode"] == "any":
            return True
        return transport_type in incoterm.get("suitable_for", [])

    @classmethod
    def get_multimodal_incoterms(cls) -> list[str]:
        """Retorna los INCOTERMS de cualquier modo de transporte."""
        cls._load_data()
        return [item["code"] for item in cls._data if item["transport_mode"] == "any"]

    @classmethod
    def get_maritime_incoterms(cls) -> list[str]:
        """Retorna los INCOTERMS exclusivos de transporte marítimo."""
        cls._load_data()
        return [item["code"] for item in cls._data if item["transport_mode"] == "maritime"]

    @classmethod
    def seller_pays_freight(cls, code: str) -> bool:
        """Indica si la regla de conveniencia asigna el flete al vendedor."""
        incoterm = cls.get_incoterm(code)
        return incoterm.get("seller_pays_freight", False) if incoterm else False

    @classmethod
    def seller_pays_insurance(cls, code: str) -> bool:
        """Indica si la regla de conveniencia asigna seguro al vendedor."""
        incoterm = cls.get_incoterm(code)
        return incoterm.get("seller_pays_insurance", False) if incoterm else False

    @classmethod
    def get_all(cls) -> list[dict]:
        """Retorna todos los INCOTERMS publicados por CCE 2.0."""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def search(cls, query: str) -> list[dict]:
        """Busca por código, nombre de conveniencia o texto oficial SAT."""
        cls._load_data()
        query_lower = query.lower()
        return [
            item
            for item in cls._data
            if (
                query_lower in item["code"].lower()
                or query_lower in item["name"].lower()
                or query_lower in item["name_es"].lower()
                or query_lower in item["description"].lower()
            )
        ]
