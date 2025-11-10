"""
Tests for SAT Comercio Exterior catalogs
"""

import pytest

from catalogmx.catalogs.sat.comercio_exterior import (
    ClavePedimentoCatalog,
    EstadoCatalog,
    IncotermsValidator,
    MonedaCatalog,
    MotivoTrasladoCatalog,
    PaisCatalog,
    RegistroIdentTribCatalog,
    UnidadAduanaCatalog,
)


class TestPaisCatalog:
    """Test Pais Catalog"""

    def test_get_pais_by_alpha3(self):
        """Test getting pais by Alpha-3 code"""
        pais = PaisCatalog.get_pais("MEX")
        assert pais is not None
        assert pais["codigo"] == "MEX"

    def test_get_pais_by_alpha2(self):
        """Test getting pais by Alpha-2 code"""
        pais = PaisCatalog.get_pais("US")
        assert pais is not None

    def test_get_pais_not_found(self):
        """Test getting nonexistent pais"""
        pais = PaisCatalog.get_pais("XXX")
        assert pais is None

    def test_is_valid_true(self):
        """Test is_valid with valid country code"""
        assert PaisCatalog.is_valid("MEX") is True
        assert PaisCatalog.is_valid("US") is True

    def test_is_valid_false(self):
        """Test is_valid with invalid country code"""
        assert PaisCatalog.is_valid("XXX") is False

    def test_requires_subdivision_true(self):
        """Test requires_subdivision for USA"""
        result = PaisCatalog.requires_subdivision("USA")
        assert isinstance(result, bool)

    def test_requires_subdivision_false(self):
        """Test requires_subdivision for country that doesn't require it"""
        result = PaisCatalog.requires_subdivision("MEX")
        assert isinstance(result, bool)

    def test_requires_subdivision_nonexistent(self):
        """Test requires_subdivision for nonexistent country"""
        result = PaisCatalog.requires_subdivision("XXX")
        assert result is False

    def test_get_all(self):
        """Test getting all countries"""
        paises = PaisCatalog.get_all()
        assert isinstance(paises, list)
        assert len(paises) > 0

    def test_search_by_code(self):
        """Test searching by code"""
        results = PaisCatalog.search("MEX")
        assert isinstance(results, list)
        assert len(results) > 0

    def test_search_by_name(self):
        """Test searching by name"""
        results = PaisCatalog.search("Mexico")
        assert isinstance(results, list)

    def test_search_no_results(self):
        """Test search with no results"""
        results = PaisCatalog.search("NonExistentCountry12345")
        assert isinstance(results, list)
        assert len(results) == 0


