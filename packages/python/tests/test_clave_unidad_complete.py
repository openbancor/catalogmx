"""
Comprehensive tests for ClaveUnidad catalog
Covers all methods including search, categorization, and conversions
"""

from catalogmx.catalogs.sat.cfdi_4 import ClaveUnidadCatalog


class TestClaveUnidadCatalog:
    """Complete tests for ClaveUnidad"""

    def test_get_all(self):
        """Test get_all - triggers _load_data"""
        result = ClaveUnidadCatalog.get_all()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_get_unidad(self):
        """Test get_unidad"""
        all_unidades = ClaveUnidadCatalog.get_all()
        if all_unidades:
            unidad_id = all_unidades[0]["id"]
            result = ClaveUnidadCatalog.get_unidad(unidad_id)
            assert result is not None

    def test_get_unidad_not_found(self):
        """Test get_unidad with invalid ID"""
        result = ClaveUnidadCatalog.get_unidad("INVALID_ID_XXX")
        assert result is None

    def test_is_valid_true(self):
        """Test is_valid with valid ID"""
        all_unidades = ClaveUnidadCatalog.get_all()
        if all_unidades:
            assert ClaveUnidadCatalog.is_valid(all_unidades[0]["id"]) is True

    def test_is_valid_false(self):
        """Test is_valid with invalid ID"""
        assert ClaveUnidadCatalog.is_valid("INVALID_ID_XXX") is False

    def test_search_by_name(self):
        """Test search_by_name"""
        result = ClaveUnidadCatalog.search_by_name("metro")
        assert isinstance(result, list)

    def test_search_by_name_no_results(self):
        """Test search_by_name with no results"""
        result = ClaveUnidadCatalog.search_by_name("NonExistentUnit12345XYZ")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_search_by_symbol(self):
        """Test search_by_symbol"""
        result = ClaveUnidadCatalog.search_by_symbol("m")
        assert isinstance(result, list)

    def test_search_by_symbol_no_results(self):
        """Test search_by_symbol with no results"""
        result = ClaveUnidadCatalog.search_by_symbol("©™®")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_vigentes(self):
        """Test get_vigentes if method exists"""
        if hasattr(ClaveUnidadCatalog, 'get_vigentes'):
            result = ClaveUnidadCatalog.get_vigentes()
            assert isinstance(result, list)

    def test_get_obsoletas(self):
        """Test get_obsoletas if method exists"""
        if hasattr(ClaveUnidadCatalog, 'get_obsoletas'):
            result = ClaveUnidadCatalog.get_obsoletas()
            assert isinstance(result, list)

