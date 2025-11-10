"""Catálogo de Tasa o Cuota (SAT)"""
import json
from pathlib import Path


class TasaOCuota:
    _data = None

    @classmethod
    def _load_data(cls):
        if cls._data is None:
            path = Path(__file__).parent.parent.parent.parent.parent / 'shared-data' / 'sat' / 'cfdi_4.0' / 'c_TasaOCuota.json'
            with open(path, encoding='utf-8') as f:
                json_data = json.load(f)
                # This catalog has a more complex structure, let's index by a combination of fields
                cls._data = json_data['data']
        return cls._data

    @classmethod
    def get_data(cls):
        return cls._load_data()

    @classmethod
    def get_by_range_and_tax(cls, valor_min, valor_max, impuesto, factor, trasladado, retenido):
        """Finds a rate based on multiple criteria."""
        data = cls.get_data()
        # This is a placeholder for a more complex search logic
        return [
            item for item in data
            if item.get('valor_mínimo') == valor_min and
               item.get('valor_máximo') == valor_max and
               item.get('impuesto') == impuesto and
               item.get('factor') == factor
        ]
