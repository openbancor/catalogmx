__version__ = "0.3.0"

# RFC imports
from .validators.rfc import (
    RFCValidator,
    RFCGenerator,
    RFCGeneratorFisicas,
    RFCGeneratorMorales,
)

# CURP imports
from .validators.curp import (
    CURPValidator,
    CURPGenerator,
    CURPException,
    CURPLengthError,
    CURPStructureError,
)

# Modern helper functions (recommended API)
from .helpers import (
    # RFC helpers
    generate_rfc_persona_fisica,
    generate_rfc_persona_moral,
    validate_rfc,
    detect_rfc_type,
    is_valid_rfc,
    # CURP helpers
    generate_curp,
    validate_curp,
    get_curp_info,
    is_valid_curp,
)

__all__ = [
    # RFC Classes (legacy/advanced usage)
    'RFCValidator',
    'RFCGenerator',
    'RFCGeneratorFisicas',
    'RFCGeneratorMorales',
    # CURP Classes (legacy/advanced usage)
    'CURPValidator',
    'CURPGenerator',
    'CURPException',
    'CURPLengthError',
    'CURPStructureError',
    # Modern helper functions (recommended)
    'generate_rfc_persona_fisica',
    'generate_rfc_persona_moral',
    'validate_rfc',
    'detect_rfc_type',
    'is_valid_rfc',
    'generate_curp',
    'validate_curp',
    'get_curp_info',
    'is_valid_curp',
]
