#!/usr/bin/python
"""
Modern, user-friendly API for RFC and CURP generation and validation.

This module provides simple functions for common use cases, making it easier
to work with Mexican identification codes without dealing with class constructors.
"""

import datetime

from .validators.curp import CURPGenerator, CURPValidator
from .validators.rfc import RFCGeneratorFisicas, RFCGeneratorMorales, RFCValidator

# ============================================================================
# RFC Helper Functions
# ============================================================================


def generate_rfc_persona_fisica(
    nombre: str,
    apellido_paterno: str,
    apellido_materno: str,
    fecha_nacimiento: datetime.date | str,
    **kwargs,
) -> str:
    """
    Generate RFC for a natural person (Persona Física).

    Args:
        nombre: First name(s)
        apellido_paterno: Father's surname
        apellido_materno: Mother's surname
        fecha_nacimiento: Birth date (datetime.date or 'YYYY-MM-DD' string)
        **kwargs: Additional arguments passed to RFCGeneratorFisicas

    Returns:
        str: 13-character RFC code

    Example:
        >>> rfc = generate_rfc_persona_fisica(
        ...     nombre='Juan',
        ...     apellido_paterno='Pérez',
        ...     apellido_materno='García',
        ...     fecha_nacimiento='1990-05-15'
        ... )
        >>> print(rfc)  # PEGJ900515...
    """
    # Convert string date to datetime.date if needed
    if isinstance(fecha_nacimiento, str):
        fecha_nacimiento = datetime.datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()

    generator = RFCGeneratorFisicas(
        paterno=apellido_paterno,
        materno=apellido_materno,
        nombre=nombre,
        fecha=fecha_nacimiento,
        **kwargs,
    )
    return generator.rfc


def generate_rfc_persona_moral(
    razon_social: str, fecha_constitucion: datetime.date | str, **kwargs
) -> str:
    """
    Generate RFC for a legal entity (Persona Moral/company).

    Args:
        razon_social: Company name
        fecha_constitucion: Constitution date (datetime.date or 'YYYY-MM-DD' string)
        **kwargs: Additional arguments passed to RFCGeneratorMorales

    Returns:
        str: 12-character RFC code

    Example:
        >>> rfc = generate_rfc_persona_moral(
        ...     razon_social='Grupo Bimbo S.A.B. de C.V.',
        ...     fecha_constitucion='1981-06-15'
        ... )
        >>> print(rfc)  # GBI810615...
    """
    # Convert string date to datetime.date if needed
    if isinstance(fecha_constitucion, str):
        fecha_constitucion = datetime.datetime.strptime(fecha_constitucion, "%Y-%m-%d").date()

    generator = RFCGeneratorMorales(razon_social=razon_social, fecha=fecha_constitucion, **kwargs)
    return generator.rfc


def validate_rfc(rfc: str, check_checksum: bool = True) -> bool:
    """
    Validate an RFC code.

    Args:
        rfc: RFC code to validate
        check_checksum: Whether to validate the checksum digit (default: True)

    Returns:
        bool: True if valid, False otherwise

    Example:
        >>> validate_rfc('PEGJ900515KL8')
        True
        >>> validate_rfc('INVALID')
        False
    """
    try:
        validator = RFCValidator(rfc)
        if not validator.validate_general_regex():
            return False
        if check_checksum:
            return validator.validate_checksum()
        return True
    except:
        return False


def detect_rfc_type(rfc: str) -> str | None:
    """
    Detect the type of RFC (Persona Física, Persona Moral, or Genérico).

    Args:
        rfc: RFC code to analyze

    Returns:
        str: 'fisica', 'moral', 'generico', or None if invalid

    Example:
        >>> detect_rfc_type('PEGJ900515KL8')
        'fisica'
        >>> detect_rfc_type('GBI810615945')
        'moral'
    """
    try:
        validator = RFCValidator(rfc)
        tipo = validator.detect_fisica_moral()
        if tipo == "Persona Física":
            return "fisica"
        elif tipo == "Persona Moral":
            return "moral"
        elif tipo == "Genérico":
            return "generico"
        return None
    except:
        return None


# ============================================================================
# CURP Helper Functions
# ============================================================================


