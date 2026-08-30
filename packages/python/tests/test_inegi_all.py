"""
Complete tests for INEGI catalogs
"""

from catalogmx.catalogs.inegi import (
    LocalidadesCatalog,
    MunicipiosCatalog,
    MunicipiosCompletoCatalog,
    StateCatalog,
)
from catalogmx.catalogs.inegi.states import get_state_names, get_states_dict


class TestLocalidadesCatalog:
    """Test Localidades Catalog"""

    def test_get_all(self):
        """Test getting all localidades"""
        result = LocalidadesCatalog.get_all()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_localidad_not_found(self):
        """Test getting nonexistent localidad"""
        result = LocalidadesCatalog.get_localidad("9999999999")
        assert result is None

    def test_is_valid_false(self):
        """Test is_valid with invalid cvegeo"""
        assert LocalidadesCatalog.is_valid("9999999999") is False

    def test_get_by_municipio(self):
        """Test getting by municipio"""
        result = LocalidadesCatalog.get_by_municipio("01001")
        assert isinstance(result, list)

    def test_get_by_entidad(self):
        """Test getting by entidad"""
        result = LocalidadesCatalog.get_by_entidad("01")
        assert isinstance(result, list)

    def test_get_urbanas(self):
        """Test getting urbanas"""
        result = LocalidadesCatalog.get_urbanas()
        assert isinstance(result, list)

    def test_get_rurales(self):
        """Test getting rurales"""
        result = LocalidadesCatalog.get_rurales()
        assert isinstance(result, list)

    def test_search_by_name(self):
        """Test searching by name"""
        result = LocalidadesCatalog.search_by_name("Guadalajara")
        assert isinstance(result, list)

    def test_search_by_name_not_found(self):
        """Test searching by nonexistent name"""
        result = LocalidadesCatalog.search_by_name("NonExistent12345XYZ")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_by_coordinates(self):
        """Test getting by coordinates"""
        result = LocalidadesCatalog.get_by_coordinates(19.4326, -99.1332, radio_km=10)
        assert isinstance(result, list)

    def test_get_by_population_range(self):
        """Test getting by population range"""
        result = LocalidadesCatalog.get_by_population_range(100000)
        assert isinstance(result, list)

    def test_get_by_population_range_with_max(self):
        """Test getting by population range with max"""
        result = LocalidadesCatalog.get_by_population_range(10000, 50000)
        assert isinstance(result, list)


class TestMunicipiosCompletoCatalog:
    """Test Municipios Completo Catalog"""

    def test_get_all(self):
        """Test getting all municipios"""
        result = MunicipiosCompletoCatalog.get_all()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_municipio_not_found(self):
        """Test getting nonexistent municipio"""
        result = MunicipiosCompletoCatalog.get_municipio("99999")
        assert result is None

    def test_get_by_entidad(self):
        """Test getting by entidad"""
        result = MunicipiosCompletoCatalog.get_by_entidad("01")
        assert isinstance(result, list)

    def test_get_by_entidad_not_found(self):
        """Test getting by nonexistent entidad"""
        result = MunicipiosCompletoCatalog.get_by_entidad("99")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_search_by_name(self):
        """Test searching by name"""
        result = MunicipiosCompletoCatalog.search_by_name("Guadalajara")
        assert isinstance(result, list)

    def test_search_by_name_not_found(self):
        """Test searching by nonexistent name"""
        result = MunicipiosCompletoCatalog.search_by_name("NonExistent12345XYZ")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_by_state_name(self):
        """Test getting by state name"""
        result = MunicipiosCompletoCatalog.get_by_state_name("Jalisco")
        assert isinstance(result, list)

    def test_get_by_state_name_not_found(self):
        """Test getting by nonexistent state name"""
        result = MunicipiosCompletoCatalog.get_by_state_name("NonExistent")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_count_by_entidad(self):
        """Test getting count by entidad"""
        result = MunicipiosCompletoCatalog.get_count_by_entidad("01")
        assert isinstance(result, int)

    def test_get_count_by_entidad_not_found(self):
        """Test getting count for nonexistent entidad"""
        result = MunicipiosCompletoCatalog.get_count_by_entidad("99")
        assert result == 0

    def test_is_valid_false(self):
        """Test is_valid with invalid code"""
        assert MunicipiosCompletoCatalog.is_valid("99999") is False

    def test_get_total_count(self):
        """Test getting total count"""
        result = MunicipiosCompletoCatalog.get_total_count()
        assert isinstance(result, int)
        assert result > 0

    def test_get_estadisticas(self):
        """Test getting statistics"""
        stats = MunicipiosCompletoCatalog.get_estadisticas()
        assert isinstance(stats, dict)
        assert "total_municipios" in stats


