"""
Catálogos INEGI

Catálogos incluidos:
- MunicipiosCatalog: Municipios de México
- MunicipiosCompletoCatalog: Catálogo completo de 2,469 municipios
- LocalidadesCatalog: Localidades con 1,000+ habitantes
- StateCatalog: Estados de México
"""

from .localidades import LocalidadesCatalog
from .municipios import MunicipiosCatalog
from .municipios_completo import MunicipiosCompletoCatalog
from .states import StateCatalog

__all__ = [
    "MunicipiosCatalog",
    "MunicipiosCompletoCatalog",
    "LocalidadesCatalog",
    "StateCatalog",
]