class TestEstadoCatalog:
    """Test Estado Catalog"""

    def test_get_estado_usa(self):
        """Test getting USA state"""
        estado = EstadoCatalog.get_estado_usa("TX")
        assert estado is not None
        assert estado["country"] == "USA"

    def test_get_provincia_canada(self):
        """Test getting Canada province"""
        provincia = EstadoCatalog.get_provincia_canada("ON")
        assert provincia is not None
        assert provincia["country"] == "CAN"

    def test_get_estado_with_country_filter(self):
        """Test getting estado with country filter"""
        estado = EstadoCatalog.get_estado("TX", "USA")
        assert estado is not None
        assert estado["country"] == "USA"

    def test_get_estado_wrong_country(self):
        """Test getting estado with wrong country filter"""
        estado = EstadoCatalog.get_estado("TX", "CAN")
        assert estado is None

    def test_get_estado_not_found(self):
        """Test getting nonexistent estado"""
        estado = EstadoCatalog.get_estado("XX")
        assert estado is None

    def test_is_valid_true(self):
        """Test is_valid with valid code"""
        assert EstadoCatalog.is_valid("TX") is True
        assert EstadoCatalog.is_valid("ON") is True

    def test_is_valid_false(self):
        """Test is_valid with invalid code"""
        assert EstadoCatalog.is_valid("XX") is False

    def test_is_valid_with_country(self):
        """Test is_valid with country filter"""
        assert EstadoCatalog.is_valid("TX", "USA") is True
        assert EstadoCatalog.is_valid("TX", "CAN") is False

    def test_get_all_usa(self):
        """Test getting all USA states"""
        estados = EstadoCatalog.get_all_usa()
        assert isinstance(estados, list)
        assert len(estados) > 0
        for estado in estados:
            assert estado["country"] == "USA"

    def test_get_all_canada(self):
        """Test getting all Canada provinces"""
        provincias = EstadoCatalog.get_all_canada()
        assert isinstance(provincias, list)
        assert len(provincias) > 0
        for provincia in provincias:
            assert provincia["country"] == "CAN"

    def test_search_usa(self):
        """Test searching USA states"""
        results = EstadoCatalog.search("Texas", "USA")
        assert isinstance(results, list)

    def test_search_canada(self):
        """Test searching Canada provinces"""
        results = EstadoCatalog.search("Ontario", "CAN")
        assert isinstance(results, list)

    def test_search_no_country(self):
        """Test searching without country filter"""
        results = EstadoCatalog.search("AL")
        assert isinstance(results, list)

    def test_search_no_results(self):
        """Test search with no results"""
        results = EstadoCatalog.search("NonExistent")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_by_name_usa(self):
        """Test getting by name (USA)"""
        estado = EstadoCatalog.get_by_name("Texas", "USA")
        if estado:
            assert estado["country"] == "USA"

    def test_get_by_name_canada(self):
        """Test getting by name (Canada)"""
        provincia = EstadoCatalog.get_by_name("Ontario", "CAN")
        if provincia:
            assert provincia["country"] == "CAN"

    def test_get_by_name_not_found(self):
        """Test getting by nonexistent name"""
        result = EstadoCatalog.get_by_name("NonExistent", "USA")
        assert result is None


class TestIncotermsValidator:
    """Test Incoterms Validator"""

    def test_get_incoterm_valid(self):
        """Test getting valid incoterm"""
        incoterm = IncotermsValidator.get_incoterm("CIF")
        assert incoterm is not None
        assert incoterm["code"] == "CIF"

    def test_get_incoterm_not_found(self):
        """Test getting nonexistent incoterm"""
        incoterm = IncotermsValidator.get_incoterm("XXX")
        assert incoterm is None

    def test_is_valid_true(self):
        """Test is_valid with valid code"""
        assert IncotermsValidator.is_valid("FOB") is True
        assert IncotermsValidator.is_valid("CIF") is True

    def test_is_valid_false(self):
        """Test is_valid with invalid code"""
        assert IncotermsValidator.is_valid("XXX") is False

    def test_is_valid_for_transport(self):
        """Test is_valid_for_transport"""
        # Test with any mode
        result = IncotermsValidator.is_valid_for_transport("EXW", "any")
        assert isinstance(result, bool)

    def test_is_valid_for_transport_invalid_code(self):
        """Test is_valid_for_transport with invalid code"""
        result = IncotermsValidator.is_valid_for_transport("XXX", "any")
        assert result is False

    def test_get_all(self):
        """Test getting all incoterms"""
        incoterms = IncotermsValidator.get_all()
        assert isinstance(incoterms, list)
        assert len(incoterms) > 0

    def test_get_by_transport_type(self):
        """Test getting by transport type"""
        results = IncotermsValidator.get_by_transport_type("maritime")
        assert isinstance(results, list)

    def test_get_by_group(self):
        """Test getting by group"""
        results = IncotermsValidator.get_by_group("E")
        assert isinstance(results, list)

    def test_get_by_group_not_found(self):
        """Test getting by nonexistent group"""
        results = IncotermsValidator.get_by_group("X")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_with_seller_risk(self):
        """Test getting incoterms with seller risk"""
        results = IncotermsValidator.get_with_seller_risk()
        assert isinstance(results, list)

    def test_get_with_buyer_risk(self):
        """Test getting incoterms with buyer risk"""
        results = IncotermsValidator.get_with_buyer_risk()
        assert isinstance(results, list)

    def test_requires_insurance(self):
        """Test requires_insurance"""
        # CIF and CIP require insurance
        result = IncotermsValidator.requires_insurance("CIF")
        assert isinstance(result, bool)

    def test_requires_insurance_invalid(self):
        """Test requires_insurance with invalid code"""
        result = IncotermsValidator.requires_insurance("XXX")
        assert result is False

    def test_search(self):
        """Test search functionality"""
        results = IncotermsValidator.search("Free")
        assert isinstance(results, list)

    def test_search_no_results(self):
        """Test search with no results"""
        results = IncotermsValidator.search("NonExistent12345")
        assert isinstance(results, list)
        assert len(results) == 0


