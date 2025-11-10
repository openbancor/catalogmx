"""Catálogo de Códigos Postales SEPOMEX"""
import json
from pathlib import Path

from catalogmx.utils.text import normalize_text


class CodigosPostales:
    _data: list[dict] | None = None
    _by_cp: dict[str, list[dict]] | None = None
    _by_estado: dict[str, list[dict]] | None = None
    _by_estado_normalized: dict[str, list[dict]] | None = None
    _by_municipio_normalized: dict[str, list[dict]] | None = None

    @classmethod
    def _load_data(cls) -> None:
        if cls._data is None:
            # Path: catalogmx/packages/python/catalogmx/catalogs/sepomex/codigos_postales.py
            # Target: catalogmx/packages/shared-data/sepomex/codigos_postales_completo.json
            path = Path(__file__).parent.parent.parent.parent.parent / 'shared-data' / 'sepomex' / 'codigos_postales_completo.json'
            with open(path, encoding='utf-8') as f:
                cls._data = json.load(f)

            # Index by CP (can have multiple settlements)
            cls._by_cp = {}
            for item in cls._data:
                cp = item['cp']
                if cp not in cls._by_cp:
                    cls._by_cp[cp] = []
                cls._by_cp[cp].append(item)

            # Index by estado
            cls._by_estado = {}
            for item in cls._data:
                estado = item['estado']
                if estado not in cls._by_estado:
                    cls._by_estado[estado] = []
                cls._by_estado[estado].append(item)

            # Index by estado normalized (accent-insensitive)
            cls._by_estado_normalized = {}
            for item in cls._data:
                estado_norm = normalize_text(item['estado'])
                if estado_norm not in cls._by_estado_normalized:
                    cls._by_estado_normalized[estado_norm] = []
                cls._by_estado_normalized[estado_norm].append(item)

            # Index by municipio normalized (accent-insensitive)
            cls._by_municipio_normalized = {}
            for item in cls._data:
                municipio_norm = normalize_text(item['municipio'])
                if municipio_norm not in cls._by_municipio_normalized:
                    cls._by_municipio_normalized[municipio_norm] = []
                cls._by_municipio_normalized[municipio_norm].append(item)

    @classmethod
    def get_by_cp(cls, cp: str) -> list[dict]:
        """Obtiene todos los asentamientos de un código postal"""
        cls._load_data()
        return cls._by_cp.get(cp, [])

    @classmethod
    def is_valid(cls, cp: str) -> bool:
        """Verifica si un código postal existe"""
        cls._load_data()
        return cp in cls._by_cp

    @classmethod
    def get_by_estado(cls, estado: str) -> list[dict]:
        """Obtiene todos los códigos postales de un estado (insensible a acentos)"""
        cls._load_data()
        estado_normalized = normalize_text(estado)
        return cls._by_estado_normalized.get(estado_normalized, [])

    @classmethod
    def get_by_municipio(cls, municipio: str) -> list[dict]:
        """Obtiene todos los códigos postales de un municipio (insensible a acentos)"""
        cls._load_data()
        municipio_normalized = normalize_text(municipio)
        return cls._by_municipio_normalized.get(municipio_normalized, [])

    @classmethod
    def search_by_colonia(cls, colonia: str) -> list[dict]:
        """Busca códigos postales por nombre de colonia (insensible a acentos)"""
        cls._load_data()
        colonia_normalized = normalize_text(colonia)
        return [
            item for item in cls._data
            if colonia_normalized in normalize_text(item['asentamiento'])
        ]

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todos los códigos postales"""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_municipio(cls, cp: str) -> str | None:
        """Obtiene el municipio de un código postal"""
        settlements = cls.get_by_cp(cp)
        return settlements[0]['municipio'] if settlements else None

    @classmethod
    def get_estado(cls, cp: str) -> str | None:
        """Obtiene el estado de un código postal"""
        settlements = cls.get_by_cp(cp)
        return settlements[0]['estado'] if settlements else None


class CodigosPostalesSQLite:
    _db_path = None
    _connection = None

    @classmethod
    def _get_db_path(cls):
        if cls._db_path is None:
            cls._db_path = Path(__file__).parent.parent.parent.parent.parent / 'shared-data' / 'sqlite' / 'sepomex.db'
        return cls._db_path

    @classmethod
    def _get_connection(cls):
        import sqlite3
        if cls._connection is None:
            path = cls._get_db_path()
            if not path.exists():
                raise FileNotFoundError(f"Database not found at {path}. Please run the migration script.")
            cls._connection = sqlite3.connect(path)
            cls._connection.row_factory = sqlite3.Row
        return cls._connection

    @classmethod
    def _query(cls, query: str, params: tuple = ()):
        conn = cls._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    @classmethod
    def get_by_cp(cls, cp: str) -> list[dict]:
        """Obtiene todos los asentamientos de un código postal desde SQLite"""
        return cls._query("SELECT * FROM codigos_postales WHERE cp = ?", (cp,))

    @classmethod
    def is_valid(cls, cp: str) -> bool:
        """Verifica si un código postal existe en SQLite"""
        result = cls._query("SELECT 1 FROM codigos_postales WHERE cp = ? LIMIT 1", (cp,))
        return len(result) > 0

    @classmethod
    def get_by_estado(cls, estado: str) -> list[dict]:
        """Obtiene todos los códigos postales de un estado desde SQLite"""
        return cls._query("SELECT * FROM codigos_postales WHERE estado = ?", (estado,))

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todos los códigos postales desde SQLite"""
        return cls._query("SELECT * FROM codigos_postales")

    @classmethod
    def get_municipio(cls, cp: str) -> str | None:
        """Obtiene el municipio de un código postal desde SQLite"""
        settlements = cls.get_by_cp(cp)
        return settlements[0]['municipio'] if settlements else None

    @classmethod
    def get_estado(cls, cp: str) -> str | None:
        """Obtiene el estado de un código postal desde SQLite"""
        settlements = cls.get_by_cp(cp)
        return settlements[0]['estado'] if settlements else None
