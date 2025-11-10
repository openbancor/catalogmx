#!/usr/bin/env python3
import datetime
import re

import unidecode


class CURPException(Exception):
    pass


class CURPLengthError(CURPException):
    pass


class CURPStructureError(CURPException):
    pass


class CURPGeneral:
    """
    General Functions for CURP (Clave Única de Registro de Población)

    CURP is an 18-character unique identifier for people in Mexico.
    Format: AAAA-YYMMDD-H-EE-BBB-CC
    Where:
        AAAA: 4 letters from name (like RFC)
        YYMMDD: Birth date
        H: Gender (H=Male/Hombre, M=Female/Mujer)
        EE: State code (2 letters)
        BBB: Internal consonants from paterno, materno, nombre
        CC: Homoclave (2 digits/letters)
    """
    general_regex = re.compile(
        r"[A-Z][AEIOUX][A-Z]{2}[0-9]{2}[0-1][0-9][0-3][0-9][MH][A-Z]{2}[BCDFGHJKLMNPQRSTVWXYZ]{3}[0-9A-Z]{2}"
    )
    length = 18

    # Mexican state codes
    state_codes = {
        'AGUASCALIENTES': 'AS',
        'BAJA CALIFORNIA': 'BC',
        'BAJA CALIFORNIA SUR': 'BS',
        'CAMPECHE': 'CC',
        'COAHUILA': 'CL',
        'COLIMA': 'CM',
        'CHIAPAS': 'CS',
        'CHIHUAHUA': 'CH',
        'CIUDAD DE MEXICO': 'DF',  # Also accepts CDMX
        'DISTRITO FEDERAL': 'DF',
        'CDMX': 'DF',
        'DURANGO': 'DG',
        'GUANAJUATO': 'GT',
        'GUERRERO': 'GR',
        'HIDALGO': 'HG',
        'JALISCO': 'JC',
        'ESTADO DE MEXICO': 'MC',
        'MEXICO': 'MC',
        'MICHOACAN': 'MN',
        'MORELOS': 'MS',
        'NAYARIT': 'NT',
        'NUEVO LEON': 'NL',
        'OAXACA': 'OC',
        'PUEBLA': 'PL',
        'QUERETARO': 'QT',
        'QUINTANA ROO': 'QR',
        'SAN LUIS POTOSI': 'SP',
        'SINALOA': 'SL',
        'SONORA': 'SR',
        'TABASCO': 'TC',
        'TAMAULIPAS': 'TS',
        'TLAXCALA': 'TL',
        'VERACRUZ': 'VZ',
        'YUCATAN': 'YN',
        'ZACATECAS': 'ZS',
        'NACIDO EN EL EXTRANJERO': 'NE',  # Born abroad
        'EXTRANJERO': 'NE',
    }

    vocales = 'AEIOU'
    consonantes = 'BCDFGHJKLMNPQRSTVWXYZ'

    # Lista oficial completa de palabras inconvenientes según Anexo 2 del Instructivo Normativo CURP
    # Cuando se detectan estas palabras en las primeras 4 letras, la segunda letra se sustituye con 'X'
    cacophonic_words = [
        'BACA', 'BAKA', 'BUEI', 'BUEY',
        'CACA', 'CACO', 'CAGA', 'CAGO', 'CAKA', 'KAKO', 'COGE', 'COGI', 'COJA', 'COJE', 'COJI', 'COJO', 'COLA', 'CULO',
        'FALO', 'FETO',
        'GETA', 'GUEI', 'GUEY',
        'JETA', 'JOTO',
        'KACA', 'KACO', 'KAGA', 'KAGO', 'KAKA', 'KAKO', 'KOGE', 'KOGI', 'KOJA', 'KOJE', 'KOJI', 'KOJO', 'KOLA', 'KULO',
        'LILO', 'LOCA', 'LOCO', 'LOKA', 'LOKO',
        'MAME', 'MAMO', 'MEAR', 'MEAS', 'MEON', 'MIAR', 'MION', 'MOCO', 'MOKO', 'MULA', 'MULO',
        'NACA', 'NACO',
        'PEDA', 'PEDO', 'PENE', 'PIPI', 'PITO', 'POPO', 'PUTA', 'PUTO',
        'QULO',
        'RATA', 'ROBA', 'ROBE', 'ROBO', 'RUIN',
        'SENO',
        'TETA',
        'VACA', 'VAGA', 'VAGO', 'VAKA', 'VUEI', 'VUEY',
        'WUEI', 'WUEY',
    ]

    excluded_words = [
        'DE', 'LA', 'LAS', 'MC', 'VON', 'DEL', 'LOS', 'Y', 'MAC', 'VAN', 'MI',
        'DA', 'DAS', 'DE', 'DEL', 'DER', 'DI', 'DIE', 'DD', 'EL', 'LA',
        'LOS', 'LAS', 'LE', 'LES', 'MAC', 'MC', 'VAN', 'VON', 'Y'
    ]

    allowed_chars = list('ABCDEFGHIJKLMNÑOPQRSTUVWXYZ')


