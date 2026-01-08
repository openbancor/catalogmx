"""
CLABE Utilities - Enhanced CLABE generation, decoding, and validation

This module provides comprehensive CLABE (Clave Bancaria Estandarizada) utilities
including generation with optional parameters, decoding with full bank/plaza info,
and example generation.

Examples:
    >>> from catalogmx.utils.clabe_utils import generate_clabe_random, decode_clabe
    >>>
    >>> # Generate a random CLABE for BBVA in CDMX
    >>> clabe = generate_clabe_random(bank_code="012", plaza_code="180")
    >>> print(clabe)
    012180XXXXXXXXXXX
    >>>
    >>> # Decode a CLABE to get full info
    >>> info = decode_clabe("002010077777777771")
    >>> print(info["bank"]["name"])
    BANAMEX
"""

import random
from typing import TYPE_CHECKING, TypedDict

# Lazy imports to avoid circular dependencies
if TYPE_CHECKING:
    pass


def _get_bank_catalog():
    """Lazy import of BankCatalog to avoid circular imports."""
    from catalogmx.catalogs.banxico.banks import BankCatalog

    return BankCatalog


def _get_plaza_catalog():
    """Lazy import of CodigosPlazaCatalog to avoid circular imports."""
    from catalogmx.catalogs.banxico.codigos_plaza import CodigosPlazaCatalog

    return CodigosPlazaCatalog


def _get_clabe_functions():
    """Lazy import of CLABE functions to avoid circular imports."""
    from catalogmx.validators.clabe import generate_clabe, validate_clabe

    return generate_clabe, validate_clabe


class BankInfo(TypedDict, total=False):
    """Bank information from catalog."""

    code: str
    name: str
    full_name: str
    rfc: str | None
    spei: bool


class PlazaInfo(TypedDict, total=False):
    """Plaza information from catalog."""

    codigo: str
    plaza: str
    estado: str
    cve_entidad: str


class DecodedCLABE(TypedDict, total=False):
    """Full decoded CLABE information."""

    clabe: str
    is_valid: bool
    bank_code: str
    plaza_code: str
    account_number: str
    check_digit: str
    bank: BankInfo | None
    plaza: PlazaInfo | None
    all_plazas: list[PlazaInfo]  # Some plaza codes map to multiple locations


def decode_clabe(clabe: str) -> DecodedCLABE | None:
    """
    Decode a CLABE to extract all information including bank and plaza details.

    Args:
        clabe: 18-digit CLABE number

    Returns:
        Dictionary with full CLABE breakdown or None if format is invalid

    Examples:
        >>> info = decode_clabe("002010077777777771")
        >>> info["is_valid"]
        True
        >>> info["bank"]["name"]
        'BANAMEX'
        >>> info["bank"]["full_name"]
        'Banco Nacional de México, S.A.'

        >>> # Invalid check digit
        >>> info = decode_clabe("002010077777777770")
        >>> info["is_valid"]
        False

        >>> # Get plaza info
        >>> info = decode_clabe("012180000000000001")
        >>> info["plaza"]["plaza"]
        'Ciudad de México'
    """
    clabe = clabe.strip() if clabe else ""

    if len(clabe) != 18 or not clabe.isdigit():
        return None

    bank_code = clabe[:3]
    plaza_code = clabe[3:6]
    account_number = clabe[6:17]
    check_digit = clabe[17]

    # Lazy imports
    BankCatalog = _get_bank_catalog()
    CodigosPlazaCatalog = _get_plaza_catalog()
    _, validate_clabe = _get_clabe_functions()

    # Get bank info
    bank_data = BankCatalog.get_bank_by_code(bank_code)
    bank_info: BankInfo | None = None
    if bank_data:
        bank_info = {
            "code": bank_data["code"],
            "name": bank_data["name"],
            "full_name": bank_data.get("full_name", ""),
            "rfc": bank_data.get("rfc"),
            "spei": bank_data.get("spei", False),
        }

    # Get plaza info (may have multiple matches)
    all_plazas = CodigosPlazaCatalog.buscar_por_codigo(plaza_code)
    plaza_info: PlazaInfo | None = None
    if all_plazas:
        plaza_info = all_plazas[0]  # Return first match as primary

    return {
        "clabe": clabe,
        "is_valid": validate_clabe(clabe),
        "bank_code": bank_code,
        "plaza_code": plaza_code,
        "account_number": account_number,
        "check_digit": check_digit,
        "bank": bank_info,
        "plaza": plaza_info,
        "all_plazas": all_plazas,
    }


