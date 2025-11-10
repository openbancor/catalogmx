"""
Tests for SAT Carta Porte catalogs
"""

from catalogmx.catalogs.sat.carta_porte import (
    AeropuertosCatalog,
    CarreterasCatalog,
    ConfigAutotransporteCatalog,
    MaterialPeligrosoCatalog,
    PuertosMaritimos,
    TipoEmbalajeCatalog,
    TipoPermisoCatalog,
)


class TestAeropuertosCatalog:
    """Test Aeropuertos Catalog"""

    def test_get_aeropuerto_valid(self):
        """Test getting valid aeropuerto"""
        aeropuertos = AeropuertosCatalog.get_all()
        if aeropuertos:
            aeropuerto = AeropuertosCatalog.get_aeropuerto(aeropuertos[0]["code"])
            assert aeropuerto is not None

    def test_get_aeropuerto_not_found(self):
        """Test getting nonexistent aeropuerto"""
        aeropuerto = AeropuertosCatalog.get_aeropuerto("XXX")
        assert aeropuerto is None

    def test_get_by_iata_valid(self):
        """Test getting by valid IATA code"""
        aeropuertos = AeropuertosCatalog.get_all()
        if aeropuertos:
            aeropuerto = AeropuertosCatalog.get_by_iata(aeropuertos[0]["iata"])
            assert aeropuerto is not None

    def test_get_by_iata_not_found(self):
        """Test getting by nonexistent IATA code"""
        aeropuerto = AeropuertosCatalog.get_by_iata("XXX")
        assert aeropuerto is None

    def test_get_by_icao_valid(self):
        """Test getting by valid ICAO code"""
        aeropuertos = AeropuertosCatalog.get_all()
        if aeropuertos:
            aeropuerto = AeropuertosCatalog.get_by_icao(aeropuertos[0]["icao"])
            assert aeropuerto is not None

    def test_get_by_icao_not_found(self):
        """Test getting by nonexistent ICAO code"""
        aeropuerto = AeropuertosCatalog.get_by_icao("XXXX")
        assert aeropuerto is None

    def test_is_valid_true(self):
        """Test is_valid with valid code"""
        aeropuertos = AeropuertosCatalog.get_all()
        if aeropuertos:
            assert AeropuertosCatalog.is_valid(aeropuertos[0]["code"]) is True

    def test_is_valid_false(self):
        """Test is_valid with invalid code"""
        assert AeropuertosCatalog.is_valid("XXX") is False

    def test_get_all(self):
        """Test getting all aeropuertos"""
        aeropuertos = AeropuertosCatalog.get_all()
        assert isinstance(aeropuertos, list)
        assert len(aeropuertos) > 0

    def test_get_by_state(self):
        """Test getting by state"""
        aeropuertos = AeropuertosCatalog.get_all()
        if aeropuertos:
            state = aeropuertos[0].get("estado", aeropuertos[0].get("state", ""))
            results = AeropuertosCatalog.get_by_state(state)
            assert isinstance(results, list)

    def test_get_by_state_not_found(self):
        """Test getting by nonexistent state"""
        results = AeropuertosCatalog.get_by_state("NonExistentState")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_search_by_name(self):
        """Test searching by name"""
        aeropuertos = AeropuertosCatalog.get_all()
        if aeropuertos:
            name = aeropuertos[0]["name"][:5]
            results = AeropuertosCatalog.search_by_name(name)
            assert isinstance(results, list)

    def test_search_by_name_not_found(self):
        """Test searching by nonexistent name"""
        results = AeropuertosCatalog.search_by_name("NonExistent12345")
        assert isinstance(results, list)
        assert len(results) == 0


class TestCarreterasCatalog:
    """Test Carreteras Catalog"""

    def test_get_carretera_valid(self):
        """Test getting valid carretera"""
        carreteras = CarreterasCatalog.get_all()
        if carreteras:
            carretera = CarreterasCatalog.get_carretera(carreteras[0]["code"])
            assert carretera is not None

    def test_get_carretera_not_found(self):
        """Test getting nonexistent carretera"""
        carretera = CarreterasCatalog.get_carretera("XXX")
        assert carretera is None

    def test_is_valid_true(self):
        """Test is_valid with valid code"""
        carreteras = CarreterasCatalog.get_all()
        if carreteras:
            assert CarreterasCatalog.is_valid(carreteras[0]["code"]) is True

    def test_is_valid_false(self):
        """Test is_valid with invalid code"""
        assert CarreterasCatalog.is_valid("XXX") is False

    def test_get_all(self):
        """Test getting all carreteras"""
        carreteras = CarreterasCatalog.get_all()
        assert isinstance(carreteras, list)
        assert len(carreteras) > 0

    def test_get_by_type(self):
        """Test getting by type"""
        carreteras = CarreterasCatalog.get_all()
        if carreteras:
            tipo = carreteras[0]["type"]
            results = CarreterasCatalog.get_by_type(tipo)
            assert isinstance(results, list)
            assert len(results) > 0

    def test_get_by_type_not_found(self):
        """Test getting by nonexistent type"""
        results = CarreterasCatalog.get_by_type("NonExistent")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_search_by_name(self):
        """Test searching by name"""
        carreteras = CarreterasCatalog.get_all()
        if carreteras:
            name = carreteras[0].get("nombre", carreteras[0].get("name", ""))[:5]
            results = CarreterasCatalog.search_by_name(name)
            assert isinstance(results, list)

    def test_search_by_name_not_found(self):
        """Test searching by nonexistent name"""
        results = CarreterasCatalog.search_by_name("NonExistent12345")
        assert isinstance(results, list)
        assert len(results) == 0


