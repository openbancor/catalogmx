"""
Mexican National Catalogs

This module provides access to various Mexican national catalogs.
"""

from .placas_formatos import PlacasFormatosCatalog
from .salarios_minimos import SalariosMinimos
from .uma import UMACatalog
from .hoy_no_circula import HoyNoCirculaCatalog

__all__ = [
    'PlacasFormatosCatalog',
    'SalariosMinimos',
    'UMACatalog',
    'HoyNoCirculaCatalog',
]
