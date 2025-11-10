"""
Tests for TasaOCuota catalog
"""

from catalogmx.catalogs.sat.cfdi_4.tasa_o_cuota import TasaOCuota


class TestTasaOCuota:
    """Test TasaOCuota catalog"""

    def test_get_data(self):
        """Test getting all data"""
        data = TasaOCuota.get_data()
        assert data is not None
        assert isinstance(data, list)
        assert len(data) > 0

    def test_load_data_caching(self):
        """Test that data is cached after first load"""
        # First call loads data
        data1 = TasaOCuota.get_data()
        # Second call should use cached data
        data2 = TasaOCuota.get_data()
        assert data1 is data2  # Same object reference

    def test_get_by_range_and_tax(self):
        """Test getting rate by range and tax criteria"""
        # Get all data first to know what values exist
        data = TasaOCuota.get_data()
        
        if len(data) > 0:
            # Use actual values from the data
            first_item = data[0]
            results = TasaOCuota.get_by_range_and_tax(
                valor_min=first_item.get("valor_mínimo"),
                valor_max=first_item.get("valor_máximo"),
                impuesto=first_item.get("impuesto"),
                factor=first_item.get("factor"),
                trasladado=None,
                retenido=None
            )
            assert isinstance(results, list)
            if len(results) > 0:
                assert results[0] == first_item

    def test_get_by_range_and_tax_no_match(self):
        """Test searching with criteria that don't match"""
        results = TasaOCuota.get_by_range_and_tax(
            valor_min="NONEXISTENT",
            valor_max="NONEXISTENT",
            impuesto="NONEXISTENT",
            factor="NONEXISTENT",
            trasladado=None,
            retenido=None
        )
        assert isinstance(results, list)
        assert len(results) == 0

    def test_data_structure(self):
        """Test that loaded data has expected structure"""
        data = TasaOCuota.get_data()
        assert isinstance(data, list)
        
        if len(data) > 0:
            # Check that items are dictionaries
            assert isinstance(data[0], dict)

    def test_multiple_criteria_filtering(self):
        """Test filtering with multiple criteria"""
        data = TasaOCuota.get_data()
        
        if len(data) > 0:
            # Test that the method filters correctly
            test_item = data[0]
            results = TasaOCuota.get_by_range_and_tax(
                valor_min=test_item.get("valor_mínimo"),
                valor_max=test_item.get("valor_máximo"),
                impuesto=test_item.get("impuesto"),
                factor=test_item.get("factor"),
                trasladado=None,
                retenido=None
            )
            
            # All results should match the criteria
            for result in results:
                assert result.get("valor_mínimo") == test_item.get("valor_mínimo")
                assert result.get("valor_máximo") == test_item.get("valor_máximo")
                assert result.get("impuesto") == test_item.get("impuesto")
                assert result.get("factor") == test_item.get("factor")

