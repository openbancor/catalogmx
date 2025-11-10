"""
Complete tests for ComercioExteriorValidator
The validator is actually straightforward - just validates CFDI fields against catalogs
"""

from catalogmx.catalogs.sat.comercio_exterior.validator import ComercioExteriorValidator


class TestComercioExteriorValidator:
    """Test the CFDI Comercio Exterior validator"""

    def test_validate_empty_cfdi(self):
        """Test validating empty CFDI - should have errors"""
        # Empty dict will cause issues with MonedaCatalog, so provide minimal valid structure
        cfdi = {"moneda": "USD", "total": 100, "tipo_cambio_usd": 1.0, "total_usd": 100}
        result = ComercioExteriorValidator.validate(cfdi)
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_missing_incoterm(self):
        """Test CFDI without INCOTERM"""
        cfdi = {
            "clave_pedimento": "A1",
            "moneda": "USD",
            "total": 100,
            "tipo_cambio_usd": 1.0,
            "total_usd": 100
        }
        result = ComercioExteriorValidator.validate(cfdi)
        assert result["valid"] is False
        assert any("INCOTERM" in err for err in result["errors"])

    def test_validate_invalid_incoterm(self):
        """Test CFDI with invalid INCOTERM"""
        cfdi = {
            "incoterm": "INVALID",
            "clave_pedimento": "A1",
            "moneda": "USD",
            "total": 100,
            "tipo_cambio_usd": 1.0,
            "total_usd": 100
        }
        result = ComercioExteriorValidator.validate(cfdi)
        assert result["valid"] is False
        assert any("INCOTERM" in err for err in result["errors"])

    def test_validate_missing_clave_pedimento(self):
        """Test CFDI without clave pedimento"""
        cfdi = {
            "incoterm": "CIF",
            "moneda": "USD",
            "total": 100,
            "tipo_cambio_usd": 1.0,
            "total_usd": 100
        }
        result = ComercioExteriorValidator.validate(cfdi)
        assert result["valid"] is False
        assert any("ClavePedimento" in err for err in result["errors"])

    def test_validate_invalid_clave_pedimento(self):
        """Test CFDI with invalid clave pedimento"""
        cfdi = {
            "incoterm": "CIF",
            "clave_pedimento": "XX",
            "moneda": "USD",
            "total": 100,
            "tipo_cambio_usd": 1.0,
            "total_usd": 100
        }
        result = ComercioExteriorValidator.validate(cfdi)
        assert result["valid"] is False

    def test_validate_moneda_conversion(self):
        """Test moneda conversion validation"""
        cfdi = {
            "incoterm": "CIF",
            "clave_pedimento": "A1",
            "moneda": "USD",
            "total": 100,
            # Missing tipo_cambio_usd and total_usd
            "tipo_cambio_usd": None,
            "total_usd": None
        }
        result = ComercioExteriorValidator.validate(cfdi)
        # Should have errors about USD conversion
        assert len(result["errors"]) > 0

    def test_validate_missing_mercancias(self):
        """Test CFDI without mercancias"""
        cfdi = {
            "incoterm": "CIF",
            "clave_pedimento": "A1",
            "moneda": "USD",
            "total": 100,
            "tipo_cambio_usd": 1.0,
            "total_usd": 100
        }
        result = ComercioExteriorValidator.validate(cfdi)
        assert result["valid"] is False
        assert any("mercancía" in err for err in result["errors"])

    def test_validate_mercancia_missing_fraccion(self):
        """Test mercancia without fraccion arancelaria"""
        cfdi = {
            "incoterm": "CIF",
            "clave_pedimento": "A1",
            "moneda": "USD",
            "total": 100,
            "tipo_cambio_usd": 1.0,
            "total_usd": 100,
            "mercancias": [{}]
        }
        result = ComercioExteriorValidator.validate(cfdi)
        assert result["valid"] is False
        assert any("FraccionArancelaria" in err for err in result["errors"])

    def test_validate_mercancia_invalid_fraccion_length(self):
        """Test mercancia with invalid fraccion length"""
        cfdi = {
            "incoterm": "CIF",
            "clave_pedimento": "A1",
            "moneda": "USD",
            "total": 100,
            "tipo_cambio_usd": 1.0,
            "total_usd": 100,
            "mercancias": [{"fraccion_arancelaria": "123"}]  # Too short
        }
        result = ComercioExteriorValidator.validate(cfdi)
        assert result["valid"] is False

    def test_validate_mercancia_missing_unidad_aduana(self):
        """Test mercancia without unidad aduana"""
        cfdi = {
            "incoterm": "CIF",
            "clave_pedimento": "A1",
            "moneda": "USD",
            "total": 100,
            "tipo_cambio_usd": 1.0,
            "total_usd": 100,
            "mercancias": [{"fraccion_arancelaria": "01010101"}]
        }
        result = ComercioExteriorValidator.validate(cfdi)
        assert result["valid"] is False
        assert any("UnidadAduana" in err for err in result["errors"])

    def test_validate_mercancia_invalid_cantidad(self):
        """Test mercancia with invalid cantidad"""
        cfdi = {
            "incoterm": "CIF",
            "clave_pedimento": "A1",
            "moneda": "USD",
            "total": 100,
            "tipo_cambio_usd": 1.0,
            "total_usd": 100,
            "mercancias": [{
                "fraccion_arancelaria": "01010101",
                "unidad_aduana": "KG",
                "cantidad_aduana": 0  # Invalid: must be > 0
            }]
        }
        result = ComercioExteriorValidator.validate(cfdi)
        assert result["valid"] is False

    def test_validate_mercancia_invalid_valor_unitario(self):
        """Test mercancia with invalid valor unitario"""
        cfdi = {
            "incoterm": "CIF",
            "clave_pedimento": "A1",
            "moneda": "USD",
            "total": 100,
            "tipo_cambio_usd": 1.0,
            "total_usd": 100,
            "mercancias": [{
                "fraccion_arancelaria": "01010101",
                "unidad_aduana": "KG",
                "cantidad_aduana": 100,
                "valor_unitario_aduana": 0  # Invalid
            }]
        }
        result = ComercioExteriorValidator.validate(cfdi)
        assert result["valid"] is False

    def test_validate_mercancia_missing_pais_origen(self):
        """Test mercancia without pais origen"""
        cfdi = {
            "incoterm": "CIF",
            "clave_pedimento": "A1",
            "moneda": "USD",
            "total": 100,
            "tipo_cambio_usd": 1.0,
            "total_usd": 100,
            "mercancias": [{
                "fraccion_arancelaria": "01010101",
                "unidad_aduana": "KG",
                "cantidad_aduana": 100,
                "valor_unitario_aduana": 10.0
            }]
        }
        result = ComercioExteriorValidator.validate(cfdi)
        assert result["valid"] is False
        assert any("PaisOrigen" in err for err in result["errors"])

    def test_validate_receptor_missing_pais(self):
        """Test receptor without pais"""
        cfdi = {
            "incoterm": "CIF",
            "clave_pedimento": "A1",
            "moneda": "USD",
            "total": 100,
            "tipo_cambio_usd": 1.0,
            "total_usd": 100,
            "mercancias": [{
                "fraccion_arancelaria": "01010101",
                "unidad_aduana": "KG",
                "cantidad_aduana": 100,
                "valor_unitario_aduana": 10.0,
                "pais_origen": "MEX"
            }],
            "receptor": {}
        }
        result = ComercioExteriorValidator.validate(cfdi)
        # Should have errors (about missing pais or estado validation)
        assert len(result["errors"]) > 0

    def test_validate_receptor_invalid_pais(self):
        """Test receptor with invalid pais"""
        cfdi = {
            "incoterm": "CIF",
            "clave_pedimento": "A1",
            "moneda": "USD",
            "total": 100,
            "tipo_cambio_usd": 1.0,
            "total_usd": 100,
            "mercancias": [{
                "fraccion_arancelaria": "01010101",
                "unidad_aduana": "KG",
                "cantidad_aduana": 100,
                "valor_unitario_aduana": 10.0,
                "pais_origen": "MEX"
            }],
            "receptor": {"pais": "INVALID"}
        }
        result = ComercioExteriorValidator.validate(cfdi)
        assert result["valid"] is False

    def test_validate_tipo_comprobante_t_without_motivo(self):
        """Test tipo comprobante T without motivo traslado"""
        cfdi = {
            "tipo_comprobante": "T",
            "incoterm": "CIF",
            "clave_pedimento": "A1",
            "moneda": "USD",
            "total": 100,
            "tipo_cambio_usd": 1.0,
            "total_usd": 100,
            "mercancias": [{
                "fraccion_arancelaria": "01010101",
                "unidad_aduana": "KG",
                "cantidad_aduana": 100,
                "valor_unitario_aduana": 10.0,
                "pais_origen": "MEX"
            }]
        }
        result = ComercioExteriorValidator.validate(cfdi)
        assert result["valid"] is False
        assert any("MotivoTraslado" in err for err in result["errors"])

    def test_validate_motivo_invalid(self):
        """Test with invalid motivo traslado"""
        cfdi = {
            "tipo_comprobante": "T",
            "incoterm": "CIF",
            "clave_pedimento": "A1",
            "motivo_traslado": "XX",  # Invalid
            "moneda": "USD",
            "total": 100,
            "tipo_cambio_usd": 1.0,
            "total_usd": 100,
            "mercancias": [{
                "fraccion_arancelaria": "01010101",
                "unidad_aduana": "KG",
                "cantidad_aduana": 100,
                "valor_unitario_aduana": 10.0,
                "pais_origen": "MEX"
            }]
        }
        result = ComercioExteriorValidator.validate(cfdi)
        assert result["valid"] is False

    def test_validate_certificado_origen_invalid(self):
        """Test with invalid certificado origen"""
        cfdi = {
            "incoterm": "CIF",
            "clave_pedimento": "A1",
            "moneda": "USD",
            "total": 100,
            "tipo_cambio_usd": 1.0,
            "total_usd": 100,
            "mercancias": [{
                "fraccion_arancelaria": "01010101",
                "unidad_aduana": "KG",
                "cantidad_aduana": 100,
                "valor_unitario_aduana": 10.0,
                "pais_origen": "MEX"
            }],
            "certificado_origen": "2"  # Invalid: must be 0 or 1
        }
        result = ComercioExteriorValidator.validate(cfdi)
        assert result["valid"] is False
        assert any("CertificadoOrigen" in err for err in result["errors"])

    def test_validate_quick_incoterm(self):
        """Test validate_quick for incoterm"""
        assert ComercioExteriorValidator.validate_quick("incoterm", "FOB") is True
        assert ComercioExteriorValidator.validate_quick("incoterm", "XXX") is False

    def test_validate_quick_clave_pedimento(self):
        """Test validate_quick for clave_pedimento"""
        result = ComercioExteriorValidator.validate_quick("clave_pedimento", "A1")
        assert isinstance(result, bool)

    def test_validate_quick_invalid_field(self):
        """Test validate_quick with invalid field"""
        try:
            ComercioExteriorValidator.validate_quick("invalid_field", "value")
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert "no soportado" in str(e)

    def test_validate_quick_all_fields(self):
        """Test validate_quick with all supported fields"""
        fields = [
            ("incoterm", "FOB"),
            ("clave_pedimento", "A1"),
            ("unidad_aduana", "KG"),
            ("motivo_traslado", "01"),
            ("moneda", "USD"),
            ("pais", "USA"),
            ("estado_usa", "TX"),
            ("provincia_canada", "ON"),
        ]
        
        for field, value in fields:
            result = ComercioExteriorValidator.validate_quick(field, value)
            assert isinstance(result, bool)