class CURPValidator(CURPGeneral):
    """
    Validates a CURP (Clave Única de Registro de Población)
    """

    def __init__(self, curp: str | None) -> None:
        """
        :param curp: The CURP code to be validated
        """
        self.curp = ''
        if bool(curp) and isinstance(curp, str):
            self.curp = curp.upper().strip()

    def validate(self) -> bool:
        """
        Validates the CURP structure
        :return: True if valid, raises exception if invalid
        """
        value = self.curp.strip()
        if len(value) != self.length:
            raise CURPLengthError("CURP length must be 18")
        if self.general_regex.match(value):
            return True
        else:
            raise CURPStructureError("Invalid CURP structure")

    def is_valid(self) -> bool:
        """
        Checks if CURP is valid without raising exceptions
        :return: True if valid, False otherwise
        """
        try:
            return self.validate()
        except CURPException:
            return False

    def validate_check_digit(self) -> bool:
        """
        Valida el dígito verificador (posición 18) del CURP

        :return: True si el dígito verificador es correcto, False en caso contrario
        """
        if len(self.curp) != 18:
            return False

        # Obtener los primeros 17 caracteres
        curp_17 = self.curp[:17]

        # Calcular el dígito verificador esperado
        expected_digit = CURPGenerator.calculate_check_digit(curp_17)

        # Comparar con el dígito actual
        actual_digit = self.curp[17]

        return expected_digit == actual_digit


class CURPGeneratorUtils(CURPGeneral):
    """
    Utility functions for CURP generation
    """

    @classmethod
    def clean_name(cls, nombre: str | None) -> str:
        """Clean name by removing excluded words and special characters"""
        if not nombre:
            return ''
        result = "".join(
            char if char in cls.allowed_chars else unidecode.unidecode(char)
            for char in " ".join(
                elem for elem in nombre.split(" ")
                if elem.upper() not in cls.excluded_words
            ).strip().upper()
        ).strip().upper()
        return result

    @staticmethod
    def name_adapter(name: str | None, non_strict: bool = False) -> str:
        """Adapt name to uppercase and strip"""
        if isinstance(name, str):
            return name.upper().strip()
        elif non_strict:
            if name is None or not name:
                return ''
        else:
            raise ValueError('Name must be a string')

    @classmethod
    def get_first_consonant(cls, word: str) -> str:
        """
        Get the first internal consonant from a word
        (the first consonant that is not the first letter)
        """
        if not word or len(word) <= 1:
            return 'X'

        for char in word[1:]:
            if char in cls.consonantes:
                return char
        return 'X'

    @classmethod
    def get_state_code(cls, state: str | None) -> str:
        """
        Get the two-letter state code from state name
        """
        if not state:
            return 'NE'  # Born abroad default

        state_upper = state.upper().strip()

        # Try exact match first
        if state_upper in cls.state_codes:
            return cls.state_codes[state_upper]

        # Clean the state name and try again
        state_clean = cls.clean_name(state).upper()
        if state_clean in cls.state_codes:
            return cls.state_codes[state_clean]

        # Try to find partial match
        for state_name, code in cls.state_codes.items():
            if state_name in state_upper or state_upper in state_name:
                return code

        # If it's already a 2-letter code, validate and return
        if len(state_upper) == 2 and state_upper[0] in cls.allowed_chars and state_upper[1] in cls.allowed_chars:
            return state_upper

        return 'NE'  # Default to born abroad