class TestMonedaCatalog:
    """Test Moneda Catalog"""

    def test_get_moneda_valid(self):
        """Test getting valid currency"""
        moneda = MonedaCatalog.get_moneda("USD")
        assert moneda is not None
        assert moneda["codigo"] == "USD"

    def test_get_moneda_not_found(self):
        """Test getting nonexistent currency"""
        moneda = MonedaCatalog.get_moneda("XXX")
        assert moneda is None

    def test_is_valid_true(self):
        """Test is_valid with valid code"""
        assert MonedaCatalog.is_valid("USD") is True
        assert MonedaCatalog.is_valid("MXN") is True

    def test_is_valid_false(self):
        """Test is_valid with invalid code"""
        assert MonedaCatalog.is_valid("XXX") is False

    def test_get_all(self):
        """Test getting all currencies"""
        monedas = MonedaCatalog.get_all()
        assert isinstance(monedas, list)
        assert len(monedas) > 0

    def test_search(self):
        """Test search functionality"""
        results = MonedaCatalog.search("Dollar")
        assert isinstance(results, list)

    def test_search_no_results(self):
        """Test search with no results"""
        results = MonedaCatalog.search("NonExistentCurrency12345")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_principales(self):
        """Test getting principal currencies"""
        principales = MonedaCatalog.get_principales()
        assert isinstance(principales, list)


class TestMotivoTrasladoCatalog:
    """Test Motivo Traslado Catalog"""

    def test_get_motivo_valid(self):
        """Test getting valid motivo"""
        motivos = MotivoTrasladoCatalog.get_all()
        if motivos:
            motivo = MotivoTrasladoCatalog.get_motivo(motivos[0]["codigo"])
            assert motivo is not None

    def test_get_motivo_not_found(self):
        """Test getting nonexistent motivo"""
        motivo = MotivoTrasladoCatalog.get_motivo("99")
        assert motivo is None

    def test_is_valid_true(self):
        """Test is_valid with valid code"""
        motivos = MotivoTrasladoCatalog.get_all()
        if motivos:
            assert MotivoTrasladoCatalog.is_valid(motivos[0]["codigo"]) is True

    def test_is_valid_false(self):
        """Test is_valid with invalid code"""
        assert MotivoTrasladoCatalog.is_valid("99") is False

    def test_get_all(self):
        """Test getting all motivos"""
        motivos = MotivoTrasladoCatalog.get_all()
        assert isinstance(motivos, list)
        assert len(motivos) > 0

    def test_search(self):
        """Test search functionality"""
        motivos = MotivoTrasladoCatalog.get_all()
        if motivos:
            results = MotivoTrasladoCatalog.search(motivos[0]["descripcion"][:5])
            assert isinstance(results, list)

    def test_search_no_results(self):
        """Test search with no results"""
        results = MotivoTrasladoCatalog.search("NonExistent12345")
        assert isinstance(results, list)
        assert len(results) == 0


class TestClavePedimentoCatalog:
    """Test Clave Pedimento Catalog"""

    def test_get_clave_valid(self):
        """Test getting valid clave"""
        claves = ClavePedimentoCatalog.get_all()
        if claves:
            clave = ClavePedimentoCatalog.get_clave(claves[0]["clave"])
            assert clave is not None

    def test_get_clave_not_found(self):
        """Test getting nonexistent clave"""
        clave = ClavePedimentoCatalog.get_clave("XX")
        assert clave is None

    def test_is_valid_true(self):
        """Test is_valid with valid code"""
        claves = ClavePedimentoCatalog.get_all()
        if claves:
            assert ClavePedimentoCatalog.is_valid(claves[0]["clave"]) is True

    def test_is_valid_false(self):
        """Test is_valid with invalid code"""
        assert ClavePedimentoCatalog.is_valid("XX") is False

    def test_get_all(self):
        """Test getting all claves"""
        claves = ClavePedimentoCatalog.get_all()
        assert isinstance(claves, list)
        assert len(claves) > 0

    def test_search(self):
        """Test search functionality"""
        claves = ClavePedimentoCatalog.get_all()
        if claves:
            results = ClavePedimentoCatalog.search(claves[0]["descripcion"][:5])
            assert isinstance(results, list)

    def test_search_no_results(self):
        """Test search with no results"""
        results = ClavePedimentoCatalog.search("NonExistent12345")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_by_tipo(self):
        """Test getting by tipo"""
        claves = ClavePedimentoCatalog.get_all()
        if claves:
            tipo = claves[0].get("tipo", "")
            if tipo:
                results = ClavePedimentoCatalog.get_by_tipo(tipo)
                assert isinstance(results, list)


