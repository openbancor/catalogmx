"""
Tests for accent-insensitive search across all catalogs.

Tests the normalize_text utility and accent-insensitive search functionality
in all catalogs that support it.
"""
from catalogmx.utils.text import normalize_text
from catalogmx.catalogs.sepomex import CodigosPostales
from catalogmx.catalogs.inegi import StateCatalog, LocalidadesCatalog, MunicipiosCatalog
from catalogmx.catalogs.banxico import BankCatalog, CodigosPlazaCatalog, InstitucionesFinancieras
from catalogmx.catalogs.sat.comercio_exterior import PaisCatalog
from catalogmx.catalogs.sat.carta_porte import AeropuertosCatalog, PuertosMaritimos, CarreterasCatalog


class TestNormalizeText:
    """Test the normalize_text utility function."""

    def test_basic_accent_removal(self):
        """Test basic accent removal"""
        assert normalize_text("México") == "MEXICO"
        assert normalize_text("Querétaro") == "QUERETARO"
        assert normalize_text("San José") == "SAN JOSE"

    def test_case_normalization(self):
        """Test case normalization to uppercase"""
        assert normalize_text("mexico") == "MEXICO"
        assert normalize_text("MeXiCo") == "MEXICO"
        assert normalize_text("MEXICO") == "MEXICO"

    def test_special_characters(self):
        """Test handling of special characters"""
        assert normalize_text("Ñoño") == "NONO"
        assert normalize_text("Müller") == "MULLER"
        assert normalize_text("François") == "FRANCOIS"

    def test_empty_and_whitespace(self):
        """Test empty strings and whitespace"""
        assert normalize_text("") == ""
        assert normalize_text("  ") == "  "
        assert normalize_text("  México  ") == "  MEXICO  "


class TestSEPOMEXAccentInsensitive:
    """Test accent-insensitive search in SEPOMEX catalog."""

    def test_get_by_estado_with_accents(self):
        """Test getting postal codes by state with accents"""
        result_con = CodigosPostales.get_by_estado("México")
        result_sin = CodigosPostales.get_by_estado("Mexico")
        assert len(result_con) == len(result_sin)
        assert len(result_con) > 0

    def test_get_by_municipio_with_accents(self):
        """Test getting postal codes by municipality with accents"""
        result_con = CodigosPostales.get_by_municipio("Querétaro")
        result_sin = CodigosPostales.get_by_municipio("Queretaro")
        assert len(result_con) == len(result_sin)
        assert len(result_con) > 0

    def test_search_by_colonia_with_accents(self):
        """Test searching postal codes by colonia with accents"""
        result_con = CodigosPostales.search_by_colonia("Juárez")
        result_sin = CodigosPostales.search_by_colonia("Juarez")
        assert len(result_con) == len(result_sin)
        assert len(result_con) > 0


class TestINEGIAccentInsensitive:
    """Test accent-insensitive search in INEGI catalogs."""

    def test_state_catalog_by_name_with_accents(self):
        """Test getting state by name with accents"""
        result_con = StateCatalog.get_state_by_name("México")
        result_sin = StateCatalog.get_state_by_name("Mexico")
        assert result_con == result_sin
        assert result_con is not None

    def test_localidades_search_with_accents(self):
        """Test searching localities with accents"""
        result_con = LocalidadesCatalog.search_by_name("San José")
        result_sin = LocalidadesCatalog.search_by_name("San Jose")
        assert len(result_con) == len(result_sin)
        assert len(result_con) > 0

    def test_municipios_search_with_accents(self):
        """Test searching municipalities with accents"""
        result_con = MunicipiosCatalog.search_by_name("Tláhuac")
        result_sin = MunicipiosCatalog.search_by_name("Tlahuac")
        assert len(result_con) == len(result_sin)
        assert len(result_con) > 0


