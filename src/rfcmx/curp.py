#!/usr/bin/python
# -*- coding: utf-8 -*-
from six import string_types
import re
import datetime
import unidecode


class CURPException(Exception):
    pass


class CURPLengthError(CURPException):
    pass


class CURPStructureError(CURPException):
    pass


class CURPGeneral(object):
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

    cacophonic_words = ['BUEI', 'BUEY', 'CACA', 'CACO', 'CAGA', 'CAGO',
                        'CAKA', 'COGE', 'COJA', 'COJE', 'COJI', 'COJO',
                        'CULO', 'FETO', 'GUEY', 'JOTO', 'KACA', 'KACO',
                        'KAGA', 'KAGO', 'KOGE', 'KOJO', 'KAKA', 'KULO',
                        'MAME', 'MAMO', 'MEAR', 'MEON', 'MION', 'MOCO',
                        'MULA', 'PEDA', 'PEDO', 'PENE', 'PUTA', 'PUTO',
                        'QULO', 'RATA', 'RUIN',
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

    def __init__(self, curp):
        """
        :param curp: The CURP code to be validated
        """
        self.curp = ''
        if bool(curp) and isinstance(curp, string_types):
            self.curp = curp.upper().strip()

    def validate(self):
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

    def is_valid(self):
        """
        Checks if CURP is valid without raising exceptions
        :return: True if valid, False otherwise
        """
        try:
            return self.validate()
        except CURPException:
            return False


class CURPGeneratorUtils(CURPGeneral):
    """
    Utility functions for CURP generation
    """

    @classmethod
    def clean_name(cls, nombre):
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
    def name_adapter(name, non_strict=False):
        """Adapt name to uppercase and strip"""
        if isinstance(name, string_types):
            return name.upper().strip()
        elif non_strict:
            if name is None or not name:
                return ''
        else:
            raise ValueError('Name must be a string')

    @classmethod
    def get_first_consonant(cls, word):
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
    def get_state_code(cls, state):
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

    def __init__(self, nombre, paterno, materno, fecha_nacimiento, sexo, estado):
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
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, value):
        self._nombre = self.name_adapter(value)

    @property
    def paterno(self):
        return self._paterno

    @paterno.setter
    def paterno(self, value):
        self._paterno = self.name_adapter(value)

    @property
    def materno(self):
        return self._materno

    @materno.setter
    def materno(self, value):
        self._materno = self.name_adapter(value, non_strict=True)

    @property
    def nombre_calculo(self):
        """Get cleaned first name"""
        return self.clean_name(self.nombre)

    @property
    def paterno_calculo(self):
        """Get cleaned first surname"""
        return self.clean_name(self.paterno)

    @property
    def materno_calculo(self):
        """Get cleaned second surname"""
        return self.clean_name(self.materno) if self.materno else ''

    @property
    def nombre_iniciales(self):
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

    def generate_letters(self):
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

        # Check for cacophonic words and replace last character with 'X'
        if result in self.cacophonic_words:
            result = result[:-1] + 'X'

        return result

    def generate_date(self):
        """Generate date portion in YYMMDD format"""
        return self.fecha_nacimiento.strftime('%y%m%d')

    def generate_consonants(self):
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

    def generate_homoclave(self):
        """
        Generate the 2-character homoclave

        In practice, this is assigned by the Mexican government's registry.
        For generation purposes, we'll use a placeholder "00" or calculate
        a simple checksum.
        """
        # Simplified version - in reality this is assigned by RENAPO
        # For now, we'll use "00" as default
        return "00"

    @property
    def curp(self):
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