def generate_clabe_random(
    bank_code: str | None = None,
    plaza_code: str | None = None,
    account_number: str | None = None,
) -> str:
    """
    Generate a valid CLABE with optional parameters.

    Any parameter not provided will be randomly generated.

    Args:
        bank_code: 3-digit bank code (optional, e.g., "012" for BBVA)
        plaza_code: 3-digit plaza code (optional, e.g., "180" for CDMX)
        account_number: 11-digit account number (optional)

    Returns:
        Valid 18-digit CLABE

    Examples:
        >>> # Fully random CLABE
        >>> clabe = generate_clabe_random()
        >>> len(clabe)
        18

        >>> # CLABE for BBVA (code 012)
        >>> clabe = generate_clabe_random(bank_code="012")
        >>> clabe[:3]
        '012'

        >>> # CLABE for any bank in CDMX (plaza 180)
        >>> clabe = generate_clabe_random(plaza_code="180")
        >>> clabe[3:6]
        '180'

        >>> # Fully specified
        >>> clabe = generate_clabe_random("012", "180", "12345678901")
        >>> clabe
        '012180123456789010'
    """
    # Lazy imports
    BankCatalog = _get_bank_catalog()
    CodigosPlazaCatalog = _get_plaza_catalog()
    generate_clabe, _ = _get_clabe_functions()

    # Get or generate bank code
    if bank_code is None:
        all_banks = BankCatalog.get_spei_banks()
        if all_banks:
            bank_code = random.choice(all_banks)["code"]
        else:
            bank_code = str(random.randint(1, 999)).zfill(3)

    # Get or generate plaza code
    if plaza_code is None:
        all_plazas = CodigosPlazaCatalog.get_all()
        if all_plazas:
            plaza_code = random.choice(all_plazas)["codigo"]
        else:
            plaza_code = str(random.randint(1, 999)).zfill(3)

    # Get or generate account number
    if account_number is None:
        account_number = str(random.randint(0, 99999999999)).zfill(11)

    return generate_clabe(bank_code, plaza_code, account_number)


def generate_clabe_examples(count: int = 5) -> list[dict]:
    """
    Generate example CLABEs with full decoded information.

    Useful for testing, demos, and documentation.

    Args:
        count: Number of examples to generate (default 5)

    Returns:
        List of decoded CLABE dictionaries

    Examples:
        >>> examples = generate_clabe_examples(3)
        >>> len(examples)
        3
        >>> examples[0]["is_valid"]
        True
        >>> examples[0]["bank"]["name"]  # Will vary
        'BBVA'
    """
    examples = []
    for _ in range(count):
        clabe = generate_clabe_random()
        decoded = decode_clabe(clabe)
        if decoded:
            examples.append(decoded)
    return examples


def generate_clabe_for_bank(bank_name: str, plaza_name: str | None = None) -> str | None:
    """
    Generate a CLABE for a specific bank (by name).

    Args:
        bank_name: Bank name (case-insensitive, e.g., "BBVA", "Banamex")
        plaza_name: Optional plaza name (case-insensitive)

    Returns:
        Valid 18-digit CLABE or None if bank not found

    Examples:
        >>> clabe = generate_clabe_for_bank("BBVA")
        >>> decode_clabe(clabe)["bank"]["name"]
        'BBVA'

        >>> clabe = generate_clabe_for_bank("Santander", "Guadalajara")
        >>> info = decode_clabe(clabe)
        >>> info["bank"]["name"]
        'SANTANDER'
    """
    # Lazy imports
    BankCatalog = _get_bank_catalog()
    CodigosPlazaCatalog = _get_plaza_catalog()

    bank = BankCatalog.get_bank_by_name(bank_name)
    if not bank:
        return None

    bank_code = bank["code"]

    plaza_code = None
    if plaza_name:
        plazas = CodigosPlazaCatalog.buscar_por_plaza(plaza_name)
        if plazas:
            plaza_code = plazas[0]["codigo"]

    return generate_clabe_random(bank_code=bank_code, plaza_code=plaza_code)


