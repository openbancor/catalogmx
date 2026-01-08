"""
Catálogos INEGI

Catálogos incluidos:
- MunicipiosCatalog: Municipios de México
- MunicipiosCompletoCatalog: Catálogo completo de 2,469 municipios
- LocalidadesCatalog: Localidades con 1,000+ habitantes
- StateCatalog: Estados de México
- SCIANCatalog: Sistema de Clasificación Industrial de América del Norte
"""

from .localidades import LocalidadesCatalog
from .municipios import MunicipiosCatalog
from .municipios_completo import MunicipiosCompletoCatalog
from .scian import SCIANCatalog
from .states import StateCatalog

# Aliases for convenience
States = StateCatalog
Estados = StateCatalog
Municipios = MunicipiosCatalog
Localidades = LocalidadesCatalog
SCIAN = SCIANCatalog

__all__ = [
    # Main classes
    "MunicipiosCatalog",
    "MunicipiosCompletoCatalog",
    "LocalidadesCatalog",
    "StateCatalog",
    "SCIANCatalog",
    # Aliases
    "States",
    "Estados",
    "Municipios",
    "Localidades",
    "SCIAN",
]
