"""
Catálogo de Zonas Metropolitanas de México 2020

Fuente: SEDATU/INEGI/CONAPO - Metrópolis de México 2020
https://www.datos.gob.mx/dataset/metropolis_mexico_2020

Contiene 92 metrópolis conformadas por 421 municipios:
- 48 zonas metropolitanas (345 municipios)
- 22 metrópolis municipales
- 22 zonas conurbadas (54 municipios)
"""

import csv

from catalogmx.utils.shared_data import get_shared_data_path


class ZonasMetropolitanasCatalog:
    """Catálogo de Zonas Metropolitanas de México 2020"""

    _data: list[dict] | None = None
    _by_clave: dict[str, dict] | None = None
    _by_municipio: dict[str, list[dict]] | None = None
    _metropolis: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga los datos del catálogo"""
        if cls._data is not None:
            return

        data_path = get_shared_data_path("conapo", "municipios_tipologia.csv")

        cls._data = []
        cls._by_clave = {}
        cls._by_municipio = {}
        cls._metropolis = {}

        with open(data_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Normalizar claves INEGI
                cve_ent = str(row["clave_entidad"]).zfill(2)
                cve_mun = str(row["clave_municipio"]).zfill(3)
                cve_compuesta = f"{cve_ent}{cve_mun}"

                record = {
                    "clave_metropoli": row["clave_metropoli"],
                    "tipo": row["tipo"],
                    "nombre_metropoli": row["nombre"],
                    "cve_entidad": cve_ent,
                    "entidad": row["entidad"],
                    "cve_municipio": cve_mun,
                    "cve_inegi": cve_compuesta,
                    "municipio": row["municipio"],
                    "es_central": (
                        row.get("centrales_conurbacion_fisica") == "True"
                        or row.get("centrales_integracion_funcional") == "True"
                        or row.get("centrales_capital_200khab") == "True"
                        or row.get("centrales_0100khab") == "True"
                        or row.get("centrales_50khab") == "True"
                    ),
                    "es_exterior": (
                        row.get("exteriores_integracion_funcional") == "True"
                        or row.get("exteriores_continuidad_geografica") == "True"
                    ),
                }

                cls._data.append(record)
                cls._by_clave[cve_compuesta] = record

                # Index by municipio
                if cve_compuesta not in cls._by_municipio:
                    cls._by_municipio[cve_compuesta] = []
                cls._by_municipio[cve_compuesta].append(record)

                # Build metropolis index
                clave_m = row["clave_metropoli"]
                if clave_m not in cls._metropolis:
                    cls._metropolis[clave_m] = {
                        "clave": clave_m,
                        "nombre": row["nombre"],
                        "tipo": row["tipo"],
                        "municipios": [],
                    }
                cls._metropolis[clave_m]["municipios"].append(record)

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todos los registros de municipios metropolitanos"""
        cls._load_data()
        return cls._data.copy() if cls._data else []

    @classmethod
    def get_metropolis(cls) -> list[dict]:
        """Obtiene lista de todas las metrópolis"""
        cls._load_data()
        if not cls._metropolis:
            return []
        return [
            {
                "clave": m["clave"],
                "nombre": m["nombre"],
                "tipo": m["tipo"],
                "num_municipios": len(m["municipios"]),
            }
            for m in cls._metropolis.values()
        ]

    @classmethod
    def get_por_tipo(cls, tipo: str) -> list[dict]:
        """
        Obtiene metrópolis por tipo.

        Args:
            tipo: 'Zona metropolitana', 'Metrópoli municipal', 'Zona conurbada'
        """
        cls._load_data()
        if not cls._metropolis:
            return []
        return [
            {
                "clave": m["clave"],
                "nombre": m["nombre"],
                "tipo": m["tipo"],
                "num_municipios": len(m["municipios"]),
            }
            for m in cls._metropolis.values()
            if m["tipo"] == tipo
        ]

    @classmethod
    def buscar_por_municipio(cls, cve_entidad: str, cve_municipio: str) -> dict | None:
        """
        Busca si un municipio pertenece a alguna metrópolis.

        Args:
            cve_entidad: Clave de entidad INEGI (01-32)
            cve_municipio: Clave de municipio INEGI (001-570)

        Returns:
            Dict con información de la metrópolis o None
        """
        cls._load_data()
        cve = f"{cve_entidad.zfill(2)}{cve_municipio.zfill(3)}"
        records = cls._by_municipio.get(cve, []) if cls._by_municipio else []
        return records[0] if records else None

    @classmethod
    def get_municipios_de_metropoli(cls, clave_metropoli: str) -> list[dict]:
        """
        Obtiene todos los municipios de una metrópolis.

        Args:
            clave_metropoli: Clave de la metrópolis (ej: "01.1.01")

        Returns:
            Lista de municipios con sus datos INEGI
        """
        cls._load_data()
        if not cls._metropolis:
            return []
        m = cls._metropolis.get(clave_metropoli)
        return m["municipios"].copy() if m else []

    @classmethod
    def buscar_por_nombre(cls, nombre: str) -> list[dict]:
        """
        Busca metrópolis por nombre (búsqueda parcial).

        Args:
            nombre: Nombre o parte del nombre de la metrópolis

        Returns:
            Lista de metrópolis que coinciden
        """
        cls._load_data()
        if not cls._metropolis:
            return []
        nombre_upper = nombre.upper()
        return [
            {
                "clave": m["clave"],
                "nombre": m["nombre"],
                "tipo": m["tipo"],
                "num_municipios": len(m["municipios"]),
            }
            for m in cls._metropolis.values()
            if nombre_upper in m["nombre"].upper()
        ]

    @classmethod
    def es_municipio_metropolitano(cls, cve_entidad: str, cve_municipio: str) -> bool:
        """
        Verifica si un municipio pertenece a alguna metrópolis.

        Args:
            cve_entidad: Clave de entidad INEGI
            cve_municipio: Clave de municipio INEGI

        Returns:
            True si el municipio es metropolitano
        """
        return cls.buscar_por_municipio(cve_entidad, cve_municipio) is not None

    @classmethod
    def get_estadisticas(cls) -> dict:
        """Obtiene estadísticas del catálogo"""
        cls._load_data()

        if not cls._data or not cls._metropolis:
            return {}

        tipos = {}
        for m in cls._metropolis.values():
            t = m["tipo"]
            if t not in tipos:
                tipos[t] = {"metropolis": 0, "municipios": 0}
            tipos[t]["metropolis"] += 1
            tipos[t]["municipios"] += len(m["municipios"])

        return {
            "total_metropolis": len(cls._metropolis),
            "total_municipios": len(cls._data),
            "por_tipo": tipos,
        }
