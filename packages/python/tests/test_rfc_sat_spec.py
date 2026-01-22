"""
RFC SAT Specification Tests

Tests based on official SAT algorithm specification (IFAI 0610100135506)
Reference: https://www.mariovaldez.net/files/IFAI%200610100135506%20065%20Algoritmo%20para%20generar%20el%20RFC%20con%20homoclave%20para%20personas%20fisicas%20y%20morales.pdf
"""
import datetime
import json
from pathlib import Path

import pytest

from catalogmx.validators.rfc import RFCGenerator, RFCValidator


# Load SAT specification vectors
VECTORS_PATH = (
    Path(__file__).resolve().parents[2]
    / "shared-data"
    / "tests"
    / "rfc_sat_spec_vectors.json"
)

with open(VECTORS_PATH, encoding="utf-8") as f:
    SAT_SPEC = json.load(f)


def extract_rfc_base(rfc: str) -> str:
    """Extract RFC base (initials + date) from full RFC"""
    if len(rfc) == 12:
        # Persona Moral: 3 letters + 6 date + 3 homoclave+checksum
        return rfc[:9]
    else:
        # Persona Física: 4 letters + 6 date + 3 homoclave+checksum
        return rfc[:10]


def parse_date(date_str: str) -> datetime.date:
    """Parse ISO date string to datetime.date"""
    return datetime.date.fromisoformat(date_str)


# ============================================================================
# PERSONAS MORALES TESTS
# ============================================================================


