#!/usr/bin/env python3
import re
import datetime
import unidecode


class RFCGeneral:
    """
    General Functions for RFC, Mexican Tax ID Code (Registro Federal de Contribuyentes),
    Variables:
        general_regex:
            a regex upon which all valid RFC must validate.
            All RFC are composed of 3 or 4 characters [A-Z&Ñ] (based on name or company),
            a date in format YYMMDD (based on birth or foundation date),
            2 characters [A-Z0-9] but not O, and a checksum composed of [0-9A] (homoclave)
        date_regex:
            a regex to capture the date element in the RFC and validate it.
        homoclave_regex:
            a regex to capture the homoclave element in the RFC and validate it.
        homoclave_characters:
            all possible characters in homoclave's first 2 characters
        checksum_table:
            Replace characters in RFC to calculate the checksum
    """
    general_regex = re.compile(r"[A-Z&Ñ]{3,4}[0-9]{6}[A-Z0-9]{2}[0-9A]")
    date_regex = r"[A-Z&Ñ]{3,4}([0-9]{6})[A-Z0-9]{2}[0-9A]"
    homoclave_regex = r"[A-Z&Ñ]{3,4}[0-9]{6}([A-Z0-9]{2})[0-9A]"
    homoclave_characters = 'ABCDEFGHIJKLMNPQRSTUVWXYZ0123456789'

    checksum_table = {
        '0': '00',
        '1': '01',
        '2': '02',
        '3': '03',
        '4': '04',
        '5': '05',
        '6': '06',
        '7': '07',
        '8': '08',
        '9': '09',
        'A': '10',
        'B': '11',
        'C': '12',
        'D': '13',
        'E': '14',
        'F': '15',
        'G': '16',
        'H': '17',
        'I': '18',
        'J': '19',
        'K': '20',
        'L': '21',
        'M': '22',
        'N': '23',
        '&': '24',
        'O': '25',
        'P': '26',
        'Q': '27',
        'R': '28',
        'S': '29',
        'T': '30',
        'U': '31',
        'V': '32',
        'W': '33',
        'X': '34',
        'Y': '35',
        'Z': '36',
        ' ': '37',
        'Ñ': '38',
    }
    quotient_remaining_table = {
        ' ': '00',
        '0': '00',
        '1': '01',
        '2': '02',
        '3': '03',
        '4': '04',
        '5': '05',
        '6': '06',
        '7': '07',
        '8': '08',
        '9': '09',
        '&': '10',
        'A': '11',
        'B': '12',
        'C': '13',
        'D': '14',
        'E': '15',
        'F': '16',
        'G': '17',
        'H': '18',
        'I': '19',
        'J': '21',
        'K': '22',
        'L': '23',
        'M': '24',
        'N': '25',
        'O': '26',
        'P': '27',
        'Q': '28',
        'R': '29',
        'S': '32',
        'T': '33',
        'U': '34',
        'V': '35',
        'W': '36',
        'X': '37',
        'Y': '38',
        'Z': '39',
        'Ñ': '40',
    }

    homoclave_assign_table = [
        '1',
        '2',
        '3',
        '4',
        '5',
        '6',
        '7',
        '8',
        '9',
        'A',
        'B',
        'C',
        'D',
        'E',
        'F',
        'G',
        'H',
        'I',
        'J',
        'K',
        'L',
        'M',
        'N',
        'P',
        'Q',
        'R',
        'S',
        'T',
        'U',
        'V',
        'W',
        'X',
        'Y',
        'Z'
    ]


