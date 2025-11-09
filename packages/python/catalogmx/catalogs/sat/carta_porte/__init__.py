"""Catálogos SAT Carta Porte 3.0"""

from .aeropuertos import AeropuertosCatalog
from .puertos_maritimos import PuertosMaritimos
from .tipo_permiso import TipoPermisoCatalog
from .config_autotransporte import ConfigAutotransporteCatalog
from .tipo_embalaje import TipoEmbalajeCatalog
from .carreteras import CarreterasCatalog
from .material_peligroso import MaterialPeligrosoCatalog

__all__ = [
    'AeropuertosCatalog',
    'PuertosMaritimos',
    'TipoPermisoCatalog',
    'ConfigAutotransporteCatalog',
    'TipoEmbalajeCatalog',
    'CarreterasCatalog',
    'MaterialPeligrosoCatalog',
]
