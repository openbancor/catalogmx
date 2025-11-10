"""
Catálogo de Códigos de Plaza CLABE
=====================================

Códigos de plaza para el sistema CLABE (Clave Bancaria Estandarizada).
Los códigos de plaza son identificadores de 3 dígitos que indican la ubicación
geográfica de las sucursales bancarias en México.

Fuente: Banco de México (BANXICO) / Sistema de Pagos Electrónicos Interbancarios (SPEI)
"""

import json
import os
from typing import TypedDict

try:
    from unidecode import unidecode
except ImportError:
    # Fallback if unidecode not available
    def unidecode(text):
        return text

class CodigoPlaza(TypedDict):
    """Estructura de un código de plaza CLABE."""
    codigo: str          # Código de 3 dígitos
    plaza: str           # Nombre de la plaza/ciudad
    estado: str          # Estado
    cve_entidad: str     # Código INEGI del estado


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

        data_path = os.path.join(
            os.path.dirname(__file__),
            '../../../../shared-data/banxico/codigos_plaza.json'
        )

        with open(data_path, encoding='utf-8') as f:
            catalog = json.load(f)
            cls._data = catalog['plazas']

        # Build indices
        cls._by_codigo = {}
        cls._by_estado = {}
        cls._by_plaza = {}
        cls._by_plaza_normalized = {}

        for plaza in cls._data:
            # By codigo (puede haber múltiples plazas con el mismo código)
            if plaza['codigo'] not in cls._by_codigo:
                cls._by_codigo[plaza['codigo']] = []
            cls._by_codigo[plaza['codigo']].append(plaza)

            # By estado
            if plaza['estado'] not in cls._by_estado:
                cls._by_estado[plaza['estado']] = []
            cls._by_estado[plaza['estado']].append(plaza)

            # By plaza name (exact match)
            plaza_key = plaza['plaza'].upper()
            if plaza_key not in cls._by_plaza:
                cls._by_plaza[plaza_key] = []
            cls._by_plaza[plaza_key].append(plaza)

            # By plaza name (normalized, accent-insensitive)
            plaza_normalized = cls._normalize(plaza['plaza'])
            if plaza_normalized not in cls._by_plaza_normalized:
                cls._by_plaza_normalized[plaza_normalized] = []
            cls._by_plaza_normalized[plaza_normalized].append(plaza)

    @classmethod
    def get_all(cls) -> list[CodigoPlaza]:
        """
        Obtiene todos los códigos de plaza.

        Returns:
            Lista con todos los códigos de plaza
        """
        cls._load()
        return cls._data.copy()

    @classmethod
    def buscar_por_codigo(cls, codigo: str) -> list[CodigoPlaza]:
        """
        Busca plazas por código.

        Args:
            codigo: Código de plaza (3 dígitos)

        Returns:
            Lista de plazas con ese código (puede haber múltiples)

        Examples:
            >>> plazas = CodigosPlazaCatalog.buscar_por_codigo("320")
            >>> for p in plazas:
            ...     print(f"{p['plaza']}, {p['estado']}")
            Guadalajara, Jalisco
            Tonala, Jalisco
            ...
        """
        cls._load()
        codigo_padded = codigo.zfill(3)
        return cls._by_codigo.get(codigo_padded, [])

    @classmethod
    def buscar_por_plaza(cls, nombre_plaza: str) -> list[CodigoPlaza]:
        """
        Busca códigos por nombre de plaza (insensible a acentos).

        Args:
            nombre_plaza: Nombre de la plaza/ciudad

        Returns:
            Lista de códigos para esa plaza

        Examples:
            >>> # Tonalá aparece en dos estados diferentes
            >>> plazas = CodigosPlazaCatalog.buscar_por_plaza("Tonala")
            >>> for p in plazas:
            ...     print(f"Código {p['codigo']}: {p['plaza']}, {p['estado']}")
            Código 135: Tonala, Chiapas
            Código 320: Tonala, Jalisco

            >>> # Búsqueda insensible a acentos
            >>> tuxpam = CodigosPlazaCatalog.buscar_por_plaza("Tuxpam")  # sin acento
            >>> print(len(tuxpam))  # Encuentra "Túxpam" con acento
            2
        """
        cls._load()
        plaza_normalized = cls._normalize(nombre_plaza)
        return cls._by_plaza_normalized.get(plaza_normalized, [])

    @classmethod
    def get_por_estado(cls, estado: str) -> list[CodigoPlaza]:
        """
        Obtiene todas las plazas de un estado.

        Args:
            estado: Nombre del estado

        Returns:
            Lista de plazas en ese estado

        Examples:
            >>> plazas = CodigosPlazaCatalog.get_por_estado("Jalisco")
            >>> print(f"Jalisco tiene {len(plazas)} plazas")
        """
        cls._load()
        return cls._by_estado.get(estado, [])

    @classmethod
    def get_por_cve_entidad(cls, cve_entidad: str) -> list[CodigoPlaza]:
        """
        Obtiene todas las plazas por código INEGI de entidad.

        Args:
            cve_entidad: Código INEGI del estado (2 dígitos)

        Returns:
            Lista de plazas en esa entidad

        Examples:
            >>> # Jalisco tiene cve_entidad '14'
            >>> plazas = CodigosPlazaCatalog.get_por_cve_entidad("14")
            >>> print(f"Entidad 14 tiene {len(plazas)} plazas")
        """
        cls._load()
        return [p for p in cls._data if p['cve_entidad'] == cve_entidad]

    @classmethod
    def validar_codigo_clabe(cls, codigo_plaza: str) -> dict:
        """
        Valida un código de plaza dentro de una CLABE.

        Args:
            codigo_plaza: Código de plaza (3 dígitos)

        Returns:
            Diccionario con información de validación

        Examples:
            >>> result = CodigosPlazaCatalog.validar_codigo_clabe("180")
            >>> print(result['valido'])
            True
            >>> print(result['plazas'][0]['plaza'])
            Ciudad de México
        """
        cls._load()
        codigo_padded = codigo_plaza.zfill(3)
        plazas = cls.buscar_por_codigo(codigo_padded)

        return {
            'valido': len(plazas) > 0,
            'codigo': codigo_padded,
            'plazas': plazas,
            'num_plazas': len(plazas)
        }

    @classmethod
    def get_plazas_duplicadas(cls) -> dict[str, list[CodigoPlaza]]:
        """
        Obtiene plazas con nombres duplicados en diferentes estados.

        Returns:
            Diccionario con nombres de plaza y sus instancias

        Examples:
            >>> duplicadas = CodigosPlazaCatalog.get_plazas_duplicadas()
            >>> for nombre, plazas in duplicadas.items():
            ...     print(f"{nombre}: {len(plazas)} ubicaciones")
            Tonala: 2 ubicaciones (Chiapas, Jalisco)
            Túxpam: 2 ubicaciones (Jalisco, Nayarit)
        """
        cls._load()
        duplicadas = {}
        for nombre, plazas in cls._by_plaza.items():
            if len(plazas) > 1:
                duplicadas[nombre] = plazas
        return duplicadas

    @classmethod
    def search(cls, query: str) -> list[CodigoPlaza]:
        """
        Busca plazas por nombre parcial (insensible a acentos y mayúsculas).

        Args:
            query: Texto a buscar

        Returns:
            Lista de plazas que coinciden

        Examples:
            >>> # Buscar todas las plazas con "San" en el nombre
            >>> plazas = CodigosPlazaCatalog.search("San")
            >>> for p in plazas[:5]:
            ...     print(f"{p['codigo']}: {p['plaza']}, {p['estado']}")

            >>> # Búsqueda insensible a acentos
            >>> plazas = CodigosPlazaCatalog.search("Tuxpam")  # sin acento
            >>> print(len(plazas))  # Encuentra "Túxpam" con acento
            3
        """
        cls._load()
        query_normalized = cls._normalize(query)
        return [p for p in cls._data if query_normalized in cls._normalize(p['plaza'])]

    @classmethod
    def get_estadisticas(cls) -> dict:
        """
        Obtiene estadísticas del catálogo.

        Returns:
            Diccionario con estadísticas
        """
        cls._load()

        estados = {p['estado'] for p in cls._data}
        codigos_unicos = len(cls._by_codigo)

        return {
            'total_plazas': len(cls._data),
            'codigos_unicos': codigos_unicos,
            'estados_cubiertos': len(estados),
            'plazas_duplicadas': len(cls.get_plazas_duplicadas())
        }


__all__ = ['CodigosPlazaCatalog', 'CodigoPlaza']
