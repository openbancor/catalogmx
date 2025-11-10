"""
Catálogo de monedas y divisas internacionales (Banxico)

Este módulo proporciona acceso al catálogo de monedas y divisas
internacionales utilizadas en operaciones cambiarias en México,
basado en códigos ISO 4217.
"""

import json
from pathlib import Path
from typing import TypedDict


class MonedaDivisa(TypedDict, total=False):
    """Estructura de una moneda o divisa"""

    codigo_iso: str
    numero_iso: str
    moneda: str
    pais: str
    simbolo: str
    decimales: int
    moneda_nacional: bool
    tipo_cambio_banxico: bool
    tipo_cambio_fix: bool  # Optional
    activa: bool
    notas: str  # Optional


class MonedasDivisas:
    """
    Catálogo de monedas y divisas internacionales.

    Incluye todas las monedas con las que Banco de México publica
    tipos de cambio, más otras monedas internacionales relevantes.

    Características:
    - Códigos ISO 4217 (código y número)
    - Símbolos y decimales de cada moneda
    - Indicación de tipo de cambio publicado por Banxico
    - Indicación de tipo de cambio FIX
    - Agrupación por regiones geográficas
    - Formateo de montos en cada moneda

    Ejemplo:
        >>> from catalogmx.catalogs.banxico import MonedasDivisas
        >>>
        >>> # Obtener información del dólar
        >>> usd = MonedasDivisas.get_por_codigo("USD")
        >>> print(f"{usd['moneda']}: {usd['simbolo']}")
        >>>
        >>> # Obtener monedas con tipo de cambio Banxico
        >>> con_tc = MonedasDivisas.get_con_tipo_cambio_banxico()
        >>> print(f"Monedas con TC Banxico: {len(con_tc)}")
        >>>
        >>> # Formatear monto
        >>> formatted = MonedasDivisas.formatear_monto(1234.56, "USD")
        >>> print(formatted)  # "US$ 1,234.56"
    """

    _data: list[MonedaDivisa] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga lazy de datos desde JSON"""
        if cls._data is not None:
            return

        # Path: catalogmx/packages/python/catalogmx/catalogs/banxico/monedas_divisas.py
        # Target: catalogmx/packages/shared-data/banxico/monedas_divisas.json
        data_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "shared-data"
            / "banxico"
            / "monedas_divisas.json"
        )

        with open(data_path, encoding="utf-8") as f:
            json_data = json.load(f)
            cls._data = json_data["monedas"]

    @classmethod
    def get_all(cls) -> list[MonedaDivisa]:
        """
        Obtiene todas las monedas.

        Returns:
            Lista completa de monedas y divisas

        Ejemplo:
            >>> monedas = MonedasDivisas.get_all()
            >>> print(f"Total monedas: {len(monedas)}")
        """
        cls._load_data()
        return cls._data.copy()  # type: ignore

    @classmethod
    def get_por_codigo(cls, codigo_iso: str) -> MonedaDivisa | None:
        """
        Busca moneda por código ISO.

        Args:
            codigo_iso: Código ISO 4217 de la moneda (ej: "USD", "EUR", "MXN")

        Returns:
            Información de la moneda o None si no existe

        Ejemplo:
            >>> usd = MonedasDivisas.get_por_codigo("USD")
            >>> print(usd['moneda'])  # "Dólar Estadounidense"
        """
        cls._load_data()
        codigo_upper = codigo_iso.upper()
        for moneda in cls._data:  # type: ignore
            if moneda["codigo_iso"].upper() == codigo_upper:
                return moneda
        return None

    @classmethod
    def get_por_pais(cls, pais: str) -> list[MonedaDivisa]:
        """
        Busca monedas por país.

        Args:
            pais: Nombre del país (búsqueda parcial, case-insensitive)

        Returns:
            Lista de monedas del país

        Ejemplo:
            >>> mexico = MonedasDivisas.get_por_pais("México")
            >>> for m in mexico:
            ...     print(f"{m['moneda']} ({m['codigo_iso']})")
        """
        cls._load_data()
        pais_lower = pais.lower()
        return [m for m in cls._data if pais_lower in m["pais"].lower()]  # type: ignore

    @classmethod
    def get_con_tipo_cambio_banxico(cls) -> list[MonedaDivisa]:
        """
        Obtiene monedas con tipo de cambio publicado por Banxico.

        Returns:
            Lista de monedas con tipo de cambio Banxico

        Ejemplo:
            >>> con_tc = MonedasDivisas.get_con_tipo_cambio_banxico()
            >>> for m in con_tc:
            ...     print(f"{m['codigo_iso']}: {m['moneda']}")
        """
        cls._load_data()
        return [m for m in cls._data if m["tipo_cambio_banxico"]]  # type: ignore

    @classmethod
    def get_con_tipo_cambio_fix(cls) -> list[MonedaDivisa]:
        """
        Obtiene monedas con tipo de cambio FIX.

        Returns:
            Lista de monedas con tipo de cambio FIX

        Ejemplo:
            >>> fix = MonedasDivisas.get_con_tipo_cambio_fix()
            >>> for m in fix:
            ...     print(f"{m['codigo_iso']}: {m['moneda']}")
        """
        cls._load_data()
        return [m for m in cls._data if m.get("tipo_cambio_fix", False)]  # type: ignore

    @classmethod
    def get_por_region(cls, region: str) -> list[MonedaDivisa]:
        """
        Obtiene monedas de una región específica.

        Regiones soportadas:
        - America del Norte
        - America Latina
        - Europa
        - Asia-Pacifico
        - Africa

        Args:
            region: Nombre de la región

        Returns:
            Lista de monedas de esa región

        Ejemplo:
            >>> latam = MonedasDivisas.get_por_region("America Latina")
            >>> for m in latam:
            ...     print(f"{m['codigo_iso']}: {m['pais']}")
        """
        cls._load_data()

        regiones: dict[str, list[str]] = {
            "America del Norte": ["USD", "CAD", "MXN"],
            "America Latina": ["ARS", "BRL", "CLP", "COP", "PEN", "GTQ", "CRC", "UYU", "VES"],
            "Europa": ["EUR", "GBP", "CHF", "SEK", "NOK", "DKK", "RUB"],
            "Asia-Pacifico": ["JPY", "CNY", "AUD", "NZD", "SGD", "HKD", "INR", "KRW"],
            "Africa": ["ZAR"],
        }

        codigos = regiones.get(region, [])
        return [m for m in cls._data if m["codigo_iso"] in codigos]  # type: ignore

    @classmethod
    def get_principales(cls) -> list[MonedaDivisa]:
        """
        Obtiene monedas principales para operaciones en México.

        Returns:
            Lista de monedas principales (MXN, USD, EUR, CAD, GBP, JPY, CHF)

        Ejemplo:
            >>> principales = MonedasDivisas.get_principales()
            >>> for m in principales:
            ...     print(f"{m['codigo_iso']}: {m['moneda']}")
        """
        cls._load_data()
        principales = ["MXN", "USD", "EUR", "CAD", "GBP", "JPY", "CHF"]
        return [m for m in cls._data if m["codigo_iso"] in principales]  # type: ignore

    @classmethod
    def get_latam(cls) -> list[MonedaDivisa]:
        """
        Obtiene monedas latinoamericanas.

        Returns:
            Lista de monedas de América Latina

        Ejemplo:
            >>> latam = MonedasDivisas.get_latam()
            >>> for m in latam:
            ...     print(f"{m['codigo_iso']}: {m['pais']}")
        """
        cls._load_data()
        latam = ["MXN", "ARS", "BRL", "CLP", "COP", "PEN", "GTQ", "CRC", "UYU", "VES"]
        return [m for m in cls._data if m["codigo_iso"] in latam]  # type: ignore

    @classmethod
    def validar_codigo_iso(cls, codigo: str) -> bool:
        """
        Valida código ISO de moneda.

        Args:
            codigo: Código ISO a validar

        Returns:
            True si el código existe, False en caso contrario

        Ejemplo:
            >>> MonedasDivisas.validar_codigo_iso("USD")  # True
            >>> MonedasDivisas.validar_codigo_iso("XXX")  # False
        """
        cls._load_data()
        codigo_upper = codigo.upper()
        return any(m["codigo_iso"].upper() == codigo_upper for m in cls._data)  # type: ignore

    @classmethod
    def get_formato_moneda(cls, codigo_iso: str) -> dict[str, str | int] | None:
        """
        Obtiene información de formato de moneda.

        Args:
            codigo_iso: Código ISO de la moneda

        Returns:
            Diccionario con símbolo, decimales y formato de ejemplo

        Ejemplo:
            >>> formato = MonedasDivisas.get_formato_moneda("USD")
            >>> print(formato['formato_ejemplo'])  # "US$ 1234.56"
        """
        moneda = cls.get_por_codigo(codigo_iso)
        if not moneda:
            return None

        ejemplo_monto = 1234.56
        if moneda["decimales"] == 0:
            monto_formateado = str(round(ejemplo_monto))
        else:
            monto_formateado = f"{ejemplo_monto:.{moneda['decimales']}f}"

        return {
            "simbolo": moneda["simbolo"],
            "decimales": moneda["decimales"],
            "formato_ejemplo": f"{moneda['simbolo']} {monto_formateado}",
        }

    @classmethod
    def formatear_monto(cls, monto: float, codigo_iso: str) -> str:
        """
        Formatea monto en una moneda específica.

        Args:
            monto: Monto a formatear
            codigo_iso: Código ISO de la moneda

        Returns:
            Monto formateado con símbolo de moneda

        Ejemplo:
            >>> MonedasDivisas.formatear_monto(1234.56, "USD")
            "US$ 1,234.56"
            >>> MonedasDivisas.formatear_monto(1234.56, "JPY")
            "¥ 1,235"
        """
        moneda = cls.get_por_codigo(codigo_iso)
        if not moneda:
            return str(monto)

        if moneda["decimales"] == 0:
            monto_formateado = f"{round(monto):,.0f}".replace(",", " ")
        else:
            monto_formateado = f"{monto:,.{moneda['decimales']}f}".replace(",", " ")

        return f"{moneda['simbolo']} {monto_formateado}"

    @classmethod
    def get_mxn(cls) -> MonedaDivisa | None:
        """Obtiene peso mexicano (MXN)."""
        return cls.get_por_codigo("MXN")

    @classmethod
    def get_usd(cls) -> MonedaDivisa | None:
        """Obtiene dólar estadounidense (USD)."""
        return cls.get_por_codigo("USD")

    @classmethod
    def get_eur(cls) -> MonedaDivisa | None:
        """Obtiene euro (EUR)."""
        return cls.get_por_codigo("EUR")

    @classmethod
    def buscar_por_nombre(cls, nombre: str) -> list[MonedaDivisa]:
        """
        Busca monedas por nombre.

        Args:
            nombre: Texto a buscar en el nombre de la moneda

        Returns:
            Lista de monedas que coinciden

        Ejemplo:
            >>> dolares = MonedasDivisas.buscar_por_nombre("dólar")
            >>> for m in dolares:
            ...     print(f"{m['codigo_iso']}: {m['moneda']}")
        """
        cls._load_data()
        nombre_lower = nombre.lower()
        return [m for m in cls._data if nombre_lower in m["moneda"].lower()]  # type: ignore

    @classmethod
    def get_activas(cls) -> list[MonedaDivisa]:
        """
        Obtiene monedas activas.

        Returns:
            Lista de monedas activas

        Ejemplo:
            >>> activas = MonedasDivisas.get_activas()
            >>> print(f"Monedas activas: {len(activas)}")
        """
        cls._load_data()
        return [m for m in cls._data if m["activa"]]  # type: ignore

    @classmethod
    def get_info_tipo_cambio_fix(cls) -> dict[str, str]:
        """
        Información del tipo de cambio FIX.

        Returns:
            Diccionario con información del tipo de cambio FIX

        Ejemplo:
            >>> info = MonedasDivisas.get_info_tipo_cambio_fix()
            >>> print(info['horario'])
        """
        return {
            "descripcion": "Tipo de cambio FIX determinado por Banco de México - Promedio ponderado de cotizaciones del mercado de cambios al mayoreo",
            "horario": "12:00 hrs (mediodía) tiempo de la Ciudad de México",
            "uso": "Referencia oficial para liquidación de obligaciones denominadas en dólares",
        }