class CURPGenerator(CURPGeneratorUtils):
    """
    CURP Generator for Mexican citizens and residents

    Generates an 18-character CURP based on:
    - Personal names (paterno, materno, nombre)
    - Birth date
    - Gender
    - Birth state
    """

    def __init__(self, nombre: str, paterno: str, materno: str | None, fecha_nacimiento: datetime.date, sexo: str, estado: str | None) -> None:
        """
        Initialize CURP Generator

        :param nombre: First name(s)
        :param paterno: First surname (apellido paterno)
        :param materno: Second surname (apellido materno) - can be empty
        :param fecha_nacimiento: Birth date (datetime.date object)
        :param sexo: Gender - 'H' for male (Hombre), 'M' for female (Mujer)
        :param estado: Birth state (Mexican state name or code)
        """
        if not paterno or not paterno.strip():
            raise ValueError('Apellido paterno is required')
        if not nombre or not nombre.strip():
            raise ValueError('Nombre is required')
        if not isinstance(fecha_nacimiento, datetime.date):
            raise ValueError('fecha_nacimiento must be a datetime.date object')
        if sexo.upper() not in ('H', 'M'):
            raise ValueError('sexo must be "H" (Hombre) or "M" (Mujer)')

        self.nombre = nombre
        self.paterno = paterno
        self.materno = materno if materno else ''
        self.fecha_nacimiento = fecha_nacimiento
        self.sexo = sexo.upper()
        self.estado = estado
        self._curp = ''

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, value: str) -> None:
        self._nombre = self.name_adapter(value)

    @property
    def paterno(self) -> str:
        return self._paterno

    @paterno.setter
    def paterno(self, value: str) -> None:
        self._paterno = self.name_adapter(value)

    @property
    def materno(self) -> str:
        return self._materno

    @materno.setter
    def materno(self, value: str | None) -> None:
        self._materno = self.name_adapter(value, non_strict=True)

    @property
    def nombre_calculo(self) -> str:
        """Get cleaned first name"""
        return self.clean_name(self.nombre)

    @property
    def paterno_calculo(self) -> str:
        """Get cleaned first surname"""
        return self.clean_name(self.paterno)

    @property
    def materno_calculo(self) -> str:
        """Get cleaned second surname"""
        return self.clean_name(self.materno) if self.materno else ''

    @property
    def nombre_iniciales(self) -> str:
        """
        Get the first name to use for initials
        Skip common first names like JOSE and MARIA in compound names
        """
        if not self.nombre_calculo:
            return self.nombre_calculo

        words = self.nombre_calculo.split()
        if len(words) > 1:
            if words[0] in ('MARIA', 'JOSE', 'MA', 'MA.', 'J', 'J.'):
                return " ".join(words[1:])
        return self.nombre_calculo

    def generate_letters(self) -> str:
        """
        Generate the first 4 letters of CURP

        1. First letter of paterno
        2. First vowel of paterno (after first letter)
        3. First letter of materno (or X if none)
        4. First letter of nombre
        """
        clave = []

        # First letter of paterno
        paterno = self.paterno_calculo
        if not paterno:
            raise ValueError('Apellido paterno cannot be empty')

        clave.append(paterno[0])

        # First vowel of paterno (after first letter)
        vowel_found = False
        for char in paterno[1:]:
            if char in self.vocales:
                clave.append(char)
                vowel_found = True
                break

        if not vowel_found:
            clave.append('X')

        # First letter of materno (or X if none)
        materno = self.materno_calculo
        if materno:
            clave.append(materno[0])
        else:
            clave.append('X')

        # First letter of nombre
        nombre = self.nombre_iniciales
        if not nombre:
            raise ValueError('Nombre cannot be empty')

        clave.append(nombre[0])

        result = "".join(clave)

        # Check for cacophonic words and replace second character (first vowel) with 'X'
        # Según el Instructivo Normativo CURP, Anexo 2
        if result in self.cacophonic_words:
            result = result[0] + 'X' + result[2:]

        return result

    def generate_date(self) -> str:
        """Generate date portion in YYMMDD format"""
        return self.fecha_nacimiento.strftime('%y%m%d')

    def generate_consonants(self) -> str:
        """
        Generate the 3-consonant section

        1. First internal consonant of paterno
        2. First internal consonant of materno (or X if none)
        3. First internal consonant of nombre
        """
        consonants = []

        # First internal consonant of paterno
        paterno = self.paterno_calculo
        consonants.append(self.get_first_consonant(paterno))

        # First internal consonant of materno
        materno = self.materno_calculo
        if materno:
            consonants.append(self.get_first_consonant(materno))
        else:
            consonants.append('X')

        # First internal consonant of nombre
        nombre = self.nombre_iniciales
        consonants.append(self.get_first_consonant(nombre))

        return "".join(consonants)

    def generate_homoclave(self) -> str:
        """
        Generate the 2-character homoclave (positions 17-18)

        IMPORTANTE: Según el Instructivo Normativo oficial:
        - Posición 17: Diferenciador de homonimia asignado ALEATORIAMENTE por RENAPO
                       (no es calculable algorítmicamente)
                       Para nacidos antes del 2000: números 0-9
                       Para nacidos después del 2000: letras A-Z o números 0-9
        - Posición 18: Dígito verificador calculado mediante algoritmo oficial

        Este método genera valores por defecto ya que la homoclave real solo puede
        ser asignada oficialmente por RENAPO.
        """
        # Posición 17: Diferenciador (asignado por RENAPO, usamos '0' por defecto)
        if self.fecha_nacimiento.year < 2000:
            differentiator = '0'  # Para antes del 2000: 0-9
        else:
            differentiator = 'A'  # Para después del 2000: A-Z o 0-9

        # Posición 18: Dígito verificador (calculable)
        temp_curp = (self.generate_letters() +
                     self.generate_date() +
                     self.sexo +
                     self.get_state_code(self.estado) +
                     self.generate_consonants() +
                     differentiator)

        check_digit = self.calculate_check_digit(temp_curp)

        return differentiator + check_digit

    @staticmethod
    def calculate_check_digit(curp_17: str) -> str:
        """
        Calcula el dígito verificador (posición 18) según el algoritmo oficial RENAPO

        Algoritmo:
        1. Diccionario de valores: "0123456789ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"
        2. Para cada carácter de los primeros 17:
           valor = índice_en_diccionario * (18 - posición)
        3. Suma todos los valores
        4. dígito = 10 - (suma % 10)
        5. Si dígito == 10, entonces dígito = 0

        :param curp_17: Los primeros 17 caracteres del CURP
        :return: Dígito verificador (0-9)
        """
        if len(curp_17) != 17:
            raise ValueError("CURP debe tener exactamente 17 caracteres para calcular dígito verificador")

        # Diccionario oficial de valores
        dictionary = "0123456789ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"

        suma = 0
        for i, char in enumerate(curp_17):
            # Obtener el índice del carácter en el diccionario
            try:
                char_value = dictionary.index(char)
            except ValueError:
                # Si el carácter no está en el diccionario, usar 0
                char_value = 0

            # Multiplicar por (18 - posición)
            suma += char_value * (18 - i)

        # Calcular dígito verificador
        digito = 10 - (suma % 10)

        # Si es 10, retornar 0
        if digito == 10:
            digito = 0

        return str(digito)

    @property
    def curp(self) -> str:
        """Generate and return the complete CURP"""
        if not self._curp:
            letters = self.generate_letters()
            date = self.generate_date()
            gender = self.sexo
            state = self.get_state_code(self.estado)
            consonants = self.generate_consonants()
            homoclave = self.generate_homoclave()

            self._curp = letters + date + gender + state + consonants + homoclave

        return self._curp
