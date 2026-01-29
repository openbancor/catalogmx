"""
Identity generators for Mexican test data.

This module provides functions to generate complete Mexican identities
with realistic data for testing and development purposes.
"""

from catalogmx.generators.identity import (
    IdentityGenerator,
    generate_identity,
    generate_persona_fisica,
    generate_persona_moral,
)

__all__ = [
    "IdentityGenerator",
    "generate_identity",
    "generate_persona_fisica",
    "generate_persona_moral",
]
