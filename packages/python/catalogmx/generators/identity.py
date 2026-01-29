"""
Mexican Identity Generator

Generates complete Mexican identities with realistic data for testing.
Uses Faker for random data generation and catalogmx validators for
RFC, CURP, CLABE, and NSS generation.

Usage:
    from catalogmx.generators import generate_identity

    # Generate a random persona física
    identity = generate_identity()

    # Generate with specific parameters
    identity = generate_identity(
        sexo='M',
        estado='Jalisco',
        min_age=25,
        max_age=45
    )

    print(identity['nombre_completo'])
    print(identity['rfc'])
    print(identity['curp'])
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Literal

try:
    from faker import Faker
except ImportError:
    Faker = None  # type: ignore

from catalogmx.helpers import (
    generate_clabe,
    generate_curp,
    generate_rfc_persona_fisica,
    generate_rfc_persona_moral,
)
from catalogmx.validators.nss import generate_nss


def _get_faker() -> Faker:
    """Get a Faker instance with Mexican locale."""
    if Faker is None:
        raise ImportError(
            "Faker is required for identity generation. "
            "Install it with: pip install faker"
        )
    return Faker("es_MX")


# Mexican states with CURP codes
ESTADOS_MEXICO = [
    {"name": "AGUASCALIENTES", "code": "AS", "inegi": "01"},
    {"name": "BAJA CALIFORNIA", "code": "BC", "inegi": "02"},
    {"name": "BAJA CALIFORNIA SUR", "code": "BS", "inegi": "03"},
    {"name": "CAMPECHE", "code": "CC", "inegi": "04"},
    {"name": "CHIAPAS", "code": "CS", "inegi": "07"},
    {"name": "CHIHUAHUA", "code": "CH", "inegi": "08"},
    {"name": "CIUDAD DE MEXICO", "code": "DF", "inegi": "09"},
    {"name": "COAHUILA", "code": "CL", "inegi": "05"},
    {"name": "COLIMA", "code": "CM", "inegi": "06"},
    {"name": "DURANGO", "code": "DG", "inegi": "10"},
    {"name": "ESTADO DE MEXICO", "code": "MC", "inegi": "15"},
    {"name": "GUANAJUATO", "code": "GT", "inegi": "11"},
    {"name": "GUERRERO", "code": "GR", "inegi": "12"},
    {"name": "HIDALGO", "code": "HG", "inegi": "13"},
    {"name": "JALISCO", "code": "JC", "inegi": "14"},
    {"name": "MICHOACAN", "code": "MN", "inegi": "16"},
    {"name": "MORELOS", "code": "MS", "inegi": "17"},
    {"name": "NAYARIT", "code": "NT", "inegi": "18"},
    {"name": "NUEVO LEON", "code": "NL", "inegi": "19"},
    {"name": "OAXACA", "code": "OC", "inegi": "20"},
    {"name": "PUEBLA", "code": "PL", "inegi": "21"},
    {"name": "QUERETARO", "code": "QT", "inegi": "22"},
    {"name": "QUINTANA ROO", "code": "QR", "inegi": "23"},
    {"name": "SAN LUIS POTOSI", "code": "SP", "inegi": "24"},
    {"name": "SINALOA", "code": "SL", "inegi": "25"},
    {"name": "SONORA", "code": "SR", "inegi": "26"},
    {"name": "TABASCO", "code": "TC", "inegi": "27"},
    {"name": "TAMAULIPAS", "code": "TS", "inegi": "28"},
    {"name": "TLAXCALA", "code": "TL", "inegi": "29"},
    {"name": "VERACRUZ", "code": "VZ", "inegi": "30"},
    {"name": "YUCATAN", "code": "YN", "inegi": "31"},
    {"name": "ZACATECAS", "code": "ZS", "inegi": "32"},
]

# Common Mexican banks with CLABE codes
BANCOS_MEXICO = [
    {"code": "002", "name": "BANAMEX"},
    {"code": "012", "name": "BBVA MEXICO"},
    {"code": "014", "name": "SANTANDER"},
    {"code": "021", "name": "HSBC"},
    {"code": "030", "name": "BAJIO"},
    {"code": "036", "name": "INBURSA"},
    {"code": "044", "name": "SCOTIABANK"},
    {"code": "058", "name": "BANREGIO"},
    {"code": "072", "name": "BANORTE"},
    {"code": "127", "name": "AZTECA"},
    {"code": "130", "name": "COMPARTAMOS"},
    {"code": "137", "name": "BANCOPPEL"},
]

# Regímenes fiscales for persona física
REGIMENES_PERSONA_FISICA = [
    {"code": "605", "name": "Sueldos y Salarios e Ingresos Asimilados a Salarios"},
    {"code": "606", "name": "Arrendamiento"},
    {"code": "612", "name": "Personas Físicas con Actividades Empresariales y Profesionales"},
    {"code": "621", "name": "Incorporación Fiscal"},
    {"code": "625", "name": "Régimen de las Actividades Empresariales con ingresos a través de Plataformas Tecnológicas"},
    {"code": "626", "name": "Régimen Simplificado de Confianza"},
]


@dataclass
class PersonaFisica:
    """Represents a Mexican natural person (persona física)."""

    nombre: str
    apellido_paterno: str
    apellido_materno: str
    fecha_nacimiento: date
    sexo: Literal["H", "M"]
    estado_nacimiento: str
    estado_nacimiento_code: str

    # Calculated identifiers
    rfc: str = ""
    curp: str = ""
    nss: str = ""

    # Banking
    banco: dict = field(default_factory=dict)
    clabe: str = ""
    cuenta: str = ""
    tarjeta_debito: str = ""

    # Address
    calle: str = ""
    numero_exterior: str = ""
    numero_interior: str = ""
    colonia: str = ""
    codigo_postal: str = ""
    municipio: str = ""
    estado: str = ""

    # Contact
    telefono: str = ""
    email: str = ""

    # Fiscal
    regimen_fiscal: dict = field(default_factory=dict)

    @property
    def nombre_completo(self) -> str:
        """Full name."""
        return f"{self.nombre} {self.apellido_paterno} {self.apellido_materno}".strip()

    @property
    def edad(self) -> int:
        """Age in years."""
        today = date.today()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "tipo": "persona_fisica",
            "nombre": self.nombre,
            "apellido_paterno": self.apellido_paterno,
            "apellido_materno": self.apellido_materno,
            "nombre_completo": self.nombre_completo,
            "fecha_nacimiento": self.fecha_nacimiento.isoformat(),
            "edad": self.edad,
            "sexo": self.sexo,
            "sexo_descripcion": "Masculino" if self.sexo == "H" else "Femenino",
            "estado_nacimiento": self.estado_nacimiento,
            "estado_nacimiento_code": self.estado_nacimiento_code,
            "rfc": self.rfc,
            "curp": self.curp,
            "nss": self.nss,
            "banco": self.banco,
            "clabe": self.clabe,
            "cuenta": self.cuenta,
            "tarjeta_debito": self.tarjeta_debito,
            "direccion": {
                "calle": self.calle,
                "numero_exterior": self.numero_exterior,
                "numero_interior": self.numero_interior,
                "colonia": self.colonia,
                "codigo_postal": self.codigo_postal,
                "municipio": self.municipio,
                "estado": self.estado,
            },
            "telefono": self.telefono,
            "email": self.email,
            "regimen_fiscal": self.regimen_fiscal,
        }


@dataclass
class PersonaMoral:
    """Represents a Mexican legal entity (persona moral)."""

    razon_social: str
    fecha_constitucion: date

    # Calculated identifiers
    rfc: str = ""

    # Banking
    banco: dict = field(default_factory=dict)
    clabe: str = ""
    cuenta: str = ""

    # Address
    calle: str = ""
    numero_exterior: str = ""
    numero_interior: str = ""
    colonia: str = ""
    codigo_postal: str = ""
    municipio: str = ""
    estado: str = ""

    # Contact
    telefono: str = ""
    email: str = ""

    # Fiscal
    regimen_fiscal: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "tipo": "persona_moral",
            "razon_social": self.razon_social,
            "fecha_constitucion": self.fecha_constitucion.isoformat(),
            "rfc": self.rfc,
            "banco": self.banco,
            "clabe": self.clabe,
            "cuenta": self.cuenta,
            "direccion": {
                "calle": self.calle,
                "numero_exterior": self.numero_exterior,
                "numero_interior": self.numero_interior,
                "colonia": self.colonia,
                "codigo_postal": self.codigo_postal,
                "municipio": self.municipio,
                "estado": self.estado,
            },
            "telefono": self.telefono,
            "email": self.email,
            "regimen_fiscal": self.regimen_fiscal,
        }


class IdentityGenerator:
    """
    Generator for Mexican identities.

    Uses Faker for random data and catalogmx for RFC, CURP, CLABE, NSS generation.
    """

    def __init__(self, seed: int | None = None):
        """
        Initialize the generator.

        Args:
            seed: Optional random seed for reproducible results
        """
        self.faker = _get_faker()
        if seed is not None:
            self.faker.seed_instance(seed)
            random.seed(seed)

    def generate_persona_fisica(
        self,
        sexo: Literal["H", "M"] | None = None,
        estado: str | None = None,
        min_age: int = 18,
        max_age: int = 65,
        include_banking: bool = True,
        include_address: bool = True,
        include_contact: bool = True,
    ) -> PersonaFisica:
        """
        Generate a random Mexican persona física.

        Args:
            sexo: Gender ('H' for male, 'M' for female), random if None
            estado: Birth state name, random if None
            min_age: Minimum age (default 18)
            max_age: Maximum age (default 65)
            include_banking: Include banking details
            include_address: Include address
            include_contact: Include contact info

        Returns:
            PersonaFisica with all generated data
        """
        # Random sex if not specified
        if sexo is None:
            sexo = random.choice(["H", "M"])

        # Generate name based on sex
        if sexo == "H":
            nombre = self.faker.first_name_male()
        else:
            nombre = self.faker.first_name_female()

        apellido_paterno = self.faker.last_name()
        apellido_materno = self.faker.last_name()

        # Random birth date within age range
        today = date.today()
        min_birth = today - timedelta(days=max_age * 365)
        max_birth = today - timedelta(days=min_age * 365)
        days_range = (max_birth - min_birth).days
        fecha_nacimiento = min_birth + timedelta(days=random.randint(0, days_range))

        # Random state if not specified
        if estado:
            estado_info = next(
                (e for e in ESTADOS_MEXICO if e["name"].upper() == estado.upper()),
                random.choice(ESTADOS_MEXICO)
            )
        else:
            estado_info = random.choice(ESTADOS_MEXICO)

        estado_nacimiento = estado_info["name"]
        estado_nacimiento_code = estado_info["code"]

        # Generate RFC
        rfc = generate_rfc_persona_fisica(
            nombre=nombre,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            fecha_nacimiento=fecha_nacimiento,
        )

        # Generate CURP
        curp = generate_curp(
            nombre=nombre,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            fecha_nacimiento=fecha_nacimiento,
            sexo=sexo,
            estado=estado_nacimiento,
        )

        # Generate NSS
        subdelegation = random.randint(1, 97)
        registration_year = random.randint(0, 99)
        birth_year = fecha_nacimiento.year % 100
        sequential = random.randint(0, 9999)
        nss = generate_nss(subdelegation, registration_year, birth_year, sequential)

        persona = PersonaFisica(
            nombre=nombre,
            apellido_paterno=apellido_paterno,
            apellido_materno=apellido_materno,
            fecha_nacimiento=fecha_nacimiento,
            sexo=sexo,
            estado_nacimiento=estado_nacimiento,
            estado_nacimiento_code=estado_nacimiento_code,
            rfc=rfc,
            curp=curp,
            nss=nss,
            regimen_fiscal=random.choice(REGIMENES_PERSONA_FISICA),
        )

        if include_banking:
            self._add_banking(persona)

        if include_address:
            self._add_address(persona)

        if include_contact:
            self._add_contact(persona, nombre, apellido_paterno)

        return persona

    def generate_persona_moral(
        self,
        include_banking: bool = True,
        include_address: bool = True,
        include_contact: bool = True,
    ) -> PersonaMoral:
        """
        Generate a random Mexican persona moral (company).

        Args:
            include_banking: Include banking details
            include_address: Include address
            include_contact: Include contact info

        Returns:
            PersonaMoral with all generated data
        """
        # Generate company name
        company_types = ["S.A. de C.V.", "S.A.P.I. de C.V.", "S. de R.L. de C.V.", "S.C."]
        company_name = self.faker.company()
        razon_social = f"{company_name} {random.choice(company_types)}"

        # Random constitution date (1-50 years ago)
        today = date.today()
        min_date = today - timedelta(days=50 * 365)
        max_date = today - timedelta(days=365)
        days_range = (max_date - min_date).days
        fecha_constitucion = min_date + timedelta(days=random.randint(0, days_range))

        # Generate RFC
        rfc = generate_rfc_persona_moral(
            razon_social=razon_social,
            fecha_constitucion=fecha_constitucion,
        )

        persona = PersonaMoral(
            razon_social=razon_social,
            fecha_constitucion=fecha_constitucion,
            rfc=rfc,
            regimen_fiscal={"code": "601", "name": "General de Ley Personas Morales"},
        )

        if include_banking:
            self._add_banking(persona)

        if include_address:
            self._add_address(persona)

        if include_contact:
            # Use company name for email domain
            domain = company_name.lower().replace(" ", "").replace(",", "")[:15]
            persona.email = f"contacto@{domain}.com.mx"
            persona.telefono = self._generate_phone()

        return persona

    def _add_banking(self, persona: PersonaFisica | PersonaMoral) -> None:
        """Add banking information to persona."""
        banco = random.choice(BANCOS_MEXICO)
        persona.banco = banco

        # Generate CLABE
        branch = str(random.randint(1, 999)).zfill(3)
        account = str(random.randint(0, 99999999999)).zfill(11)
        persona.clabe = generate_clabe(banco["code"], branch, account)
        persona.cuenta = account

        # Generate debit card (Visa or Mastercard)
        card_type = random.choice(["visa", "mastercard"])
        if card_type == "visa":
            prefix = "4"
            persona.tarjeta_debito = prefix + "".join(str(random.randint(0, 9)) for _ in range(15))
        else:
            prefix = "5" + str(random.randint(1, 5))
            persona.tarjeta_debito = prefix + "".join(str(random.randint(0, 9)) for _ in range(14))

        # Add Luhn check digit
        persona.tarjeta_debito = self._add_luhn_checksum(persona.tarjeta_debito[:-1])

    def _add_luhn_checksum(self, card_number: str) -> str:
        """Calculate and append Luhn checksum digit."""
        digits = [int(d) for d in card_number]
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]

        total = sum(odd_digits)
        for d in even_digits:
            total += sum(divmod(d * 2, 10))

        check_digit = (10 - (total % 10)) % 10
        return card_number + str(check_digit)

    def _add_address(self, persona: PersonaFisica | PersonaMoral) -> None:
        """Add address information to persona."""
        persona.calle = self.faker.street_name()
        persona.numero_exterior = str(random.randint(1, 9999))
        persona.numero_interior = "" if random.random() > 0.3 else str(random.randint(1, 50))
        persona.colonia = self.faker.city_suffix() + " " + self.faker.last_name()
        persona.codigo_postal = str(random.randint(1000, 99999)).zfill(5)
        persona.municipio = self.faker.city()
        persona.estado = random.choice(ESTADOS_MEXICO)["name"].title()

    def _add_contact(
        self, persona: PersonaFisica, nombre: str, apellido: str
    ) -> None:
        """Add contact information to persona física."""
        persona.telefono = self._generate_phone()

        # Generate email
        email_styles = [
            f"{nombre.lower()}_{apellido.lower()}",
            f"{nombre.lower()}.{apellido.lower()}",
            f"{nombre.lower()}{random.randint(1, 99)}",
            f"{apellido.lower()}.{nombre.lower()}",
        ]
        email_domains = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com.mx", "proton.me"]

        email_user = random.choice(email_styles)
        # Normalize email (remove accents)
        import unicodedata
        email_user = unicodedata.normalize("NFD", email_user)
        email_user = "".join(c for c in email_user if unicodedata.category(c) != "Mn")

        persona.email = f"{email_user}@{random.choice(email_domains)}"

    def _generate_phone(self) -> str:
        """Generate a Mexican phone number (10 digits)."""
        # Mexican area codes (LADA)
        ladas = ["55", "33", "81", "222", "442", "477", "614", "656", "664", "744", "998"]
        lada = random.choice(ladas)

        remaining = 10 - len(lada)
        number = "".join(str(random.randint(0, 9)) for _ in range(remaining))

        return lada + number


def generate_identity(
    tipo: Literal["fisica", "moral"] = "fisica",
    **kwargs,
) -> dict:
    """
    Generate a complete Mexican identity.

    Args:
        tipo: Type of identity ('fisica' or 'moral')
        **kwargs: Additional arguments passed to generator
            For persona física:
                - sexo: 'H' or 'M'
                - estado: Birth state name
                - min_age: Minimum age (default 18)
                - max_age: Maximum age (default 65)
            For persona moral:
                - No additional options

    Returns:
        Dictionary with complete identity data

    Example:
        >>> identity = generate_identity()
        >>> print(identity['nombre_completo'])
        'Juan Pérez García'
        >>> print(identity['rfc'])
        'PEGJ900515XXX'
    """
    generator = IdentityGenerator()

    if tipo == "moral":
        return generator.generate_persona_moral(**kwargs).to_dict()
    else:
        return generator.generate_persona_fisica(**kwargs).to_dict()


def generate_persona_fisica(**kwargs) -> dict:
    """
    Generate a Mexican persona física identity.

    Shortcut for generate_identity(tipo='fisica', **kwargs)
    """
    return generate_identity(tipo="fisica", **kwargs)


def generate_persona_moral(**kwargs) -> dict:
    """
    Generate a Mexican persona moral identity.

    Shortcut for generate_identity(tipo='moral', **kwargs)
    """
    return generate_identity(tipo="moral", **kwargs)
