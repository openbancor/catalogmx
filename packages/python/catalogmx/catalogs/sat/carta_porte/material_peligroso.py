"""Catálogo c_MaterialPeligroso - Materiales Peligrosos ONU."""

from catalogmx.catalogs.sat.carta_porte._resolver_views import (
    material_peligroso_rows,
)


class MaterialPeligrosoCatalog:
    _data: list[dict] | None = None
    _by_un_number: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        if cls._data is None:
            cls._data = material_peligroso_rows()
            cls._by_un_number = {item["code"]: item for item in cls._data}

    @classmethod
    def get_material(cls, un_number: str) -> dict | None:
        """Obtiene material peligroso por número ONU."""
        cls._load_data()
        return cls._by_un_number.get(un_number)

    @classmethod
    def is_valid(cls, un_number: str) -> bool:
        """Verifica si un número ONU es válido."""
        return cls.get_material(un_number) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene el catálogo canónico completo de materiales peligrosos."""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_by_class(cls, hazard_class: str) -> list[dict]:
        """Obtiene materiales por clase de peligro principal (1-9)."""
        cls._load_data()
        return [m for m in cls._data if m["clase_riesgo"].startswith(hazard_class)]

    @classmethod
    def get_by_packing_group(cls, packing_group: str) -> list[dict]:
        """Retorna coincidencias por grupo de embalaje cuando existe esa dimensión.

        Carta Porte 3.1 no publica grupo de embalaje en
        ``c_MaterialPeligroso``. El método se conserva por compatibilidad, pero
        no inventa valores a partir del snapshot JSON histórico.
        """
        cls._load_data()
        return [
            material for material in cls._data if material.get("packing_group") == packing_group
        ]

    @classmethod
    def requires_special_handling(cls, un_number: str) -> bool:
        """Compatibilidad: no infiere manejo especial sin grupo SAT publicado."""
        material = cls.get_material(un_number)
        if not material:
            return False
        packing_group = material.get("packing_group")
        return packing_group in {"I", "II"}