def get_common_banks() -> list[dict]:
    """
    Get list of common banks used for CLABE generation.

    Returns:
        List of bank dictionaries with code, name, full_name

    Examples:
        >>> banks = get_common_banks()
        >>> len(banks) > 10
        True
        >>> banks[0]["name"]
        'BANAMEX'
    """
    BankCatalog = _get_bank_catalog()
    return BankCatalog.get_spei_banks()


def get_plaza_suggestions(query: str) -> list[dict]:
    """
    Search plazas by name for autocomplete/suggestions.

    Args:
        query: Search query (partial name)

    Returns:
        List of matching plazas

    Examples:
        >>> plazas = get_plaza_suggestions("Guada")
        >>> any(p["plaza"] == "Guadalajara" for p in plazas)
        True
    """
    CodigosPlazaCatalog = _get_plaza_catalog()
    return CodigosPlazaCatalog.search(query)


def format_clabe(clabe: str, separator: str = "-") -> str:
    """
    Format a CLABE with separators for readability.

    Args:
        clabe: 18-digit CLABE
        separator: Separator character (default "-")

    Returns:
        Formatted CLABE: XXX-XXX-XXXXXXXXXXX-X

    Examples:
        >>> format_clabe("002010077777777771")
        '002-010-07777777777-1'

        >>> format_clabe("002010077777777771", " ")
        '002 010 07777777777 1'
    """
    if len(clabe) != 18:
        return clabe
    return f"{clabe[:3]}{separator}{clabe[3:6]}{separator}{clabe[6:17]}{separator}{clabe[17]}"


def describe_clabe(clabe: str) -> str:
    """
    Get a human-readable description of a CLABE.

    Args:
        clabe: 18-digit CLABE

    Returns:
        Human-readable description

    Examples:
        >>> print(describe_clabe("002010077777777771"))
        CLABE: 002-010-07777777777-1
        Estado: Válida ✓
        Banco: BANAMEX (Banco Nacional de México, S.A.)
        Plaza: Aguascalientes, Aguascalientes
        Cuenta: 07777777777
    """
    info = decode_clabe(clabe)
    if not info:
        return f"CLABE inválida: {clabe}"

    lines = [
        f"CLABE: {format_clabe(clabe)}",
        f"Estado: {'Válida ✓' if info['is_valid'] else 'Inválida ✗'}",
    ]

    if info["bank"]:
        bank = info["bank"]
        bank_line = f"Banco: {bank['name']}"
        if bank.get("full_name"):
            bank_line += f" ({bank['full_name']})"
        lines.append(bank_line)
    else:
        lines.append(f"Banco: Código {info['bank_code']} (no encontrado)")

    if info["plaza"]:
        plaza = info["plaza"]
        lines.append(f"Plaza: {plaza['plaza']}, {plaza['estado']}")
        if len(info["all_plazas"]) > 1:
            lines.append(f"  (Nota: {len(info['all_plazas'])} ubicaciones con este código)")
    else:
        lines.append(f"Plaza: Código {info['plaza_code']} (no encontrado)")

    lines.append(f"Cuenta: {info['account_number']}")

    return "\n".join(lines)


__all__ = [
    "decode_clabe",
    "generate_clabe_random",
    "generate_clabe_examples",
    "generate_clabe_for_bank",
    "get_common_banks",
    "get_plaza_suggestions",
    "format_clabe",
    "describe_clabe",
    "DecodedCLABE",
    "BankInfo",
    "PlazaInfo",
]
