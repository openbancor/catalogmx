"""
Catálogo de códigos LADA (plan de numeración telefónica) en México (IFT)

Este módulo proporciona acceso al catálogo completo de códigos LADA
del Instituto Federal de Telecomunicaciones (IFT).
"""

import json
from pathlib import Path
from typing import TypedDict

from catalogmx.utils.text import normalize_text


class CodigoLADA(TypedDict):
    """Estructura de un código LADA"""
    lada: str
    ciudad: str
    estado: str
    tipo: str  # metropolitana | fronteriza | turistica | normal
    region: str


class ValidacionNumero(TypedDict):
    """Resultado de validación de número telefónico"""
    valid: bool
    lada: str | None
    numero_local: str | None
    ciudad: str | None
    estado: str | None
    error: str | None


class InfoNumero(TypedDict):
    """Información detallada de un número telefónico"""
    lada: str
    ciudad: str
    estado: str
    tipo: str
    region: str


class CodigosLADACatalog:
    """
    Catálogo de códigos LADA de México.

    Proporciona métodos para búsqueda, validación y formato de números telefónicos.

    Características:
    - 231+ códigos LADA (expandible a 397 según plan IFT)
    - Cobertura nacional (32 estados)
    - Clasificación por tipo (metropolitana, fronteriza, turística, normal)
    - Validación de números telefónicos de 10 dígitos
    - Formateo automático de números

    Ejemplo:
        >>> from catalogmx.catalogs.ift import CodigosLADACatalog
        >>>
        >>> # Buscar por LADA
        >>> codigo = CodigosLADACatalog.buscar_por_lada("33")
        >>> print(codigo['ciudad'])  # "Guadalajara"
        >>>
        >>> # Validar número telefónico
        >>> info = CodigosLADACatalog.validar_numero("3312345678")
        >>> print(info['valid'])  # True
        >>> print(info['ciudad'])  # "Guadalajara"
    """

    _data: list[CodigoLADA] | None = None
    _by_lada: dict[str, CodigoLADA] | None = None
    _by_estado: dict[str, list[CodigoLADA]] | None = None
    _by_tipo: dict[str, list[CodigoLADA]] | None = None
    _by_region: dict[str, list[CodigoLADA]] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy de datos desde JSON"""
        if cls._data is not None:
            return

        # Path: catalogmx/packages/python/catalogmx/catalogs/ift/codigos_lada.py
        # Target: catalogmx/packages/shared-data/ift/codigos_lada.json
        data_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / 'shared-data' / 'ift' / 'codigos_lada.json'
        )

        with open(data_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            cls._data = json_data['codigos']

        # Crear índices para búsquedas rápidas
        cls._by_lada = {item['lada']: item for item in cls._data}

        # Índice por estado
        cls._by_estado = {}
        for item in cls._data:
            estado = item['estado'].lower()
            if estado not in cls._by_estado:
                cls._by_estado[estado] = []
            cls._by_estado[estado].append(item)

        # Índice por tipo
        cls._by_tipo = {}
        for item in cls._data:
            tipo = item['tipo']
            if tipo not in cls._by_tipo:
                cls._by_tipo[tipo] = []
            cls._by_tipo[tipo].append(item)

        # Índice por región
        cls._by_region = {}
        for item in cls._data:
            region = item['region'].lower()
            if region not in cls._by_region:
                cls._by_region[region] = []
            cls._by_region[region].append(item)

    @classmethod
    def get_all(cls) -> list[CodigoLADA]:
        """
        Obtiene todos los códigos LADA.

        Returns:
            Lista completa de códigos LADA
        """
        cls._load_data()
        return cls._data.copy()  # type: ignore

    @classmethod
    def buscar_por_lada(cls, lada: str) -> CodigoLADA | None:
        """
        Busca un código LADA específico.

        Args:
            lada: Código LADA a buscar (ej: "33", "55", "664")

        Returns:
            Información del código LADA o None si no existe

        Ejemplo:
            >>> codigo = CodigosLADACatalog.buscar_por_lada("33")
            >>> print(codigo['ciudad'])  # "Guadalajara"
            >>> print(codigo['estado'])  # "Jalisco"
        """
        cls._load_data()
        return cls._by_lada.get(lada)  # type: ignore

    @classmethod
    def buscar_por_ciudad(cls, ciudad: str) -> list[CodigoLADA]:
        """
        Busca códigos LADA por nombre de ciudad (búsqueda parcial, insensible a acentos).

        Args:
            ciudad: Nombre o parte del nombre de la ciudad

        Returns:
            Lista de códigos LADA que coinciden

        Ejemplo:
            >>> # Búsqueda con o sin acentos funciona igual
            >>> codigos = CodigosLADACatalog.buscar_por_ciudad("san jose")
            >>> codigos = CodigosLADACatalog.buscar_por_ciudad("san josé")  # mismo resultado
            >>> for codigo in codigos:
            ...     print(f"{codigo['lada']} - {codigo['ciudad']}")
        """
        cls._load_data()
        ciudad_normalized = normalize_text(ciudad)
        return [
            item for item in cls._data  # type: ignore
            if ciudad_normalized in normalize_text(item['ciudad'])
        ]

    @classmethod
    def get_por_estado(cls, estado: str) -> list[CodigoLADA]:
        """
        Obtiene todos los códigos LADA de un estado.

        Args:
            estado: Nombre del estado (ej: "Jalisco", "CDMX")

        Returns:
            Lista de códigos LADA del estado

        Ejemplo:
            >>> codigos = CodigosLADACatalog.get_por_estado("Jalisco")
            >>> print(f"Jalisco tiene {len(codigos)} códigos LADA")
        """
        cls._load_data()
        estado_lower = estado.lower()
        return cls._by_estado.get(estado_lower, []).copy()  # type: ignore

    @classmethod
    def get_por_tipo(cls, tipo: str) -> list[CodigoLADA]:
        """
        Obtiene códigos LADA por tipo.

        Args:
            tipo: Tipo de código ("metropolitana", "fronteriza", "turistica", "normal")

        Returns:
            Lista de códigos del tipo especificado

        Ejemplo:
            >>> metropolitanas = CodigosLADACatalog.get_por_tipo("metropolitana")
            >>> for codigo in metropolitanas:
            ...     print(f"{codigo['lada']} - {codigo['ciudad']}")
        """
        cls._load_data()
        return cls._by_tipo.get(tipo, []).copy()  # type: ignore

    @classmethod
    def get_por_region(cls, region: str) -> list[CodigoLADA]:
        """
        Obtiene códigos LADA por región geográfica.

        Args:
            region: Región ("noroeste", "norte", "noreste", "occidente",
                           "centro", "golfo", "sur", "sureste")

        Returns:
            Lista de códigos de la región

        Ejemplo:
            >>> codigos_norte = CodigosLADACatalog.get_por_region("norte")
            >>> print(f"Región norte: {len(codigos_norte)} códigos")
        """
        cls._load_data()
        region_lower = region.lower()
        return cls._by_region.get(region_lower, []).copy()  # type: ignore

    @classmethod
    def get_metropolitanas(cls) -> list[CodigoLADA]:
        """
        Obtiene códigos LADA de zonas metropolitanas.

        Returns:
            Lista de códigos metropolitanos
        """
        return cls.get_por_tipo('metropolitana')

    @classmethod
    def get_fronterizas(cls) -> list[CodigoLADA]:
        """
        Obtiene códigos LADA de ciudades fronterizas.

        Returns:
            Lista de códigos fronterizos
        """
        return cls.get_por_tipo('fronteriza')

    @classmethod
    def get_turisticas(cls) -> list[CodigoLADA]:
        """
        Obtiene códigos LADA de destinos turísticos.

        Returns:
            Lista de códigos turísticos
        """
        return cls.get_por_tipo('turistica')

    @classmethod
    def validar_numero(cls, numero: str) -> ValidacionNumero:
        """
        Valida y analiza un número telefónico mexicano.

        Desde agosto 2019, México usa un plan de marcación cerrado de 10 dígitos.
        Este método valida el formato y extrae información geográfica.

        Args:
            numero: Número telefónico (puede contener espacios o guiones)

        Returns:
            Diccionario con validación e información del número

        Ejemplo:
            >>> info = CodigosLADACatalog.validar_numero("33 1234 5678")
            >>> if info['valid']:
            ...     print(f"LADA: {info['lada']}")
            ...     print(f"Ciudad: {info['ciudad']}")
            ...     print(f"Número local: {info['numero_local']}")
        """
        cls._load_data()

        # Limpiar número (eliminar espacios y guiones)
        numero_limpio = numero.replace(' ', '').replace('-', '')

        # Validar que sean 10 dígitos
        if not numero_limpio.isdigit() or len(numero_limpio) != 10:
            return {
                'valid': False,
                'lada': None,
                'numero_local': None,
                'ciudad': None,
                'estado': None,
                'error': 'El número debe tener exactamente 10 dígitos'
            }

        # Intentar extraer LADA (primeros 2 o 3 dígitos)
        # Primero intentar con 3 dígitos
        lada = numero_limpio[:3]
        codigo = cls._by_lada.get(lada)  # type: ignore

        # Si no se encuentra, intentar con 2 dígitos
        if not codigo:
            lada = numero_limpio[:2]
            codigo = cls._by_lada.get(lada)  # type: ignore

        if codigo:
            numero_local = numero_limpio[len(lada):]
            return {
                'valid': True,
                'lada': codigo['lada'],
                'numero_local': numero_local,
                'ciudad': codigo['ciudad'],
                'estado': codigo['estado'],
                'error': None
            }

        return {
            'valid': False,
            'lada': lada,
            'numero_local': None,
            'ciudad': None,
            'estado': None,
            'error': f'Código LADA {lada} no encontrado en el catálogo'
        }

    @classmethod
    def formatear_numero(cls, numero: str) -> str:
        """
        Formatea un número telefónico al formato estándar.

        Args:
            numero: Número telefónico sin formato

        Returns:
            Número formateado (LADA XXXX XXXX)

        Ejemplo:
            >>> formateado = CodigosLADACatalog.formatear_numero("3312345678")
            >>> print(formateado)  # "33 1234 5678"
        """
        validacion = cls.validar_numero(numero)

        if not validacion['valid'] or not validacion['lada'] or not validacion['numero_local']:
            return numero

        lada = validacion['lada']
        local = validacion['numero_local']

        # Formato: LADA XXXX XXXX
        if len(local) == 7:
            return f"{lada} {local[:3]} {local[3:]}"
        elif len(local) == 8:
            return f"{lada} {local[:4]} {local[4:]}"
        else:
            return f"{lada} {local}"

    @classmethod
    def get_info_numero(cls, numero: str) -> InfoNumero | None:
        """
        Obtiene información completa de un número telefónico.

        Args:
            numero: Número telefónico

        Returns:
            Información completa del número o None si es inválido

        Ejemplo:
            >>> info = CodigosLADACatalog.get_info_numero("3312345678")
            >>> if info:
            ...     print(f"Ciudad: {info['ciudad']}")
            ...     print(f"Estado: {info['estado']}")
            ...     print(f"Tipo: {info['tipo']}")
            ...     print(f"Región: {info['region']}")
        """
        validacion = cls.validar_numero(numero)

        if not validacion['valid'] or not validacion['lada']:
            return None

        codigo = cls.buscar_por_lada(validacion['lada'])

        if not codigo:
            return None

        return {
            'lada': codigo['lada'],
            'ciudad': codigo['ciudad'],
            'estado': codigo['estado'],
            'tipo': codigo['tipo'],
            'region': codigo['region']
        }

    @classmethod
    def get_estadisticas(cls) -> dict[str, int | dict]:
        """
        Obtiene estadísticas del catálogo.

        Returns:
            Diccionario con estadísticas del catálogo

        Ejemplo:
            >>> stats = CodigosLADACatalog.get_estadisticas()
            >>> print(f"Total códigos: {stats['total_codigos']}")
            >>> print(f"Estados: {stats['estados_cubiertos']}")
        """
        cls._load_data()

        return {
            'total_codigos': len(cls._data),  # type: ignore
            'codigos_metropolitanos': len(cls.get_metropolitanas()),
            'codigos_fronterizos': len(cls.get_fronterizas()),
            'codigos_turisticos': len(cls.get_turisticas()),
            'estados_cubiertos': len(cls._by_estado),  # type: ignore
            'regiones': list(cls._by_region.keys()),  # type: ignore
            'tipos': list(cls._by_tipo.keys())  # type: ignore
        }