class TestSatSpecPersonasMorales:
    """Tests for Persona Moral RFC generation based on SAT specification"""

    @pytest.mark.parametrize(
        "vector", SAT_SPEC["personas_morales"]["regla_1_tres_o_mas_palabras"]
    )
    def test_regla_1_tres_o_mas_palabras(self, vector: dict) -> None:
        """Regla 1: Se toman las primeras letras de las tres primeras palabras"""
        rfc = RFCGenerator.generate_moral(
            razon_social=vector["razon_social"],
            fecha=parse_date(vector["fecha"]),
        )
        rfc_base = extract_rfc_base(rfc)
        assert rfc_base == vector["rfc_base"], f"Expected {vector['rfc_base']}, got {rfc_base}"

    @pytest.mark.parametrize(
        "vector", SAT_SPEC["personas_morales"]["regla_2_fecha_constitucion"]
    )
    def test_regla_2_fecha_constitucion(self, vector: dict) -> None:
        """Regla 2: Fecha de constitución en formato AAMMDD"""
        rfc = RFCGenerator.generate_moral(
            razon_social=vector["razon_social"],
            fecha=parse_date(vector["fecha"]),
        )
        rfc_base = extract_rfc_base(rfc)
        assert rfc_base == vector["rfc_base"]

    @pytest.mark.parametrize(
        "vector", SAT_SPEC["personas_morales"]["regla_3_letras_compuestas"]
    )
    def test_regla_3_letras_compuestas(self, vector: dict) -> None:
        """Regla 3: CH -> C, LL -> L"""
        rfc = RFCGenerator.generate_moral(
            razon_social=vector["razon_social"],
            fecha=parse_date(vector["fecha"]),
        )
        rfc_base = extract_rfc_base(rfc)
        assert rfc_base == vector["rfc_base"]

    @pytest.mark.parametrize(
        "vector", SAT_SPEC["personas_morales"]["regla_4_iniciales_como_palabras"]
    )
    def test_regla_4_iniciales_como_palabras(self, vector: dict) -> None:
        """Regla 4: Las iniciales se consideran palabras individuales"""
        rfc = RFCGenerator.generate_moral(
            razon_social=vector["razon_social"],
            fecha=parse_date(vector["fecha"]),
        )
        rfc_base = extract_rfc_base(rfc)
        assert rfc_base == vector["rfc_base"]

    @pytest.mark.parametrize(
        "vector", SAT_SPEC["personas_morales"]["regla_5_abreviaturas_sociedad"]
    )
    def test_regla_5_abreviaturas_sociedad(self, vector: dict) -> None:
        """Regla 5: No se toman en consideración abreviaturas de tipo de sociedad"""
        rfc = RFCGenerator.generate_moral(
            razon_social=vector["razon_social"],
            fecha=parse_date(vector["fecha"]),
        )
        rfc_base = extract_rfc_base(rfc)
        assert rfc_base == vector["rfc_base"]

    @pytest.mark.parametrize(
        "vector", SAT_SPEC["personas_morales"]["regla_6_dos_palabras"]
    )
    def test_regla_6_dos_palabras(self, vector: dict) -> None:
        """Regla 6: Dos palabras - inicial primera + dos primeras de segunda"""
        rfc = RFCGenerator.generate_moral(
            razon_social=vector["razon_social"],
            fecha=parse_date(vector["fecha"]),
        )
        rfc_base = extract_rfc_base(rfc)
        assert rfc_base == vector["rfc_base"]

    @pytest.mark.parametrize(
        "vector", SAT_SPEC["personas_morales"]["regla_7_una_sola_palabra"]
    )
    def test_regla_7_una_sola_palabra(self, vector: dict) -> None:
        """Regla 7: Una sola palabra - tres primeras letras"""
        rfc = RFCGenerator.generate_moral(
            razon_social=vector["razon_social"],
            fecha=parse_date(vector["fecha"]),
        )
        rfc_base = extract_rfc_base(rfc)
        assert rfc_base == vector["rfc_base"]

    @pytest.mark.parametrize(
        "vector", SAT_SPEC["personas_morales"]["regla_8_menos_de_tres_letras"]
    )
    def test_regla_8_menos_de_tres_letras(self, vector: dict) -> None:
        """Regla 8: Una palabra con menos de 3 letras - se suple con X"""
        rfc = RFCGenerator.generate_moral(
            razon_social=vector["razon_social"],
            fecha=parse_date(vector["fecha"]),
        )
        rfc_base = extract_rfc_base(rfc)
        assert rfc_base == vector["rfc_base"]

    @pytest.mark.parametrize(
        "vector", SAT_SPEC["personas_morales"]["regla_9_articulos_preposiciones"]
    )
    def test_regla_9_articulos_preposiciones(self, vector: dict) -> None:
        """Regla 9: No se toman artículos, preposiciones y conjunciones"""
        rfc = RFCGenerator.generate_moral(
            razon_social=vector["razon_social"],
            fecha=parse_date(vector["fecha"]),
        )
        rfc_base = extract_rfc_base(rfc)
        assert rfc_base == vector["rfc_base"]

    @pytest.mark.parametrize(
        "vector", SAT_SPEC["personas_morales"]["regla_10_numeros"]
    )
    def test_regla_10_numeros(self, vector: dict) -> None:
        """Regla 10: Números arábigos y romanos se convierten a texto"""
        rfc = RFCGenerator.generate_moral(
            razon_social=vector["razon_social"],
            fecha=parse_date(vector["fecha"]),
        )
        rfc_base = extract_rfc_base(rfc)
        assert rfc_base == vector["rfc_base"]

    @pytest.mark.parametrize(
        "vector", SAT_SPEC["personas_morales"]["regla_11_compania_sociedad"]
    )
    def test_regla_11_compania_sociedad(self, vector: dict) -> None:
        """Regla 11: Las palabras Compañía, Cía., Sociedad, Soc. no se incluyen"""
        rfc = RFCGenerator.generate_moral(
            razon_social=vector["razon_social"],
            fecha=parse_date(vector["fecha"]),
        )
        rfc_base = extract_rfc_base(rfc)
        assert rfc_base == vector["rfc_base"]

    @pytest.mark.parametrize(
        "vector", SAT_SPEC["personas_morales"]["regla_12_caracteres_especiales"]
    )
    def test_regla_12_caracteres_especiales(self, vector: dict) -> None:
        """Regla 12: Caracteres especiales se excluyen"""
        rfc = RFCGenerator.generate_moral(
            razon_social=vector["razon_social"],
            fecha=parse_date(vector["fecha"]),
        )
        rfc_base = extract_rfc_base(rfc)
        assert rfc_base == vector["rfc_base"]


# ============================================================================
# PERSONAS FISICAS TESTS
# ============================================================================


