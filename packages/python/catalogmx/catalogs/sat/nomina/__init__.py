"""SAT Nómina 1.2 catalogs."""

from .banco import BancoCatalog
from .origen_recurso import OrigenRecursoCatalog
from .periodicidad_pago import PeriodicidadPagoCatalog
from .riesgo_puesto import RiesgoPuestoCatalog
from .tipo_contrato import TipoContratoCatalog
from .tipo_deduccion import TipoDeduccionCatalog
from .tipo_horas import TipoHorasCatalog
from .tipo_incapacidad import TipoIncapacidadCatalog
from .tipo_jornada import TipoJornadaCatalog
from .tipo_nomina import TipoNominaCatalog
from .tipo_otro_pago import TipoOtroPagoCatalog
from .tipo_percepcion import TipoPercepcionCatalog
from .tipo_regimen import TipoRegimenCatalog

__all__ = [
    "BancoCatalog",
    "OrigenRecursoCatalog",
    "PeriodicidadPagoCatalog",
    "RiesgoPuestoCatalog",
    "TipoContratoCatalog",
    "TipoDeduccionCatalog",
    "TipoHorasCatalog",
    "TipoIncapacidadCatalog",
    "TipoJornadaCatalog",
    "TipoNominaCatalog",
    "TipoOtroPagoCatalog",
    "TipoPercepcionCatalog",
    "TipoRegimenCatalog",
]
