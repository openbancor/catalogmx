"""
Complete tests for INEGI catalogs
"""

from catalogmx.catalogs.inegi import LocalidadesCatalog, MunicipiosCatalog, MunicipiosCompletoCatalog, StateCatalog


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