class TestSatSpecPersonasFisicas:
    """Tests for Persona Física RFC generation based on SAT specification"""

    @pytest.mark.parametrize(
        "vector", SAT_SPEC["personas_fisicas"]["regla_1_formacion_basica"]
    )
    def test_regla_1_formacion_basica(self, vector: dict) -> None:
        """Regla 1: Primera letra + primera vocal paterno + inicial materno + inicial nombre"""
        rfc = RFCGenerator.generate_fisica(
            nombre=vector["nombre"],
            paterno=vector["apellido_paterno"],
            materno=vector["apellido_materno"],
            fecha=parse_date(vector["fecha"]),
        )
        rfc_base = extract_rfc_base(rfc)
        assert rfc_base == vector["rfc_base"]

    @pytest.mark.parametrize(
        "vector", SAT_SPEC["personas_fisicas"]["regla_2_fecha_nacimiento"]
    )
    def test_regla_2_fecha_nacimiento(self, vector: dict) -> None:
        """Regla 2: Fecha de nacimiento en formato AAMMDD"""
        rfc = RFCGenerator.generate_fisica(
            nombre=vector["nombre"],
            paterno=vector["apellido_paterno"],
            materno=vector["apellido_materno"],
            fecha=parse_date(vector["fecha"]),
        )
        rfc_base = extract_rfc_base(rfc)
        assert rfc_base == vector["rfc_base"]

    @pytest.mark.parametrize(
        "vector", SAT_SPEC["personas_fisicas"]["regla_3_letras_compuestas"]
    )
    def test_regla_3_letras_compuestas(self, vector: dict) -> None:
        """Regla 3: CH -> C, LL -> L"""
        rfc = RFCGenerator.generate_fisica(
            nombre=vector["nombre"],
            paterno=vector["apellido_paterno"],
            materno=vector["apellido_materno"],
            fecha=parse_date(vector["fecha"]),
        )
        rfc_base = extract_rfc_base(rfc)
        assert rfc_base == vector["rfc_base"]

    @pytest.mark.parametrize(
        "vector", SAT_SPEC["personas_fisicas"]["regla_4_apellido_paterno_corto"]
    )
    def test_regla_4_apellido_paterno_corto(self, vector: dict) -> None:
        """Regla 4: Apellido paterno de 1-2 letras - iniciales diferentes"""
        rfc = RFCGenerator.generate_fisica(
            nombre=vector["nombre"],
            paterno=vector["apellido_paterno"],
            materno=vector["apellido_materno"],
            fecha=parse_date(vector["fecha"]),
        )
        rfc_base = extract_rfc_base(rfc)
        assert rfc_base == vector["rfc_base"]

    @pytest.mark.parametrize(
        "vector", SAT_SPEC["personas_fisicas"]["regla_5_apellidos_compuestos"]
    )
    def test_regla_5_apellidos_compuestos(self, vector: dict) -> None:
        """Regla 5: Apellidos compuestos - se toma primera palabra"""
        rfc = RFCGenerator.generate_fisica(
            nombre=vector["nombre"],
            paterno=vector["apellido_paterno"],
            materno=vector["apellido_materno"],
            fecha=parse_date(vector["fecha"]),
        )
        rfc_base = extract_rfc_base(rfc)
        assert rfc_base == vector["rfc_base"]

    @pytest.mark.parametrize(
        "vector", SAT_SPEC["personas_fisicas"]["regla_6_nombres_maria_jose"]
    )
    def test_regla_6_nombres_maria_jose(self, vector: dict) -> None:
        """Regla 6: Si primer nombre es MARIA o JOSE, se usa inicial del segundo"""
        rfc = RFCGenerator.generate_fisica(
            nombre=vector["nombre"],
            paterno=vector["apellido_paterno"],
            materno=vector["apellido_materno"],
            fecha=parse_date(vector["fecha"]),
        )
        rfc_base = extract_rfc_base(rfc)
        assert rfc_base == vector["rfc_base"]

    @pytest.mark.parametrize(
        "vector", SAT_SPEC["personas_fisicas"]["regla_7_un_solo_apellido"]
    )
    def test_regla_7_un_solo_apellido(self, vector: dict) -> None:
        """Regla 7: Un solo apellido - dos primeras apellido + dos primeras nombre"""
        rfc = RFCGenerator.generate_fisica(
            nombre=vector["nombre"],
            paterno=vector["apellido_paterno"],
            materno=vector["apellido_materno"],
            fecha=parse_date(vector["fecha"]),
        )
        rfc_base = extract_rfc_base(rfc)
        assert rfc_base == vector["rfc_base"]

    @pytest.mark.parametrize(
        "vector", SAT_SPEC["personas_fisicas"]["regla_8_articulos_preposiciones"]
    )
    def test_regla_8_articulos_preposiciones(self, vector: dict) -> None:
        """Regla 8: No se toman artículos, preposiciones y conjunciones"""
        rfc = RFCGenerator.generate_fisica(
            nombre=vector["nombre"],
            paterno=vector["apellido_paterno"],
            materno=vector["apellido_materno"],
            fecha=parse_date(vector["fecha"]),
        )
        rfc_base = extract_rfc_base(rfc)
        assert rfc_base == vector["rfc_base"]

    @pytest.mark.parametrize(
        "vector", SAT_SPEC["personas_fisicas"]["regla_10_caracteres_especiales"]
    )
    def test_regla_10_caracteres_especiales(self, vector: dict) -> None:
        """Regla 10: Caracteres especiales se excluyen"""
        rfc = RFCGenerator.generate_fisica(
            nombre=vector["nombre"],
            paterno=vector["apellido_paterno"],
            materno=vector["apellido_materno"],
            fecha=parse_date(vector["fecha"]),
        )
        rfc_base = extract_rfc_base(rfc)
        assert rfc_base == vector["rfc_base"]


