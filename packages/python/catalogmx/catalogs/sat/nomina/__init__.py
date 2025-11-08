"""Catálogos SAT Nómina 1.2"""

from .tipo_nomina import TipoNominaCatalog
from .tipo_contrato import TipoContratoCatalog
from .tipo_jornada import TipoJornadaCatalog
from .tipo_regimen import TipoRegimenCatalog
from .periodicidad_pago import PeriodicidadPagoCatalog
from .riesgo_puesto import RiesgoPuestoCatalog
from .banco import BancoCatalog

__all__ = [
    'TipoNominaCatalog',
    'TipoContratoCatalog',
    'TipoJornadaCatalog',
    'TipoRegimenCatalog',
    'PeriodicidadPagoCatalog',
    'RiesgoPuestoCatalog',
    'BancoCatalog',
]
