"""Catálogo de Localidades INEGI (filtrado por población)"""
import json
from pathlib import Path

from catalogmx.utils.text import normalize_text


class LocalidadesCatalog:
    """
    Catálogo de localidades de México con 1,000+ habitantes.

    Incluye:
    - 10,635 localidades con población >= 1,000 habitantes
    - Coordenadas GPS (latitud, longitud)
    - Población y viviendas habitadas
    - Clasificación urbano/rural
    """

    _data: list[dict] | None = None
    _by_cvegeo: dict[str, dict] | None = None
    _by_municipio: dict[str, list[dict]] | None = None
    _by_entidad: dict[str, list[dict]] | None = None

    @classmethod
    def _load_data(cls) -> None:
        if cls._data is None:
            # Path: catalogmx/packages/python/catalogmx/catalogs/inegi/localidades.py
            # Target: catalogmx/packages/shared-data/inegi/localidades.json
            path = Path(__file__).parent.parent.parent.parent.parent / 'shared-data' / 'inegi' / 'localidades.json'
            with open(path, encoding='utf-8') as f:
                cls._data = json.load(f)

            # Crear índices
            cls._by_cvegeo = {item['cvegeo']: item for item in cls._data}

            # Índice por municipio
            cls._by_municipio = {}
            for item in cls._data:
                cve_mun = item['cve_municipio']
                if cve_mun not in cls._by_municipio:
                    cls._by_municipio[cve_mun] = []
                cls._by_municipio[cve_mun].append(item)

            # Índice por entidad
            cls._by_entidad = {}
            for item in cls._data:
                cve_ent = item['cve_entidad']
                if cve_ent not in cls._by_entidad:
                    cls._by_entidad[cve_ent] = []
                cls._by_entidad[cve_ent].append(item)

    @classmethod
    def get_localidad(cls, cvegeo: str) -> dict | None:
        """
        Obtiene una localidad por su clave geoestadística (CVEGEO).

        Args:
            cvegeo: Clave geoestadística (ej: "010010001")

        Returns:
            Diccionario con datos de la localidad o None si no existe
        """
        cls._load_data()
        return cls._by_cvegeo.get(cvegeo)

    @classmethod
    def is_valid(cls, cvegeo: str) -> bool:
        """Verifica si una clave geoestadística existe"""
        return cls.get_localidad(cvegeo) is not None

    @classmethod
    def get_by_municipio(cls, cve_municipio: str) -> list[dict]:
        """
        Obtiene todas las localidades de un municipio.

        Args:
            cve_municipio: Código del municipio (ej: "001")

        Returns:
            Lista de localidades del municipio
        """
        cls._load_data()
        return cls._by_municipio.get(cve_municipio, []).copy()

    @classmethod
    def get_by_entidad(cls, cve_entidad: str) -> list[dict]:
        """
        Obtiene todas las localidades de un estado.

        Args:
            cve_entidad: Código del estado (ej: "01")

        Returns:
            Lista de localidades del estado
        """
        cls._load_data()
        cve_ent = cve_entidad.zfill(2)
        return cls._by_entidad.get(cve_ent, []).copy()

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todas las localidades"""
        cls._load_data()
        return cls._data.copy()

    @classmethod
    def get_urbanas(cls) -> list[dict]:
        """Obtiene solo localidades urbanas"""
        cls._load_data()
        return [loc for loc in cls._data if loc['ambito'] == 'U']

    @classmethod
    def get_rurales(cls) -> list[dict]:
        """Obtiene solo localidades rurales"""
        cls._load_data()
        return [loc for loc in cls._data if loc['ambito'] == 'R']

    @classmethod
    def search_by_name(cls, nombre: str) -> list[dict]:
        """
        Busca localidades por nombre (búsqueda parcial, insensible a acentos).

        Args:
            nombre: Nombre o parte del nombre a buscar

        Returns:
            Lista de localidades que coinciden

        Ejemplo:
            >>> # Búsqueda con o sin acentos funciona igual
            >>> locs = LocalidadesCatalog.search_by_name("san jose")
            >>> locs = LocalidadesCatalog.search_by_name("san josé")  # mismo resultado
        """
        cls._load_data()
        nombre_normalized = normalize_text(nombre)
        return [loc for loc in cls._data
                if nombre_normalized in normalize_text(loc['nom_localidad'])]

    @classmethod
    def get_by_coordinates(cls, lat: float, lon: float, radio_km: float = 10) -> list[dict]:
        """
        Busca localidades cercanas a unas coordenadas.

        Args:
            lat: Latitud
            lon: Longitud
            radio_km: Radio de búsqueda en kilómetros (default: 10)

        Returns:
            Lista de localidades dentro del radio, ordenadas por distancia
        """
        from math import atan2, cos, radians, sin, sqrt

        cls._load_data()

        def distancia_haversine(lat1, lon1, lat2, lon2):
            """Calcula distancia en km entre dos puntos GPS"""
            R = 6371  # Radio de la Tierra en km

            dlat = radians(lat2 - lat1)
            dlon = radians(lon2 - lon1)

            a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))

            return R * c

        resultados = []
        for loc in cls._data:
            if loc['latitud'] is None or loc['longitud'] is None:
                continue

            distancia = distancia_haversine(lat, lon, loc['latitud'], loc['longitud'])
            if distancia <= radio_km:
                loc_con_distancia = loc.copy()
                loc_con_distancia['distancia_km'] = round(distancia, 2)
                resultados.append(loc_con_distancia)

        # Ordenar por distancia
        resultados.sort(key=lambda x: x['distancia_km'])
        return resultados

    @classmethod
    def get_by_population_range(cls, min_pob: int, max_pob: int | None = None) -> list[dict]:
        """
        Obtiene localidades en un rango de población.

        Args:
            min_pob: Población mínima
            max_pob: Población máxima (None para sin límite)

        Returns:
            Lista de localidades en el rango
        """
        cls._load_data()

        if max_pob is None:
            return [loc for loc in cls._data if loc['poblacion_total'] >= min_pob]
        else:
            return [loc for loc in cls._data
                    if min_pob <= loc['poblacion_total'] <= max_pob]

