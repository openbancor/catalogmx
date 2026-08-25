import datetime

import pytest

import catalogmx.helpers as helpers
from catalogmx.catalogs.inegi.scian import SCIANCatalog
from catalogmx.catalogs.mexico.giros_mercantiles import GirosMercantilesCatalog
from catalogmx.catalogs.sat.cfdi_4.codigo_postal import CodigoPostalCatalog
from catalogmx.validators.curp import CURPGenerator, CURPGeneratorUtils
from catalogmx.validators.rfc import RFCGeneratorMorales, RFCGeneratorUtils, RFCValidator


def test_rfc_validator_defensive_regex_mismatches(monkeypatch):
    validator = RFCValidator("MANO610814JL5")

    monkeypatch.setattr(validator, "date_regex", r"NO_MATCH")
    assert validator.validate_date() is False

    monkeypatch.setattr(validator, "date_regex", RFCValidator.date_regex)
    monkeypatch.setattr(validator, "homoclave_regex", r"NO_MATCH")
    assert validator.validate_homoclave() is False

    validator = RFCValidator("MANO610814JO5")
    assert validator.validate_general_regex() is True
    assert validator.validate_homoclave() is False


def test_rfc_validator_type_detection_raises_for_invalid_rfc():
    validator = RFCValidator("INVALID")

    with pytest.raises(ValueError, match="Invalid RFC"):
        validator.is_fisica()

    with pytest.raises(ValueError, match="Invalid RFC"):
        validator.is_moral()


def test_rfc_number_text_conversion_edges():
    assert RFCGeneratorUtils._convert_arabigo_a_texto(-7) == "-7"
    assert RFCGeneratorUtils._convert_arabigo_a_texto(100000) == "CIEN MIL"
    assert RFCGeneratorUtils._convert_arabigo_a_texto(1234) == "MIL DOSCIENTOS TREINTA CUATRO"
    assert RFCGeneratorUtils._convert_arabigo_a_texto(45000) == "CUARENTA CINCO MIL"
    assert RFCGeneratorUtils.convertir_numero_a_texto("not-a-number") == "NOT-A-NUMBER"


def test_rfc_moral_cleaning_and_generation_edge_paths(monkeypatch):
    trailing_comma = RFCGeneratorMorales("Servicios,SA", datetime.date(2020, 1, 1))
    assert trailing_comma.razon_social_calculo == "SERVICIOS"

    initials = RFCGeneratorMorales("F.A.Z., S.A.", datetime.date(2020, 1, 1))
    assert initials.razon_social_calculo == "F A Z"

    accented = RFCGeneratorMorales("Café Ünico", datetime.date(2020, 1, 1))
    assert accented.razon_social_calculo == "CAFE UNICO"

    one_letter_second_word = RFCGeneratorMorales("Sol Z", datetime.date(2020, 1, 1))
    assert one_letter_second_word.generate_letters() == "SZX"

    monkeypatch.setattr(RFCGeneratorMorales, "cacophonic_words", ["BUE"])
    cacophonic = RFCGeneratorMorales("Bue", datetime.date(2020, 1, 1))
    assert cacophonic.generate_letters() == "BUX"

    spaces = RFCGeneratorMorales("La Casa", datetime.date(2020, 1, 1))
    assert spaces.cadena_homoclave.startswith("0")


def test_rfc_moral_generate_letters_empty_states(monkeypatch):
    generator = RFCGeneratorMorales("Empresa", datetime.date(2020, 1, 1))

    monkeypatch.setattr(RFCGeneratorMorales, "razon_social_calculo", property(lambda self: ""))
    with pytest.raises(ValueError, match="Company name is empty"):
        generator.generate_letters()

    monkeypatch.setattr(RFCGeneratorMorales, "razon_social_calculo", property(lambda self: "   "))
    with pytest.raises(ValueError, match="No valid words"):
        generator.generate_letters()


