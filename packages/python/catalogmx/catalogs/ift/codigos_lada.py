"""
Catálogo de Códigos LADA de México

Basado en el Plan de Numeración Nacional del IFT (Instituto Federal de Telecomunicaciones).
Incluye mapeo geográfico a códigos INEGI y zonas metropolitanas.
"""

import json
import random

from catalogmx.utils.shared_data import get_shared_data_path


class CodigosLADACatalog:
    """Catálogo de códigos LADA con mapeo geográfico"""

    _data: list[dict] | None = None
    _by_lada: dict[str, dict] | None = None
    _by_municipio: dict[tuple[str, str], list[dict]] | None = None
    _by_entidad: dict[str, list[dict]] | None = None

    # Zonas metropolitanas principales (LADA compartida entre municipios de distintos estados)
    ZONAS_METROPOLITANAS: dict[str, dict] = {
        "55": {  # CDMX - Valle de México
            "nombre": "Zona Metropolitana del Valle de México",
            "municipios": [
                # CDMX (todos los municipios/alcaldías)
                ("09", None),  # Toda la entidad 09
                # Estado de México - municipios de Zona 5 IFT (60 municipios)
                ("15", "002"),  # Acolman
                ("15", "009"),  # Amecameca
                ("15", "010"),  # Apaxco
                ("15", "011"),  # Atenco
                ("15", "013"),  # Atizapán de Zaragoza
                ("15", "015"),  # Atlautla
                ("15", "016"),  # Axapusco
                ("15", "017"),  # Ayapango
                ("15", "020"),  # Coacalco de Berriozábal
                ("15", "022"),  # Cocotitlán
                ("15", "023"),  # Coyotepec
                ("15", "024"),  # Cuautitlán
                ("15", "025"),  # Chalco
                ("15", "026"),  # Chapa de Mota
                ("15", "028"),  # Chiautla
                ("15", "029"),  # Chicoloapan
                ("15", "030"),  # Chiconcuac
                ("15", "031"),  # Chimalhuacán
                ("15", "033"),  # Ecatepec de Morelos
                ("15", "034"),  # Ecatzingo
                ("15", "035"),  # Huehuetoca
                ("15", "036"),  # Hueypoxtla
                ("15", "037"),  # Huixquilucan
                ("15", "038"),  # Isidro Fabela
                ("15", "039"),  # Ixtapaluca
                ("15", "044"),  # Jaltenco
                ("15", "046"),  # Jilotzingo
                ("15", "050"),  # Juchitepec
                ("15", "053"),  # Melchor Ocampo
                ("15", "057"),  # Naucalpan de Juárez
                ("15", "058"),  # Nezahualcóyotl
                ("15", "059"),  # Nextlalpan
                ("15", "060"),  # Nicolás Romero
                ("15", "061"),  # Nopaltepec
                ("15", "065"),  # Otumba
                ("15", "068"),  # Ozumba
                ("15", "069"),  # Papalotla
                ("15", "070"),  # La Paz
                ("15", "075"),  # San Martín de las Pirámides
                ("15", "081"),  # Tecámac
                ("15", "083"),  # Temamatla
                ("15", "084"),  # Temascalapa
                ("15", "089"),  # Tenango del Aire
                ("15", "091"),  # Teoloyucan
                ("15", "092"),  # Teotihuacán
                ("15", "093"),  # Tepetlaoxtoc
                ("15", "094"),  # Tepetlixpa
                ("15", "095"),  # Tepotzotlán
                ("15", "096"),  # Tequixquiac
                ("15", "099"),  # Texcoco
                ("15", "100"),  # Tezoyuca
                ("15", "103"),  # Tlalmanalco
                ("15", "104"),  # Tlalnepantla de Baz
                ("15", "108"),  # Tultepec
                ("15", "109"),  # Tultitlán
                ("15", "112"),  # Villa del Carbón
                ("15", "120"),  # Zumpango
                ("15", "121"),  # Cuautitlán Izcalli
                ("15", "122"),  # Valle de Chalco Solidaridad
                ("15", "125"),  # Tonanitla
                # Hidalgo
                ("13", "069"),  # Tizayuca
            ],
        },
        "33": {  # Guadalajara
            "nombre": "Zona Metropolitana de Guadalajara",
            "municipios": [
                ("14", "039"),  # Guadalajara
                ("14", "070"),  # El Salto
                ("14", "097"),  # Tlajomulco de Zúñiga
                ("14", "098"),  # Tlaquepaque
                ("14", "101"),  # Tonalá
                ("14", "120"),  # Zapopan
                ("14", "124"),  # Juanacatlán
                ("14", "044"),  # Ixtlahuacán de los Membrillos
            ],
        },
        "81": {  # Monterrey
            "nombre": "Zona Metropolitana de Monterrey",
            "municipios": [
                ("19", "006"),  # Apodaca
                ("19", "009"),  # Cadereyta Jiménez
                ("19", "010"),  # El Carmen
                ("19", "018"),  # García
                ("19", "019"),  # San Pedro Garza García
                ("19", "021"),  # General Escobedo
                ("19", "026"),  # Guadalupe
                ("19", "031"),  # Juárez
                ("19", "039"),  # Monterrey
                ("19", "045"),  # Salinas Victoria
                ("19", "046"),  # San Nicolás de los Garza
                ("19", "048"),  # Santa Catarina
                ("19", "049"),  # Santiago
            ],
        },
        "222": {  # Puebla-Tlaxcala (también 220, 221)
            "nombre": "Zona Metropolitana de Puebla-Tlaxcala",
            "municipios": [
                # Puebla
                ("21", "114"),  # Puebla
                ("21", "015"),  # Amozoc
                ("21", "034"),  # Coronango
                ("21", "041"),  # Cuautlancingo
                ("21", "074"),  # Huejotzingo
                ("21", "090"),  # Juan C. Bonilla
                ("21", "106"),  # Ocoyucan
                ("21", "119"),  # San Andrés Cholula
                ("21", "132"),  # San Martín Texmelucan
                ("21", "140"),  # San Pedro Cholula
                # Tlaxcala
                ("29", "022"),  # Mazatecochco de José María Morelos
                ("29", "024"),  # Papalotla de Xicohténcatl
                ("29", "028"),  # San Pablo del Monte
                ("29", "032"),  # Tenancingo
                ("29", "033"),  # Teolocholco
                ("29", "034"),  # Tepeyanco
                ("29", "038"),  # Xicohtzinco
                ("29", "044"),  # Zacatelco
            ],
        },
        "664": {  # Tijuana-Tecate-Rosarito (también 661, 663, 665)
            "nombre": "Zona Metropolitana de Tijuana",
            "municipios": [
                # Baja California
                ("02", "004"),  # Tijuana
                ("02", "003"),  # Tecate
                ("02", "005"),  # Playas de Rosarito
            ],
        },
        "656": {  # Ciudad Juárez (también 657)
            "nombre": "Zona Metropolitana de Ciudad Juárez",
            "municipios": [
                # Chihuahua
                ("08", "037"),  # Juárez
                ("08", "031"),  # Guadalupe (Chihuahua)
                ("08", "051"),  # Praxedis G. Guerrero
            ],
        },
        "999": {  # Mérida (también 990)
            "nombre": "Zona Metropolitana de Mérida",
            "municipios": [
                # Yucatán
                ("31", "050"),  # Mérida
                ("31", "041"),  # Kanasín
                ("31", "100"),  # Ucú
                ("31", "101"),  # Umán
                ("31", "013"),  # Conkal
                ("31", "059"),  # Progreso
            ],
        },
        "998": {  # Cancún-Riviera Maya
            "nombre": "Zona Metropolitana de Cancún",
            "municipios": [
                # Quintana Roo
                ("23", "005"),  # Benito Juárez (Cancún)
                ("23", "008"),  # Solidaridad (Playa del Carmen)
                ("23", "009"),  # Tulum
                ("23", "004"),  # Isla Mujeres
                ("23", "011"),  # Puerto Morelos
            ],
        },
    }

    # Prefijos asociados a cada zona metropolitana
    # Solo CDMX (55), GDL (33) y MTY (81) son de 2 dígitos
    # Las expansiones son específicas por ciudad, NO por patrón de zona
    LADAS_METROPOLITANAS: dict[str, list[str]] = {
        "55": ["55", "56"],  # CDMX: 55 + 56x (expansión móvil)
        "33": ["33"],  # Guadalajara
        "81": ["81"],  # Monterrey
        "222": ["220", "221", "222"],  # Puebla-Tlaxcala (expansiones)
        "664": ["663", "664"],  # Tijuana (663 overlay 2018)
        "656": ["656", "657"],  # Ciudad Juárez (657 overlay)
        "999": ["990", "999"],  # Mérida (990 expansión)
        "998": ["998"],  # Cancún
    }

    # Lookup de zona metropolitana: (cve_entidad, cve_municipio) -> LADA
    _zm_lookup: dict[tuple[str, str | None], str] | None = None

    @classmethod
    def _load_data(cls) -> None:
        """Carga los datos del catálogo"""
        if cls._data is not None:
            return

        data_path = get_shared_data_path("ift", "codigos_lada.json")

        with open(data_path, encoding="utf-8") as f:
            raw = json.load(f)

        cls._data = raw.get("codigos", raw) if isinstance(raw, dict) else raw

        if not cls._data:
            cls._data = []

        # Build indexes
        cls._by_lada = {c["lada"]: c for c in cls._data}
        cls._by_municipio = {}
        cls._by_entidad = {}

        for c in cls._data:
            ent = c.get("cve_entidad")
            mun = c.get("cve_municipio")

            if ent and mun:
                key = (ent, mun)
                if key not in cls._by_municipio:
                    cls._by_municipio[key] = []
                cls._by_municipio[key].append(c)

            if ent:
                if ent not in cls._by_entidad:
                    cls._by_entidad[ent] = []
                cls._by_entidad[ent].append(c)

        # Build ZM lookup
        cls._zm_lookup = {}
        for lada, zm in cls.ZONAS_METROPOLITANAS.items():
            for cve_ent, cve_mun in zm["municipios"]:
                cls._zm_lookup[(cve_ent, cve_mun)] = lada

    @classmethod
    def get_all(cls) -> list[dict]:
        """Obtiene todos los códigos LADA"""
        cls._load_data()
        return cls._data.copy() if cls._data else []

    @classmethod
    def buscar_por_lada(cls, lada: str) -> dict | None:
        """Busca información por código LADA"""
        cls._load_data()
        return cls._by_lada.get(lada) if cls._by_lada else None

    @classmethod
    def buscar_por_ciudad(cls, ciudad: str) -> list[dict]:
        """Busca códigos LADA por nombre de ciudad"""
        cls._load_data()
        if not cls._data:
            return []
        ciudad_upper = ciudad.upper()
        return [c for c in cls._data if ciudad_upper in c.get("ciudad", "").upper()]

    @classmethod
    def get_por_estado(cls, estado: str) -> list[dict]:
        """Obtiene códigos LADA por estado"""
        cls._load_data()
        if not cls._data:
            return []
        estado_upper = estado.upper()
        return [c for c in cls._data if estado_upper in c.get("estado", "").upper()]

    @classmethod
    def get_por_cve_entidad(cls, cve_entidad: str) -> list[dict]:
        """Obtiene códigos LADA por clave de entidad INEGI"""
        cls._load_data()
        return cls._by_entidad.get(cve_entidad, []).copy() if cls._by_entidad else []

    @classmethod
    def get_por_municipio(cls, cve_entidad: str, cve_municipio: str) -> list[dict]:
        """Obtiene códigos LADA por municipio INEGI"""
        cls._load_data()
        key = (cve_entidad, cve_municipio)
        return cls._by_municipio.get(key, []).copy() if cls._by_municipio else []

    @classmethod
    def get_por_tipo(cls, tipo: str) -> list[dict]:
        """Obtiene códigos LADA por tipo (metropolitana, fronteriza, turistica, normal)"""
        cls._load_data()
        if not cls._data:
            return []
        return [c for c in cls._data if c.get("tipo") == tipo]

    @classmethod
    def get_por_region(cls, region: str) -> list[dict]:
        """Obtiene códigos LADA por región"""
        cls._load_data()
        if not cls._data:
            return []
        return [c for c in cls._data if c.get("region") == region]

    @classmethod
    def get_prefijos_por_municipio(cls, cve_entidad: str, cve_municipio: str) -> list[str]:
        """
        Obtiene todos los prefijos telefónicos probables para un municipio.

        Retorna todos los prefijos que podrían corresponder a ese municipio,
        incluyendo expansiones metropolitanas. Los teléfonos siempre se
        completan a 10 dígitos.

        Args:
            cve_entidad: Clave de entidad INEGI (01-32)
            cve_municipio: Clave de municipio INEGI (001-570)

        Returns:
            Lista de prefijos (ej: ["55", "561", "562", ...])
        """
        cls._load_data()
        prefijos: list[str] = []

        # 1. Verificar si pertenece a una zona metropolitana con LADAs asociadas
        if cls._zm_lookup:
            # Buscar por municipio específico
            lada = cls._zm_lookup.get((cve_entidad, cve_municipio))
            if lada and lada in cls.LADAS_METROPOLITANAS:
                prefijos.extend(cls.LADAS_METROPOLITANAS[lada])

            # Buscar si toda la entidad está en una ZM (ej: CDMX)
            if not prefijos:
                lada = cls._zm_lookup.get((cve_entidad, None))
                if lada and lada in cls.LADAS_METROPOLITANAS:
                    prefijos.extend(cls.LADAS_METROPOLITANAS[lada])

        # 2. Agregar LADAs directamente mapeadas al municipio
        if cls._by_municipio:
            for c in cls._by_municipio.get((cve_entidad, cve_municipio), []):
                if c["lada"] not in prefijos:
                    prefijos.append(c["lada"])

        # 3. Si no hay nada, buscar por entidad (estado)
        if not prefijos and cls._by_entidad:
            for c in cls._by_entidad.get(cve_entidad, []):
                if c["lada"] not in prefijos:
                    prefijos.append(c["lada"])
                    break  # Solo el principal del estado

        return prefijos

    @classmethod
    def get_lada_for_location(
        cls, cve_entidad: str, cve_municipio: str | None = None
    ) -> dict | None:
        """
        Obtiene el código LADA más apropiado para una ubicación geográfica.

        Prioridad:
        1. Zona metropolitana (si el municipio pertenece a una)
        2. Municipio específico
        3. Estado (ciudad principal)

        Args:
            cve_entidad: Clave de entidad INEGI (01-32)
            cve_municipio: Clave de municipio INEGI (opcional)

        Returns:
            Dict con información del LADA o None
        """
        cls._load_data()

        # Priority 1: Check zona metropolitana
        if cls._zm_lookup:
            # Check specific municipality
            if cve_municipio:
                lada = cls._zm_lookup.get((cve_entidad, cve_municipio))
                if lada and cls._by_lada:
                    return cls._by_lada.get(lada)
            # Check if entire state is in ZM
            lada = cls._zm_lookup.get((cve_entidad, None))
            if lada and cls._by_lada:
                return cls._by_lada.get(lada)

        # Priority 2: Specific municipality
        if cve_municipio and cls._by_municipio:
            candidates = cls._by_municipio.get((cve_entidad, cve_municipio), [])
            if candidates:
                # Prefer metropolitana type
                for c in candidates:
                    if c.get("tipo") == "metropolitana":
                        return c
                return candidates[0]

        # Priority 3: State level - prefer metropolitana
        if cls._by_entidad:
            candidates = cls._by_entidad.get(cve_entidad, [])
            if candidates:
                # Sort by type priority
                tipo_priority = {
                    "metropolitana": 0,
                    "turistica": 1,
                    "fronteriza": 2,
                    "normal": 3,
                }
                candidates.sort(key=lambda x: tipo_priority.get(x.get("tipo", ""), 99))
                return candidates[0]

        return None

    @classmethod
    def get_municipios_por_lada(cls, lada: str) -> list[tuple[str, str | None]]:
        """
        Obtiene todos los municipios INEGI asociados a una LADA.

        Para LADAs metropolitanas, retorna todos los municipios de la zona.
        Para LADAs regulares, retorna el municipio principal del catálogo.

        Args:
            lada: Código LADA (ej: "55", "222", "561")

        Returns:
            Lista de tuplas (cve_entidad, cve_municipio) con códigos INEGI
        """
        cls._load_data()

        # Check if this LADA belongs to a metropolitan area
        for main_lada, associated_ladas in cls.LADAS_METROPOLITANAS.items():
            if lada in associated_ladas:
                # Return all municipalities from this metropolitan zone
                zm = cls.ZONAS_METROPOLITANAS.get(main_lada)
                if zm:
                    return list(zm["municipios"])

        # Check direct metropolitan zones
        if lada in cls.ZONAS_METROPOLITANAS:
            return list(cls.ZONAS_METROPOLITANAS[lada]["municipios"])

        # Regular LADA - return municipality from catalog
        info = cls.buscar_por_lada(lada)
        if info and info.get("cve_entidad") and info.get("cve_municipio"):
            return [(info["cve_entidad"], info["cve_municipio"])]

        return []

    @classmethod
    def get_zona_metropolitana(cls, lada: str) -> dict | None:
        """
        Obtiene información de la zona metropolitana para una LADA.

        Args:
            lada: Código LADA (ej: "55", "222", "561")

        Returns:
            Dict con nombre, municipios y LADAs asociadas, o None
        """
        # Check if this LADA belongs to a metropolitan area
        for main_lada, associated_ladas in cls.LADAS_METROPOLITANAS.items():
            if lada in associated_ladas:
                zm = cls.ZONAS_METROPOLITANAS.get(main_lada)
                if zm:
                    return {
                        "lada_principal": main_lada,
                        "nombre": zm["nombre"],
                        "municipios": zm["municipios"],
                        "ladas_asociadas": associated_ladas,
                    }

        # Check direct metropolitan zones
        if lada in cls.ZONAS_METROPOLITANAS:
            zm = cls.ZONAS_METROPOLITANAS[lada]
            return {
                "lada_principal": lada,
                "nombre": zm["nombre"],
                "municipios": zm["municipios"],
                "ladas_asociadas": cls.LADAS_METROPOLITANAS.get(lada, [lada]),
            }

        return None

    @classmethod
    def generar_telefono(
        cls,
        cve_entidad: str,
        cve_municipio: str | None = None,
        _tipo: str = "fijo",  # Reserved for future mobile vs fixed differentiation
    ) -> str | None:
        """
        Genera un número de teléfono válido para una ubicación.

        Args:
            cve_entidad: Clave de entidad INEGI
            cve_municipio: Clave de municipio INEGI (opcional)
            tipo: 'fijo' o 'movil'

        Returns:
            Número de teléfono de 10 dígitos o None
        """
        lada_info = cls.get_lada_for_location(cve_entidad, cve_municipio)
        if not lada_info:
            return None

        lada = lada_info["lada"]

        # Generate remaining digits
        # LADA can be 2 or 3 digits, total number is always 10
        remaining = 10 - len(lada)

        # Generate random digits (avoid starting with 0)
        first_digit = random.randint(1, 9)
        other_digits = "".join(str(random.randint(0, 9)) for _ in range(remaining - 1))

        return f"{lada}{first_digit}{other_digits}"

    @classmethod
    def validar_numero(cls, numero: str) -> dict:
        """
        Valida un número de teléfono mexicano.

        Args:
            numero: Número de teléfono (10 dígitos)

        Returns:
            Dict con información de validación
        """
        cls._load_data()

        # Clean number
        numero_clean = "".join(c for c in numero if c.isdigit())

        result = {
            "numero": numero_clean,
            "valido": False,
            "lada": None,
            "ciudad": None,
            "estado": None,
            "tipo": None,
            "error": None,
        }

        if len(numero_clean) != 10:
            result["error"] = "Debe tener 10 dígitos"
            return result

        # Try 2-digit LADA first (55, 33, 81)
        lada_2 = numero_clean[:2]
        if lada_2 in ("55", "33", "81") and cls._by_lada:
            info = cls._by_lada.get(lada_2)
            if info:
                result["valido"] = True
                result["lada"] = lada_2
                result["ciudad"] = info.get("ciudad")
                result["estado"] = info.get("estado")
                result["tipo"] = info.get("tipo")
                return result

        # Try 3-digit LADA
        lada_3 = numero_clean[:3]
        if cls._by_lada:
            info = cls._by_lada.get(lada_3)
            if info:
                result["valido"] = True
                result["lada"] = lada_3
                result["ciudad"] = info.get("ciudad")
                result["estado"] = info.get("estado")
                result["tipo"] = info.get("tipo")
                return result

        result["error"] = "LADA no reconocida"
        return result

    @classmethod
    def formatear_numero(cls, numero: str) -> str:
        """
        Formatea un número de teléfono mexicano.

        Args:
            numero: Número de teléfono (10 dígitos)

        Returns:
            Número formateado (ej: "55 1234 5678" o "333 123 4567")
        """
        numero_clean = "".join(c for c in numero if c.isdigit())

        if len(numero_clean) != 10:
            return numero

        # Check if 2-digit LADA
        if numero_clean[:2] in ("55", "33", "81"):
            return f"{numero_clean[:2]} {numero_clean[2:6]} {numero_clean[6:]}"

        # 3-digit LADA
        return f"{numero_clean[:3]} {numero_clean[3:6]} {numero_clean[6:]}"

    @classmethod
    def get_estadisticas(cls) -> dict:
        """Obtiene estadísticas del catálogo"""
        cls._load_data()

        if not cls._data:
            return {}

        tipos = {}
        regiones = {}
        estados = {}

        for c in cls._data:
            t = c.get("tipo", "unknown")
            tipos[t] = tipos.get(t, 0) + 1

            r = c.get("region", "unknown")
            regiones[r] = regiones.get(r, 0) + 1

            e = c.get("estado", "unknown")
            estados[e] = estados.get(e, 0) + 1

        return {
            "total_codigos": len(cls._data),
            "por_tipo": tipos,
            "por_region": regiones,
            "estados_cubiertos": len(estados),
            "zonas_metropolitanas": len(cls.ZONAS_METROPOLITANAS),
        }
