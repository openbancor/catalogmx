"""
Mexican National Catalogs

This module provides access to various Mexican national catalogs.
"""

from .hoy_no_circula import HoyNoCirculaCatalog
from .placas_formatos import PlacasFormatosCatalog
from .salarios_minimos import SalariosMinimos
from .uma import UMACatalog

__all__ = [
    "PlacasFormatosCatalog",
    "SalariosMinimos",
    "UMACatalog",
    "HoyNoCirculaCatalog",
]
