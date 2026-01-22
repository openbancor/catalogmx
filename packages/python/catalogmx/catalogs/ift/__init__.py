"""
catalogmx.catalogs.ift - Catálogos del IFT

Catálogos del Instituto Federal de Telecomunicaciones:
- CodigosLADACatalog: Códigos LADA con mapeo geográfico INEGI
- OperadoresMovilesCatalog: Operadores de telefonía móvil
"""

from .codigos_lada import CodigosLADACatalog
from .operadores_moviles import OperadoresMovilesCatalog

__all__ = [
    "CodigosLADACatalog",
    "OperadoresMovilesCatalog",
]
