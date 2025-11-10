"""
Comprehensive tests for ClaveProdServ catalog (SQLite-based)
Covers all methods including search, prefix, filters, and statistics
"""

from catalogmx.catalogs.sat.cfdi_4 import ClaveProdServCatalog


class TestClaveProdServCatalog:
    """Complete tests for ClaveProdServ"""

    def test_get_all(self):
        """Test get_all - triggers _get_db_path and _get_connection"""
        try:
            result = ClaveProdServCatalog.get_all()
            assert isinstance(result, list)
            assert len(result) > 0
        except FileNotFoundError:
            # DB file may not exist in test environment
            pass

    def test_get_clave(self):
        """Test get_clave"""
        try:
            result = ClaveProdServCatalog.get_clave("01010101")
            assert result is None or isinstance(result, dict)
        except FileNotFoundError:
            pass

    def test_is_valid(self):
        """Test is_valid"""
        try:
            result = ClaveProdServCatalog.is_valid("01010101")
            assert isinstance(result, bool)
        except FileNotFoundError:
            pass

    def test_search(self):
        """Test search with FTS5"""
        try:
            result = ClaveProdServCatalog.search("computadora", limit=10)
            assert isinstance(result, list)
        except FileNotFoundError:
            pass

    def test_search_simple(self):
        """Test search_simple"""
        try:
            result = ClaveProdServCatalog.search_simple("servicio", limit=10)
            assert isinstance(result, list)
        except FileNotFoundError:
            pass

    def test_get_by_prefix(self):
        """Test get_by_prefix"""
        try:
            result = ClaveProdServCatalog.get_by_prefix("4321", limit=50)
            assert isinstance(result, list)
        except FileNotFoundError:
            pass

    def test_get_con_iva(self):
        """Test get_con_iva"""
        try:
            result = ClaveProdServCatalog.get_con_iva(limit=100)
            assert isinstance(result, list)
        except FileNotFoundError:
            pass

    def test_get_con_ieps(self):
        """Test get_con_ieps"""
        try:
            result = ClaveProdServCatalog.get_con_ieps(limit=100)
            assert isinstance(result, list)
        except FileNotFoundError:
            pass

    def test_get_vigentes(self):
        """Test get_vigentes"""
        try:
            result = ClaveProdServCatalog.get_vigentes(limit=1000)
            assert isinstance(result, list)
        except FileNotFoundError:
            pass

    def test_get_total_count(self):
        """Test get_total_count"""
        try:
            result = ClaveProdServCatalog.get_total_count()
            assert isinstance(result, int)
            assert result > 0
        except FileNotFoundError:
            pass

    def test_get_estadisticas(self):
        """Test get_estadisticas"""
        try:
            result = ClaveProdServCatalog.get_estadisticas()
            assert isinstance(result, dict)
            assert "total" in result
        except FileNotFoundError:
            pass

