"""
Sistema Urbano Nacional 2020

Fuente: CONAPO
https://www.datos.gob.mx/dataset/sistema_urbano_nacional
"""

import csv

from catalogmx.utils.shared_data import get_shared_data_path


class SistemaUrbanoNacionalCatalog:
    """Catálogo del Sistema Urbano Nacional 2020"""

    _data: list[dict] | None = None
    _by_clave: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga los datos del catálogo"""
        if cls._data is not None:
            return

        data_path = get_shared_data_path("conapo", "sun_2020.csv")

        cls._data = []
        cls._by_clave = {}

        with open(data_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                record = {
                    "cve_ciudad": row["cve_cd"],
                    "nombre": row["nom_cd"],
                    "poblacion_2020": int(row["pob_2020"]),
                }
                cls._data.append(record)
                cls._by_clave[row["cve_cd"]] = record

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todas las ciudades del SUN"""
        cls._load_data()
        return cls._data.copy() if cls._data else []

    @classmethod
    def get_por_clave(cls, cve_ciudad: str) -> dict | None:
        """Obtiene ciudad por clave"""
        cls._load_data()
        return cls._by_clave.get(cve_ciudad) if cls._by_clave else None