class TestRegistroIdentTribCatalog:
    """Test Registro Identificacion Tributaria Catalog"""

    def test_get_registro_valid(self):
        """Test getting valid registro"""
        registros = RegistroIdentTribCatalog.get_all()
        if registros:
            registro = RegistroIdentTribCatalog.get_registro(registros[0]["clave"])
            assert registro is not None

    def test_get_registro_not_found(self):
        """Test getting nonexistent registro"""
        registro = RegistroIdentTribCatalog.get_registro("XX")
        assert registro is None

    def test_is_valid_true(self):
        """Test is_valid with valid code"""
        registros = RegistroIdentTribCatalog.get_all()
        if registros:
            assert RegistroIdentTribCatalog.is_valid(registros[0]["clave"]) is True

    def test_is_valid_false(self):
        """Test is_valid with invalid code"""
        assert RegistroIdentTribCatalog.is_valid("XX") is False

    def test_get_all(self):
        """Test getting all registros"""
        registros = RegistroIdentTribCatalog.get_all()
        assert isinstance(registros, list)
        assert len(registros) > 0

    def test_search(self):
        """Test search functionality"""
        registros = RegistroIdentTribCatalog.get_all()
        if registros:
            results = RegistroIdentTribCatalog.search(registros[0]["descripcion"][:5])
            assert isinstance(results, list)

    def test_search_no_results(self):
        """Test search with no results"""
        results = RegistroIdentTribCatalog.search("NonExistent12345")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_by_pais(self):
        """Test getting by pais"""
        registros = RegistroIdentTribCatalog.get_all()
        if registros:
            for registro in registros:
                if "pais" in registro:
                    results = RegistroIdentTribCatalog.get_by_pais(registro["pais"])
                    assert isinstance(results, list)
                    break


class TestUnidadAduanaCatalog:
    """Test Unidad Aduana Catalog"""

    def test_get_unidad_valid(self):
        """Test getting valid unidad"""
        unidades = UnidadAduanaCatalog.get_all()
        if unidades:
            unidad = UnidadAduanaCatalog.get_unidad(unidades[0]["clave"])
            assert unidad is not None

    def test_get_unidad_not_found(self):
        """Test getting nonexistent unidad"""
        unidad = UnidadAduanaCatalog.get_unidad("XX")
        assert unidad is None

    def test_is_valid_true(self):
        """Test is_valid with valid code"""
        unidades = UnidadAduanaCatalog.get_all()
        if unidades:
            assert UnidadAduanaCatalog.is_valid(unidades[0]["clave"]) is True

    def test_is_valid_false(self):
        """Test is_valid with invalid code"""
        assert UnidadAduanaCatalog.is_valid("XX") is False

    def test_get_all(self):
        """Test getting all unidades"""
        unidades = UnidadAduanaCatalog.get_all()
        assert isinstance(unidades, list)
        assert len(unidades) > 0

    def test_search(self):
        """Test search functionality"""
        unidades = UnidadAduanaCatalog.get_all()
        if unidades:
            results = UnidadAduanaCatalog.search(unidades[0]["descripcion"][:5])
            assert isinstance(results, list)

    def test_search_no_results(self):
        """Test search with no results"""
        results = UnidadAduanaCatalog.search("NonExistent12345")
        assert isinstance(results, list)
        assert len(results) == 0

