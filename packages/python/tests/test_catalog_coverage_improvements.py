"""Focused coverage tests for catalog public APIs."""

from pathlib import Path

import pytest

from catalogmx.catalogs.conapo.sistema_urbano_nacional import SistemaUrbanoNacionalCatalog
from catalogmx.catalogs.conapo.zonas_metropolitanas import ZonasMetropolitanasCatalog
from catalogmx.catalogs.ift.codigos_lada import CodigosLADACatalog
from catalogmx.catalogs.inegi.scian import SCIANCatalog
from catalogmx.catalogs.mexico.giros_mercantiles import GirosMercantilesCatalog
from catalogmx.catalogs.sat.cfdi_4.codigo_postal import CodigoPostalCatalog


@pytest.fixture(autouse=True)
def reset_catalog_connections():
    """Reset catalog caches changed by these tests."""
    CodigoPostalCatalog.close()
    CodigoPostalCatalog._db_path = None
    CodigosLADACatalog._data = None
    CodigosLADACatalog._by_lada = None
    CodigosLADACatalog._by_municipio = None
    CodigosLADACatalog._by_entidad = None
    CodigosLADACatalog._zm_lookup = None
    GirosMercantilesCatalog._data = None
    GirosMercantilesCatalog._giros = None
    GirosMercantilesCatalog._categorias = None
    GirosMercantilesCatalog._by_id = None
    GirosMercantilesCatalog._by_categoria = None
    SistemaUrbanoNacionalCatalog._data = None
    SistemaUrbanoNacionalCatalog._by_clave = None
    ZonasMetropolitanasCatalog._data = None
    ZonasMetropolitanasCatalog._by_clave = None
    ZonasMetropolitanasCatalog._by_municipio = None
    ZonasMetropolitanasCatalog._metropolis = None
    SCIANCatalog._data = None
    SCIANCatalog._sectores = None
    SCIANCatalog._by_codigo = None
    yield
    CodigoPostalCatalog.close()
    CodigoPostalCatalog._db_path = None
    CodigosLADACatalog._data = None
    CodigosLADACatalog._by_lada = None
    CodigosLADACatalog._by_municipio = None
    CodigosLADACatalog._by_entidad = None
    CodigosLADACatalog._zm_lookup = None
    GirosMercantilesCatalog._data = None
    GirosMercantilesCatalog._giros = None
    GirosMercantilesCatalog._categorias = None
    GirosMercantilesCatalog._by_id = None
    GirosMercantilesCatalog._by_categoria = None
    SistemaUrbanoNacionalCatalog._data = None
    SistemaUrbanoNacionalCatalog._by_clave = None
    ZonasMetropolitanasCatalog._data = None
    ZonasMetropolitanasCatalog._by_clave = None
    ZonasMetropolitanasCatalog._by_municipio = None
    ZonasMetropolitanasCatalog._metropolis = None
    SCIANCatalog._data = None
    SCIANCatalog._sectores = None
    SCIANCatalog._by_codigo = None


class TestCodigoPostalCatalogCoverage:
    """Exercise the SAT CFDI postal-code catalog."""

    def test_format_validation(self):
        assert CodigoPostalCatalog.is_valid_format("01000") is True
        assert CodigoPostalCatalog.is_valid_format("1000") is False
        assert CodigoPostalCatalog.is_valid_format("ABCDE") is False

    def test_lookup_valid_codigo_postal(self):
        info = CodigoPostalCatalog.get_codigo_postal("01000")

        assert info is not None
        assert info["cp"] == "01000"
        assert info["estado"] == "Ciudad de México"
        assert info["codigo_estado"] == "09"
        assert info["municipio"] == "Álvaro Obregón"
        assert info["codigo_municipio"] == "010"
        assert "San Ángel" in info["asentamientos"]

    def test_lookup_invalid_and_missing_codigo_postal(self):
        assert CodigoPostalCatalog.get_codigo_postal("invalid") is None
        assert CodigoPostalCatalog.get_codigo_postal("99999") is None
        assert CodigoPostalCatalog.is_valid("invalid") is False
        assert CodigoPostalCatalog.is_valid("99999") is False

    def test_convenience_getters(self):
        assert CodigoPostalCatalog.is_valid("01000") is True
        assert CodigoPostalCatalog.get_estado("01000") == "Ciudad de México"
        assert CodigoPostalCatalog.get_municipio("01000") == "Álvaro Obregón"
        assert CodigoPostalCatalog.get_codigo_estado("01000") == "09"
        assert CodigoPostalCatalog.get_estado("99999") is None
        assert CodigoPostalCatalog.get_municipio("99999") is None
        assert CodigoPostalCatalog.get_codigo_estado("99999") is None

    def test_get_by_estado_search_and_stats(self):
        by_estado = CodigoPostalCatalog.get_by_estado("09", limit=3)
        assert len(by_estado) == 3
        assert all(row["estado"] == "Ciudad de México" for row in by_estado)

        search_results = CodigoPostalCatalog.search("San Ángel", limit=5)
        assert any(row["cp"] == "01000" for row in search_results)

        stats = CodigoPostalCatalog.get_estadisticas()
        assert stats["total_codigos_postales"] > 0
        assert stats["total_asentamientos"] >= stats["total_codigos_postales"]
        assert stats["total_estados"] >= 32

    def test_close_resets_connection(self):
        first_connection = CodigoPostalCatalog._get_connection()
        CodigoPostalCatalog.close()

        assert CodigoPostalCatalog._connection is None
        assert CodigoPostalCatalog._get_connection() is not first_connection

    def test_missing_database_raises_file_not_found(self, tmp_path):
        CodigoPostalCatalog._db_path = tmp_path / "missing.db"

        with pytest.raises(FileNotFoundError):
            CodigoPostalCatalog._get_connection()


