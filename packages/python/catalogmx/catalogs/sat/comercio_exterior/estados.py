"""Catálogo c_Estado - Estados de USA y provincias de Canadá."""

from catalogmx.catalogs.sat.comercio_exterior._resolver_views import estado_rows


class EstadoCatalog:
    """Catálogo de estados/provincias de USA y Canadá para comercio exterior."""

    _estados_usa: list[dict] | None = None
    _provincias_canada: list[dict] | None = None
    _estado_by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga el subconjunto USA/Canadá desde el artifact canónico CCE 2.0."""
        if cls._estados_usa is None:
            data = estado_rows()
            cls._estados_usa = [item for item in data if item["country"] == "USA"]
            cls._provincias_canada = [item for item in data if item["country"] == "CAN"]
            cls._estado_by_code = {item["code"]: item for item in data}

    @classmethod
    def get_estado(cls, code: str, country: str | None = None) -> dict | None:
        """Obtiene un estado/provincia por código y país opcional."""
        cls._load_data()
        estado = cls._estado_by_code.get(code.upper())
        if estado and country and estado["country"] != country.upper():
            return None
        return estado

    @classmethod
    def get_estado_usa(cls, code: str) -> dict | None:
        """Obtiene un estado de USA por su código."""
        return cls.get_estado(code, "USA")

    @classmethod
    def get_provincia_canada(cls, code: str) -> dict | None:
        """Obtiene una provincia de Canadá por su código."""
        return cls.get_estado(code, "CAN")

    @classmethod
    def is_valid(cls, code: str, country: str | None = None) -> bool:
        """Verifica si un código de estado/provincia es válido."""
        return cls.get_estado(code, country) is not None

    @classmethod
    def get_all_usa(cls) -> list[dict]:
        """Retorna los 50 estados publicados por CCE 2.0 para USA."""
        cls._load_data()
        return cls._estados_usa.copy()

    @classmethod
    def get_all_canada(cls) -> list[dict]:
        """Retorna las 13 provincias/territorios publicados para Canadá."""
        cls._load_data()
        return cls._provincias_canada.copy()

    @classmethod
    def get_all(cls) -> list[dict]:
        """Retorna todos los estados/provincias USA y Canadá."""
        cls._load_data()
        return cls._estados_usa.copy() + cls._provincias_canada.copy()

    @classmethod
    def validate_foreign_address(cls, address_data: dict) -> dict:
        """Valida la subdivisión obligatoria para direcciones USA/Canadá."""
        errors = []
        pais = address_data.get("pais", "").upper()
        estado = address_data.get("estado", "").upper()

        if pais in ["USA", "CAN"]:
            if not estado:
                errors.append(f"Campo Estado es obligatorio para país {pais}")
            elif not cls.is_valid(estado, pais):
                errors.append(f"Estado {estado} no válido para país {pais}")

        return {"valid": len(errors) == 0, "errors": errors}