def generate_curp(
    nombre: str,
    apellido_paterno: str,
    apellido_materno: str | None,
    fecha_nacimiento: datetime.date | str,
    sexo: str,
    estado: str,
    differentiator: str | None = None,
) -> str:
    """
    Generate a CURP code.

    Args:
        nombre: First name(s)
        apellido_paterno: Father's surname
        apellido_materno: Mother's surname (can be empty string or None)
        fecha_nacimiento: Birth date (datetime.date or 'YYYY-MM-DD' string)
        sexo: Gender ('H' for male, 'M' for female)
        estado: Birth state (name or 2-letter code)
        differentiator: Optional custom differentiator (position 17)

    Returns:
        str: 18-character CURP code

    Example:
        >>> curp = generate_curp(
        ...     nombre='Juan',
        ...     apellido_paterno='Pérez',
        ...     apellido_materno='García',
        ...     fecha_nacimiento='1990-05-15',
        ...     sexo='H',
        ...     estado='Jalisco'
        ... )
        >>> print(curp)  # PEGJ900515HJCRRN...
    """
    # Convert string date to datetime.date if needed
    if isinstance(fecha_nacimiento, str):
        fecha_nacimiento = datetime.datetime.strptime(fecha_nacimiento, "%Y-%m-%d").date()

    # Handle empty apellido_materno
    if not apellido_materno:
        apellido_materno = ""

    generator = CURPGenerator(
        nombre=nombre,
        paterno=apellido_paterno,
        materno=apellido_materno,
        fecha_nacimiento=fecha_nacimiento,
        sexo=sexo,
        estado=estado,
    )

    # If custom differentiator is provided, regenerate homoclave
    if differentiator is not None:
        # Generate base CURP (first 16 characters)
        base = (
            generator.generate_letters()
            + generator.generate_date()
            + generator.sexo
            + generator.get_state_code(generator.estado)
            + generator.generate_consonants()
        )
        # Add custom differentiator and calculate check digit
        check_digit = CURPGenerator.calculate_check_digit(base + differentiator)
        return base + differentiator + check_digit

    return generator.curp


def validate_curp(curp: str, check_digit: bool = True) -> bool:
    """
    Validate a CURP code.

    Args:
        curp: CURP code to validate
        check_digit: Whether to validate the check digit (default: True)

    Returns:
        bool: True if valid, False otherwise

    Example:
        >>> validate_curp('PEGJ900515HJCRRN05')
        True
        >>> validate_curp('INVALID')
        False
    """
    try:
        validator = CURPValidator(curp)
        if not validator.validate():
            return False
        if check_digit:
            return validator.validate_check_digit()
        return True
    except:
        return False


def get_curp_info(curp: str) -> dict | None:
    """
    Extract information from a CURP code.

    Args:
        curp: CURP code to analyze

    Returns:
        dict: Extracted information or None if invalid

    Example:
        >>> info = get_curp_info('PEGJ900515HJCRRN05')
        >>> print(info['fecha_nacimiento'])
        '1990-05-15'
        >>> print(info['sexo'])
        'Hombre'
    """
    try:
        validator = CURPValidator(curp)
        if not validator.validate():
            return None

        # Extract information
        year = int(curp[4:6])
        # Assume year 2000+ if < 50, otherwise 1900+
        year = 2000 + year if year < 50 else 1900 + year
        month = int(curp[6:8])
        day = int(curp[8:10])

        sexo_code = curp[10]
        estado_code = curp[11:13]

        return {
            "fecha_nacimiento": f"{year:04d}-{month:02d}-{day:02d}",
            "sexo": "Hombre" if sexo_code == "H" else "Mujer",
            "sexo_code": sexo_code,
            "estado_code": estado_code,
            "differentiator": curp[16],
            "check_digit": curp[17],
            "check_digit_valid": validator.validate_check_digit(),
        }
    except:
        return None


# ============================================================================
# Quick validation functions
# ============================================================================


def is_valid_rfc(rfc: str) -> bool:
    """Quick RFC validation. Alias for validate_rfc()."""
    return validate_rfc(rfc)


def is_valid_curp(curp: str) -> bool:
    """Quick CURP validation. Alias for validate_curp()."""
    return validate_curp(curp)


# ============================================================================
# Path Helper Functions
# ============================================================================
from pathlib import Path


def get_project_root() -> Path:
    """Returns the project root folder by searching for a .git directory."""
    current_path = Path(__file__).parent
    while current_path.parent != current_path:
        if (current_path / ".git").exists():
            return current_path
        current_path = current_path.parent
    raise FileNotFoundError("Project root not found. Could not find .git directory.")