def test_helper_exception_paths(monkeypatch):
    class RaisingRFCValidator:
        def __init__(self, value):
            self.value = value

        def validate_general_regex(self):
            raise RuntimeError("boom")

        def detect_fisica_moral(self):
            raise RuntimeError("boom")

    class RaisingCLABEValidator:
        def __init__(self, value):
            self.value = value

        def is_valid(self):
            raise RuntimeError("boom")

    class RaisingNSSValidator:
        def __init__(self, value):
            self.value = value

        def is_valid(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(helpers, "RFCValidator", RaisingRFCValidator)
    assert helpers.validate_rfc("MANO610814JL5") is False
    assert helpers.detect_rfc_type("MANO610814JL5") is None

    monkeypatch.setattr(helpers, "CLABEValidator", RaisingCLABEValidator)
    assert helpers.validate_clabe("002010077777777771") is False
    assert helpers.get_clabe_info("002010077777777771") is None

    monkeypatch.setattr(helpers, "NSSValidator", RaisingNSSValidator)
    assert helpers.validate_nss("12345678903") is False
    assert helpers.get_nss_info("12345678903") is None


def test_helper_info_paths_and_project_root_failure(monkeypatch):
    assert helpers.validate_curp("INVALID") is False
    assert helpers.get_curp_info("INVALID") is None

    clabe_info = helpers.get_clabe_info("002010077777777771")
    assert clabe_info == {
        "bank_code": "002",
        "branch_code": "010",
        "account_number": "07777777777",
        "check_digit": "1",
        "is_valid": True,
    }

    nss_info = helpers.get_nss_info("12345678903")
    assert nss_info == {
        "subdelegation": "12",
        "registration_year": "34",
        "birth_year": "56",
        "sequential": "7890",
        "check_digit": "3",
        "is_valid": True,
    }

    class RootOnlyPath:
        def __init__(self, value):
            self.value = value

        @property
        def parent(self):
            return self

    monkeypatch.setattr(helpers, "Path", RootOnlyPath)
    with pytest.raises(FileNotFoundError):
        helpers.get_project_root()


def test_curp_generator_utility_edges():
    assert CURPGeneratorUtils.name_adapter(None, non_strict=True) == ""
    assert CURPGeneratorUtils.name_adapter(0, non_strict=True) == ""
    assert CURPGeneratorUtils.get_state_code("Michoacán") == "MN"
    assert CURPGeneratorUtils.get_state_code("zz") == "ZZ"
    assert CURPGenerator.calculate_check_digit("AAAAAAAAAAAAAAAA@") == "0"

    with pytest.raises(ValueError, match="exactamente 17"):
        CURPGenerator.calculate_check_digit("SHORT")


def test_curp_generator_mutated_empty_name_paths():
    generator = CURPGenerator(
        nombre="Juan",
        paterno="Perez",
        materno=None,
        fecha_nacimiento=datetime.date(1990, 5, 15),
        sexo="H",
        estado="Jalisco",
    )

    assert generator.curp == generator.curp

    generator._nombre = ""
    assert generator.nombre_iniciales == ""
    with pytest.raises(ValueError, match="Nombre cannot be empty"):
        generator.generate_letters()

    generator._nombre = "JUAN"
    generator._paterno = ""
    with pytest.raises(ValueError, match="Apellido paterno cannot be empty"):
        generator.generate_letters()


def test_scian_catalog_sector_lookups_and_empty_cache(monkeypatch):
    sectores = SCIANCatalog.get_all_sectores()
    assert len(sectores) > 0
    assert SCIANCatalog._load_data() is None

    first = sectores[0]
    assert SCIANCatalog.get_sector_by_codigo(first["codigo"]) == first
    assert SCIANCatalog.is_valid_sector(first["codigo"]) is True
    assert SCIANCatalog.is_valid_sector("00") is False
    assert SCIANCatalog.search(first["nombre_corto"])[0]["codigo"] == first["codigo"]
    assert SCIANCatalog.search("query-with-no-results") == []
    assert SCIANCatalog.get_sector_for_code("311811")["codigo"] == "31-33"
    assert SCIANCatalog.get_sector_for_code("481111")["codigo"] == "48-49"
    assert SCIANCatalog.get_sector_for_code(first["codigo"]) == first
    assert SCIANCatalog.get_sector_for_code("99") is None
    assert SCIANCatalog.count_sectores() == len(sectores)
    assert isinstance(SCIANCatalog.get_totales(), dict)

    monkeypatch.setattr(SCIANCatalog, "_sectores", [])
    monkeypatch.setattr(SCIANCatalog, "_by_codigo", {})
    assert SCIANCatalog.get_all_sectores() == []
    assert SCIANCatalog.get_sector_by_codigo(first["codigo"]) is None
    assert SCIANCatalog.search(first["nombre"]) == []
    assert SCIANCatalog.get_sector_for_code(first["codigo"]) is None
    assert SCIANCatalog.count_sectores() == 0


def test_giros_mercantiles_catalog_lookups_and_empty_cache(monkeypatch):
    giros = GirosMercantilesCatalog.get_all()
    categorias = GirosMercantilesCatalog.get_categorias()
    assert len(giros) > 0
    assert len(categorias) > 0
    assert GirosMercantilesCatalog._load_data() is None

    first = giros[0]
    assert GirosMercantilesCatalog.get_by_id(first["id"]) == first
    assert GirosMercantilesCatalog.is_valid(first["id"]) is True
    assert GirosMercantilesCatalog.is_valid("no-existe") is False
    assert first in GirosMercantilesCatalog.get_by_categoria(first["categoria"])
    assert GirosMercantilesCatalog.get_by_categoria("no-existe") == []
    assert isinstance(GirosMercantilesCatalog.get_requieren_licencia_alcohol(), list)
    assert GirosMercantilesCatalog.search(first["nombre"][:4])
    assert GirosMercantilesCatalog.search("query-with-no-results") == []
    assert GirosMercantilesCatalog.count() == len(giros)

    monkeypatch.setattr(GirosMercantilesCatalog, "_giros", [])
    monkeypatch.setattr(GirosMercantilesCatalog, "_categorias", [])
    monkeypatch.setattr(GirosMercantilesCatalog, "_by_id", {})
    monkeypatch.setattr(GirosMercantilesCatalog, "_by_categoria", {})
    assert GirosMercantilesCatalog.get_all() == []
    assert GirosMercantilesCatalog.get_by_id(first["id"]) is None
    assert GirosMercantilesCatalog.get_categorias() == []
    assert GirosMercantilesCatalog.get_by_categoria(first["categoria"]) == []
    assert GirosMercantilesCatalog.get_requieren_licencia_alcohol() == []
    assert GirosMercantilesCatalog.search(first["nombre"]) == []
    assert GirosMercantilesCatalog.count() == 0


def test_sat_codigo_postal_catalog_sqlite_paths():
    CodigoPostalCatalog.close()
    assert CodigoPostalCatalog.is_valid_format("01000") is True
    assert CodigoPostalCatalog.is_valid_format("0100A") is False
    assert CodigoPostalCatalog.is_valid("0100A") is False

    info = CodigoPostalCatalog.get_codigo_postal("01000")
    assert info is not None
    assert info["cp"] == "01000"
    assert info["estado"]
    assert info["municipio"]
    assert info["asentamientos"]

    assert CodigoPostalCatalog.get_codigo_postal("0100A") is None
    assert CodigoPostalCatalog.get_codigo_postal("99999") is None
    assert CodigoPostalCatalog.get_estado("01000") == info["estado"]
    assert CodigoPostalCatalog.get_municipio("01000") == info["municipio"]
    assert CodigoPostalCatalog.get_codigo_estado("01000") == info["codigo_estado"]
    assert CodigoPostalCatalog.get_estado("99999") is None
    assert CodigoPostalCatalog.get_municipio("99999") is None
    assert CodigoPostalCatalog.get_codigo_estado("99999") is None

    by_estado = CodigoPostalCatalog.get_by_estado(info["codigo_estado"], limit=3)
    assert 0 < len(by_estado) <= 3
    assert all(row["cp"] for row in by_estado)

    search_results = CodigoPostalCatalog.search(info["municipio"], limit=3)
    assert 0 < len(search_results) <= 3
    assert all("estado" in row for row in search_results)

    stats = CodigoPostalCatalog.get_estadisticas()
    assert stats["total_codigos_postales"] > 0
    assert stats["total_asentamientos"] >= stats["total_codigos_postales"]
    assert stats["total_estados"] > 0

    CodigoPostalCatalog.close()
    CodigoPostalCatalog.close()
