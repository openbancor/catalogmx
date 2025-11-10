"""
Extended tests for INEGI catalogs to achieve 100% coverage
"""

from catalogmx.catalogs.inegi import (
    LocalidadesCatalog,
    MunicipiosCatalog,
    MunicipiosCompletoCatalog,
    StateCatalog,
)


class TestLocalidadesCatalogExtended:
    """Extended tests for Localidades Catalog"""

    def test_get_by_municipio_not_found(self):
        """Test getting by nonexistent municipio"""
        results = LocalidadesCatalog.get_by_municipio("99", "99")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_by_estado_not_found(self):
        """Test getting by nonexistent estado"""
        results = LocalidadesCatalog.get_by_estado("99")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_search_not_found(self):
        """Test search with no results"""
        results = LocalidadesCatalog.search("NonExistent12345XYZ")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_by_tipo_not_found(self):
        """Test getting by nonexistent tipo"""
        results = LocalidadesCatalog.get_by_tipo("NonExistent")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_urbanas(self):
        """Test getting urbanas"""
        results = LocalidadesCatalog.get_urbanas()
        assert isinstance(results, list)

    def test_get_rurales(self):
        """Test getting rurales"""
        results = LocalidadesCatalog.get_rurales()
        assert isinstance(results, list)

    def test_get_by_ambito_not_found(self):
        """Test getting by nonexistent ambito"""
        results = LocalidadesCatalog.get_by_ambito("NonExistent")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_estadisticas(self):
        """Test getting statistics"""
        stats = LocalidadesCatalog.get_estadisticas()
        assert isinstance(stats, dict)
        assert "total_localidades" in stats

    def test_get_mayores(self):
        """Test getting mayores"""
        results = LocalidadesCatalog.get_mayores(limit=5)
        assert isinstance(results, list)
        assert len(results) <= 5

    def test_get_capitales(self):
        """Test getting capitales"""
        results = LocalidadesCatalog.get_capitales()
        assert isinstance(results, list)

    def test_get_fronterizas(self):
        """Test getting fronterizas"""
        results = LocalidadesCatalog.get_fronterizas()
        assert isinstance(results, list)

    def test_get_costeras(self):
        """Test getting costeras"""
        results = LocalidadesCatalog.get_costeras()
        assert isinstance(results, list)

    def test_get_turisticas(self):
        """Test getting turisticas"""
        results = LocalidadesCatalog.get_turisticas()
        assert isinstance(results, list)

    def test_buscar_cercanas(self):
        """Test buscar cercanas"""
        results = LocalidadesCatalog.buscar_cercanas(19.4326, -99.1332, radio=50)
        assert isinstance(results, list)


class TestMunicipiosCompletoCatalogExtended:
    """Extended tests for Municipios Completo Catalog"""

    def test_get_municipio_not_found(self):
        """Test getting nonexistent municipio"""
        municipio = MunicipiosCompletoCatalog.get_municipio("99", "999")
        assert municipio is None

    def test_get_by_estado_not_found(self):
        """Test getting by nonexistent estado"""
        results = MunicipiosCompletoCatalog.get_by_estado("99")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_search_not_found(self):
        """Test search with no results"""
        results = MunicipiosCompletoCatalog.search("NonExistent12345XYZ")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_by_region_not_found(self):
        """Test getting by nonexistent region"""
        results = MunicipiosCompletoCatalog.get_by_region("NonExistent")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_fronterizos(self):
        """Test getting fronterizos"""
        results = MunicipiosCompletoCatalog.get_fronterizos()
        assert isinstance(results, list)

    def test_get_costeros(self):
        """Test getting costeros"""
        results = MunicipiosCompletoCatalog.get_costeros()
        assert isinstance(results, list)

    def test_get_con_comunidades_indigenas(self):
        """Test getting con comunidades indigenas"""
        results = MunicipiosCompletoCatalog.get_con_comunidades_indigenas()
        assert isinstance(results, list)

    def test_get_mayores_poblacion(self):
        """Test getting mayores por poblacion"""
        results = MunicipiosCompletoCatalog.get_mayores_poblacion(limit=5)
        assert isinstance(results, list)
        assert len(results) <= 5

    def test_get_estadisticas(self):
        """Test getting statistics"""
        stats = MunicipiosCompletoCatalog.get_estadisticas()
        assert isinstance(stats, dict)
        assert "total_municipios" in stats


class TestStateCatalogExtended:
    """Extended tests for State Catalog"""

    def test_get_by_code_not_found(self):
        """Test getting by nonexistent code"""
        state = StateCatalog.get_by_code("99")
        assert state is None

    def test_get_by_name_not_found(self):
        """Test getting by nonexistent name"""
        state = StateCatalog.get_by_name("NonExistent")
        assert state is None

    def test_search_not_found(self):
        """Test search with no results"""
        results = StateCatalog.search("NonExistent12345XYZ")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_by_region_not_found(self):
        """Test getting by nonexistent region"""
        results = StateCatalog.get_by_region("NonExistent")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_fronterizos(self):
        """Test getting fronterizos"""
        results = StateCatalog.get_fronterizos()
        assert isinstance(results, list)

    def test_get_costeros(self):
        """Test getting costeros"""
        results = StateCatalog.get_costeros()
        assert isinstance(results, list)

    def test_get_regiones(self):
        """Test getting regiones"""
        regiones = StateCatalog.get_regiones()
        assert isinstance(regiones, list)

    def test_is_fronterizo(self):
        """Test is_fronterizo"""
        all_states = StateCatalog.get_all()
        if all_states:
            result = StateCatalog.is_fronterizo(all_states[0]["code"])
            assert isinstance(result, bool)

    def test_is_fronterizo_not_found(self):
        """Test is_fronterizo with nonexistent code"""
        result = StateCatalog.is_fronterizo("99")
        assert result is False

    def test_is_costero(self):
        """Test is_costero"""
        all_states = StateCatalog.get_all()
        if all_states:
            result = StateCatalog.is_costero(all_states[0]["code"])
            assert isinstance(result, bool)

    def test_is_costero_not_found(self):
        """Test is_costero with nonexistent code"""
        result = StateCatalog.is_costero("99")
        assert result is False


class TestMunicipiosCatalogExtended:
    """Extended tests for Municipios Catalog"""

    def test_search_not_found(self):
        """Test search with no results"""
        results = MunicipiosCatalog.search("NonExistent12345XYZ")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_by_estado_not_found(self):
        """Test getting by nonexistent estado"""
        results = MunicipiosCatalog.get_by_estado("99")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_municipio_not_found(self):
        """Test getting nonexistent municipio"""
        municipio = MunicipiosCatalog.get_municipio("99", "999")
        assert municipio is None

    def test_is_valid_false(self):
        """Test is_valid with invalid code"""
        assert MunicipiosCatalog.is_valid("99", "999") is False

    def test_is_valid_true(self):
        """Test is_valid with valid code"""
        all_municipios = MunicipiosCatalog.get_all()
        if all_municipios:
            municipio = all_municipios[0]
            result = MunicipiosCatalog.is_valid(municipio["cve_ent"], municipio["cve_mun"])
            assert result is True