class RFCValidator(RFCGeneral):
    """
    Loads an RFC, Mexican Tax ID Code (Registro Federal de Contribuyentes),
    and provides functions to determine its validity.

    """

    def __init__(self, rfc: str):
        """

        :param rfc: The RFC code to be validated, if str then converted to unicode and then to uppercase and stripped.
        :return: RFCValidator instance
        """
        self.rfc = ''
        if bool(rfc) and isinstance(rfc, str):
            # if type(rfc) == str:
            #    rfc = rfc.decode('utf-8')
            self.rfc = rfc.upper().strip()
            self._general_validation = None
        else:
            self._general_validation = False

    def validators(self, strict: bool = True) -> dict:
        """
        Returns a dictionary with the validations.
        :param strict: If False then checksum test won't be checked.
        :return: A dictionary with the result of the validations.
        """
        validations = {
            'general_regex': self.validate_general_regex,
            'date_format': self.validate_date,
            'homoclave': self.validate_homoclave,
            'checksum': self.validate_checksum,
        }

        if not strict:
            validations = {
                'general_regex': self.validate_general_regex,
                'date_format': self.validate_date,
                'homoclave': self.validate_homoclave,
                # 'checksum': self.validate_checksum,
            }
        return {name: function() for name, function in validations.items()}

    def validate(self, strict: bool = True) -> bool:
        """
        Retrieves the result of the validations and verifies all of them passed.
        :param strict: If True checksum won't be checked:
        :return: True if the RFC is valid, False if the RFC is invalid.
        """
        return not (False in [result for name, result in self.validators(strict=strict).items()])

    is_valid = validate

    def validate_date(self) -> bool:
        """
        Checks if the date element in the RFC code is valid
        """
        if self.validate_general_regex():
            date = re.findall(self.date_regex, self.rfc)
            try:
                if not date:
                    raise ValueError()
                datetime.datetime.strptime(date[0], '%y%m%d')
                return True
            except ValueError:
                return False
        return False

    def validate_homoclave(self) -> bool:
        """
        Checks if the homoclave's first 2 characters are correct.
        """
        if self.validate_general_regex():
            homoclave = re.findall(self.homoclave_regex, self.rfc)
            try:
                if not homoclave:
                    raise ValueError()
                for character in homoclave[0]:
                    if character in self.homoclave_characters:
                        pass
                    else:
                        raise ValueError()
                return True
            except ValueError:
                return False
        return False

    def validate_general_regex(self) -> bool:
        """
        Checks if length of the RFC and a match with the general Regex
        """
        if self._general_validation is not None:
            return self._general_validation
        if len(self.rfc) not in (12, 13):
            self._general_validation = False
            return self._general_validation
        if self.general_regex.match(self.rfc):
            self._general_validation = True
        else:
            self._general_validation = False
        return self._general_validation

    def detect_fisica_moral(self) -> str:
        """
        Returns a string based on the kind of RFC, (Persona Moral, Persona Física or Genérico)
        """
        if self.validate_general_regex():
            if self.is_generic():
                return 'Genérico'
            if self.is_fisica():
                return 'Persona Física'
            if self.is_moral():
                return 'Persona Moral'
        else:
            return 'RFC Inválido'

    def is_generic(self) -> bool:
        """
        Checks if the RFC is a Generic one.

        Generic RFC is used for non-specific recipients of Electronic Invoices.
        XAXX010101000 for Mexican non-specific recipients
        XEXX010101000 for Non-Mexican recipients, usually export invoices.

        >>> RFCValidator('XAXX010101000').is_generic()
        True
        """
        if self.rfc in ('XAXX010101000', 'XEXX010101000'):
            return True
        return False

    def is_fisica(self) -> bool:
        """
        Check if the code belongs to a "persona física" (individual)
        """
        if self.validate_general_regex():
            char4 = self.rfc[3]
            if char4.isalpha() and not self.is_generic():
                return True
            else:
                return False
        raise ValueError('Invalid RFC')

    def is_moral(self) -> bool:
        """
        Check if the code belongs to "persona moral" (corporation or association)
        """
        if self.validate_general_regex():
            char4 = self.rfc[3]
            if char4.isdigit():
                return True
            else:
                return False
        raise ValueError('Invalid RFC')

    def validate_checksum(self) -> bool:
        """
        Calculates the checksum of the RFC and verifies it's equal to the last character.
        Generic RFCs' checksums are not calculated since they are incorrect (they're always 0)
        In 99% of the RFC codes this is correct. In 1% of them for unknown reasons not clarified by the Tax Authority,
        the checksum doesn't fit this checksum. Be aware that an RFC may have an "invalid" checksum but still be
        valid if a "Cédula de Identificación Fiscal" is given.
        """
        if self.validate_general_regex():
            return (self.rfc[-1] == self.calculate_last_digit(self.rfc, with_checksum=True) or self.is_generic())
        return False

    @classmethod
    def calculate_last_digit(cls, rfc: str, with_checksum: bool = True) -> str | bool:
        """
        Calculates the checksum of an RFC.

        The checksum is calculated with the first 12 digits of the RFC
        If its length is 11 then an extra space is added at the beggining of the string.
        """
        if bool(rfc) and isinstance(rfc, str):
            str_rfc = rfc.strip().upper()
        else:
            return False
        if with_checksum:
            str_rfc = str_rfc[:-1]
        assert len(str_rfc) in (11, 12)
        if len(str_rfc) == 11:
            str_rfc = str_rfc.rjust(12)
        checksum = ((int(cls.checksum_table[n]), index) for index, n in zip(range(13, 1, -1), str_rfc))
        suma = sum(int(x * y) for x, y in checksum)

        residual = suma % 11

        if residual == 0:
            return '0'
        else:
            residual = 11 - residual
            if residual == 10:
                return 'A'
            else:
                return str(residual)


