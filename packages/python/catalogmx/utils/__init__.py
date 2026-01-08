"""
catalogmx - Utility modules
"""

from catalogmx.utils.clabe_utils import (
    decode_clabe,
    describe_clabe,
    format_clabe,
    generate_clabe_examples,
    generate_clabe_for_bank,
    generate_clabe_random,
    get_common_banks,
    get_plaza_suggestions,
)
from catalogmx.utils.text import normalize_text

__all__ = [
    # Text utilities
    "normalize_text",
    # CLABE utilities
    "decode_clabe",
    "generate_clabe_random",
    "generate_clabe_examples",
    "generate_clabe_for_bank",
    "get_common_banks",
    "get_plaza_suggestions",
    "format_clabe",
    "describe_clabe",
]