class TestPuertosMaritimos:
    """Test Puertos Maritimos Catalog"""

    def test_get_puerto_valid(self):
        """Test getting valid puerto"""
        puertos = PuertosMaritimos.get_all()
        if puertos:
            puerto = PuertosMaritimos.get_puerto(puertos[0]["code"])
            assert puerto is not None

    def test_get_puerto_not_found(self):
        """Test getting nonexistent puerto"""
        puerto = PuertosMaritimos.get_puerto("XXX")
        assert puerto is None

    def test_is_valid_true(self):
        """Test is_valid with valid code"""
        puertos = PuertosMaritimos.get_all()
        if puertos:
            assert PuertosMaritimos.is_valid(puertos[0]["code"]) is True

    def test_is_valid_false(self):
        """Test is_valid with invalid code"""
        assert PuertosMaritimos.is_valid("XXX") is False

    def test_get_all(self):
        """Test getting all puertos"""
        puertos = PuertosMaritimos.get_all()
        assert isinstance(puertos, list)
        assert len(puertos) > 0

    def test_get_by_coast(self):
        """Test getting by coast"""
        puertos = PuertosMaritimos.get_all()
        if puertos:
            coast = puertos[0]["coast"]
            results = PuertosMaritimos.get_by_coast(coast)
            assert isinstance(results, list)
            assert len(results) > 0

    def test_get_by_coast_not_found(self):
        """Test getting by nonexistent coast"""
        results = PuertosMaritimos.get_by_coast("NonExistent")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_by_state(self):
        """Test getting by state"""
        puertos = PuertosMaritimos.get_all()
        if puertos:
            state = puertos[0]["state"]
            results = PuertosMaritimos.get_by_state(state)
            assert isinstance(results, list)
            assert len(results) > 0

    def test_get_by_state_not_found(self):
        """Test getting by nonexistent state"""
        results = PuertosMaritimos.get_by_state("NonExistent")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_search_by_name(self):
        """Test searching by name"""
        puertos = PuertosMaritimos.get_all()
        if puertos:
            name = puertos[0]["name"][:5]
            results = PuertosMaritimos.search_by_name(name)
            assert isinstance(results, list)

    def test_search_by_name_not_found(self):
        """Test searching by nonexistent name"""
        results = PuertosMaritimos.search_by_name("NonExistent12345")
        assert isinstance(results, list)
        assert len(results) == 0


class TestConfigAutotransporteCatalog:
    """Test Config Autotransporte Catalog"""

    def test_get_config_valid(self):
        """Test getting valid config"""
        configs = ConfigAutotransporteCatalog.get_all()
        if configs:
            config = ConfigAutotransporteCatalog.get_config(configs[0]["code"])
            assert config is not None

    def test_get_config_not_found(self):
        """Test getting nonexistent config"""
        config = ConfigAutotransporteCatalog.get_config("XXX")
        assert config is None

    def test_is_valid_true(self):
        """Test is_valid with valid code"""
        configs = ConfigAutotransporteCatalog.get_all()
        if configs:
            assert ConfigAutotransporteCatalog.is_valid(configs[0]["code"]) is True

    def test_is_valid_false(self):
        """Test is_valid with invalid code"""
        assert ConfigAutotransporteCatalog.is_valid("XXX") is False

    def test_get_all(self):
        """Test getting all configs"""
        configs = ConfigAutotransporteCatalog.get_all()
        assert isinstance(configs, list)
        assert len(configs) > 0

    def test_search(self):
        """Test search functionality"""
        configs = ConfigAutotransporteCatalog.get_all()
        if configs:
            results = ConfigAutotransporteCatalog.search(configs[0]["description"][:5])
            assert isinstance(results, list)

    def test_search_not_found(self):
        """Test search with no results"""
        results = ConfigAutotransporteCatalog.search("NonExistent12345")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_by_tipo(self):
        """Test getting by tipo"""
        configs = ConfigAutotransporteCatalog.get_all()
        if configs:
            for config in configs:
                if "tipo" in config:
                    results = ConfigAutotransporteCatalog.get_by_tipo(config["tipo"])
                    assert isinstance(results, list)
                    break