class RFCGeneratorUtils(RFCGeneral):
    vocales = 'AEIOU'
    excluded_words_fisicas = [
        'DE',
        'LA',
        'LAS',
        'MC',
        'VON',
        'DEL',
        'LOS',
        'Y',
        'MAC',
        'VAN',
        'MI'
    ]
    cacophonic_words = ['BUEI', 'BUEY', 'CACA', 'CACO', 'CAGA', 'CAGO',
                        'CAKA', 'COGE', 'COJA', 'COJE', 'COJI', 'COJO',
                        'CULO', 'FETO', 'GUEY', 'JOTO', 'KACA', 'KACO',
                        'KAGA', 'KAGO', 'KOGE', 'KOJO', 'KAKA', 'KULO',
                        'MAME', 'MAMO', 'MEAR', 'MEON', 'MION', 'MOCO',
                        'MULA', 'PEDA', 'PEDO', 'PENE', 'PUTA', 'PUTO',
                        'QULO', 'RATA', 'RUIN',
                        ]
    # Lista completa de palabras excluidas según documento SAT
    excluded_words_morales = [
        'EL', 'LA', 'DE', 'LOS', 'LAS', 'Y', 'DEL', 'MI',
        'COMPAÑIA', 'COMPAÑÍA', 'CIA', 'CIA.',
        'SOCIEDAD', 'SOC', 'SOC.',
        'COOPERATIVA', 'COOP', 'COOP.',
        'S.A.', 'SA', 'S.A', 'S. A.', 'S. A',
        'S.A.B.', 'SAB', 'S.A.B', 'S. A. B.', 'S. A. B',
        'S. DE R.L.', 'S DE RL', 'SRL', 'S.R.L.', 'S. R. L.',
        'S. EN C.', 'S EN C', 'S.C.', 'SC',
        'S. EN C. POR A.', 'S EN C POR A',
        'S. EN N.C.', 'S EN NC',
        'A.C.', 'AC', 'A. C.',
        'A. EN P.', 'A EN P',
        'S.C.L.', 'SCL',
        'S.N.C.', 'SNC',
        'C.V.', 'CV', 'C. V.',
        'SA DE CV', 'S.A. DE C.V.', 'SA DE CV MI', 'S.A. DE C.V. MI',
        'S.A.B. DE C.V.', 'SAB DE CV', 'S.A.B DE C.V',
        'SRL DE CV', 'S.R.L. DE C.V.', 'SRL DE CV MI', 'SRL MI',
        'THE', 'OF', 'COMPANY', 'AND', 'CO', 'CO.',
        'MC', 'VON', 'MAC', 'VAN',
        'PARA', 'POR', 'AL', 'E', 'EN', 'CON', 'SUS', 'A',
    ]

    allowed_chars = list('ABCDEFGHIJKLMNÑOPQRSTUVWXYZ&')

    # Tabla de conversión de números a texto
    numeros_texto = {
        '0': 'CERO', '1': 'UNO', '2': 'DOS', '3': 'TRES', '4': 'CUATRO',
        '5': 'CINCO', '6': 'SEIS', '7': 'SIETE', '8': 'OCHO', '9': 'NUEVE',
        '10': 'DIEZ', '11': 'ONCE', '12': 'DOCE', '13': 'TRECE', '14': 'CATORCE',
        '15': 'QUINCE', '16': 'DIECISEIS', '17': 'DIECISIETE', '18': 'DIECIOCHO',
        '19': 'DIECINUEVE', '20': 'VEINTE',
    }

    # Tabla de números romanos a arábigos
    numeros_romanos = {
        'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
        'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
        'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15,
        'XVI': 16, 'XVII': 17, 'XVIII': 18, 'XIX': 19, 'XX': 20,
    }

    @classmethod
    def convertir_numero_a_texto(cls, numero_str: str) -> str:
        """Convierte un número (arábigo o romano) a su representación en texto"""
        numero_str = numero_str.strip().upper()

        # Intentar como número romano
        if numero_str in cls.numeros_romanos:
            numero_arabigo = str(cls.numeros_romanos[numero_str])
            if numero_arabigo in cls.numeros_texto:
                return cls.numeros_texto[numero_arabigo]

        # Intentar como número arábigo
        if numero_str in cls.numeros_texto:
            return cls.numeros_texto[numero_str]

        # Si no está en la tabla, intentar convertir dígitos
        try:
            num = int(numero_str)
            if 0 <= num <= 20:
                return cls.numeros_texto[str(num)]
        except ValueError:
            pass

        return numero_str  # Si no se puede convertir, devolver original

    @classmethod
    def clean_name(cls, nombre: str) -> str:
        return "".join(char if char in cls.allowed_chars else unidecode.unidecode(char)
                       for char in " ".join(
            elem for elem in nombre.split(" ")
            if elem not in cls.excluded_words_fisicas).strip().upper()
                       ).strip().upper()

    @staticmethod
    def name_adapter(name: str, non_strict: bool = False) -> str:
        if isinstance(name, str):
            # if isinstance(name, str):
            #    name = name.decode('utf-8')
            return name.upper().strip()
        elif non_strict:
            if name is None or not name:
                return ''
        else:
            raise ValueError


