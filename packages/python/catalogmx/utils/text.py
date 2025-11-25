"""
Text normalization utilities for catalogmx
==========================================

Provides accent-insensitive text normalization for searching across catalogs.
"""

from collections.abc import Callable
from typing import cast

try:
    from unidecode import unidecode

    unidecode = cast(Callable[[str], str], unidecode)
except ImportError:
    # Fallback if unidecode not available
    def unidecode(text: str) -> str:
        """Fallback implementation using unicodedata."""
        import unicodedata

        nfd = unicodedata.normalize("NFD", text)
        return "".join(char for char in nfd if unicodedata.category(char) != "Mn")


def normalize_text(text: str) -> str:
    """
    Normalize text by removing accents and converting to uppercase.
    Makes text searchable without worrying about accents or case.

    Args:
        text: Text to normalize

    Returns:
        Normalized text (uppercase, no accents)

    Examples:
        >>> normalize_text("México")
        'MEXICO'
        >>> normalize_text("San José")
        'SAN JOSE'
        >>> normalize_text("Michoacán de Ocampo")
        'MICHOACAN DE OCAMPO'
    """
    result = unidecode(text)
    return str(result).upper()


def normalize_for_search(text: str) -> str:
    """
    Alias for normalize_text for clarity in search contexts.

    Args:
        text: Text to normalize for searching

    Returns:
        Normalized text suitable for accent-insensitive search
    """
    return normalize_text(text)


__all__ = ["normalize_text", "normalize_for_search", "unidecode"]
