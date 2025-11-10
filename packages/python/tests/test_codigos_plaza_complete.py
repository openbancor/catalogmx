"""
Complete tests for Codigos Plaza Catalog
"""

from catalogmx.catalogs.banxico import CodigosPlazaCatalog


class TestCodigosPlazaComplete:
    """Complete tests for Codigos Plaza"""

    def test_get_all(self):
        """Test getting all plazas"""
        result = CodigosPlazaCatalog.get_all()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_buscar_por_codigo_found(self):
        """Test searching by code"""
        all_plazas = CodigosPlazaCatalog.get_all()
        if all_plazas:
            codigo = all_plazas[0]["codigo"]
            result = CodigosPlazaCatalog.buscar_por_codigo(codigo)
            assert isinstance(result, list)
            assert len(result) > 0

    def test_buscar_por_codigo_not_found(self):
        """Test searching by nonexistent code"""
        result = CodigosPlazaCatalog.buscar_por_codigo("999")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_buscar_por_plaza_found(self):
        """Test searching by plaza name"""
        all_plazas = CodigosPlazaCatalog.get_all()
        if all_plazas:
            plaza = all_plazas[0]["plaza"]
            result = CodigosPlazaCatalog.buscar_por_plaza(plaza)
            assert isinstance(result, list)

    def test_buscar_por_plaza_not_found(self):
        """Test searching by nonexistent plaza"""
        result = CodigosPlazaCatalog.buscar_por_plaza("NonExistentPlaza12345")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_por_estado_found(self):
        """Test getting by estado"""
        all_plazas = CodigosPlazaCatalog.get_all()
        if all_plazas:
            estado = all_plazas[0]["estado"]
            result = CodigosPlazaCatalog.get_por_estado(estado)
            assert isinstance(result, list)

    def test_get_por_estado_not_found(self):
        """Test getting by nonexistent estado"""
        result = CodigosPlazaCatalog.get_por_estado("NonExistentState")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_por_cve_entidad_found(self):
        """Test getting by cve_entidad"""
        all_plazas = CodigosPlazaCatalog.get_all()
        if all_plazas:
            cve = all_plazas[0]["cve_entidad"]
            result = CodigosPlazaCatalog.get_por_cve_entidad(cve)
            assert isinstance(result, list)
            assert len(result) > 0

    def test_get_por_cve_entidad_not_found(self):
        """Test getting by nonexistent cve_entidad"""
        result = CodigosPlazaCatalog.get_por_cve_entidad("99")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_plazas_duplicadas(self):
        """Test getting duplicate plazas"""
        result = CodigosPlazaCatalog.get_plazas_duplicadas()
        assert isinstance(result, dict)

    def test_search(self):
        """Test search functionality"""
        all_plazas = CodigosPlazaCatalog.get_all()
        if all_plazas:
            query = all_plazas[0]["plaza"][:3]
            result = CodigosPlazaCatalog.search(query)
            assert isinstance(result, list)

    def test_search_not_found(self):
        """Test search with no results"""
        result = CodigosPlazaCatalog.search("NonExistent12345XYZ")
        assert isinstance(result, list)
        assert len(result) == 0

    def test_get_estadisticas(self):
        """Test getting statistics"""
        stats = CodigosPlazaCatalog.get_estadisticas()
        assert isinstance(stats, dict)
        assert "total_plazas" in stats
        assert stats["total_plazas"] > 0