class RFCGeneratorFisicas(RFCGeneratorUtils):
    def __init__(self, paterno: str, materno: str, nombre: str, fecha: datetime.date):
        _dob = datetime.datetime(2000, 1, 1)
        if (paterno.strip()
            and nombre.strip()
            and isinstance(fecha, datetime.date)
            ):
            self.paterno = paterno
            self.materno = materno
            self.nombre = nombre
            self.dob = fecha
            self._rfc = ''
        else:
            raise ValueError('Invalid Values')

    @property
    def paterno(self) -> str:
        return self._paterno

    @paterno.setter
    def paterno(self, name: str):
        self._paterno = self.name_adapter(name)

    @property
    def materno(self) -> str:
        return self._materno

    @materno.setter
    def materno(self, name: str):
        self._materno = self.name_adapter(name, non_strict=True)

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, name: str):
        self._nombre = self.name_adapter(name)

    @property
    def dob(self) -> datetime.date:
        return self._dob

    @dob.setter
    def dob(self, date: datetime.date):
        if isinstance(date, datetime.date):
            self._dob = date

    @property
    def rfc(self) -> str:
        if not self._rfc:
            partial_rfc = self.generate_letters() + self.generate_date() + self.homoclave
            self._rfc = partial_rfc + RFCValidator.calculate_last_digit(partial_rfc, with_checksum=False)
        return self._rfc

    def generate_date(self) -> str:
        return self.dob.strftime('%y%m%d')

    def generate_letters(self) -> str:
        extra_letter = False
        clave = []
        clave.append(self.paterno_calculo[0])
        second_value = list(filter(lambda x: x >= 0, map(self.paterno_calculo[1:].find, self.vocales)))
        if len(second_value) > 0:
            clave.append(self.paterno_calculo[min(second_value) + 1])
        else:
            extra_letter = True
        if self.materno_calculo:
            clave.append(self.materno_calculo[0])
        else:
            if extra_letter:
                clave.append(self.paterno_calculo[1])
            else:
                extra_letter = True
        clave.append(self.nombre_iniciales[0])
        if extra_letter:
            clave.append(self.nombre_iniciales[1])
        clave = "".join(clave)
        if clave in self.cacophonic_words:
            clave = clave[:-1] + 'X'
        return clave

    @property
    def paterno_calculo(self) -> str:
        return self.clean_name(self.paterno)

    @property
    def materno_calculo(self) -> str:
        return self.clean_name(self.materno)

    @property
    def nombre_calculo(self) -> str:
        return self.clean_name(self.nombre)

    def nombre_iscompound(self) -> bool:
        return len(self.nombre_calculo.split(" ")) > 1

    @property
    def nombre_iniciales(self) -> str:
        if self.nombre_iscompound():
            if self.nombre_calculo.split(" ")[0] in ('MARIA', 'JOSE'):
                return " ".join(self.nombre_calculo.split(" ")[1:])
            else:
                return self.nombre_calculo
        else:
            return self.nombre_calculo

    @property
    def nombre_completo(self) -> str:
        return " ".join(comp for comp in (self.paterno_calculo, self.materno_calculo, self.nombre_calculo) if comp)

    @property
    def cadena_homoclave(self) -> str:
        calc_str = ['0', ]
        for character in self.nombre_completo:
            calc_str.append(self.quotient_remaining_table[character])
        return "".join(calc_str)

    @property
    def homoclave(self) -> str:
        cadena = self.cadena_homoclave
        suma = sum(int(cadena[n:n + 2]) * int(cadena[n + 1]) for n in range(len(cadena) - 1)) % 1000
        resultado = (suma // 34, suma % 34)
        return self.homoclave_assign_table[resultado[0]] + self.homoclave_assign_table[resultado[1]]


class RFCGeneratorMorales(RFCGeneratorUtils):
    """
    RFC Generator for Persona Moral (Legal Entities/Companies)

    The RFC for a legal entity is composed of:
    - 3 letters derived from the company name
    - 6 digits for the incorporation/foundation date (YYMMDD)
    - 2 alphanumeric characters for homoclave
    - 1 checksum digit
    Total: 12 characters
    """

    def __init__(self, razon_social: str, fecha: datetime.date):
        """
        Initialize RFC Generator for Persona Moral

        :param razon_social: Company name (razón social)
        :param fecha: Incorporation/foundation date
        """
        if (razon_social.strip() and isinstance(fecha, datetime.date)):
            self.razon_social = razon_social
            self.fecha = fecha
            self._rfc = ''
        else:
            raise ValueError('Invalid Values: razon_social must be non-empty and fecha must be a date')

    @property
    def razon_social(self) -> str:
        return self._razon_social

    @razon_social.setter
    def razon_social(self, name: str):
        if isinstance(name, str):
            self._razon_social = name.upper().strip()
        else:
            raise ValueError('razon_social must be a string')

    @property
    def fecha(self) -> datetime.date:
        return self._fecha

    @fecha.setter
    def fecha(self, date: datetime.date):
        if isinstance(date, datetime.date):
            self._fecha = date
        else:
            raise ValueError('fecha must be a datetime.date')

    @property
    def rfc(self) -> str:
        """Generate and return the complete RFC"""
        if not self._rfc:
            partial_rfc = self.generate_letters() + self.generate_date() + self.homoclave
            self._rfc = partial_rfc + RFCValidator.calculate_last_digit(partial_rfc, with_checksum=False)
        return self._rfc

    def generate_date(self) -> str:
        """Generate date portion in YYMMDD format"""
        return self.fecha.strftime('%y%m%d')

    @property
    def razon_social_calculo(self) -> str:
        """
        Clean the company name according to SAT official rules:
        - Remove excluded words FIRST (S.A., DE, LA, etc.)
        - Remove special characters (&, @, %, #, !, $, ", -, /, +, (, ), etc.)
        - Substitute Ñ with X
        - Handle initials (F.A.Z. → each letter is a word)
        - Convert numbers (arabic and roman) to text
        - Handle consonant compounds (CH → C, LL → L)
        """
        razon = self.razon_social.upper().strip()

        # Step 1: First pass - remove excluded words with punctuation patterns
        # This handles cases like "S.A.", "S. A.", etc.
        # Process longer words first to avoid partial matches (e.g., S.A.B. before S.A.)
        for excluded in sorted(self.excluded_words_morales, key=len, reverse=True):
            # Try exact match
            razon = razon.replace(' ' + excluded + ' ', ' ')
            razon = razon.replace(' ' + excluded + ',', ' ')
            razon = razon.replace(' ' + excluded + '.', ' ')
            # Try at beginning
            if razon.startswith(excluded + ' '):
                razon = razon[len(excluded)+1:]
            # Try at end
            if razon.endswith(' ' + excluded):
                razon = razon[:-len(excluded)-1]
            if razon.endswith(',' + excluded):
                razon = razon[:-len(excluded)-1]

        # Step 2: Remove special characters except spaces, letters, numbers, and dots
        # Caracteres especiales a eliminar según SAT: &, @, %, #, !, $, ", -, /, +, (, ), etc.
        import string
        allowed_for_processing = string.ascii_uppercase + string.digits + ' .ÑÁÉÍÓÚÜñáéíóúü'
        razon_limpia = ''.join(c if c in allowed_for_processing else ' ' for c in razon)

        # Step 3: Substitute Ñ with X
        razon_limpia = razon_limpia.replace('Ñ', 'X').replace('ñ', 'X')

        # Step 4: Handle initials (F.A.Z. → F A Z)
        # Si hay letras separadas por puntos, expandirlas como palabras individuales
        # Marcar cuáles son iniciales para no filtrarlas después
        words_temp = []
        is_initial = []  # Track which words are initials
        for word in razon_limpia.split():
            word = word.strip()
            if not word:
                continue
            # Detectar patrón de iniciales: letra.letra.letra o similar
            if '.' in word and len(word) <= 15:  # Máximo razonable para iniciales
                # Separar por puntos y filtrar vacíos
                parts = [c.strip() for c in word.split('.') if c.strip()]
                # Si todas las partes son de 1-2 caracteres, son iniciales
                if parts and all(len(p) <= 2 and p.isalpha() for p in parts):
                    words_temp.extend(parts)
                    is_initial.extend([True] * len(parts))  # Mark all as initials
                    continue
            # Quitar puntos finales de palabras normales
            word = word.rstrip('.')
            if word:
                words_temp.append(word)
                is_initial.append(False)

        # Step 5: Convert numbers to text
        words_converted = []
        is_initial_converted = []
        for word, is_init in zip(words_temp, is_initial):
            # Verificar si es un número (arábigo o romano)
            if word.isdigit() or word in self.numeros_romanos:
                converted = self.convertir_numero_a_texto(word)
                words_converted.append(converted)
                is_initial_converted.append(is_init)
            else:
                words_converted.append(word)
                is_initial_converted.append(is_init)

        # Step 6: Second pass - Remove excluded words (but keep initials)
        filtered_words = []
        for word, is_init in zip(words_converted, is_initial_converted):
            word_clean = word.strip().upper()
            if not word_clean:
                continue
            # Keep initials even if they match excluded words
            if is_init:
                filtered_words.append(word_clean)
            elif word_clean not in self.excluded_words_morales:
                filtered_words.append(word_clean)

        # Step 7: Clean remaining special characters and accents
        cleaned = " ".join(filtered_words)
        result = ""
        for char in cleaned:
            if char in self.allowed_chars:
                result += char
            elif char == ' ':
                result += ' '
            else:
                # Use unidecode for accented characters
                decoded = unidecode.unidecode(char)
                if decoded in self.allowed_chars:
                    result += decoded

        result = result.strip().upper()

        # Step 8: Handle consonant compounds (CH → C, LL → L) at the beginning of words
        words_final = []
        for word in result.split():
            if word.startswith('CH'):
                word = 'C' + word[2:]
            elif word.startswith('LL'):
                word = 'L' + word[2:]
            words_final.append(word)

        return " ".join(words_final)

    def generate_letters(self) -> str:
        """
        Generate the 3-letter code from company name according to SAT rules:

        1 word:  First 3 letters (or pad with X if less than 3)
        2 words: 1st letter of 1st word + 1st letter of 2nd word + 2nd letter of 1st word
        3+ words: 1st letter of each of the first 3 words

        Note: According to SAT specification for 2 words, it should be:
        - First letter of first word
        - First letter of second word
        - Second letter of first word (or first two letters of second word)

        But empirical evidence shows it's actually:
        - First letter of first word
        - First vowel of first word (after first letter)
        - First letter of second word
        """
        cleaned_name = self.razon_social_calculo

        if not cleaned_name:
            raise ValueError('Company name is empty after cleaning')

        words = cleaned_name.split()

        if not words:
            raise ValueError('No valid words in company name')

        clave = []

        if len(words) == 1:
            # Single word: First 3 letters
            word = words[0]
            clave.append(word[0] if len(word) > 0 else 'X')
            clave.append(word[1] if len(word) > 1 else 'X')
            clave.append(word[2] if len(word) > 2 else 'X')
        elif len(words) == 2:
            # Two words: Initial of first word, first two letters of second word
            # According to SAT specification: "se toma la inicial de la primera y las dos primeras letras de la segunda"
            clave.append(words[0][0])  # First letter of first word
            clave.append(words[1][0])  # First letter of second word
            clave.append(words[1][1] if len(words[1]) > 1 else 'X')  # Second letter of second word
        else:
            # Three or more words: First letter of each of the first three words
            clave.append(words[0][0])
            clave.append(words[1][0])
            clave.append(words[2][0])

        result = "".join(clave)

        # Check for cacophonic words and replace last character with 'X'
        if result in self.cacophonic_words:
            result = result[:-1] + 'X'

        return result

    @property
    def nombre_completo(self) -> str:
        """Return the complete cleaned company name for homoclave calculation"""
        return self.razon_social_calculo

    @property
    def cadena_homoclave(self) -> str:
        """Generate the string used for homoclave calculation"""
        calc_str = ['0']
        for character in self.nombre_completo:
            if character in self.quotient_remaining_table:
                calc_str.append(self.quotient_remaining_table[character])
            elif character == ' ':
                calc_str.append(self.quotient_remaining_table[' '])
        return "".join(calc_str)

    @property
    def homoclave(self) -> str:
        """Calculate the 2-character homoclave"""
        cadena = self.cadena_homoclave
        suma = sum(int(cadena[n:n + 2]) * int(cadena[n + 1]) for n in range(len(cadena) - 1)) % 1000
        resultado = (suma // 34, suma % 34)
        return self.homoclave_assign_table[resultado[0]] + self.homoclave_assign_table[resultado[1]]


class RFCGenerator:
    """
    Factory class to generate RFC for either Persona Física or Persona Moral
    """

    @staticmethod
    def generate_fisica(nombre: str, paterno: str, materno: str, fecha: datetime.date) -> str:
        """Generate RFC for Persona Física (Individual)"""
        return RFCGeneratorFisicas(
            nombre=nombre,
            paterno=paterno,
            materno=materno,
            fecha=fecha
        ).rfc

    @staticmethod
    def generate_moral(razon_social: str, fecha: datetime.date) -> str:
        """Generate RFC for Persona Moral (Legal Entity/Company)"""
        return RFCGeneratorMorales(
            razon_social=razon_social,
            fecha=fecha
        ).rfc