class TestMaterialPeligrosoCatalog:
    """Test Material Peligroso Catalog"""

    def test_get_material_valid(self):
        """Test getting valid material"""
        materiales = MaterialPeligrosoCatalog.get_all()
        if materiales:
            material = MaterialPeligrosoCatalog.get_material(materiales[0]["code"])
            assert material is not None

    def test_get_material_not_found(self):
        """Test getting nonexistent material"""
        material = MaterialPeligrosoCatalog.get_material("XXXX")
        assert material is None

    def test_is_valid_true(self):
        """Test is_valid with valid code"""
        materiales = MaterialPeligrosoCatalog.get_all()
        if materiales:
            assert MaterialPeligrosoCatalog.is_valid(materiales[0]["code"]) is True

    def test_is_valid_false(self):
        """Test is_valid with invalid code"""
        assert MaterialPeligrosoCatalog.is_valid("XXXX") is False

    def test_get_all(self):
        """Test getting all materiales"""
        materiales = MaterialPeligrosoCatalog.get_all()
        assert isinstance(materiales, list)
        assert len(materiales) > 0

    def test_search(self):
        """Test search functionality"""
        materiales = MaterialPeligrosoCatalog.get_all()
        if materiales:
            results = MaterialPeligrosoCatalog.search(materiales[0]["description"][:5])
            assert isinstance(results, list)

    def test_search_not_found(self):
        """Test search with no results"""
        results = MaterialPeligrosoCatalog.search("NonExistent12345")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_by_clase(self):
        """Test getting by clase"""
        materiales = MaterialPeligrosoCatalog.get_all()
        if materiales:
            for material in materiales:
                if "clase" in material:
                    results = MaterialPeligrosoCatalog.get_by_clase(material["clase"])
                    assert isinstance(results, list)
                    break


class TestTipoEmbalajeCatalog:
    """Test Tipo Embalaje Catalog"""

    def test_get_tipo_valid(self):
        """Test getting valid tipo"""
        tipos = TipoEmbalajeCatalog.get_all()
        if tipos:
            tipo = TipoEmbalajeCatalog.get_tipo(tipos[0]["code"])
            assert tipo is not None

    def test_get_tipo_not_found(self):
        """Test getting nonexistent tipo"""
        tipo = TipoEmbalajeCatalog.get_tipo("XXX")
        assert tipo is None

    def test_is_valid_true(self):
        """Test is_valid with valid code"""
        tipos = TipoEmbalajeCatalog.get_all()
        if tipos:
            assert TipoEmbalajeCatalog.is_valid(tipos[0]["code"]) is True

    def test_is_valid_false(self):
        """Test is_valid with invalid code"""
        assert TipoEmbalajeCatalog.is_valid("XXX") is False

    def test_get_all(self):
        """Test getting all tipos"""
        tipos = TipoEmbalajeCatalog.get_all()
        assert isinstance(tipos, list)
        assert len(tipos) > 0

    def test_search(self):
        """Test search functionality"""
        tipos = TipoEmbalajeCatalog.get_all()
        if tipos:
            results = TipoEmbalajeCatalog.search(tipos[0]["description"][:5])
            assert isinstance(results, list)

    def test_search_not_found(self):
        """Test search with no results"""
        results = TipoEmbalajeCatalog.search("NonExistent12345")
        assert isinstance(results, list)
        assert len(results) == 0


class TestTipoPermisoCatalog:
    """Test Tipo Permiso Catalog"""

    def test_get_tipo_valid(self):
        """Test getting valid tipo"""
        tipos = TipoPermisoCatalog.get_all()
        if tipos:
            tipo = TipoPermisoCatalog.get_tipo(tipos[0]["code"])
            assert tipo is not None

    def test_get_tipo_not_found(self):
        """Test getting nonexistent tipo"""
        tipo = TipoPermisoCatalog.get_tipo("XXX")
        assert tipo is None

    def test_is_valid_true(self):
        """Test is_valid with valid code"""
        tipos = TipoPermisoCatalog.get_all()
        if tipos:
            assert TipoPermisoCatalog.is_valid(tipos[0]["code"]) is True

    def test_is_valid_false(self):
        """Test is_valid with invalid code"""
        assert TipoPermisoCatalog.is_valid("XXX") is False

    def test_get_all(self):
        """Test getting all tipos"""
        tipos = TipoPermisoCatalog.get_all()
        assert isinstance(tipos, list)
        assert len(tipos) > 0

    def test_search(self):
        """Test search functionality"""
        tipos = TipoPermisoCatalog.get_all()
        if tipos:
            results = TipoPermisoCatalog.search(tipos[0]["description"][:5])
            assert isinstance(results, list)

    def test_search_not_found(self):
        """Test search with no results"""
        results = TipoPermisoCatalog.search("NonExistent12345")
        assert isinstance(results, list)
        assert len(results) == 0

    def test_get_by_transporte(self):
        """Test getting by transporte"""
        tipos = TipoPermisoCatalog.get_all()
        if tipos:
            for tipo in tipos:
                if "transporte" in tipo:
                    results = TipoPermisoCatalog.get_by_transporte(tipo["transporte"])
                    assert isinstance(results, list)
                    break