class TestSCIANCatalogCoverage:
    """Exercise SCIAN sector catalog behavior."""

    def test_get_all_and_count(self):
        sectores = SCIANCatalog.get_all_sectores()

        assert SCIANCatalog.count_sectores() == 20
        assert len(sectores) == 20
        assert sectores[0]["codigo"] == "11"
        assert sectores is not SCIANCatalog._sectores

    def test_get_sector_by_codigo_and_validation(self):
        sector = SCIANCatalog.get_sector_by_codigo("31-33")

        assert sector is not None
        assert sector["nombre_corto"] == "Manufactura"
        assert SCIANCatalog.is_valid_sector("31-33") is True
        assert SCIANCatalog.is_valid_sector("99") is False
        assert SCIANCatalog.get_sector_by_codigo("99") is None

    def test_search_matches_name_short_name_and_description(self):
        assert any(s["codigo"] == "21" for s in SCIANCatalog.search("minería"))
        assert any(s["codigo"] == "31-33" for s in SCIANCatalog.search("manufactura"))
        assert any(s["codigo"] == "22" for s in SCIANCatalog.search("energía"))
        assert SCIANCatalog.search("sin coincidencias") == []

    def test_get_sector_for_code_direct_range_and_missing(self):
        assert SCIANCatalog.get_sector_for_code("112511")["codigo"] == "11"
        assert SCIANCatalog.get_sector_for_code("311811")["codigo"] == "31-33"
        assert SCIANCatalog.get_sector_for_code("492110")["codigo"] == "48-49"
        assert SCIANCatalog.get_sector_for_code("99") is None
        assert SCIANCatalog.get_sector_for_code("1") is None

    def test_get_totales(self):
        totales = SCIANCatalog.get_totales()

        assert totales["sectores"] == 20
        assert totales["clases"] == 1057

    def test_empty_cache_branches(self, monkeypatch):
        monkeypatch.setattr(SCIANCatalog, "_data", {})
        monkeypatch.setattr(SCIANCatalog, "_sectores", [])
        monkeypatch.setattr(SCIANCatalog, "_by_codigo", {})

        assert SCIANCatalog.get_all_sectores() == []
        assert SCIANCatalog.search("manufactura") == []
        assert SCIANCatalog.get_sector_for_code("31") is None
        assert SCIANCatalog.get_totales() == {}
        assert SCIANCatalog.count_sectores() == 0

    def test_load_data_uses_expected_shared_data_file(self):
        SCIANCatalog._load_data()

        data_file = (
            Path(SCIANCatalog.__module__.replace(".", "/")).parent
            / "shared-data"
            / "inegi"
            / "scian"
            / "sectores.json"
        )
        assert SCIANCatalog._data is not None
        assert data_file.parts[-3:] == ("inegi", "scian", "sectores.json")


