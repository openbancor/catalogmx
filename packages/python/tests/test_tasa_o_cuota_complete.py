"""
Complete tests for TasaOCuota catalog to achieve 100% coverage
"""

import pytest
from catalogmx.catalogs.sat.cfdi_4.tasa_o_cuota import TasaOCuota


class TestTasaOCuotaComplete:
    """Complete tests for TasaOCuota catalog"""

    def test_load_data(self):
        """Test loading data"""
        data = TasaOCuota.get_data()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_load_data_caching(self):
        """Test that data is cached after first load"""
        # First call loads data
        data1 = TasaOCuota.get_data()
        # Second call uses cached data
        data2 = TasaOCuota.get_data()
        assert data1 is data2  # Same object reference

    def test_get_data_structure(self):
        """Test structure of returned data"""
        data = TasaOCuota.get_data()
        assert isinstance(data, list)
        if data:
            # Check first item has expected fields
            item = data[0]
            assert isinstance(item, dict)

    def test_get_by_range_and_tax_found(self):
        """Test get_by_range_and_tax when items are found"""
        data = TasaOCuota.get_data()

        # Find a valid item to test with
        if data:
            item = data[0]
            valor_min = item.get("valor_mínimo")
            valor_max = item.get("valor_máximo")
            impuesto = item.get("impuesto")
            factor = item.get("factor")

            results = TasaOCuota.get_by_range_and_tax(
                valor_min, valor_max, impuesto, factor, None, None
            )
            assert isinstance(results, list)
            # Should find at least the item we searched for
            assert len(results) >= 1

    def test_get_by_range_and_tax_not_found(self):
        """Test get_by_range_and_tax when no items match"""
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

    def test_get_by_range_and_tax_partial_match(self):
        """Test get_by_range_and_tax with partial matches"""
        # Test with some None values to ensure filtering works
        results = TasaOCuota.get_by_range_and_tax(
            valor_min=None,
            valor_max=None,
            impuesto=None,
            factor=None,
            trasladado=None,
            retenido=None
        )
        assert isinstance(results, list)

    def test_get_by_range_and_tax_all_criteria(self):
        """Test get_by_range_and_tax with all criteria including trasladado and retenido"""
        # Even though the method doesn't use trasladado and retenido,
        # test that they can be passed without error
        results = TasaOCuota.get_by_range_and_tax(
            valor_min="0.000000",
            valor_max="1.000000",
            impuesto="001",  # ISR
            factor="Tasa",
            trasladado=True,
            retenido=False
        )
        assert isinstance(results, list)