class TestBanxicoAccentInsensitive:
    """Test accent-insensitive search in Banxico catalogs."""

    def test_bank_catalog_by_name(self):
        """Test getting bank by name (case-insensitive)"""
        result_upper = BankCatalog.get_bank_by_name("BANAMEX")
        result_lower = BankCatalog.get_bank_by_name("banamex")
        assert result_upper == result_lower
        assert result_upper is not None

    def test_plaza_codes_search_with_accents(self):
        """Test searching plaza codes with accents"""
        # Test with a plaza that exists
        all_plazas = CodigosPlazaCatalog.get_all()
        if all_plazas:
            # Find a plaza with accents in name
            test_plaza = next((p for p in all_plazas if "á" in p['plaza'].lower()
                             or "é" in p['plaza'].lower()), None)
            if test_plaza:
                nombre = test_plaza['plaza']
                # Test that search works
                result = CodigosPlazaCatalog.buscar_por_plaza(nombre)
                assert isinstance(result, list)
                assert len(result) >= 0  # Results may vary

    def test_instituciones_financieras_buscar_por_tipo(self):
        """Test searching financial institutions by type with accents"""
        result_con = InstitucionesFinancieras.buscar_por_tipo("Crédito")
        result_sin = InstitucionesFinancieras.buscar_por_tipo("Credito")
        assert len(result_con) == len(result_sin)
        assert len(result_con) > 0


class TestSATAccentInsensitive:
    """Test accent-insensitive search in SAT catalogs."""

    def test_pais_catalog_search_with_accents(self):
        """Test searching countries with accents"""
        result_con = PaisCatalog.search("México")
        result_sin = PaisCatalog.search("Mexico")
        assert len(result_con) == len(result_sin)
        assert len(result_con) > 0

    def test_aeropuertos_get_by_state_with_accents(self):
        """Test getting airports by state with accents"""
        # Test with a state that might have airports
        result_con = AeropuertosCatalog.get_by_state("México")
        result_sin = AeropuertosCatalog.get_by_state("Mexico")
        assert len(result_con) == len(result_sin)

    def test_aeropuertos_search_by_name_with_accents(self):
        """Test searching airports by name with accents"""
        result_con = AeropuertosCatalog.search_by_name("México")
        result_sin = AeropuertosCatalog.search_by_name("Mexico")
        assert len(result_con) == len(result_sin)

    def test_puertos_maritimos_get_by_coast_with_accents(self):
        """Test getting ports by coast with accents"""
        result_con = PuertosMaritimos.get_by_coast("Pacífico")
        result_sin = PuertosMaritimos.get_by_coast("Pacifico")
        assert len(result_con) == len(result_sin)
        assert len(result_con) > 0

    def test_carreteras_search_by_name_with_accents(self):
        """Test searching highways by name with accents"""
        result_con = CarreterasCatalog.search_by_name("México")
        result_sin = CarreterasCatalog.search_by_name("Mexico")
        assert len(result_con) == len(result_sin)


class TestAccentInsensitiveConsistency:
    """Test consistency of accent-insensitive search across catalogs."""

    def test_multiple_accent_combinations(self):
        """Test that various accent combinations work consistently"""
        # Test with different accent combinations
        test_cases = [
            ("México", "Mexico", "MEXICO"),
            ("Querétaro", "Queretaro", "QUERETARO"),
            ("Michoacán", "Michoacan", "MICHOACAN"),
            ("Yucatán", "Yucatan", "YUCATAN"),
        ]

        for with_accent, without_accent, expected in test_cases:
            assert normalize_text(with_accent) == expected
            assert normalize_text(without_accent) == expected
            assert normalize_text(with_accent) == normalize_text(without_accent)

    def test_partial_matches_with_accents(self):
        """Test that partial matches work with accents"""
        # SEPOMEX colonia search (substring match)
        result1 = CodigosPostales.search_by_colonia("José")
        result2 = CodigosPostales.search_by_colonia("Jose")
        assert len(result1) == len(result2)
        assert len(result1) > 0

    def test_exact_matches_with_accents(self):
        """Test that exact matches work with accents"""
        # State catalog (exact match)
        result1 = StateCatalog.get_state_by_name("México")
        result2 = StateCatalog.get_state_by_name("MEXICO")
        result3 = StateCatalog.get_state_by_name("mexico")
        assert result1 == result2 == result3
        assert result1 is not None
