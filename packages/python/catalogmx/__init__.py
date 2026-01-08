"""
catalogmx - Mexican Data Validation and Catalog Library

A comprehensive library for validating Mexican identifiers (RFC, CURP, CLABE, NSS),
accessing official catalogs (SAT, Banxico, INEGI, SEPOMEX, IFT, CNBV), and
calculating taxes and payroll (ISR, RESICO, IMSS, IVA, Costo del Trabajador).

Usage:
    # Validators - Simple helper functions
    from catalogmx import is_valid_rfc, is_valid_curp, is_valid_clabe, is_valid_nss

    is_valid_rfc('PEGJ900515KL8')  # True
    is_valid_curp('PEGJ900515HJCRRN05')  # True
    is_valid_clabe('002010077777777771')  # True
    is_valid_nss('12345678903')  # True

    # Generators
    from catalogmx import generate_rfc_persona_fisica, generate_curp, generate_clabe

    rfc = generate_rfc_persona_fisica(
        nombre='Juan',
        apellido_paterno='Pérez',
        apellido_materno='García',
        fecha_nacimiento='1990-05-15'
    )

    clabe = generate_clabe(
        bank_code='002',      # Banamex
        branch_code='010',    # Branch
        account_number='07777777777'
    )  # Returns: '002010077777777771'

    # Calculators
    from catalogmx.calculators import calculate_isr, calculate_resico
    from catalogmx.calculators import calcular_cuotas_obrero_patronales
    from catalogmx.calculators import IVACalculator, calcular_costo_total

    # Catalogs
    from catalogmx.catalogs.sat.cfdi_4 import FormaPago, MetodoPago, UsoCFDI
    from catalogmx.catalogs.banxico import Banks
    from catalogmx.catalogs.inegi import States, Municipios
    from catalogmx.catalogs.sepomex import CodigosPostales
"""

__version__ = "0.3.0"

# =============================================================================
# Modern Helper Functions (recommended API)
# =============================================================================
from catalogmx.helpers import (
    # RFC helpers
    detect_rfc_type,
    # CLABE helpers
    generate_clabe,
    generate_clabe_random,
    # CURP helpers
    generate_curp,
    generate_rfc_persona_fisica,
    generate_rfc_persona_moral,
    get_clabe_info,
    get_curp_info,
    # NSS helpers
    get_nss_info,
    # Utility
    get_project_root,
    is_valid_clabe,
    is_valid_curp,
    is_valid_nss,
    is_valid_rfc,
    validate_clabe,
    validate_curp,
    validate_nss,
    validate_rfc,
)

# =============================================================================
# Validator Classes (for advanced usage)
# =============================================================================
from catalogmx.validators.clabe import (
    CLABECheckDigitError,
    CLABEException,
    CLABELengthError,
    CLABEStructureError,
    CLABEValidator,
)
from catalogmx.validators.curp import (
    CURPException,
    CURPGenerator,
    CURPLengthError,
    CURPStructureError,
    CURPValidator,
)
from catalogmx.validators.nss import (
    NSSCheckDigitError,
    NSSException,
    NSSLengthError,
    NSSStructureError,
    NSSValidator,
)
from catalogmx.validators.rfc import (
    RFCGenerator,
    RFCGeneratorFisicas,
    RFCGeneratorMorales,
    RFCValidator,
)

# =============================================================================
# Submodules (import as needed)
# =============================================================================
# Catalogs: from catalogmx import catalogs
# Calculators: from catalogmx import calculators
# Validators: from catalogmx import validators

__all__ = [
    # Version
    "__version__",
    # RFC Helper Functions
    "generate_rfc_persona_fisica",
    "generate_rfc_persona_moral",
    "validate_rfc",
    "detect_rfc_type",
    "is_valid_rfc",
    # RFC Classes
    "RFCValidator",
    "RFCGenerator",
    "RFCGeneratorFisicas",
    "RFCGeneratorMorales",
    # CURP Helper Functions
    "generate_curp",
    "validate_curp",
    "get_curp_info",
    "is_valid_curp",
    # CURP Classes
    "CURPValidator",
    "CURPGenerator",
    "CURPException",
    "CURPLengthError",
    "CURPStructureError",
    # CLABE Helper Functions
    "generate_clabe",
    "generate_clabe_random",
    "validate_clabe",
    "get_clabe_info",
    "is_valid_clabe",
    # CLABE Classes
    "CLABEValidator",
    "CLABEException",
    "CLABELengthError",
    "CLABEStructureError",
    "CLABECheckDigitError",
    # NSS Helper Functions
    "validate_nss",
    "get_nss_info",
    "is_valid_nss",
    # NSS Classes
    "NSSValidator",
    "NSSException",
    "NSSLengthError",
    "NSSStructureError",
    "NSSCheckDigitError",
    # Utility
    "get_project_root",
]