class TestCONAPOCatalogCoverage:
    """Exercise CONAPO catalog public methods."""

    def test_sistema_urbano_nacional_lookup(self):
        ciudades = SistemaUrbanoNacionalCatalog.get_all()
        ciudad = SistemaUrbanoNacionalCatalog.get_por_clave("9.01")

        assert len(ciudades) > 0
        assert ciudades is not SistemaUrbanoNacionalCatalog._data
        assert ciudad is not None
        assert ciudad["nombre"] == "Ciudad de México"
        assert ciudad["poblacion_2020"] > 20_000_000
        assert SistemaUrbanoNacionalCatalog.get_por_clave("00.00") is None

    def test_zonas_metropolitanas_methods(self):
        registros = ZonasMetropolitanasCatalog.get_all()
        metropolis = ZonasMetropolitanasCatalog.get_metropolis()

        assert len(registros) > 0
        assert len(metropolis) > 0
        assert registros is not ZonasMetropolitanasCatalog._data

        aguascalientes = ZonasMetropolitanasCatalog.buscar_por_municipio("1", "1")
        assert aguascalientes is not None
        assert aguascalientes["cve_inegi"] == "01001"
        assert ZonasMetropolitanasCatalog.es_municipio_metropolitano("01", "001") is True
        assert ZonasMetropolitanasCatalog.es_municipio_metropolitano("99", "999") is False

        por_tipo = ZonasMetropolitanasCatalog.get_por_tipo("Zona metropolitana")
        assert any(m["nombre"] == "Aguascalientes" for m in por_tipo)

        municipios = ZonasMetropolitanasCatalog.get_municipios_de_metropoli("01.1.01")
        assert any(m["municipio"] == "Aguascalientes" for m in municipios)
        assert ZonasMetropolitanasCatalog.get_municipios_de_metropoli("missing") == []

        busqueda = ZonasMetropolitanasCatalog.buscar_por_nombre("Tijuana")
        assert any(m["nombre"] == "Tijuana" for m in busqueda)

        stats = ZonasMetropolitanasCatalog.get_estadisticas()
        assert stats["total_metropolis"] > 0
        assert stats["total_municipios"] > 0

    def test_zonas_metropolitanas_empty_branches(self, monkeypatch):
        monkeypatch.setattr(ZonasMetropolitanasCatalog, "_data", [])
        monkeypatch.setattr(ZonasMetropolitanasCatalog, "_metropolis", {})
        monkeypatch.setattr(ZonasMetropolitanasCatalog, "_by_municipio", {})

        assert ZonasMetropolitanasCatalog.get_all() == []
        assert ZonasMetropolitanasCatalog.get_metropolis() == []
        assert ZonasMetropolitanasCatalog.get_por_tipo("Zona metropolitana") == []
        assert ZonasMetropolitanasCatalog.buscar_por_municipio("01", "001") is None
        assert ZonasMetropolitanasCatalog.get_municipios_de_metropoli("01.1.01") == []
        assert ZonasMetropolitanasCatalog.buscar_por_nombre("Tijuana") == []
        assert ZonasMetropolitanasCatalog.get_estadisticas() == {}


class TestGirosMercantilesCoverage:
    """Exercise giros mercantiles catalog public methods."""

    def test_giros_lookup_category_search_and_counts(self):
        giros = GirosMercantilesCatalog.get_all()
        categorias = GirosMercantilesCatalog.get_categorias()

        assert len(giros) > 0
        assert len(categorias) > 0
        assert giros is not GirosMercantilesCatalog._giros
        assert categorias is not GirosMercantilesCatalog._categorias

        giro = GirosMercantilesCatalog.get_by_id("abarrotes")
        assert giro is not None
        assert giro["categoria"] == "comercio"
        assert GirosMercantilesCatalog.is_valid("abarrotes") is True
        assert GirosMercantilesCatalog.is_valid("missing") is False

        comercio = GirosMercantilesCatalog.get_by_categoria("comercio")
        assert any(g["id"] == "abarrotes" for g in comercio)
        assert GirosMercantilesCatalog.get_by_categoria("missing") == []

        alcohol = GirosMercantilesCatalog.get_requieren_licencia_alcohol()
        assert any(g["requiere_licencia_alcohol"] for g in alcohol)

        assert any(g["id"] == "abarrotes" for g in GirosMercantilesCatalog.search("abarrotes"))
        assert GirosMercantilesCatalog.search("sin coincidencias") == []
        assert GirosMercantilesCatalog.count() == len(giros)

    def test_giros_empty_branches(self, monkeypatch):
        monkeypatch.setattr(GirosMercantilesCatalog, "_data", {})
        monkeypatch.setattr(GirosMercantilesCatalog, "_giros", [])
        monkeypatch.setattr(GirosMercantilesCatalog, "_categorias", [])
        monkeypatch.setattr(GirosMercantilesCatalog, "_by_id", {})
        monkeypatch.setattr(GirosMercantilesCatalog, "_by_categoria", {})

        assert GirosMercantilesCatalog.get_all() == []
        assert GirosMercantilesCatalog.get_by_id("abarrotes") is None
        assert GirosMercantilesCatalog.get_categorias() == []
        assert GirosMercantilesCatalog.get_by_categoria("comercio") == []
        assert GirosMercantilesCatalog.get_requieren_licencia_alcohol() == []
        assert GirosMercantilesCatalog.search("abarrotes") == []
        assert GirosMercantilesCatalog.count() == 0


