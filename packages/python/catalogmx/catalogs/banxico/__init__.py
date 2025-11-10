"""
catalogmx.catalogs.banxico - Catálogos de Banxico

Catálogos incluidos:
- BankCatalog: Bancos autorizados por Banxico
- UDICatalog: UDIs (Unidades de Inversión)
- InstitucionesFinancieras: Tipos de instituciones del sistema financiero
- MonedasDivisas: Monedas y divisas internacionales
- CodigosPlazaCatalog: Códigos de plaza para CLABE
"""

from .banks import BankCatalog
from .codigos_plaza import CodigosPlazaCatalog
from .instituciones_financieras import InstitucionesFinancieras
from .monedas_divisas import MonedasDivisas
from .udis import UDICatalog

__all__ = [
    'BankCatalog',
    'UDICatalog',
    'InstitucionesFinancieras',
    'MonedasDivisas',
    'CodigosPlazaCatalog',
]
