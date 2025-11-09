"""Catálogo c_CodigoTransporteAereo - Aeropuertos"""
import json
from pathlib import Path

class AeropuertosCatalog:
    _data: list[dict] | None = None
    _by_code: dict[str, dict] | None = None
    _by_iata: dict[str, dict] | None = None
    _by_icao: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        if cls._data is None:
            path = Path(__file__).parent.parent.parent.parent.parent.parent / 'shared-data' / 'sat' / 'carta_porte_3' / 'aeropuertos.json'
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                cls._data = data['aeropuertos']
            cls._by_code = {item['code']: item for item in cls._data}
            cls._by_iata = {item['iata']: item for item in cls._data}
            cls._by_icao = {item['icao']: item for item in cls._data}

    @classmethod
    def get_aeropuerto(cls, code: str) -> dict | None:
        """Obtiene aeropuerto por código SAT"""
        cls._load_data()
        return cls._by_code.get(code)

    @classmethod
    def get_by_iata(cls, iata: str) -> dict | None:
        """Obtiene aeropuerto por código IATA"""
        cls._load_data()
        return cls._by_iata.get(iata)

    @classmethod
    def get_by_icao(cls, icao: str) -> dict | None:
        """Obtiene aeropuerto por código ICAO"""
        cls._load_data()
        return cls._by_icao.get(icao)

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si un código de aeropuerto es válido"""
        return cls.get_aeropuerto(code) is not None

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todos los aeropuertos"""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_by_state(cls, state: str) -> list[dict]:
        """Obtiene aeropuertos por estado"""
        cls._load_data()
        return [a for a in cls._data if a['state'] == state]