class TestCodigosLADACoverage:
    """Exercise IFT LADA catalog public methods."""

    def test_basic_lada_queries(self):
        all_ladas = CodigosLADACatalog.get_all()

        assert len(all_ladas) > 0
        assert all_ladas is not CodigosLADACatalog._data
        assert CodigosLADACatalog.buscar_por_lada("55")["ciudad"] == "Ciudad de México"
        assert CodigosLADACatalog.buscar_por_lada("000") is None
        assert any(c["lada"] == "55" for c in CodigosLADACatalog.buscar_por_ciudad("México"))
        assert any(c["estado"] == "Jalisco" for c in CodigosLADACatalog.get_por_estado("Jalisco"))
        assert CodigosLADACatalog.get_por_cve_entidad("09")
        assert CodigosLADACatalog.get_por_municipio("21", "114")
        assert CodigosLADACatalog.get_por_tipo("metropolitana")
        assert CodigosLADACatalog.get_por_region("centro")

    def test_location_prefijos_and_metropolitan_zones(self):
        assert CodigosLADACatalog.get_prefijos_por_municipio("09", "010") == ["55", "56"]
        assert "33" in CodigosLADACatalog.get_prefijos_por_municipio("14", "039")
        assert CodigosLADACatalog.get_prefijos_por_municipio("01", "001")
        assert CodigosLADACatalog.get_prefijos_por_municipio("99", "999") == []

        assert CodigosLADACatalog.get_lada_for_location("09", "010")["lada"] == "55"
        assert CodigosLADACatalog.get_lada_for_location("21", "114")["lada"] == "222"
        assert CodigosLADACatalog.get_lada_for_location("01") is not None
        assert CodigosLADACatalog.get_lada_for_location("99", "999") is None

        municipios = CodigosLADACatalog.get_municipios_por_lada("56")
        assert ("09", None) in municipios
        assert CodigosLADACatalog.get_municipios_por_lada("449")
        assert CodigosLADACatalog.get_municipios_por_lada("000") == []

        zona = CodigosLADACatalog.get_zona_metropolitana("56")
        assert zona["lada_principal"] == "55"
        assert CodigosLADACatalog.get_zona_metropolitana("55")["lada_principal"] == "55"
        assert CodigosLADACatalog.get_zona_metropolitana("000") is None

    def test_phone_generation_validation_format_and_stats(self, monkeypatch):
        monkeypatch.setattr("catalogmx.catalogs.ift.codigos_lada.random.randint", lambda a, b: a)

        phone = CodigosLADACatalog.generar_telefono("09", "010")
        assert phone == "5510000000"
        assert CodigosLADACatalog.generar_telefono("99", "999") is None

        valid_2_digit = CodigosLADACatalog.validar_numero("55 1234 5678")
        assert valid_2_digit["valido"] is True
        assert valid_2_digit["lada"] == "55"

        valid_3_digit = CodigosLADACatalog.validar_numero("2221234567")
        assert valid_3_digit["valido"] is True
        assert valid_3_digit["lada"] == "222"

        invalid_length = CodigosLADACatalog.validar_numero("123")
        assert invalid_length["valido"] is False
        assert invalid_length["error"] == "Debe tener 10 dígitos"

        unknown_lada = CodigosLADACatalog.validar_numero("0001234567")
        assert unknown_lada["valido"] is False
        assert unknown_lada["error"] == "LADA no reconocida"

        assert CodigosLADACatalog.formatear_numero("5512345678") == "55 1234 5678"
        assert CodigosLADACatalog.formatear_numero("2221234567") == "222 123 4567"
        assert CodigosLADACatalog.formatear_numero("123") == "123"

        stats = CodigosLADACatalog.get_estadisticas()
        assert stats["total_codigos"] > 0
        assert stats["zonas_metropolitanas"] == len(CodigosLADACatalog.ZONAS_METROPOLITANAS)

    def test_empty_lada_branches(self, monkeypatch):
        monkeypatch.setattr(CodigosLADACatalog, "_data", [])
        monkeypatch.setattr(CodigosLADACatalog, "_by_lada", {})
        monkeypatch.setattr(CodigosLADACatalog, "_by_municipio", {})
        monkeypatch.setattr(CodigosLADACatalog, "_by_entidad", {})
        monkeypatch.setattr(CodigosLADACatalog, "_zm_lookup", {})

        assert CodigosLADACatalog.get_all() == []
        assert CodigosLADACatalog.buscar_por_lada("55") is None
        assert CodigosLADACatalog.buscar_por_ciudad("México") == []
        assert CodigosLADACatalog.get_por_estado("Jalisco") == []
        assert CodigosLADACatalog.get_por_cve_entidad("09") == []
        assert CodigosLADACatalog.get_por_municipio("09", "010") == []
        assert CodigosLADACatalog.get_por_tipo("metropolitana") == []
        assert CodigosLADACatalog.get_por_region("centro") == []
        assert CodigosLADACatalog.get_prefijos_por_municipio("09", "010") == []
        assert CodigosLADACatalog.get_lada_for_location("09", "010") is None
        assert CodigosLADACatalog.generar_telefono("09", "010") is None
        assert CodigosLADACatalog.get_estadisticas() == {}
