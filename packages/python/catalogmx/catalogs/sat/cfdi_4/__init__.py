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
- c_ClaveProdServ: Claves de productos y servicios (~52,000 códigos - SQLite)
"""

from .clave_prod_serv import ClaveProdServCatalog
from .clave_unidad import ClaveUnidadCatalog
from .exportacion import ExportacionCatalog
from .forma_pago import FormaPagoCatalog
from .impuesto import ImpuestoCatalog
from .metodo_pago import MetodoPagoCatalog
from .objeto_imp import ObjetoImpCatalog
from .regimen_fiscal import RegimenFiscalCatalog
from .tipo_comprobante import TipoComprobanteCatalog
from .tipo_relacion import TipoRelacionCatalog
from .uso_cfdi import UsoCFDICatalog

__all__ = [
    "RegimenFiscalCatalog",
    "UsoCFDICatalog",
    "FormaPagoCatalog",
    "MetodoPagoCatalog",
    "TipoComprobanteCatalog",
    "ImpuestoCatalog",
    "ExportacionCatalog",
    "TipoRelacionCatalog",
    "ObjetoImpCatalog",
    "ClaveUnidadCatalog",
    "ClaveProdServCatalog",
]
