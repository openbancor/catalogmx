"""Catálogos SAT Carta Porte 3.0"""

from .aeropuertos import AeropuertosCatalog
from .carreteras import CarreterasCatalog
from .config_autotransporte import ConfigAutotransporteCatalog
from .material_peligroso import MaterialPeligrosoCatalog
from .puertos_maritimos import PuertosMaritimos
from .tipo_embalaje import TipoEmbalajeCatalog
from .tipo_permiso import TipoPermisoCatalog

__all__ = [
    "AeropuertosCatalog",
    "PuertosMaritimos",
    "TipoPermisoCatalog",
    "ConfigAutotransporteCatalog",
    "TipoEmbalajeCatalog",
    "CarreterasCatalog",
    "MaterialPeligrosoCatalog",
]
