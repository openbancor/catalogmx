"""Catálogos SAT Nómina 1.2"""

from .banco import BancoCatalog
from .periodicidad_pago import PeriodicidadPagoCatalog
from .riesgo_puesto import RiesgoPuestoCatalog
from .tipo_contrato import TipoContratoCatalog
from .tipo_jornada import TipoJornadaCatalog
from .tipo_nomina import TipoNominaCatalog
from .tipo_regimen import TipoRegimenCatalog

__all__ = [
    'TipoNominaCatalog',
    'TipoContratoCatalog',
    'TipoJornadaCatalog',
    'TipoRegimenCatalog',
    'PeriodicidadPagoCatalog',
    'RiesgoPuestoCatalog',
    'BancoCatalog',
]
