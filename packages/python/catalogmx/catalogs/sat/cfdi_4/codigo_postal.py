"""Catálogo c_CodigoPostal para CFDI 4.0

Códigos postales mexicanos usados en:
- Comprobante.LugarExpedicion (CP del domicilio fiscal del emisor)
- Receptor.DomicilioFiscalReceptor (CP del domicilio fiscal del receptor)
- ACuentaTerceros.DomicilioFiscalACuentaTerceros

Usa la base de datos SQLite de SEPOMEX (~32,000 CPs únicos, 157K+ asentamientos).
"""

import re
import sqlite3
from pathlib import Path
from typing import TypedDict


class CodigoPostalInfo(TypedDict, total=False):
    """Estructura de un código postal"""

    cp: str
    estado: str
    codigo_estado: str
    municipio: str
    codigo_municipio: str
    ciudad: str
    asentamientos: list[str]


class CodigoPostalCatalog:
    """
    Catálogo de códigos postales del SAT (c_CodigoPostal).

    Implementación basada en SQLite con datos de SEPOMEX.

    Características:
    - ~32,000 códigos postales únicos
    - 157,000+ asentamientos (colonias)
    - Mapeo a estado y municipio
    - Validación de formato y existencia

    Ejemplo:
        >>> from catalogmx.catalogs.sat.cfdi_4 import CodigoPostalCatalog
        >>>
        >>> # Validar código postal
        >>> CodigoPostalCatalog.is_valid("06600")
        True
        >>>
        >>> # Obtener información
        >>> info = CodigoPostalCatalog.get_codigo_postal("06600")
        >>> print(info['estado'])  # Ciudad de México
        >>> print(info['municipio'])  # Cuauhtémoc
        >>>
        >>> # Buscar por estado
        >>> cps = CodigoPostalCatalog.get_by_estado("09")  # CDMX
    """

    _db_path: Path | None = None
    _connection: sqlite3.Connection | None = None
    _CP_PATTERN = re.compile(r"^\d{5}$")

    @classmethod
    def _get_db_path(cls) -> Path:
        """Obtiene la ruta a la base de datos SQLite"""
        if cls._db_path is None:
            from catalogmx.utils.shared_data import get_shared_data_path

            cls._db_path = get_shared_data_path("sqlite", "sepomex.db")
        return cls._db_path

    @classmethod
    def _get_connection(cls) -> sqlite3.Connection:
        """Obtiene conexión a la base de datos (singleton)"""
        if cls._connection is None:
            db_path = cls._get_db_path()
            if not db_path.exists():
                raise FileNotFoundError(
                    f"Database not found at {db_path}. "
                    "Please ensure the sepomex.db file exists."
                )
            cls._connection = sqlite3.connect(str(db_path))
            cls._connection.row_factory = sqlite3.Row
        return cls._connection

    @classmethod
    def close(cls) -> None:
        """Cierra la conexión a la base de datos."""
        if cls._connection is not None:
            cls._connection.close()
            cls._connection = None

    @classmethod
    def is_valid_format(cls, cp: str) -> bool:
        """Valida que el formato sea 5 dígitos"""
        return bool(cls._CP_PATTERN.match(cp))

    @classmethod
    def is_valid(cls, cp: str) -> bool:
        """Valida que un código postal exista en el catálogo"""
        if not cls.is_valid_format(cp):
            return False
        conn = cls._get_connection()
        cursor = conn.execute(
            "SELECT 1 FROM codigos_postales WHERE cp = ? LIMIT 1",
            (cp,),
        )
        return cursor.fetchone() is not None

    @classmethod
    def get_codigo_postal(cls, cp: str) -> CodigoPostalInfo | None:
        """
        Obtiene información de un código postal.

        Retorna el primer asentamiento encontrado con datos de estado/municipio,
        más la lista completa de asentamientos en ese CP.
        """
        if not cls.is_valid_format(cp):
            return None
        conn = cls._get_connection()
        cursor = conn.execute(
            "SELECT cp, estado, codigo_estado, municipio, codigo_municipio, "
            "ciudad, asentamiento FROM codigos_postales WHERE cp = ?",
            (cp,),
        )
        rows = cursor.fetchall()
        if not rows:
            return None
        first = rows[0]
        return CodigoPostalInfo(
            cp=first["cp"],
            estado=first["estado"],
            codigo_estado=first["codigo_estado"],
            municipio=first["municipio"],
            codigo_municipio=first["codigo_municipio"],
            ciudad=first["ciudad"] or "",
            asentamientos=[row["asentamiento"] for row in rows],
        )

    @classmethod
    def get_estado(cls, cp: str) -> str | None:
        """Obtiene el nombre del estado para un código postal"""
        info = cls.get_codigo_postal(cp)
        return info["estado"] if info else None

    @classmethod
    def get_municipio(cls, cp: str) -> str | None:
        """Obtiene el nombre del municipio para un código postal"""
        info = cls.get_codigo_postal(cp)
        return info["municipio"] if info else None

    @classmethod
    def get_codigo_estado(cls, cp: str) -> str | None:
        """Obtiene el código de estado (2 dígitos) para un código postal"""
        info = cls.get_codigo_postal(cp)
        return info["codigo_estado"] if info else None

    @classmethod
    def get_by_estado(cls, codigo_estado: str, limit: int = 100) -> list[dict]:
        """Obtiene códigos postales por código de estado"""
        conn = cls._get_connection()
        cursor = conn.execute(
            "SELECT DISTINCT cp, estado, municipio, ciudad "
            "FROM codigos_postales WHERE codigo_estado = ? "
            "ORDER BY cp LIMIT ?",
            (codigo_estado, limit),
        )
        return [dict(row) for row in cursor.fetchall()]

    @classmethod
    def search(cls, query: str, limit: int = 20) -> list[dict]:
        """
        Busca códigos postales por asentamiento, municipio o ciudad.

        Args:
            query: Texto a buscar
            limit: Máximo de resultados

        Returns:
            Lista de resultados con cp, asentamiento, municipio, estado
        """
        conn = cls._get_connection()
        like_query = f"%{query}%"
        cursor = conn.execute(
            "SELECT cp, asentamiento, municipio, estado, ciudad "
            "FROM codigos_postales "
            "WHERE asentamiento LIKE ? OR municipio LIKE ? OR ciudad LIKE ? "
            "ORDER BY cp LIMIT ?",
            (like_query, like_query, like_query, limit),
        )
        return [dict(row) for row in cursor.fetchall()]

    @classmethod
    def get_estadisticas(cls) -> dict:
        """Obtiene estadísticas del catálogo"""
        conn = cls._get_connection()
        cursor = conn.execute("SELECT COUNT(DISTINCT cp) FROM codigos_postales")
        total_cp = cursor.fetchone()[0]
        cursor = conn.execute("SELECT COUNT(*) FROM codigos_postales")
        total_asentamientos = cursor.fetchone()[0]
        cursor = conn.execute(
            "SELECT COUNT(DISTINCT codigo_estado) FROM codigos_postales"
        )
        total_estados = cursor.fetchone()[0]
        return {
            "total_codigos_postales": total_cp,
            "total_asentamientos": total_asentamientos,
            "total_estados": total_estados,
        }
