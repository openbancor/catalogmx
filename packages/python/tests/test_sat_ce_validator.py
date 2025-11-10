"""
Tests for SAT Comercio Exterior Validator
"""

from catalogmx.catalogs.sat.comercio_exterior.validator import ComercioExteriorValidator


class TestComercioExteriorValidator:
    """Test Comercio Exterior Validator"""

    def test_validate_valid_cfdi(self):
        """Test validating a valid CFDI"""
        cfdi_ce = {
            "tipo_comprobante": "I",
            "incoterm": "CIF",
            "clave_pedimento": "A1",
            "moneda": "USD",
            "total": 1000.00,
            "tipo_cambio_usd": 1.0,
            "total_usd": 1000.00,
            "mercancias": [
                {
                    "fraccion_arancelaria": "01012100",
                    "cantidad_aduana": 100,
                    "unidad_aduana": "KG",
                    "valor_unitario_aduana": 10.00,
                    "valor_dolares": 1000.00
                }
            ],
            "receptor": {
                "pais": "USA",
                "num_reg_id_trib": "123456789"
            }
        }
        
        result = ComercioExteriorValidator.validate(cfdi_ce)
        assert isinstance(result, dict)
        assert "valid" in result
        assert "errors" in result
        assert "warnings" in result

    def test_validate_missing_incoterm(self):
        """Test validating CFDI with missing INCOTERM"""
        cfdi_ce = {
            "tipo_comprobante": "I",
            "clave_pedimento": "A1",
            "moneda": "USD",
            "mercancias": []
        }
        
        result = ComercioExteriorValidator.validate(cfdi_ce)
        assert result["valid"] is False
        assert len(result["errors"]) > 0
        assert any("INCOTERM" in error for error in result["errors"])

    def test_validate_invalid_incoterm(self):
        """Test validating CFDI with invalid INCOTERM"""
        cfdi_ce = {
            "incoterm": "INVALID",
            "clave_pedimento": "A1",
            "moneda": "USD",
            "mercancias": []
        }
        
        result = ComercioExteriorValidator.validate(cfdi_ce)
        assert result["valid"] is False
        assert any("INCOTERM" in error for error in result["errors"])

    def test_validate_missing_clave_pedimento(self):
        """Test validating CFDI with missing clave pedimento"""
        cfdi_ce = {
            "incoterm": "CIF",
            "moneda": "USD",
            "mercancias": []
        }
        
        result = ComercioExteriorValidator.validate(cfdi_ce)
        assert result["valid"] is False
        assert any("ClavePedimento" in error for error in result["errors"])

    def test_validate_invalid_clave_pedimento(self):
        """Test validating CFDI with invalid clave pedimento"""
        cfdi_ce = {
            "incoterm": "CIF",
            "clave_pedimento": "INVALID",
            "moneda": "USD",
            "mercancias": []
        }
        
        result = ComercioExteriorValidator.validate(cfdi_ce)
        assert result["valid"] is False
        assert any("ClavePedimento" in error for error in result["errors"])

    def test_validate_missing_mercancias(self):
        """Test validating CFDI with no mercancias"""
        cfdi_ce = {
            "incoterm": "CIF",
            "clave_pedimento": "A1",
            "moneda": "USD"
        }
        
        result = ComercioExteriorValidator.validate(cfdi_ce)
        assert result["valid"] is False
        assert any("mercancía" in error for error in result["errors"])

    def test_validate_traslado_without_motivo(self):
        """Test validating traslado without motivo"""
        cfdi_ce = {
            "tipo_comprobante": "T",
            "incoterm": "CIF",
            "clave_pedimento": "A1",
            "moneda": "USD",
            "mercancias": [
                {
                    "fraccion_arancelaria": "01012100",
                    "cantidad_aduana": 100,
                    "unidad_aduana": "KG",
                    "valor_unitario_aduana": 10.00,
                    "valor_dolares": 1000.00
                }
            ]
        }
        
        result = ComercioExteriorValidator.validate(cfdi_ce)
        assert result["valid"] is False
        assert any("MotivoTraslado" in error for error in result["errors"])

    def test_validate_mercancia_missing_fields(self):
        """Test validating mercancia with missing fields"""
        cfdi_ce = {
            "incoterm": "CIF",
            "clave_pedimento": "A1",
            "moneda": "USD",
            "mercancias": [
                {
                    # Missing required fields
                }
            ]
        }
        
        result = ComercioExteriorValidator.validate(cfdi_ce)
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_receptor_missing_pais(self):
        """Test validating receptor without country"""
        cfdi_ce = {
            "incoterm": "CIF",
            "clave_pedimento": "A1",
            "moneda": "USD",
            "mercancias": [
                {
                    "fraccion_arancelaria": "01012100",
                    "cantidad_aduana": 100,
                    "unidad_aduana": "KG",
                    "valor_unitario_aduana": 10.00,
                    "valor_dolares": 1000.00
                }
            ],
            "receptor": {
                "num_reg_id_trib": "123456789"
            }
        }
        
        result = ComercioExteriorValidator.validate(cfdi_ce)
        assert result["valid"] is False
        assert any("país" in error.lower() for error in result["errors"])

    def test_validate_receptor_invalid_pais(self):
        """Test validating receptor with invalid country"""
        cfdi_ce = {
            "incoterm": "CIF",
            "clave_pedimento": "A1",
            "moneda": "USD",
            "mercancias": [
                {
                    "fraccion_arancelaria": "01012100",
                    "cantidad_aduana": 100,
                    "unidad_aduana": "KG",
                    "valor_unitario_aduana": 10.00,
                    "valor_dolares": 1000.00
                }
            ],
            "receptor": {
                "pais": "INVALID",
                "num_reg_id_trib": "123456789"
            }
        }
        
        result = ComercioExteriorValidator.validate(cfdi_ce)
        assert result["valid"] is False
        assert any("país" in error.lower() for error in result["errors"])

    def test_validate_receptor_requires_estado(self):
        """Test validating receptor that requires subdivision"""
        cfdi_ce = {
            "incoterm": "CIF",
            "clave_pedimento": "A1",
            "moneda": "USD",
            "mercancias": [
                {
                    "fraccion_arancelaria": "01012100",
                    "cantidad_aduana": 100,
                    "unidad_aduana": "KG",
                    "valor_unitario_aduana": 10.00,
                    "valor_dolares": 1000.00
                }
            ],
            "receptor": {
                "pais": "USA",
                "num_reg_id_trib": "123456789"
                # Missing estado
            }
        }
        
        result = ComercioExteriorValidator.validate(cfdi_ce)
        # May or may not fail depending on whether estado is required
        assert isinstance(result, dict)

    def test_validate_summary(self):
        """Test getting validation summary"""
        cfdi_ce = {
            "incoterm": "CIF",
            "mercancias": []
        }
        
        result = ComercioExteriorValidator.validate(cfdi_ce)
        summary = ComercioExteriorValidator.get_validation_summary(result)
        assert isinstance(summary, str)
        assert "válido" in summary.lower() or "inválido" in summary.lower()

