"""
Catálogo de tipos de instituciones financieras en México (Banxico)

Este módulo proporciona acceso al catálogo de tipos de instituciones
del sistema financiero mexicano supervisadas por Banxico, CNBV, CNSF,
CONSAR y otras entidades reguladoras.
"""

import json
from pathlib import Path
from typing import TypedDict
from catalogmx.utils.text import normalize_text


class TipoInstitucionFinanciera(TypedDict):
    """Estructura de un tipo de institución financiera"""
    codigo: str
    tipo: str
    descripcion: str
    regulador: str
    ley_aplicable: str
    ejemplos: list[str]


class InstitucionesFinancieras:
    """
    Catálogo de tipos de instituciones del sistema financiero mexicano.

    Incluye todos los tipos de instituciones reguladas y supervisadas
    en México: bancos, casas de bolsa, SOFOMes, seguros, fianzas,
    AFOREs, instituciones fintech, etc.

    Características:
    - 20+ tipos de instituciones financieras
    - Información de reguladores (CNBV, CNSF, CONSAR, CONDUSEF, SHCP)
    - Leyes aplicables para cada tipo
    - Ejemplos de instituciones por categoría

    Ejemplo:
        >>> from catalogmx.catalogs.banxico import InstitucionesFinancieras
        >>>
        >>> # Obtener bancos
        >>> bancos = InstitucionesFinancieras.get_bancos()
        >>> for banco in bancos:
        ...     print(f"{banco['codigo']}: {banco['tipo']}")
        >>>
        >>> # Buscar por código
        >>> inst = InstitucionesFinancieras.get_por_codigo("01")
        >>> print(inst['tipo'])  # "Banco Múltiple"
        >>>
        >>> # Obtener instituciones por regulador
        >>> cnbv = InstitucionesFinancieras.get_por_regulador("CNBV")
        >>> print(f"Instituciones reguladas por CNBV: {len(cnbv)}")
    """

    _data: list[TipoInstitucionFinanciera] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy de datos desde JSON"""
        if cls._data is not None:
            return

        # Path: catalogmx/packages/python/catalogmx/catalogs/banxico/instituciones_financieras.py
        # Target: catalogmx/packages/shared-data/banxico/instituciones_financieras.json
        data_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / 'shared-data' / 'banxico' / 'instituciones_financieras.json'
        )

        with open(data_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            cls._data = json_data['tipos_institucion']

    @classmethod
    def get_all(cls) -> list[TipoInstitucionFinanciera]:
        """
        Obtiene todos los tipos de instituciones financieras.

        Returns:
            Lista completa de tipos de instituciones

        Ejemplo:
            >>> instituciones = InstitucionesFinancieras.get_all()
            >>> print(f"Total tipos: {len(instituciones)}")
        """
        cls._load_data()
        return cls._data.copy()  # type: ignore

    @classmethod
    def get_por_codigo(cls, codigo: str) -> TipoInstitucionFinanciera | None:
        """
        Busca tipo de institución por código.

        Args:
            codigo: Código del tipo de institución (ej: "01", "02")

        Returns:
            Información del tipo de institución o None si no existe

        Ejemplo:
            >>> banco = InstitucionesFinancieras.get_por_codigo("01")
            >>> print(banco['tipo'])  # "Banco Múltiple"
        """
        cls._load_data()
        for inst in cls._data:  # type: ignore
            if inst['codigo'] == codigo:
                return inst
        return None

    @classmethod
    def buscar_por_tipo(cls, tipo: str) -> list[TipoInstitucionFinanciera]:
        """
        Busca por tipo de institución (insensible a acentos y mayúsculas).

        Args:
            tipo: Texto a buscar en el tipo de institución

        Returns:
            Lista de tipos de instituciones que coinciden

        Ejemplo:
            >>> bancos = InstitucionesFinancieras.buscar_por_tipo("banco")
            >>> for b in bancos:
            ...     print(b['tipo'])
        """
        cls._load_data()
        tipo_normalized = normalize_text(tipo)
        return [
            inst for inst in cls._data  # type: ignore
            if tipo_normalized in normalize_text(inst['tipo'])
        ]

    @classmethod
    def get_por_regulador(cls, regulador: str) -> list[TipoInstitucionFinanciera]:
        """
        Obtiene instituciones por regulador (insensible a acentos).

        Args:
            regulador: Nombre o siglas del regulador (CNBV, CNSF, CONSAR, etc.)

        Returns:
            Lista de instituciones reguladas por esa entidad

        Ejemplo:
            >>> cnbv = InstitucionesFinancieras.get_por_regulador("CNBV")
            >>> print(f"Instituciones reguladas por CNBV: {len(cnbv)}")
        """
        cls._load_data()
        regulador_normalized = normalize_text(regulador)
        return [
            inst for inst in cls._data  # type: ignore
            if regulador_normalized in normalize_text(inst['regulador'])
        ]

    @classmethod
    def get_bancos(cls) -> list[TipoInstitucionFinanciera]:
        """
        Obtiene bancos (múltiples y de desarrollo).

        Returns:
            Lista de tipos de bancos

        Ejemplo:
            >>> bancos = InstitucionesFinancieras.get_bancos()
            >>> for banco in bancos:
            ...     print(f"{banco['tipo']}: {', '.join(banco['ejemplos'][:3])}")
        """
        cls._load_data()
        return [
            inst for inst in cls._data  # type: ignore
            if 'banco' in inst['tipo'].lower()
        ]

    @classmethod
    def get_sofomes(cls) -> list[TipoInstitucionFinanciera]:
        """
        Obtiene SOFOMes (ENR y ER).

        Returns:
            Lista de tipos de SOFOMes

        Ejemplo:
            >>> sofomes = InstitucionesFinancieras.get_sofomes()
            >>> for sofom in sofomes:
            ...     print(f"{sofom['tipo']} - {sofom['regulador']}")
        """
        cls._load_data()
        return [
            inst for inst in cls._data  # type: ignore
            if 'SOFOM' in inst['tipo']
        ]

    @classmethod
    def get_sector_popular(cls) -> list[TipoInstitucionFinanciera]:
        """
        Obtiene instituciones de ahorro y crédito popular.

        Returns:
            Lista de instituciones del sector popular

        Ejemplo:
            >>> sector_popular = InstitucionesFinancieras.get_sector_popular()
            >>> for inst in sector_popular:
            ...     print(inst['tipo'])
        """
        cls._load_data()
        return [
            inst for inst in cls._data  # type: ignore
            if any(keyword in inst['tipo'] for keyword in [
                'Cooperativa', 'Financiera Popular', 'Ahorro y Crédito'
            ])
        ]

    @classmethod
    def get_seguros_y_fianzas(cls) -> list[TipoInstitucionFinanciera]:
        """
        Obtiene instituciones de seguros y fianzas.

        Returns:
            Lista de instituciones de seguros y fianzas

        Ejemplo:
            >>> seguros = InstitucionesFinancieras.get_seguros_y_fianzas()
            >>> for inst in seguros:
            ...     print(f"{inst['tipo']} - {inst['regulador']}")
        """
        cls._load_data()
        return [
            inst for inst in cls._data  # type: ignore
            if 'Seguros' in inst['tipo'] or 'Fianzas' in inst['tipo']
        ]

    @classmethod
    def get_mercado_valores(cls) -> list[TipoInstitucionFinanciera]:
        """
        Obtiene instituciones del mercado de valores.

        Returns:
            Lista de instituciones del mercado de valores

        Ejemplo:
            >>> mercado = InstitucionesFinancieras.get_mercado_valores()
            >>> for inst in mercado:
            ...     print(inst['tipo'])
        """
        cls._load_data()
        return [
            inst for inst in cls._data  # type: ignore
            if any(keyword in inst['tipo'] for keyword in [
                'Bolsa', 'Casa de Bolsa', 'Valores', 'Inversión'
            ])
        ]

    @classmethod
    def get_fintech(cls) -> list[TipoInstitucionFinanciera]:
        """
        Obtiene instituciones de tecnología financiera (Fintech).

        Returns:
            Lista de instituciones fintech

        Ejemplo:
            >>> fintech = InstitucionesFinancieras.get_fintech()
            >>> for inst in fintech:
            ...     print(f"{inst['tipo']} - {inst['ley_aplicable']}")
        """
        cls._load_data()
        return [
            inst for inst in cls._data  # type: ignore
            if 'Tecnología Financiera' in inst['tipo']
        ]

    @classmethod
    def get_retiro(cls) -> list[TipoInstitucionFinanciera]:
        """
        Obtiene AFOREs y SIEFOREs.

        Returns:
            Lista de instituciones del sistema de ahorro para el retiro

        Ejemplo:
            >>> retiro = InstitucionesFinancieras.get_retiro()
            >>> for inst in retiro:
            ...     print(f"{inst['tipo']} - {inst['regulador']}")
        """
        cls._load_data()
        return [
            inst for inst in cls._data  # type: ignore
            if 'AFORE' in inst['tipo'] or 'SIEFORE' in inst['tipo']
        ]

    @classmethod
    def validar_codigo(cls, codigo: str) -> bool:
        """
        Valida código de institución.

        Args:
            codigo: Código a validar

        Returns:
            True si el código existe, False en caso contrario

        Ejemplo:
            >>> InstitucionesFinancieras.validar_codigo("01")  # True
            >>> InstitucionesFinancieras.validar_codigo("99")  # False
        """
        cls._load_data()
        return any(inst['codigo'] == codigo for inst in cls._data)  # type: ignore

    @classmethod
    def get_descripcion_regulador(cls, siglas: str) -> str | None:
        """
        Obtiene descripción de regulador.

        Args:
            siglas: Siglas del regulador (CNBV, CNSF, CONSAR, etc.)

        Returns:
            Descripción completa del regulador o None si no existe

        Ejemplo:
            >>> desc = InstitucionesFinancieras.get_descripcion_regulador("CNBV")
            >>> print(desc)  # "Comisión Nacional Bancaria y de Valores"
        """
        reguladores = {
            'CNBV': 'Comisión Nacional Bancaria y de Valores',
            'CNSF': 'Comisión Nacional de Seguros y Fianzas',
            'CONSAR': 'Comisión Nacional del Sistema de Ahorro para el Retiro',
            'CONDUSEF': 'Comisión Nacional para la Protección y Defensa de los Usuarios de Servicios Financieros',
            'SHCP': 'Secretaría de Hacienda y Crédito Público',
        }
        return reguladores.get(siglas.upper())
