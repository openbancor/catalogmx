__version__ = "0.2.0"

# RFC imports
from .rfc import (
    RFCValidator,
    RFCGenerator,
    RFCGeneratorFisicas,
    RFCGeneratorMorales,
)

# CURP imports
from .curp import (
    CURPValidator,
    CURPGenerator,
    CURPException,
    CURPLengthError,
    CURPStructureError,
)

__all__ = [
    # RFC
    'RFCValidator',
    'RFCGenerator',
    'RFCGeneratorFisicas',
    'RFCGeneratorMorales',
    # CURP
    'CURPValidator',
    'CURPGenerator',
    'CURPException',
    'CURPLengthError',
    'CURPStructureError',
]
