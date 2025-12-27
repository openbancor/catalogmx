"""
catalogmx.catalogs.banxico - Catálogos de Banxico

Catálogos incluidos:
- BankCatalog: Bancos autorizados por Banxico
- UDICatalog: UDIs (Unidades de Inversión)
- TipoCambioUSDCatalog: Tipo de cambio USD/MXN FIX
- TIIE28Catalog: TIIE 28 días
- CETES28Catalog: CETES 28 días
- InflacionAnualCatalog: Inflación anual (INPC)
- SalariosMinimosCatalog: Salarios mínimos por zona
- InstitucionesFinancieras: Tipos de instituciones del sistema financiero
- MonedasDivisas: Monedas y divisas internacionales
- CodigosPlazaCatalog: Códigos de plaza para CLABE
"""

# Static catalogs (JSON-based, don't change frequently)
from .banks import BankCatalog
from .cetes_sqlite import CETESCatalog as CETES28Catalog
from .codigos_plaza import CodigosPlazaCatalog
from .inflacion_sqlite import InflacionCatalog as InflacionAnualCatalog
from .instituciones_financieras import InstitucionesFinancieras
from .monedas_divisas import MonedasDivisas
from .salarios_minimos_sqlite import SalariosMinimosCatalog
from .tiie_sqlite import TIIECatalog as TIIE28Catalog
from .tipo_cambio_usd_sqlite import TipoCambioUSDCatalog

# Dynamic catalogs (SQLite-based, auto-updating)
from .udis_sqlite import UDICatalog

__all__ = [
    "BankCatalog",
    "CETES28Catalog",
    "CodigosPlazaCatalog",
    "InflacionAnualCatalog",
    "InstitucionesFinancieras",
    "MonedasDivisas",
    "SalariosMinimosCatalog",
    "TIIE28Catalog",
    "TipoCambioUSDCatalog",
    "UDICatalog",
]
