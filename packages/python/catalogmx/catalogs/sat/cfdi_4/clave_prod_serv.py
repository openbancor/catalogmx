"""
SAT CFDI 4.0 - Clave de Producto o Servicio (c_ClaveProdServ)

Catálogo de claves de productos y servicios para facturación CFDI.
Contiene ~52,000 códigos oficiales basados en UNSPSC (United Nations
Standard Products and Services Code).

Este módulo usa SQLite con FTS5 para búsqueda eficiente de texto completo.
"""

import sqlite3
from pathlib import Path
from typing import TypedDict


class ClaveProdServ(TypedDict):
    """Estructura de una clave de producto/servicio"""

    id: str
    descripcion: str
    incluirIVATrasladado: str
    incluirIEPSTrasladado: str
    complementoQueDebeIncluir: str
    palabrasSimilares: str
    fechaInicioVigencia: str
    fechaFinVigencia: str
    estimuloFranjaFronteriza: str


class ClaveProdServCatalog:
    """
    Catálogo de claves de productos y servicios SAT CFDI 4.0.

    Implementación basada en SQLite con búsqueda FTS5 para alto rendimiento.

    Características:
    - ~52,000 códigos de productos y servicios
    - Basado en estándar UNSPSC (ONU)
    - Búsqueda full-text con FTS5
    - Estructura jerárquica (segmento → familia → clase → producto)
    - Indicadores de IVA e IEPS

    WARNING: Este es un catálogo grande. Use search() o get_by_prefix()
    en lugar de get_all() para mejor rendimiento.

    Ejemplo:
        >>> from catalogmx.catalogs.sat.cfdi_4 import ClaveProdServCatalog
        >>>
        >>> # Buscar productos
        >>> results = ClaveProdServCatalog.search("computadora", limit=10)
        >>> for item in results:
        ...     print(f"{item['id']}: {item['descripcion']}")
        >>>
        >>> # Obtener por clave exacta
        >>> producto = ClaveProdServCatalog.get_clave("43211500")
        >>> print(producto['descripcion'])
        >>>
        >>> # Buscar por prefijo (navegación jerárquica)
        >>> familia = ClaveProdServCatalog.get_by_prefix("4321", limit=50)
        >>> print(f"Productos en familia 4321: {len(familia)}")
    """

    _db_path: Path | None = None
    _connection: sqlite3.Connection | None = None

    @classmethod
    def _get_db_path(cls) -> Path:
        """Obtiene la ruta a la base de datos SQLite"""
        if cls._db_path is None:
            # Path: catalogmx/packages/python/catalogmx/catalogs/sat/cfdi_4/clave_prod_serv.py
            # Target: catalogmx/packages/shared-data/sqlite/clave_prod_serv.db
            cls._db_path = (
                Path(__file__).parent.parent.parent.parent.parent.parent
                / "shared-data"
                / "sqlite"
                / "clave_prod_serv.db"
            )
        return cls._db_path

    @classmethod
    def _get_connection(cls) -> sqlite3.Connection:
        """Obtiene conexión a la base de datos (singleton)"""
        if cls._connection is None:
            db_path = cls._get_db_path()
            if not db_path.exists():
                raise FileNotFoundError(
                    f"Database not found at {db_path}. "
                    "Please ensure the clave_prod_serv.db file exists."
                )
            cls._connection = sqlite3.connect(str(db_path))
            cls._connection.row_factory = sqlite3.Row
            cls._ensure_schema(cls._connection)
        return cls._connection

    @classmethod
    def _ensure_schema(cls, conn: sqlite3.Connection) -> None:
        """Crea tablas mínimas si el archivo existe pero está vacío."""
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS clave_prod_serv (
                clave TEXT PRIMARY KEY,
                descripcion TEXT,
                incluye_iva INTEGER,
                incluye_ieps INTEGER,
                complemento TEXT,
                palabras_similares TEXT,
                fecha_inicio_vigencia TEXT,
                fecha_fin_vigencia TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS clave_prod_serv_fts USING fts5(
                clave,
                descripcion,
                complemento,
                palabras_similares,
                content='clave_prod_serv',
                content_rowid='rowid'
            )
            """
        )
        cursor.execute("SELECT COUNT(*) FROM clave_prod_serv")
        (count,) = cursor.fetchone()
        if count == 0:
            sample_rows = [
                (
                    "01010101",
                    "No aplica",
                    0,
                    0,
                    "",
                    "servicio no aplica",
                    "",
                    "",
                ),
                (
                    "43211500",
                    "Computadoras personales",
                    1,
                    0,
                    "",
                    "computadora pc laptop",
                    "",
                    "",
                ),
            ]
            cursor.executemany(
                """
                INSERT INTO clave_prod_serv
                (clave, descripcion, incluye_iva, incluye_ieps, complemento, palabras_similares, fecha_inicio_vigencia, fecha_fin_vigencia)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                sample_rows,
            )
            cursor.executemany(
                "INSERT INTO clave_prod_serv_fts (clave, descripcion, complemento, palabras_similares) VALUES (?, ?, ?, ?)",
                [(row[0], row[1], row[4], row[5]) for row in sample_rows],
            )
            conn.commit()

    @classmethod
    def _row_to_clave(cls, row: sqlite3.Row) -> ClaveProdServ:
        """Convierte una fila de SQLite a ClaveProdServ"""
        return {
            "id": row["clave"],
            "descripcion": row["descripcion"],
            "incluirIVATrasladado": "Sí" if row["incluye_iva"] == 1 else "No",
            "incluirIEPSTrasladado": "Sí" if row["incluye_ieps"] == 1 else "No",
            "complementoQueDebeIncluir": row["complemento"] or "",
            "palabrasSimilares": row["palabras_similares"] or "",
            "fechaInicioVigencia": row["fecha_inicio_vigencia"] or "",
            "fechaFinVigencia": row["fecha_fin_vigencia"] or "",
            "estimuloFranjaFronteriza": "",
        }

    @classmethod
    def get_all(cls) -> list[ClaveProdServ]:
        """
        Obtiene todas las claves de productos/servicios.

        WARNING: Retorna ~52,000 productos/servicios. Para mejor rendimiento,
        use search() o get_by_prefix() en su lugar.

        Returns:
            Lista completa de productos/servicios

        Ejemplo:
            >>> all_claves = ClaveProdServCatalog.get_all()
            >>> print(f"Total: {len(all_claves)}")  # ~52,000
        """
        conn = cls._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clave_prod_serv")
        return [cls._row_to_clave(row) for row in cursor.fetchall()]

    @classmethod
    def get_clave(cls, id: str) -> ClaveProdServ | None:
        """
        Obtiene una clave por su ID.

        Args:
            id: Clave de 8 dígitos (ej: "10101500", "43211500")

        Returns:
            Producto/servicio o None si no existe

        Ejemplo:
            >>> producto = ClaveProdServCatalog.get_clave("43211500")
            >>> if producto:
            ...     print(producto['descripcion'])
        """
        conn = cls._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clave_prod_serv WHERE clave = ?", (id,))
        row = cursor.fetchone()
        return cls._row_to_clave(row) if row else None

    @classmethod
    def is_valid(cls, id: str) -> bool:
        """
        Verifica si una clave de producto/servicio existe.

        Args:
            id: Clave de 8 dígitos

        Returns:
            True si existe, False en caso contrario

        Ejemplo:
            >>> ClaveProdServCatalog.is_valid("43211500")  # True
            >>> ClaveProdServCatalog.is_valid("99999999")  # False
        """
        return cls.get_clave(id) is not None

    @classmethod
    def search(cls, keyword: str, limit: int = 100) -> list[ClaveProdServ]:
        """
        Busca productos/servicios usando FTS5 full-text search.

        Busca en: descripción, complemento y palabras similares.

        Args:
            keyword: Palabra clave a buscar
            limit: Máximo número de resultados (default: 100)

        Returns:
            Lista de productos/servicios que coinciden

        Ejemplo:
            >>> resultados = ClaveProdServCatalog.search("computadora", limit=20)
            >>> for item in resultados:
            ...     print(f"{item['id']}: {item['descripcion']}")
        """
        conn = cls._get_connection()
        cursor = conn.cursor()

        # Use FTS5 for fast full-text search
        query = """
            SELECT cps.*
            FROM clave_prod_serv_fts fts
            JOIN clave_prod_serv cps ON fts.clave = cps.clave
            WHERE clave_prod_serv_fts MATCH ?
            LIMIT ?
        """

        cursor.execute(query, (keyword, limit))
        return [cls._row_to_clave(row) for row in cursor.fetchall()]

    @classmethod
    def search_simple(cls, keyword: str, limit: int = 100) -> list[ClaveProdServ]:
        """
        Búsqueda simple sin FTS5 (fallback o búsqueda parcial).

        Args:
            keyword: Palabra clave a buscar en descripción y palabras similares
            limit: Máximo número de resultados (default: 100)

        Returns:
            Lista de productos/servicios que coinciden

        Ejemplo:
            >>> resultados = ClaveProdServCatalog.search_simple("comput", limit=10)
        """
        conn = cls._get_connection()
        cursor = conn.cursor()

        keyword_pattern = f"%{keyword}%"
        query = """
            SELECT * FROM clave_prod_serv
            WHERE descripcion LIKE ? OR palabras_similares LIKE ?
            LIMIT ?
        """

        cursor.execute(query, (keyword_pattern, keyword_pattern, limit))
        return [cls._row_to_clave(row) for row in cursor.fetchall()]

    @classmethod
    def get_by_prefix(cls, prefix: str, limit: int = 500) -> list[ClaveProdServ]:
        """
        Obtiene productos/servicios por prefijo de clave.

        Útil para navegación jerárquica del catálogo UNSPSC:
        - 2 dígitos: Segmento (ej: "43" = Tecnología de información)
        - 4 dígitos: Familia (ej: "4321" = Computadoras)
        - 6 dígitos: Clase (ej: "432115" = Computadoras personales)
        - 8 dígitos: Producto específico

        Args:
            prefix: Prefijo de la clave (2, 4, 6 u 8 dígitos)
            limit: Máximo número de resultados (default: 500)

        Returns:
            Lista de productos/servicios con ese prefijo

        Ejemplo:
            >>> # Todos los productos en segmento 43 (TI)
            >>> ti = ClaveProdServCatalog.get_by_prefix("43", limit=100)
            >>>
            >>> # Familia 4321 (Computadoras)
            >>> comps = ClaveProdServCatalog.get_by_prefix("4321", limit=50)
        """
        conn = cls._get_connection()
        cursor = conn.cursor()

        query = """
            SELECT * FROM clave_prod_serv
            WHERE clave LIKE ?
            LIMIT ?
        """

        cursor.execute(query, (f"{prefix}%", limit))
        return [cls._row_to_clave(row) for row in cursor.fetchall()]

    @classmethod
    def get_con_iva(cls, limit: int = 1000) -> list[ClaveProdServ]:
        """
        Obtiene productos/servicios que incluyen IVA trasladado.

        Args:
            limit: Máximo número de resultados (default: 1000)

        Returns:
            Lista de productos/servicios con IVA

        Ejemplo:
            >>> con_iva = ClaveProdServCatalog.get_con_iva(limit=100)
            >>> print(f"Productos con IVA: {len(con_iva)}")
        """
        conn = cls._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clave_prod_serv WHERE incluye_iva = 1 LIMIT ?", (limit,))
        return [cls._row_to_clave(row) for row in cursor.fetchall()]

    @classmethod
    def get_con_ieps(cls, limit: int = 1000) -> list[ClaveProdServ]:
        """
        Obtiene productos/servicios que incluyen IEPS trasladado.

        Args:
            limit: Máximo número de resultados (default: 1000)

        Returns:
            Lista de productos/servicios con IEPS

        Ejemplo:
            >>> con_ieps = ClaveProdServCatalog.get_con_ieps(limit=100)
            >>> print(f"Productos con IEPS: {len(con_ieps)}")
        """
        conn = cls._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clave_prod_serv WHERE incluye_ieps = 1 LIMIT ?", (limit,))
        return [cls._row_to_clave(row) for row in cursor.fetchall()]

    @classmethod
    def get_vigentes(cls, limit: int = 10000) -> list[ClaveProdServ]:
        """
        Obtiene productos/servicios vigentes (sin fecha de fin de vigencia).

        Args:
            limit: Máximo número de resultados (default: 10000)

        Returns:
            Lista de productos/servicios vigentes

        Ejemplo:
            >>> vigentes = ClaveProdServCatalog.get_vigentes(limit=100)
        """
        conn = cls._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM clave_prod_serv WHERE fecha_fin_vigencia IS NULL OR fecha_fin_vigencia = '' LIMIT ?",
            (limit,),
        )
        return [cls._row_to_clave(row) for row in cursor.fetchall()]

    @classmethod
    def get_total_count(cls) -> int:
        """
        Obtiene el total de productos/servicios en el catálogo.

        Returns:
            Número total de productos/servicios (~52,000)

        Ejemplo:
            >>> total = ClaveProdServCatalog.get_total_count()
            >>> print(f"Total productos/servicios: {total:,}")
        """
        conn = cls._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM clave_prod_serv")
        return cursor.fetchone()[0]

    @classmethod
    def get_estadisticas(cls) -> dict[str, int]:
        """
        Obtiene estadísticas del catálogo.

        Returns:
            Diccionario con estadísticas

        Ejemplo:
            >>> stats = ClaveProdServCatalog.get_estadisticas()
            >>> print(f"Total: {stats['total']:,}")
            >>> print(f"Con IVA: {stats['con_iva']:,}")
            >>> print(f"Con IEPS: {stats['con_ieps']:,}")
        """
        conn = cls._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM clave_prod_serv")
        total = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM clave_prod_serv WHERE incluye_iva = 1")
        con_iva = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM clave_prod_serv WHERE incluye_ieps = 1")
        con_ieps = cursor.fetchone()[0]

        cursor.execute(
            "SELECT COUNT(*) FROM clave_prod_serv WHERE fecha_fin_vigencia IS NULL OR fecha_fin_vigencia = ''"
        )
        vigentes = cursor.fetchone()[0]

        return {
            "total": total,
            "con_iva": con_iva,
            "con_ieps": con_ieps,
            "vigentes": vigentes,
            "obsoletos": total - vigentes,
        }
