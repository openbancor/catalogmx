"""
SAT Anexo 24 - Código agrupador de cuentas.

Incluye versiones 2024 y 2026 del catálogo oficial.
"""

import json
from pathlib import Path
from typing import TypedDict


class CodigoAgrupadorSAT(TypedDict, total=False):
    """Estructura de un código agrupador SAT."""

    codigo: str
    nombre: str
    nivel: int | None


class CodigoAgrupadorSATCatalog:
    """Catálogo del código agrupador de cuentas del SAT (Anexo 24 RMF)."""

    _VERSION_FILES = {
        "2024-01-22": "codigo_agrupador_2024.json",
        "2026-01-13": "codigo_agrupador_2026.json",
    }
    _VERSION_ALIASES = {
        "2024": "2024-01-22",
        "2026": "2026-01-13",
        "latest": "2026-01-13",
    }
    _DEFAULT_VERSION = "2026-01-13"

    _data_by_version: dict[str, list[CodigoAgrupadorSAT]] = {}
    _by_codigo_by_version: dict[str, dict[str, CodigoAgrupadorSAT]] = {}

    @classmethod
    def _resolve_version(cls, version: str | None) -> str:
        if not version:
            return cls._DEFAULT_VERSION
        normalized = version.strip().lower()
        if normalized in cls._VERSION_ALIASES:
            return cls._VERSION_ALIASES[normalized]
        if version in cls._VERSION_FILES:
            return version
        raise ValueError(f"Versión no soportada: {version}")

    @classmethod
    def _load_items(cls, version: str) -> list[CodigoAgrupadorSAT]:
        if version in cls._data_by_version:
            return cls._data_by_version[version]

        filename = cls._VERSION_FILES[version]
        data_path = (
            Path(__file__).parent.parent.parent.parent.parent.parent
            / "shared-data"
            / "sat"
            / "contabilidad_electronica"
            / filename
        )

        with open(data_path, encoding="utf-8") as fh:
            payload = json.load(fh)

        if isinstance(payload, list):
            items = payload
        elif isinstance(payload, dict):
            if isinstance(payload.get("items"), list):
                items = payload["items"]
            elif isinstance(payload.get("data"), list):
                items = payload["data"]
            else:
                items = [payload]
        else:
            items = []

        cls._data_by_version[version] = items
        cls._by_codigo_by_version[version] = {
            item["codigo"]: item for item in items if "codigo" in item
        }
        return items

    @classmethod
    def get_versions(cls) -> list[str]:
        """Lista de versiones disponibles."""

        return list(cls._VERSION_FILES.keys())

    @classmethod
    def get_default_version(cls) -> str:
        """Versión por defecto (más reciente)."""

        return cls._DEFAULT_VERSION

    @classmethod
    def get_all(cls, version: str | None = None) -> list[CodigoAgrupadorSAT]:
        """Obtiene todos los códigos agrupadores para una versión."""

        resolved = cls._resolve_version(version)
        return cls._load_items(resolved).copy()

    @classmethod
    def get_by_codigo(cls, codigo: str, version: str | None = None) -> CodigoAgrupadorSAT | None:
        """Obtiene un código agrupador por su clave."""

        resolved = cls._resolve_version(version)
        cls._load_items(resolved)
        return cls._by_codigo_by_version[resolved].get(codigo)

    @classmethod
    def is_valid(cls, codigo: str, version: str | None = None) -> bool:
        """Valida si un código existe."""

        return cls.get_by_codigo(codigo, version=version) is not None

    @classmethod
    def search(cls, query: str, version: str | None = None) -> list[CodigoAgrupadorSAT]:
        """Búsqueda parcial por nombre."""

        if not query:
            return []
        resolved = cls._resolve_version(version)
        data = cls._load_items(resolved)
        query_lower = query.lower()
        return [item for item in data if query_lower in item["nombre"].lower()]

    @classmethod
    def count(cls, version: str | None = None) -> int:
        """Número de registros en la versión indicada."""

        return len(cls.get_all(version=version))

    @classmethod
    def get_diff_2024_2026(cls) -> dict:
        """Obtiene el diff oficial entre 2024 y 2026."""

        data_path = (
            Path(__file__).parent.parent.parent.parent.parent.parent
            / "shared-data"
            / "sat"
            / "contabilidad_electronica"
            / "codigo_agrupador_diff_2024_2026.json"
        )
        with open(data_path, encoding="utf-8") as fh:
            return json.load(fh)