# ============================================================================
# COMPLETE EXAMPLE WITH HOMOCLAVE
# ============================================================================


class TestSatSpecCompleteExample:
    """Test the complete SAT example with homoclave and checksum"""

    def test_emma_gomez_diaz_complete_rfc(self) -> None:
        """Emma Gómez Díaz generates correct RFC with homoclave and checksum"""
        example = SAT_SPEC["ejemplo_completo_con_homoclave"]
        rfc = RFCGenerator.generate_fisica(
            nombre=example["nombre"],
            paterno=example["apellido_paterno"],
            materno=example["apellido_materno"],
            fecha=parse_date(example["fecha"]),
        )

        # Test complete RFC
        assert rfc == example["rfc_completo"]

        # Test RFC base
        assert rfc[:10] == example["rfc_base"]

        # Test homoclave
        assert rfc[10:12] == example["homoclave"]

        # Test checksum
        assert rfc[12:] == example["digito_verificador"]

    def test_rfc_validates_correctly(self) -> None:
        """Generated RFC validates correctly"""
        example = SAT_SPEC["ejemplo_completo_con_homoclave"]
        validator = RFCValidator(example["rfc_completo"])
        assert validator.is_valid() is True

    def test_rfc_detected_as_persona_fisica(self) -> None:
        """RFC is detected as persona física"""
        example = SAT_SPEC["ejemplo_completo_con_homoclave"]
        validator = RFCValidator(example["rfc_completo"])
        assert validator.is_fisica() is True


# ============================================================================
# CHECKSUM VALIDATION
# ============================================================================


class TestSatSpecChecksumValidation:
    """Test RFC checksum validation"""

    def test_checksum_validated_independently(self) -> None:
        """RFC checksum can be validated independently"""
        # From the SAT document, the checksum calculation for GODE561231GR is 8
        validator = RFCValidator("GODE561231GR8")
        assert validator.validate_checksum() is True

        # Wrong checksum should fail
        wrong_validator = RFCValidator("GODE561231GR9")
        assert wrong_validator.validate_checksum() is False

    def test_generic_rfcs_validate(self) -> None:
        """Generic RFCs validate correctly"""
        assert RFCValidator("XAXX010101000").is_valid() is True
        assert RFCValidator("XEXX010101000").is_valid() is True


# ============================================================================
# PALABRAS INCONVENIENTES
# ============================================================================


class TestSatSpecPalabrasInconvenientes:
    """Test palabras inconvenientes (cacophonic words)"""

    @pytest.mark.parametrize("palabra", SAT_SPEC["palabras_inconvenientes"])
    def test_palabras_inconvenientes_end_with_x(self, palabra: dict) -> None:
        """Palabras inconvenientes should end with X when corrected"""
        assert palabra["corregido"].endswith("X")
        assert palabra["original"][:3] == palabra["corregido"][:3]
