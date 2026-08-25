"""
Catálogo de Códigos de Plaza CLABE
=====================================

Códigos de plaza para el sistema CLABE (Clave Bancaria Estandarizada).
Los códigos de plaza son identificadores de 3 dígitos que indican la ubicación
geográfica de las sucursales bancarias en México.

Fuente: Banco de México (BANXICO) / Sistema de Pagos Electrónicos Interbancarios (SPEI)
"""

import json
from typing import TypedDict

from catalogmx.utils.shared_data import get_shared_data_path

try:
    from unidecode import unidecode
except ImportError:
    # Fallback if unidecode not available
    def unidecode(text):
        return text


class CodigoPlaza(TypedDict):
    """Estructura de un código de plaza CLABE."""

    codigo: str  # Código de 3 dígitos
    plaza: str  # Nombre de la plaza/ciudad
    estado: str  # Estado
    cve_entidad: str  # Código INEGI del estado


class CodigosPlazaCatalog:
    """Catálogo de códigos de plaza para CLABE."""

    _data: list[CodigoPlaza] | None = None
    _by_codigo: dict[str, list[CodigoPlaza]] | None = None
    _by_estado: dict[str, list[CodigoPlaza]] | None = None
    _by_plaza: dict[str, list[CodigoPlaza]] | None = None
    _by_plaza_normalized: dict[str, list[CodigoPlaza]] | None = None

    @classmethod
    def _normalize(cls, text: str) -> str:
        """Normaliza texto removiendo acentos y convirtiendo a mayúsculas."""
        return unidecode(text).upper()

    @classmethod
    def _load(cls) -> None:
        """Carga los datos del catálogo."""
        if cls._data is not None:
            return

        data_path = get_shared_data_path("banxico", "codigos_plaza.json")

        with open(data_path, encoding="utf-8") as f:
            catalog = json.load(f)
            cls._data = catalog["plazas"]

        # Build indices
        cls._by_codigo = {}
        cls._by_estado = {}
        cls._by_plaza = {}
        cls._by_plaza_normalized = {}

        for plaza in cls._data:
            # By codigo (puede haber múltiples plazas con el mismo código)
            if plaza["codigo"] not in cls._by_codigo:
                cls._by_codigo[plaza["codigo"]] = []
            cls._by_codigo[plaza["codigo"]].append(plaza)

            # By estado
            if plaza["estado"] not in cls._by_estado:
                cls._by_estado[plaza["estado"]] = []
            cls._by_estado[plaza["estado"]].append(plaza)

            # By plaza name (exact match)
            plaza_key = plaza["plaza"].upper()
            if plaza_key not in cls._by_plaza:
                cls._by_plaza[plaza_key] = []
            cls._by_plaza[plaza_key].append(plaza)

            # By plaza name (normalized, accent-insensitive)
            plaza_normalized = cls._normalize(plaza["plaza"])
            if plaza_normalized not in cls._by_plaza_normalized:
                cls._by_plaza_normalized[plaza_normalized] = []
            cls._by_plaza_normalized[plaza_normalized].append(plaza)

    @classmethod
    def get_all(cls) -> list[CodigoPlaza]:
        """Obtiene todos los códigos de plaza."""
        cls._load()
        return cls._data.copy()

    @classmethod
    def buscar_por_codigo(cls, codigo: str) -> list[CodigoPlaza]:
        """Busca plazas por código."""
        cls._load()
        codigo_padded = codigo.zfill(3)
        return cls._by_codigo.get(codigo_padded, [])

    @classmethod
    def buscar_por_plaza(cls, nombre_plaza: str) -> list[CodigoPlaza]:
        """Busca códigos por nombre de plaza (insensible a acentos)."""
        cls._load()
        plaza_normalized = cls._normalize(nombre_plaza)
        return cls._by_plaza_normalized.get(plaza_normalized, [])

    @classmethod
    def get_por_estado(cls, estado: str) -> list[CodigoPlaza]:
        """Obtiene todas las plazas de un estado."""
        cls._load()
        return cls._by_estado.get(estado, [])

    @classmethod
    def get_por_cve_entidad(cls, cve_entidad: str) -> list[CodigoPlaza]:
        """Obtiene todas las plazas por código INEGI de entidad."""
        cls._load()
        return [p for p in cls._data if p["cve_entidad"] == cve_entidad]

    @classmethod
    def validar_codigo_clabe(cls, codigo_plaza: str) -> dict:
        """Valida un código de plaza dentro de una CLABE."""
        cls._load()
        codigo_padded = codigo_plaza.zfill(3)
        plazas = cls.buscar_por_codigo(codigo_padded)

        return {
            "valido": len(plazas) > 0,
            "codigo": codigo_padded,
            "plazas": plazas,
            "num_plazas": len(plazas),
        }

    @classmethod
    def get_plazas_duplicadas(cls) -> dict[str, list[CodigoPlaza]]:
        """Obtiene plazas con nombres duplicados en diferentes estados."""
        cls._load()
        duplicadas = {}
        for nombre, plazas in cls._by_plaza.items():
            if len(plazas) > 1:
                duplicadas[nombre] = plazas
        return duplicadas

    @classmethod
    def search(cls, query: str) -> list[CodigoPlaza]:
        """Busca plazas por nombre parcial."""
        cls._load()
        query_normalized = cls._normalize(query)
        return [p for p in cls._data if query_normalized in cls._normalize(p["plaza"])]

    @classmethod
    def get_estadisticas(cls) -> dict:
        """Obtiene estadísticas del catálogo."""
        cls._load()

        estados = {p["estado"] for p in cls._data}
        codigos_unicos = len(cls._by_codigo)

        return {
            "total_plazas": len(cls._data),
            "codigos_unicos": codigos_unicos,
            "estados_cubiertos": len(estados),
            "plazas_duplicadas": len(cls.get_plazas_duplicadas()),
        }


__all__ = ["CodigosPlazaCatalog", "CodigoPlaza"]
