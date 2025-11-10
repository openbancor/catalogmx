"""
INEGI - Catálogo Completo de Municipios Mexicanos

Catálogo completo de todos los 2,469 municipios de México
(2,462 municipios + 7 alcaldías CDMX)
"""

import json
from pathlib import Path


class MunicipiosCompletoCatalog:
    """
    Catálogo completo de municipios mexicanos.

    Incluye todos los 2,469 municipios (2,462 municipios + 7 alcaldías CDMX)
    con información demográfica completa.

    WARNING: Este catálogo carga todos los municipios en memoria (~940KB).
    Para consultas simples, considere usar MunicipiosCatalog en su lugar.

    Características:
    - 2,469 municipios totales
    - Población total, masculina, femenina
    - Viviendas habitadas
    - Nombre de cabecera municipal
    - Códigos INEGI completos

    Ejemplo:
        >>> from catalogmx.catalogs.inegi import MunicipiosCompletoCatalog
        >>>
        >>> # Obtener todos los municipios
        >>> municipios = MunicipiosCompletoCatalog.get_all()
        >>> print(f"Total municipios: {len(municipios)}")
        >>>
        >>> # Buscar municipio por código
        >>> guadalajara = MunicipiosCompletoCatalog.get_municipio("14039")
        >>> print(f"{guadalajara['nom_municipio']}: {guadalajara['poblacion_total']:,} habitantes")
        >>>
        >>> # Obtener municipios por estado
        >>> jalisco = MunicipiosCompletoCatalog.get_by_entidad("14")
        >>> print(f"Jalisco tiene {len(jalisco)} municipios")
    """

    _data: list[dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy de datos desde JSON"""
        if cls._data is not None:
            return

        # Path: catalogmx/packages/python/catalogmx/catalogs/inegi/municipios_completo.py
        # Target: catalogmx/packages/shared-data/inegi/municipios_completo.json
        data_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "shared-data"
            / "inegi"
            / "municipios_completo.json"
        )

        with open(data_path, encoding="utf-8") as f:
            cls._data = json.load(f)

    @classmethod
    def get_all(cls) -> list[dict]:
        """
        Obtiene todos los municipios (2,469 total).

        WARNING: Retorna todos los municipios en memoria.

        Returns:
            Lista completa de municipios

        Ejemplo:
            >>> municipios = MunicipiosCompletoCatalog.get_all()
            >>> print(f"Total: {len(municipios)}")  # 2469
        """
        cls._load_data()
        return cls._data.copy()  # type: ignore

    @classmethod
    def get_municipio(cls, cve_completa: str) -> dict | None:
        """
        Obtiene municipio por código completo (cve_completa).

        Args:
            cve_completa: Código completo de 5 dígitos (ej: "14039" para Guadalajara)

        Returns:
            Información del municipio o None si no existe

        Ejemplo:
            >>> mun = MunicipiosCompletoCatalog.get_municipio("14039")
            >>> print(mun['nom_municipio'])  # "Guadalajara"
        """
        cls._load_data()
        for mun in cls._data:  # type: ignore
            if mun["cve_completa"] == cve_completa:
                return mun
        return None

    @classmethod
    def get_by_entidad(cls, cve_entidad: str) -> list[dict]:
        """
        Obtiene municipios por estado (cve_entidad).

        Args:
            cve_entidad: Código de entidad de 2 dígitos (ej: "14" para Jalisco)

        Returns:
            Lista de municipios del estado

        Ejemplo:
            >>> jalisco = MunicipiosCompletoCatalog.get_by_entidad("14")
            >>> print(f"Jalisco: {len(jalisco)} municipios")
        """
        cls._load_data()
        return [mun for mun in cls._data if mun["cve_entidad"] == cve_entidad]  # type: ignore

    @classmethod
    def search_by_name(cls, name: str) -> list[dict]:
        """
        Busca municipios por nombre (case-insensitive).

        Args:
            name: Nombre o parte del nombre a buscar

        Returns:
            Lista de municipios que coinciden

        Ejemplo:
            >>> san = MunicipiosCompletoCatalog.search_by_name("San")
            >>> for mun in san[:5]:
            ...     print(f"{mun['nom_municipio']}, {mun['nom_entidad']}")
        """
        cls._load_data()
        search_term = name.upper()
        return [
            mun for mun in cls._data if search_term in mun["nom_municipio"].upper()  # type: ignore
        ]

    @classmethod
    def get_by_state_name(cls, state_name: str) -> list[dict]:
        """
        Obtiene municipios por nombre de estado.

        Args:
            state_name: Nombre del estado (ej: "Jalisco", "CDMX")

        Returns:
            Lista de municipios del estado

        Ejemplo:
            >>> jalisco = MunicipiosCompletoCatalog.get_by_state_name("Jalisco")
            >>> for mun in jalisco[:5]:
            ...     print(mun['nom_municipio'])
        """
        cls._load_data()
        search_term = state_name.upper()
        return [
            mun for mun in cls._data if mun["nom_entidad"].upper() == search_term  # type: ignore
        ]

    @classmethod
    def get_count_by_entidad(cls, cve_entidad: str) -> int:
        """
        Obtiene el número de municipios en un estado.

        Args:
            cve_entidad: Código de entidad de 2 dígitos

        Returns:
            Número de municipios en el estado

        Ejemplo:
            >>> count = MunicipiosCompletoCatalog.get_count_by_entidad("14")
            >>> print(f"Jalisco tiene {count} municipios")
        """
        return len(cls.get_by_entidad(cve_entidad))

    @classmethod
    def is_valid(cls, cve_completa: str) -> bool:
        """
        Valida código de municipio.

        Args:
            cve_completa: Código completo de 5 dígitos

        Returns:
            True si el código existe, False en caso contrario

        Ejemplo:
            >>> MunicipiosCompletoCatalog.is_valid("14039")  # True
            >>> MunicipiosCompletoCatalog.is_valid("99999")  # False
        """
        return cls.get_municipio(cve_completa) is not None

    @classmethod
    def get_total_count(cls) -> int:
        """
        Obtiene el total de municipios.

        Returns:
            Número total de municipios (2,469)

        Ejemplo:
            >>> total = MunicipiosCompletoCatalog.get_total_count()
            >>> print(f"Total municipios: {total}")  # 2469
        """
        cls._load_data()
        return len(cls._data)  # type: ignore

    @classmethod
    def get_estadisticas(cls) -> dict[str, int]:
        """
        Obtiene estadísticas del catálogo.

        Returns:
            Diccionario con estadísticas de municipios

        Ejemplo:
            >>> stats = MunicipiosCompletoCatalog.get_estadisticas()
            >>> print(f"Total municipios: {stats['total_municipios']}")
            >>> print(f"Total estados: {stats['total_estados']}")
        """
        cls._load_data()

        estados = {mun["cve_entidad"] for mun in cls._data}  # type: ignore
        poblacion_total = sum(mun["poblacion_total"] for mun in cls._data)  # type: ignore

        return {
            "total_municipios": len(cls._data),  # type: ignore
            "total_estados": len(estados),
            "poblacion_total": poblacion_total,
        }
