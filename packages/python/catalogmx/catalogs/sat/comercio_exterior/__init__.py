"""
Catálogos del SAT para Complemento de Comercio Exterior 2.0

Este módulo contiene los catálogos oficiales del SAT necesarios para la emisión
de CFDI con Complemento de Comercio Exterior versión 2.0 (vigente desde enero 18, 2024).

Catálogos incluidos:
- c_INCOTERM: 11 Incoterms 2020
- c_ClavePedimento: ~40 claves de pedimento aduanero
- c_UnidadAduana: ~30 unidades de medida aduanera
- c_MotivoTraslado: 6 motivos de traslado
- c_RegistroIdentTribReceptor: Tipos de identificación tributaria
- c_Moneda: ~180 monedas ISO 4217
- c_Pais: ~250 países ISO 3166-1
- c_Estado: Estados USA y provincias Canadá
- c_FraccionArancelaria: ~20,000 fracciones arancelarias TIGIE/NICO
"""

from .claves_pedimento import ClavePedimentoCatalog
from .estados import EstadoCatalog
from .incoterms import IncotermsValidator
from .monedas import MonedaCatalog
from .motivos_traslado import MotivoTrasladoCatalog
from .paises import PaisCatalog
from .registro_ident_trib import RegistroIdentTribCatalog
from .unidades_aduana import UnidadAduanaCatalog
from .validator import ComercioExteriorValidator

__all__ = [
    'IncotermsValidator',
    'ClavePedimentoCatalog',
    'UnidadAduanaCatalog',
    'MotivoTrasladoCatalog',
    'RegistroIdentTribCatalog',
    'MonedaCatalog',
    'PaisCatalog',
    'EstadoCatalog',
    'ComercioExteriorValidator',
]
