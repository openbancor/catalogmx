"""
catalogmx.catalogs.conapo - Catálogos de CONAPO

Catálogos del Consejo Nacional de Población:
- ZonasMetropolitanasCatalog: Metrópolis de México 2020 (SEDATU/INEGI/CONAPO)
- SistemaUrbanoNacionalCatalog: Sistema Urbano Nacional 2020
"""

from .sistema_urbano_nacional import SistemaUrbanoNacionalCatalog
from .zonas_metropolitanas import ZonasMetropolitanasCatalog

__all__ = [
    "ZonasMetropolitanasCatalog",
    "SistemaUrbanoNacionalCatalog",
]
