# python-rfcmx

🇲🇽 **Complete RFC and CURP generator and validator for Mexico**

A modern Python library to generate and validate Mexican tax identification codes (RFC) and population registry codes (CURP) according to official SAT and RENAPO specifications.

[![Tests](https://img.shields.io/badge/tests-49%20passing-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.6+-blue)]()
[![License](https://img.shields.io/badge/license-BSD-blue)]()

## Features

✅ **RFC (Registro Federal de Contribuyentes)**
- Generate RFC for individuals (Persona Física)
- Generate RFC for companies (Persona Moral)
- Complete SAT official rules implementation
- Cacophonic word handling
- Number conversion (Arabic & Roman numerals)
- Homoclave calculation

✅ **CURP (Clave Única de Registro de Población)**
- Generate CURP for Mexican citizens
- Complete RENAPO official specifications
- 70+ inconvenient words list (Anexo 2)
- Check digit calculation and validation
- Homonymy support with customizable differentiator
- State code validation for all 32 Mexican states

✅ **Modern & Easy-to-Use API**
- Simple function-based interface
- Type hints support
- String date support (`'YYYY-MM-DD'`)
- Comprehensive validation
- Extract information from existing codes

## Installation

```bash
pip install rfcmx
```

## Quick Start

### RFC - Persona Física (Individual)

```python
from rfcmx import generate_rfc_persona_fisica, validate_rfc

# Generate RFC
rfc = generate_rfc_persona_fisica(
    nombre='Juan',
    apellido_paterno='Pérez',
    apellido_materno='García',
    fecha_nacimiento='1990-05-15'  # String or datetime.date
)
print(rfc)  # PEGJ900515KL8

# Validate RFC
is_valid = validate_rfc('PEGJ900515KL8')
print(is_valid)  # True
```

### RFC - Persona Moral (Company)

```python
from rfcmx import generate_rfc_persona_moral

# Generate company RFC
rfc = generate_rfc_persona_moral(
    razon_social='Grupo Bimbo S.A.B. de C.V.',
    fecha_constitucion='1981-06-15'
)
print(rfc)  # GBI810615945
```

### CURP

```python
from rfcmx import generate_curp, validate_curp, get_curp_info

# Generate CURP
curp = generate_curp(
    nombre='Juan',
    apellido_paterno='Pérez',
    apellido_materno='García',
    fecha_nacimiento='1990-05-15',
    sexo='H',  # H=Hombre, M=Mujer
    estado='Jalisco'
)
print(curp)  # PEGJ900515HJCRRN05

# Validate CURP (including check digit)
is_valid = validate_curp('PEGJ900515HJCRRN05')
print(is_valid)  # True

# Extract information from CURP
info = get_curp_info('PEGJ900515HJCRRN05')
print(info)
# {
#     'fecha_nacimiento': '1990-05-15',
#     'sexo': 'Hombre',
#     'sexo_code': 'H',
#     'estado_code': 'JC',
#     'differentiator': '0',
#     'check_digit': '5',
#     'check_digit_valid': True
# }
```

## Advanced Usage

### CURP with Custom Differentiator (for homonyms)

When two people have the same first 16 CURP characters, RENAPO assigns different differentiators:

```python
from rfcmx import generate_curp

base_data = {
    'nombre': 'Juan',
    'apellido_paterno': 'Pérez',
    'apellido_materno': 'García',
    'fecha_nacimiento': '1990-05-15',
    'sexo': 'H',
    'estado': 'Jalisco'
}

# First person (default differentiator '0')
curp1 = generate_curp(**base_data)
print(curp1)  # PEGJ900515HJCRRN05

# Second person (homonym, differentiator '1')
curp2 = generate_curp(**base_data, differentiator='1')
print(curp2)  # PEGJ900515HJCRRN13

# Third person (homonym, differentiator '2')
curp3 = generate_curp(**base_data, differentiator='2')
print(curp3)  # PEGJ900515HJCRRN21
```

Each differentiator generates a different check digit, making each CURP unique.

### Detect RFC Type

```python
from rfcmx import detect_rfc_type

# Returns 'fisica', 'moral', or 'generico'
tipo = detect_rfc_type('PEGJ900515KL8')
print(tipo)  # 'fisica'

tipo = detect_rfc_type('GBI810615945')
print(tipo)  # 'moral'
```

### Using Class-Based API (Advanced)

For more control, you can use the underlying classes:

```python
import datetime
from rfcmx import RFCGeneratorFisicas, CURPGenerator

# RFC with class
generator = RFCGeneratorFisicas(
    nombres='Juan',
    apellido_paterno='Pérez',
    apellido_materno='García',
    fecha_nacimiento=datetime.date(1990, 5, 15)
)
print(generator.rfc)              # Full RFC
print(generator.generate_letters())  # Just the letters part
print(generator.homoclave)        # Just the homoclave

# CURP with class
generator = CURPGenerator(
    nombre='Juan',
    paterno='Pérez',
    materno='García',
    fecha_nacimiento=datetime.date(1990, 5, 15),
    sexo='H',
    estado='Jalisco'
)
print(generator.curp)                # Full CURP
print(generator.generate_letters())  # Just the letters part
print(generator.generate_date())     # Just the date part
```

## Real-World Examples

### Validate User Input

```python
from rfcmx import is_valid_rfc, is_valid_curp

def validate_user_rfc(rfc_input):
    if not rfc_input:
        return "RFC is required"

    if not is_valid_rfc(rfc_input):
        return "Invalid RFC format"

    return "RFC is valid"

# Use in your application
result = validate_user_rfc('PEGJ900515KL8')
print(result)  # "RFC is valid"
```

### Generate for Database

```python
from rfcmx import generate_curp
import datetime

def create_user_curp(user_data):
    """Generate CURP from user registration data"""
    return generate_curp(
        nombre=user_data['first_name'],
        apellido_paterno=user_data['last_name_paternal'],
        apellido_materno=user_data['last_name_maternal'],
        fecha_nacimiento=user_data['birth_date'],
        sexo='H' if user_data['gender'] == 'male' else 'M',
        estado=user_data['birth_state']
    )

# Example usage
user = {
    'first_name': 'María',
    'last_name_paternal': 'Ramírez',
    'last_name_maternal': 'Sánchez',
    'birth_date': '1995-03-20',
    'gender': 'female',
    'birth_state': 'Jalisco'
}

curp = create_user_curp(user)
print(curp)
```

## Supported Mexican States

All 32 Mexican states are supported with their official codes:

```
AS - Aguascalientes    BC - Baja California
BS - Baja California Sur    CC - Campeche
CL - Coahuila    CM - Colima
CS - Chiapas    CH - Chihuahua
DF - Ciudad de México    DG - Durango
GT - Guanajuato    GR - Guerrero
HG - Hidalgo    JC - Jalisco
MC - Estado de México    MN - Michoacán
MS - Morelos    NT - Nayarit
NL - Nuevo León    OC - Oaxaca
PL - Puebla    QT - Querétaro
QR - Quintana Roo    SP - San Luis Potosí
SL - Sinaloa    SR - Sonora
TC - Tabasco    TS - Tamaulipas
TL - Tlaxcala    VZ - Veracruz
YN - Yucatán    ZS - Zacatecas
NE - Nacido en el Extranjero (Born Abroad)
```

## Official Specifications

This library implements the complete official specifications:

### RFC (SAT - Servicio de Administración Tributaria)
- Letter generation rules
- Number conversion (Arabic 0-20, Roman I-XX)
- Special character handling
- Ñ → X substitution
- Excluded words list (S.A., S. DE R.L., etc.)
- Cacophonic word replacement
- Consonant compound handling (CH→C, LL→L)
- Homoclave calculation

### CURP (RENAPO - Registro Nacional de Población)
- 4-letter code generation
- María/José name handling
- 70+ inconvenient words list (Anexo 2)
- Consonant extraction
- Homonymy differentiator (position 17)
- Check digit algorithm (position 18)

See [CURP_ESPECIFICACIONES_OFICIALES.md](CURP_ESPECIFICACIONES_OFICIALES.md) for complete specifications.

## Testing

All functionality is thoroughly tested:

```bash
# Run tests
PYTHONPATH=src python -m unittest discover -s tests

# Expected output
Ran 49 tests in 0.019s
OK
```

## API Reference

### Quick Functions

**RFC:**
- `generate_rfc_persona_fisica(nombre, apellido_paterno, apellido_materno, fecha_nacimiento)` → str
- `generate_rfc_persona_moral(razon_social, fecha_constitucion)` → str
- `validate_rfc(rfc, check_checksum=True)` → bool
- `detect_rfc_type(rfc)` → str | None
- `is_valid_rfc(rfc)` → bool

**CURP:**
- `generate_curp(nombre, apellido_paterno, apellido_materno, fecha_nacimiento, sexo, estado, differentiator=None)` → str
- `validate_curp(curp, check_digit=True)` → bool
- `get_curp_info(curp)` → dict | None
- `is_valid_curp(curp)` → bool

### Classes (Advanced Usage)

**RFC:**
- `RFCValidator(rfc)` - Validate and analyze RFC codes
- `RFCGeneratorFisicas(nombres, apellido_paterno, apellido_materno, fecha_nacimiento)` - Generate RFC for individuals
- `RFCGeneratorMorales(razon_social, fecha)` - Generate RFC for companies

**CURP:**
- `CURPValidator(curp)` - Validate and analyze CURP codes
- `CURPGenerator(nombre, paterno, materno, fecha_nacimiento, sexo, estado)` - Generate CURP

## License

BSD License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Authors

- Original author: [joyinsky](https://github.com/joyinsky)
- Complete specifications implementation: 2025

## Links

- [Official SAT RFC Specifications](https://www.sat.gob.mx/)
- [Official RENAPO CURP Specifications](https://www.gob.mx/curp/)
- [GitHub Repository](https://github.com/joyinsky/python-rfcmx)

---

Made with ❤️ for the Mexican developer community
