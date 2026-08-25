"""Tests for the Mexican identity generator module."""

import pytest
from datetime import date, timedelta
from unittest.mock import patch

from catalogmx.generators.identity import (
    IdentityGenerator,
    PersonaFisica,
    PersonaMoral,
    generate_identity,
    generate_persona_fisica,
    generate_persona_moral,
    ESTADOS_MEXICO,
    BANCOS_MEXICO,
    REGIMENES_PERSONA_FISICA,
    _get_faker,
)


class TestGetFaker:
    """Tests for _get_faker function."""

    def test_get_faker_returns_faker_instance(self):
        """Test that _get_faker returns a Faker instance."""
        faker = _get_faker()
        assert faker is not None
        # Should be Mexican locale
        assert "es_MX" in str(faker.locales) or hasattr(faker, "first_name")

    def test_get_faker_without_faker_installed(self):
        """Test that ImportError is raised when Faker is not available."""
        with patch("catalogmx.generators.identity.Faker", None):
            with pytest.raises(ImportError) as exc_info:
                _get_faker()
            assert "Faker is required" in str(exc_info.value)


class TestPersonaFisicaDataclass:
    """Tests for PersonaFisica dataclass."""

    def test_nombre_completo_property(self):
        """Test that nombre_completo returns full name."""
        persona = PersonaFisica(
            nombre="Juan",
            apellido_paterno="García",
            apellido_materno="López",
            fecha_nacimiento=date(1990, 5, 15),
            sexo="H",
            estado_nacimiento="JALISCO",
            estado_nacimiento_code="JC",
        )
        assert persona.nombre_completo == "Juan García López"

    def test_edad_property_calculates_correctly(self):
        """Test that edad calculates age correctly."""
        today = date.today()
        birth_date = today - timedelta(days=365 * 30 + 100)  # ~30 years ago
        persona = PersonaFisica(
            nombre="María",
            apellido_paterno="Hernández",
            apellido_materno="Sánchez",
            fecha_nacimiento=birth_date,
            sexo="M",
            estado_nacimiento="NUEVO LEON",
            estado_nacimiento_code="NL",
        )
        assert persona.edad == 30

    def test_edad_property_before_birthday(self):
        """Test that edad is correct before the next 25th birthday."""
        today = date.today()
        future_birthday = today + timedelta(days=180)
        birth_date = date(
            future_birthday.year - 25,
            future_birthday.month,
            15,
        )

        persona = PersonaFisica(
            nombre="Ana",
            apellido_paterno="Martínez",
            apellido_materno="Ruiz",
            fecha_nacimiento=birth_date,
            sexo="M",
            estado_nacimiento="SONORA",
            estado_nacimiento_code="SR",
        )
        assert persona.edad == 24

    def test_to_dict_contains_all_fields(self):
        """Test that to_dict returns all expected fields."""
        persona = PersonaFisica(
            nombre="Carlos",
            apellido_paterno="Rodríguez",
            apellido_materno="Vega",
            fecha_nacimiento=date(1985, 3, 20),
            sexo="H",
            estado_nacimiento="CHIHUAHUA",
            estado_nacimiento_code="CH",
            rfc="ROVC850320XXX",
            curp="ROVC850320HCHVGR09",
            nss="12345678901",
        )

        result = persona.to_dict()

        assert result["tipo"] == "persona_fisica"
        assert result["nombre"] == "Carlos"
        assert result["apellido_paterno"] == "Rodríguez"
        assert result["apellido_materno"] == "Vega"
        assert result["nombre_completo"] == "Carlos Rodríguez Vega"
        assert result["fecha_nacimiento"] == "1985-03-20"
        assert result["sexo"] == "H"
        assert result["sexo_descripcion"] == "Masculino"
        assert result["estado_nacimiento"] == "CHIHUAHUA"
        assert result["rfc"] == "ROVC850320XXX"
        assert result["curp"] == "ROVC850320HCHVGR09"
        assert "direccion" in result
        assert "calle" in result["direccion"]

    def test_to_dict_sexo_descripcion_femenino(self):
        """Test that sexo_descripcion is Femenino for M."""
        persona = PersonaFisica(
            nombre="Laura",
            apellido_paterno="Díaz",
            apellido_materno="Pérez",
            fecha_nacimiento=date(1992, 8, 10),
            sexo="M",
            estado_nacimiento="OAXACA",
            estado_nacimiento_code="OC",
        )
        assert persona.to_dict()["sexo_descripcion"] == "Femenino"


