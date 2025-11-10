"""
Catálogos del SAT para CFDI 4.0

Catálogos incluidos:
- c_RegimenFiscal: Regímenes fiscales
- c_UsoCFDI: Usos del CFDI
- c_FormaPago: Formas de pago
- c_MetodoPago: Método de pago
- c_TipoComprobante: Tipos de comprobante
- c_Impuesto: Impuestos
- c_Exportacion: Claves de exportación
- c_TipoRelacion: Tipos de relación entre CFDI
- c_ObjetoImp: Objeto de impuesto
- c_ClaveUnidad: Claves de unidad de medida (~2,400 unidades)
"""

from .regimen_fiscal import RegimenFiscalCatalog
from .uso_cfdi import UsoCFDICatalog
from .forma_pago import FormaPagoCatalog
from .metodo_pago import MetodoPagoCatalog
from .tipo_comprobante import TipoComprobanteCatalog
from .impuesto import ImpuestoCatalog
from .exportacion import ExportacionCatalog
from .tipo_relacion import TipoRelacionCatalog
from .objeto_imp import ObjetoImpCatalog
from .clave_unidad import ClaveUnidadCatalog

__all__ = [
    'RegimenFiscalCatalog',
    'UsoCFDICatalog',
    'FormaPagoCatalog',
    'MetodoPagoCatalog',
    'TipoComprobanteCatalog',
    'ImpuestoCatalog',
    'ExportacionCatalog',
    'TipoRelacionCatalog',
    'ObjetoImpCatalog',
    'ClaveUnidadCatalog',
]
