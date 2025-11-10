"""
Catálogo c_ClavePedimento - Claves de Pedimento Aduanero

Identificadores del tipo de operación aduanera que ampara el CFDI.

Fuente: SAT - Anexo 22 de las RGCE
"""

import json
from pathlib import Path


class ClavePedimentoCatalog:
    """Catálogo de claves de pedimento aduanero"""

    _data: list[dict] | None = None
    _clave_by_code: dict[str, dict] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga los datos del catálogo desde el archivo JSON compartido"""
        if cls._data is None:
            current_file = Path(__file__)
            shared_data_path = (
                current_file.parent.parent.parent.parent.parent.parent
                / "shared-data"
                / "sat"
                / "comercio_exterior"
                / "claves_pedimento.json"
            )

            with open(shared_data_path, encoding="utf-8") as f:
                data = json.load(f)
                cls._data = data["claves"]

            cls._clave_by_code = {item["clave"]: item for item in cls._data}

    @classmethod
    def get_clave(cls, code: str) -> dict | None:
        """Obtiene una clave de pedimento por su código"""
        cls._load_data()
        return cls._clave_by_code.get(code.upper())

    @classmethod
    def is_valid(cls, code: str) -> bool:
        """Verifica si una clave de pedimento es válida"""
        return cls.get_clave(code) is not None

    @classmethod
    def is_export(cls, code: str) -> bool:
        """Verifica si la clave corresponde a exportación"""
        clave = cls.get_clave(code)
        return clave.get("regimen") == "exportacion" if clave else False

    @classmethod
    def is_import(cls, code: str) -> bool:
        """Verifica si la clave corresponde a importación"""
        clave = cls.get_clave(code)
        return clave.get("regimen") == "importacion" if clave else False

    @classmethod
    def get_by_regime(cls, regime: str) -> list[dict]:
        """
        Obtiene claves por régimen

        Args:
            regime: exportacion, importacion, retorno, transito, etc.
        """
        cls._load_data()
        return [item for item in cls._data if item.get("regimen") == regime]

    @classmethod
    def get_all(cls) -> list[dict]:
        """Retorna todas las claves de pedimento"""
        cls._load_data()
        return cls._data.copy()