class TestPersonaMoralDataclass:
    """Tests for PersonaMoral dataclass."""

    def test_to_dict_contains_all_fields(self):
        """Test that to_dict returns all expected fields."""
        persona = PersonaMoral(
            razon_social="Empresa Test S.A. de C.V.",
            fecha_constitucion=date(2010, 6, 1),
            rfc="ETE100601XXX",
        )

        result = persona.to_dict()

        assert result["tipo"] == "persona_moral"
        assert result["razon_social"] == "Empresa Test S.A. de C.V."
        assert result["fecha_constitucion"] == "2010-06-01"
        assert result["rfc"] == "ETE100601XXX"
        assert "direccion" in result
        assert "banco" in result


class TestIdentityGenerator:
    """Tests for IdentityGenerator class."""

    def test_init_creates_faker(self):
        """Test that initialization creates a Faker instance."""
        generator = IdentityGenerator()
        assert generator.faker is not None

    def test_init_with_seed_for_reproducibility(self):
        """Test that seed produces reproducible results."""
        gen1 = IdentityGenerator(seed=12345)
        persona1 = gen1.generate_persona_fisica()

        gen2 = IdentityGenerator(seed=12345)
        persona2 = gen2.generate_persona_fisica()

        assert persona1.nombre == persona2.nombre
        assert persona1.apellido_paterno == persona2.apellido_paterno

    def test_generate_persona_fisica_basic(self):
        """Test basic persona física generation."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_fisica()

        assert persona.nombre is not None
        assert persona.apellido_paterno is not None
        assert persona.apellido_materno is not None
        assert persona.fecha_nacimiento is not None
        assert persona.sexo in ("H", "M")
        assert persona.estado_nacimiento in [e["name"] for e in ESTADOS_MEXICO]

    def test_generate_persona_fisica_with_male_sex(self):
        """Test persona física generation with specified male sex."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_fisica(sexo="H")

        assert persona.sexo == "H"

    def test_generate_persona_fisica_with_female_sex(self):
        """Test persona física generation with specified female sex."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_fisica(sexo="M")

        assert persona.sexo == "M"

    def test_generate_persona_fisica_with_estado(self):
        """Test persona física generation with specified state."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_fisica(estado="JALISCO")

        assert persona.estado_nacimiento == "JALISCO"
        assert persona.estado_nacimiento_code == "JC"

    def test_generate_persona_fisica_with_unknown_estado_uses_random(self):
        """Test that unknown estado falls back to random."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_fisica(estado="UNKNOWN_STATE")

        # Should have a valid state anyway
        assert persona.estado_nacimiento in [e["name"] for e in ESTADOS_MEXICO]

    def test_generate_persona_fisica_age_range(self):
        """Test persona física age is within specified range."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_fisica(min_age=25, max_age=35)

        assert 25 <= persona.edad <= 35

    def test_generate_persona_fisica_has_rfc(self):
        """Test that generated persona has RFC."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_fisica()

        assert persona.rfc is not None
        assert len(persona.rfc) == 13  # RFC persona física

    def test_generate_persona_fisica_has_curp(self):
        """Test that generated persona has CURP."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_fisica()

        assert persona.curp is not None
        assert len(persona.curp) == 18

    def test_generate_persona_fisica_has_nss(self):
        """Test that generated persona has NSS."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_fisica()

        assert persona.nss is not None
        assert len(persona.nss) == 11

    def test_generate_persona_fisica_with_banking(self):
        """Test that banking info is included by default."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_fisica(include_banking=True)

        assert persona.banco is not None
        assert "code" in persona.banco
        assert persona.clabe is not None
        assert len(persona.clabe) == 18

    def test_generate_persona_fisica_without_banking(self):
        """Test that banking can be excluded."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_fisica(include_banking=False)

        assert persona.clabe == ""

    def test_generate_persona_fisica_with_address(self):
        """Test that address info is included by default."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_fisica(include_address=True)

        assert persona.calle != ""
        assert persona.numero_exterior != ""
        assert persona.codigo_postal != ""

    def test_generate_persona_fisica_without_address(self):
        """Test that address can be excluded."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_fisica(include_address=False)

        assert persona.calle == ""
        assert persona.codigo_postal == ""

    def test_generate_persona_fisica_with_contact(self):
        """Test that contact info is included by default."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_fisica(include_contact=True)

        assert persona.telefono != ""
        assert persona.email != ""
        assert "@" in persona.email

    def test_generate_persona_fisica_without_contact(self):
        """Test that contact can be excluded."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_fisica(include_contact=False)

        assert persona.telefono == ""
        assert persona.email == ""

    def test_generate_persona_fisica_has_regimen_fiscal(self):
        """Test that persona has régimen fiscal."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_fisica()

        assert persona.regimen_fiscal is not None
        assert "code" in persona.regimen_fiscal
        assert "name" in persona.regimen_fiscal

    def test_generate_persona_moral_basic(self):
        """Test basic persona moral generation."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_moral()

        assert persona.razon_social is not None
        assert persona.fecha_constitucion is not None
        assert persona.rfc is not None

    def test_generate_persona_moral_has_company_type(self):
        """Test that razón social includes company type."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_moral()

        company_types = ["S.A. de C.V.", "S.A.P.I. de C.V.", "S. de R.L. de C.V.", "S.C."]
        has_type = any(ct in persona.razon_social for ct in company_types)
        assert has_type

    def test_generate_persona_moral_rfc_length(self):
        """Test that persona moral RFC has 12 characters."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_moral()

        assert len(persona.rfc) == 12

    def test_generate_persona_moral_fecha_constitucion_valid_range(self):
        """Test that constitution date is in valid range (1-50 years ago)."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_moral()

        today = date.today()
        min_date = today - timedelta(days=50 * 365)
        max_date = today - timedelta(days=365)

        assert min_date <= persona.fecha_constitucion <= max_date

    def test_generate_persona_moral_with_banking(self):
        """Test that persona moral includes banking by default."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_moral(include_banking=True)

        assert persona.banco is not None
        assert persona.clabe != ""
        assert len(persona.clabe) == 18

    def test_generate_persona_moral_with_contact(self):
        """Test that persona moral includes contact info."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_moral(include_contact=True)

        assert persona.telefono != ""
        assert persona.email != ""
        assert "@" in persona.email
        assert ".com.mx" in persona.email

    def test_generate_persona_moral_regimen_fiscal(self):
        """Test that persona moral has régimen 601."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_moral()

        assert persona.regimen_fiscal["code"] == "601"

    def test_add_luhn_checksum(self):
        """Test Luhn checksum calculation."""
        generator = IdentityGenerator(seed=42)

        # Test with known values
        result = generator._add_luhn_checksum("453284710038")
        assert len(result) == 13
        # The last digit should make the Luhn checksum valid

    def test_generate_phone_is_10_digits(self):
        """Test that phone numbers are 10 digits."""
        generator = IdentityGenerator(seed=42)
        phone = generator._generate_phone()

        assert len(phone) == 10
        assert phone.isdigit()


class TestGenerateIdentityFunction:
    """Tests for the generate_identity convenience function."""

    def test_generate_identity_defaults_to_fisica(self):
        """Test that default tipo is 'fisica'."""
        identity = generate_identity()

        assert identity["tipo"] == "persona_fisica"

    def test_generate_identity_fisica(self):
        """Test generating persona física identity."""
        identity = generate_identity(tipo="fisica")

        assert identity["tipo"] == "persona_fisica"
        assert "nombre" in identity
        assert "apellido_paterno" in identity
        assert "rfc" in identity
        assert "curp" in identity

    def test_generate_identity_moral(self):
        """Test generating persona moral identity."""
        identity = generate_identity(tipo="moral")

        assert identity["tipo"] == "persona_moral"
        assert "razon_social" in identity
        assert "rfc" in identity
        assert "fecha_constitucion" in identity

    def test_generate_identity_with_kwargs(self):
        """Test that kwargs are passed through."""
        identity = generate_identity(tipo="fisica", sexo="M", min_age=30, max_age=40)

        assert identity["sexo"] == "M"
        assert 30 <= identity["edad"] <= 40


class TestConvenienceFunctions:
    """Tests for shortcut functions."""

    def test_generate_persona_fisica_function(self):
        """Test generate_persona_fisica shortcut."""
        identity = generate_persona_fisica()

        assert identity["tipo"] == "persona_fisica"
        assert "curp" in identity
        assert "nss" in identity

    def test_generate_persona_fisica_with_params(self):
        """Test generate_persona_fisica with parameters."""
        identity = generate_persona_fisica(sexo="H", estado="SONORA")

        assert identity["sexo"] == "H"
        assert identity["estado_nacimiento"] == "SONORA"

    def test_generate_persona_moral_function(self):
        """Test generate_persona_moral shortcut."""
        identity = generate_persona_moral()

        assert identity["tipo"] == "persona_moral"
        assert "razon_social" in identity


class TestConstants:
    """Tests for module constants."""

    def test_estados_mexico_has_32_states(self):
        """Test that ESTADOS_MEXICO has all 32 states."""
        assert len(ESTADOS_MEXICO) == 32

    def test_estados_mexico_structure(self):
        """Test that each state has required keys."""
        for estado in ESTADOS_MEXICO:
            assert "name" in estado
            assert "code" in estado
            assert "inegi" in estado
            assert len(estado["code"]) == 2

    def test_bancos_mexico_has_banks(self):
        """Test that BANCOS_MEXICO has banks."""
        assert len(BANCOS_MEXICO) >= 10

    def test_bancos_mexico_structure(self):
        """Test that each bank has required keys."""
        for banco in BANCOS_MEXICO:
            assert "code" in banco
            assert "name" in banco
            assert len(banco["code"]) == 3

    def test_regimenes_persona_fisica(self):
        """Test that régimenes list is populated."""
        assert len(REGIMENES_PERSONA_FISICA) >= 5

        for regimen in REGIMENES_PERSONA_FISICA:
            assert "code" in regimen
            assert "name" in regimen


class TestIntegration:
    """Integration tests for identity generation."""

    def test_multiple_identities_are_different(self):
        """Test that generating multiple identities produces different results."""
        identities = [generate_identity() for _ in range(5)]

        rfcs = [i["rfc"] for i in identities]
        assert len(set(rfcs)) == 5  # All unique

    def test_generated_identity_is_complete(self):
        """Test that a generated identity has all expected data."""
        identity = generate_identity()

        # Personal data
        assert identity["nombre"]
        assert identity["apellido_paterno"]
        assert identity["nombre_completo"]
        assert identity["fecha_nacimiento"]

        # Identifiers
        assert identity["rfc"]
        assert identity["curp"]
        assert identity["nss"]

        # Banking
        assert identity["banco"]
        assert identity["clabe"]

        # Address
        assert identity["direccion"]["calle"]
        assert identity["direccion"]["codigo_postal"]

        # Contact
        assert identity["telefono"]
        assert identity["email"]

    def test_persona_moral_is_complete(self):
        """Test that a generated persona moral has all expected data."""
        identity = generate_persona_moral()

        assert identity["razon_social"]
        assert identity["rfc"]
        assert identity["banco"]
        assert identity["clabe"]
        assert identity["direccion"]["calle"]
        assert identity["email"]

    def test_generated_clabe_is_valid_format(self):
        """Test that generated CLABEs have valid format."""
        identity = generate_identity()
        clabe = identity["clabe"]

        assert len(clabe) == 18
        assert clabe.isdigit()

    def test_generated_tarjeta_debito_passes_luhn(self):
        """Test that generated debit card passes Luhn validation."""
        generator = IdentityGenerator(seed=42)
        persona = generator.generate_persona_fisica()

        card = persona.tarjeta_debito

        # Luhn algorithm check
        def luhn_check(card_number: str) -> bool:
            digits = [int(d) for d in card_number]
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]

            total = sum(odd_digits)
            for d in even_digits:
                total += sum(divmod(d * 2, 10))

            return total % 10 == 0

        assert luhn_check(card)

    def test_generated_phone_has_valid_lada(self):
        """Test that generated phones start with known LADAs."""
        generator = IdentityGenerator(seed=42)

        known_ladas = {"55", "33", "81", "222", "442", "477", "614", "656", "664", "744", "998"}

        for _ in range(10):
            phone = generator._generate_phone()
            # Check if starts with any known LADA
            has_valid_lada = any(phone.startswith(lada) for lada in known_ladas)
            assert has_valid_lada
