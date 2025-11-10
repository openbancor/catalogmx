__version__ = "0.3.0"

# RFC imports
# Modern helper functions (recommended API)
from .helpers import (
    detect_rfc_type,
    # CURP helpers
    generate_curp,
    # RFC helpers
    generate_rfc_persona_fisica,
    generate_rfc_persona_moral,
    get_curp_info,
    is_valid_curp,
    is_valid_rfc,
    validate_curp,
    validate_rfc,
)

# CURP imports
from .validators.curp import (
    CURPException,
    CURPGenerator,
    CURPLengthError,
    CURPStructureError,
    CURPValidator,
)
from .validators.rfc import (
    RFCGenerator,
    RFCGeneratorFisicas,
    RFCGeneratorMorales,
    RFCValidator,
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