class TestStateCatalog:
    """Test State Catalog"""

    def test_get_all_states(self):
        """Test getting all states"""
        all_states = StateCatalog.get_all_states()
        assert isinstance(all_states, list)
        assert len(all_states) > 0

    def test_lookup_all_32_states_by_code(self):
        """Test every state can be looked up by CURP code"""
        all_states = [
            state
            for state in StateCatalog.get_all_states()
            if state["clave_inegi"] != "99"
        ]
        assert len(all_states) == 32

        for state in all_states:
            result = StateCatalog.get_state_by_code(state["code"])
            assert result == state
            assert StateCatalog.validate_state_code(state["code"]) is True

    def test_get_state_by_code_invalid(self):
        """Test invalid CURP state code returns None"""
        assert StateCatalog.get_state_by_code("ZZ") is None
        assert StateCatalog.validate_state_code("ZZ") is False

    def test_get_state_by_name_and_alias(self):
        """Test state lookup by name and alias"""
        jalisco = StateCatalog.get_state_by_name("Jalisco")
        assert jalisco is not None
        assert jalisco["code"] == "JC"

        cdmx = StateCatalog.get_state_by_name("Distrito Federal")
        assert cdmx is not None
        assert cdmx["code"] == "DF"

    def test_get_state_by_inegi_code(self):
        """Test state lookup by INEGI code"""
        assert StateCatalog.get_state_by_inegi_code("14")["name"] == "JALISCO"
        assert StateCatalog.get_state_by_inegi_code(9)["code"] == "DF"
        assert StateCatalog.get_state_by_inegi_code("00") is None

    def test_state_code_and_inegi_code_maps(self):
        """Test helper maps include all states"""
        state_codes = StateCatalog.get_state_codes()
        inegi_codes = StateCatalog.get_inegi_codes()

        assert len(state_codes) >= 32
        assert len(inegi_codes) >= 32
        assert state_codes["JALISCO"] == "JC"
        assert inegi_codes["JALISCO"] == "14"

    def test_state_convenience_functions(self):
        """Test module-level state convenience functions"""
        states_by_code = get_states_dict()
        state_names = get_state_names()

        assert len(states_by_code) >= 32
        assert len(state_names) >= 32
        assert states_by_code["JC"]["name"] == "JALISCO"
        assert "JALISCO" in state_names

    def test_state_abbreviations_are_available(self):
        """Test all states include abbreviation data"""
        all_states = StateCatalog.get_all_states()
        abbreviations = {state["abbreviation"] for state in all_states}

        assert len(abbreviations) >= 32
        assert {"JAL", "CDMX", "NL"}.issubset(abbreviations)


class TestMunicipiosCatalog:
    """Test Municipios Catalog"""

    def test_get_all(self):
        """Test getting all municipios"""
        result = MunicipiosCatalog.get_all()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_municipio_not_found(self):
        """Test getting nonexistent municipio"""
        result = MunicipiosCatalog.get_municipio("99999")
        assert result is None

    def test_get_by_entidad(self):
        """Test getting by entidad"""
        result = MunicipiosCatalog.get_by_entidad("01")
        assert isinstance(result, list)

    def test_get_by_entidad_not_found(self):
        """Test getting by nonexistent entidad"""
        result = MunicipiosCatalog.get_by_entidad("99")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_search_by_name(self):
        """Test searching by name"""
        result = MunicipiosCatalog.search_by_name("Guadalajara")
        assert isinstance(result, list)

    def test_search_by_name_not_found(self):
        """Test searching by nonexistent name"""
        result = MunicipiosCatalog.search_by_name("NonExistent12345")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_is_valid_false(self):
        """Test is_valid with invalid code"""
        assert MunicipiosCatalog.is_valid("99999") is False
