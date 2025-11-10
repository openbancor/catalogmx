"""
Catálogo de operadores de telefonía móvil en México (IFT)

Este módulo proporciona acceso al catálogo de operadores móviles
registrados ante el Instituto Federal de Telecomunicaciones (IFT).
"""

import json
from pathlib import Path
from typing import TypedDict


class OperadorMovil(TypedDict):
    """Estructura de un operador móvil"""
    nombre_comercial: str
    razon_social: str
    tipo: str  # OMR (Operador Móvil con Red) | OMV (Operador Móvil Virtual)
    grupo_empresarial: str
    tecnologias: list[str]  # 2G, 3G, 4G, 5G
    cobertura: str  # nacional | regional
    servicios: list[str]  # prepago, postpago, datos
    market_share_aprox: float
    fecha_inicio_operaciones: str
    activo: bool


class OperadoresMovilesCatalog:
    """
    Catálogo de operadores de telefonía móvil en México.

    Incluye operadores móviles con red propia (OMR) y operadores móviles
    virtuales (OMV).

    Características:
    - Operadores activos e históricos
    - Información de tecnologías (2G, 3G, 4G, 5G)
    - Market share aproximado
    - Clasificación por tipo (OMR/OMV)
    - Cobertura (nacional/regional)

    Ejemplo:
        >>> from catalogmx.catalogs.ift import OperadoresMovilesCatalog
        >>>
        >>> # Obtener operadores activos
        >>> activos = OperadoresMovilesCatalog.get_activos()
        >>> for op in activos:
        ...     print(f"{op['nombre_comercial']}: {op['market_share_aprox']}%")
        >>>
        >>> # Buscar por nombre
        >>> telcel = OperadoresMovilesCatalog.buscar_por_nombre("Telcel")
        >>> print(telcel['razon_social'])
    """

    _data: list[OperadorMovil] | None = None
    _by_nombre: dict[str, OperadorMovil] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy de datos desde JSON"""
        if cls._data is not None:
            return

        # Path: catalogmx/packages/python/catalogmx/catalogs/ift/operadores_moviles.py
        # Target: catalogmx/packages/shared-data/ift/operadores_moviles.json
        data_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / 'shared-data' / 'ift' / 'operadores_moviles.json'
        )

        with open(data_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            cls._data = json_data['operadores']

        # Índice por nombre comercial
        cls._by_nombre = {
            item['nombre_comercial'].lower(): item
            for item in cls._data
        }

    @classmethod
    def get_all(cls) -> list[OperadorMovil]:
        """
        Obtiene todos los operadores móviles.

        Returns:
            Lista completa de operadores

        Ejemplo:
            >>> operadores = OperadoresMovilesCatalog.get_all()
            >>> print(f"Total operadores: {len(operadores)}")
        """
        cls._load_data()
        return cls._data.copy()  # type: ignore

    @classmethod
    def get_activos(cls) -> list[OperadorMovil]:
        """
        Obtiene solo operadores activos.

        Returns:
            Lista de operadores actualmente operando

        Ejemplo:
            >>> activos = OperadoresMovilesCatalog.get_activos()
            >>> for op in activos:
            ...     print(f"{op['nombre_comercial']} ({op['tipo']})")
        """
        cls._load_data()
        return [op for op in cls._data if op['activo']]  # type: ignore

    @classmethod
    def get_inactivos(cls) -> list[OperadorMovil]:
        """
        Obtiene operadores que dejaron de operar.

        Returns:
            Lista de operadores inactivos

        Ejemplo:
            >>> inactivos = OperadoresMovilesCatalog.get_inactivos()
            >>> print(f"Operadores históricos: {len(inactivos)}")
        """
        cls._load_data()
        return [op for op in cls._data if not op['activo']]  # type: ignore

    @classmethod
    def buscar_por_nombre(cls, nombre: str) -> OperadorMovil | None:
        """
        Busca un operador por nombre comercial.

        Args:
            nombre: Nombre comercial del operador (ej: "Telcel", "AT&T")

        Returns:
            Información del operador o None si no existe

        Ejemplo:
            >>> telcel = OperadoresMovilesCatalog.buscar_por_nombre("Telcel")
            >>> if telcel:
            ...     print(f"Razón social: {telcel['razon_social']}")
            ...     print(f"Market share: {telcel['market_share_aprox']}%")
        """
        cls._load_data()
        nombre_lower = nombre.lower()

        # Búsqueda exacta
        exact = cls._by_nombre.get(nombre_lower)  # type: ignore
        if exact:
            return exact

        # Búsqueda parcial
        for op in cls._data:  # type: ignore
            if nombre_lower in op['nombre_comercial'].lower():
                return op

        return None

    @classmethod
    def get_por_tipo(cls, tipo: str) -> list[OperadorMovil]:
        """
        Obtiene operadores por tipo.

        Args:
            tipo: "OMR" (con red propia) o "OMV" (virtual)

        Returns:
            Lista de operadores del tipo especificado

        Ejemplo:
            >>> omr = OperadoresMovilesCatalog.get_por_tipo("OMR")
            >>> print(f"Operadores con red propia: {len(omr)}")
            >>>
            >>> omv = OperadoresMovilesCatalog.get_por_tipo("OMV")
            >>> print(f"Operadores virtuales: {len(omv)}")
        """
        cls._load_data()
        tipo_upper = tipo.upper()
        return [op for op in cls._data if op['tipo'] == tipo_upper]  # type: ignore

    @classmethod
    def get_con_tecnologia(cls, tecnologia: str) -> list[OperadorMovil]:
        """
        Obtiene operadores que soportan una tecnología específica.

        Args:
            tecnologia: "2G", "3G", "4G", "5G"

        Returns:
            Lista de operadores con la tecnología

        Ejemplo:
            >>> con_5g = OperadoresMovilesCatalog.get_con_tecnologia("5G")
            >>> for op in con_5g:
            ...     print(f"{op['nombre_comercial']} tiene 5G")
        """
        cls._load_data()
        tecnologia_upper = tecnologia.upper()
        return [
            op for op in cls._data  # type: ignore
            if tecnologia_upper in op['tecnologias']
        ]

    @classmethod
    def get_por_cobertura(cls, cobertura: str) -> list[OperadorMovil]:
        """
        Obtiene operadores por tipo de cobertura.

        Args:
            cobertura: "nacional" o "regional"

        Returns:
            Lista de operadores con ese tipo de cobertura

        Ejemplo:
            >>> nacionales = OperadoresMovilesCatalog.get_por_cobertura("nacional")
            >>> print(f"Operadores con cobertura nacional: {len(nacionales)}")
        """
        cls._load_data()
        cobertura_lower = cobertura.lower()
        return [
            op for op in cls._data  # type: ignore
            if op['cobertura'] == cobertura_lower
        ]

    @classmethod
    def get_por_grupo(cls, grupo: str) -> list[OperadorMovil]:
        """
        Obtiene operadores de un grupo empresarial.

        Args:
            grupo: Nombre del grupo empresarial

        Returns:
            Lista de operadores del grupo

        Ejemplo:
            >>> america_movil = OperadoresMovilesCatalog.get_por_grupo("América Móvil")
            >>> for op in america_movil:
            ...     print(op['nombre_comercial'])
        """
        cls._load_data()
        grupo_lower = grupo.lower()
        return [
            op for op in cls._data  # type: ignore
            if 'grupo_empresarial' in op and grupo_lower in op['grupo_empresarial'].lower()
        ]

    @classmethod
    def get_con_servicio(cls, servicio: str) -> list[OperadorMovil]:
        """
        Obtiene operadores que ofrecen un servicio específico.

        Args:
            servicio: "prepago", "postpago", "datos"

        Returns:
            Lista de operadores con el servicio

        Ejemplo:
            >>> prepago = OperadoresMovilesCatalog.get_con_servicio("prepago")
            >>> print(f"Operadores con prepago: {len(prepago)}")
        """
        cls._load_data()
        servicio_lower = servicio.lower()
        return [
            op for op in cls._data  # type: ignore
            if servicio_lower in op['servicios']
        ]

    @classmethod
    def get_top_por_market_share(cls, limit: int = 5) -> list[OperadorMovil]:
        """
        Obtiene los operadores con mayor market share.

        Args:
            limit: Número de operadores a retornar (default: 5)

        Returns:
            Lista de top operadores ordenados por market share

        Ejemplo:
            >>> top3 = OperadoresMovilesCatalog.get_top_por_market_share(3)
            >>> for i, op in enumerate(top3, 1):
            ...     print(f"{i}. {op['nombre_comercial']}: {op['market_share_aprox']}%")
        """
        cls._load_data()
        sorted_ops = sorted(
            [op for op in cls._data if op['activo']],  # type: ignore
            key=lambda x: x['market_share_aprox'],
            reverse=True
        )
        return sorted_ops[:limit]

    @classmethod
    def get_estadisticas(cls) -> dict[str, int | float | list]:
        """
        Obtiene estadísticas del catálogo.

        Returns:
            Diccionario con estadísticas

        Ejemplo:
            >>> stats = OperadoresMovilesCatalog.get_estadisticas()
            >>> print(f"Total operadores: {stats['total_operadores']}")
            >>> print(f"Activos: {stats['operadores_activos']}")
            >>> print(f"Con 5G: {stats['operadores_con_5g']}")
        """
        cls._load_data()

        activos = cls.get_activos()
        con_5g = cls.get_con_tecnologia('5G')

        return {
            'total_operadores': len(cls._data),  # type: ignore
            'operadores_activos': len(activos),
            'operadores_inactivos': len(cls.get_inactivos()),
            'omr_count': len(cls.get_por_tipo('OMR')),
            'omv_count': len(cls.get_por_tipo('OMV')),
            'operadores_con_5g': len(con_5g),
            'cobertura_nacional': len(cls.get_por_cobertura('nacional')),
            'market_share_total': sum(
                op['market_share_aprox'] for op in activos
            ),
            'tecnologias_disponibles': ['2G', '3G', '4G', '5G']
        }
