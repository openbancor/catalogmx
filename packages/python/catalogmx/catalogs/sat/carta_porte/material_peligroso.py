"""Catálogo c_MaterialPeligroso - Materiales Peligrosos ONU"""
import json
from pathlib import Path

class MaterialPeligrosoCatalog:
    _data: list[dict] | None = None
    _by_un_number: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        if cls._data is None:
            path = Path(__file__).parent.parent.parent.parent.parent.parent / 'shared-data' / 'sat' / 'carta_porte_3' / 'material_peligroso.json'
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['materiales']
            cls._by_un_number = {item['un_number']: item for item in cls._data}

    @classmethod
    def get_material(cls, un_number: str) -> dict | None:
        """Obtiene material peligroso por número ONU"""
        cls._load_data()
        return cls._by_un_number.get(un_number)

    @classmethod
    def is_valid(cls, un_number: str) -> bool:
        """Verifica si un número ONU es válido"""
        return cls.get_material(un_number) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todos los materiales peligrosos"""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_by_class(cls, hazard_class: str) -> list[dict]:
        """Obtiene materiales por clase de peligro (1-9)"""
        cls._load_data()
        return [m for m in cls._data if m['class'].startswith(hazard_class)]

    @classmethod
    def get_by_packing_group(cls, packing_group: str) -> list[dict]:
        """Obtiene materiales por grupo de embalaje (I, II, III)"""
        cls._load_data()
        return [m for m in cls._data if m.get('packing_group') and packing_group in m['packing_group']]

    @classmethod
    def requires_special_handling(cls, un_number: str) -> bool:
        """Verifica si requiere manejo especial (grupos I y II)"""
        material = cls.get_material(un_number)
        if not material or not material.get('packing_group'):
            return False
        return 'I' in material['packing_group'] or 'II' in material['packing_group']
