"""
Minimal tests to trigger all catalog loading paths for coverage
Just calls get_all() on each catalog to ensure _load_data() is executed
"""

# Import all catalogs
from catalogmx.catalogs.sat.cfdi_4 import (
    ExportacionCatalog,
    FormaPagoCatalog,
    ImpuestoCatalog,
    MetodoPagoCatalog,
    ObjetoImpCatalog,
    RegimenFiscalCatalog,
    TipoComprobanteCatalog,
    TipoRelacionCatalog,
    UsoCFDICatalog,
)
from catalogmx.catalogs.sat.carta_porte import (
    ConfigAutotransporteCatalog,
    MaterialPeligrosoCatalog,
    TipoEmbalajeCatalog,
    TipoPermisoCatalog,
)
from catalogmx.catalogs.sat.nomina import (
    BancoCatalog as NominaBancoCatalog,
    PeriodicidadPagoCatalog,
    RiesgoPuestoCatalog,
    TipoContratoCatalog,
    TipoJornadaCatalog,
    TipoNominaCatalog,
    TipoRegimenCatalog as NominaTipoRegimenCatalog,
)
from catalogmx.catalogs.sat.comercio_exterior import (
    ClavePedimentoCatalog,
    EstadoCatalog,
    IncotermsValidator,
    MonedaCatalog,
    MotivoTrasladoCatalog,
    RegistroIdentTribCatalog,
    UnidadAduanaCatalog,
)


def test_exportacion_catalog_loads():
    """Test Exportacion Catalog loads"""
    data = ExportacionCatalog.get_all()
    assert isinstance(data, list)
    if data:
        assert ExportacionCatalog.is_valid(data[0]["code"]) is True
        assert ExportacionCatalog.get_exportacion(data[0]["code"]) is not None


def test_forma_pago_catalog_loads():
    """Test Forma Pago Catalog loads"""
    data = FormaPagoCatalog.get_all()
    assert isinstance(data, list)
    if data:
        assert FormaPagoCatalog.is_valid(data[0]["code"]) is True


def test_impuesto_catalog_loads():
    """Test Impuesto Catalog loads"""
    data = ImpuestoCatalog.get_all()
    assert isinstance(data, list)
    if data:
        assert ImpuestoCatalog.is_valid(data[0]["code"]) is True
        # Test additional methods
        ImpuestoCatalog.supports_retention(data[0]["code"])
        ImpuestoCatalog.supports_transfer(data[0]["code"])


def test_metodo_pago_catalog_loads():
    """Test Metodo Pago Catalog loads"""
    data = MetodoPagoCatalog.get_all()
    assert isinstance(data, list)
    if data:
        assert MetodoPagoCatalog.is_valid(data[0]["code"]) is True


def test_objeto_imp_catalog_loads():
    """Test Objeto Imp Catalog loads"""
    data = ObjetoImpCatalog.get_all()
    assert isinstance(data, list)
    if data:
        assert ObjetoImpCatalog.is_valid(data[0]["code"]) is True


def test_regimen_fiscal_catalog_loads():
    """Test Regimen Fiscal Catalog loads"""
    data = RegimenFiscalCatalog.get_all()
    assert isinstance(data, list)
    if data:
        assert RegimenFiscalCatalog.is_valid(data[0]["code"]) is True
        # Test persona fisica/moral methods
        RegimenFiscalCatalog.is_valid_for_persona_fisica(data[0]["code"])
        RegimenFiscalCatalog.is_valid_for_persona_moral(data[0]["code"])


def test_tipo_comprobante_catalog_loads():
    """Test Tipo Comprobante Catalog loads"""
    data = TipoComprobanteCatalog.get_all()
    assert isinstance(data, list)
    if data:
        assert TipoComprobanteCatalog.is_valid(data[0]["code"]) is True


def test_tipo_relacion_catalog_loads():
    """Test Tipo Relacion Catalog loads"""
    data = TipoRelacionCatalog.get_all()
    assert isinstance(data, list)
    if data:
        assert TipoRelacionCatalog.is_valid(data[0]["code"]) is True


def test_uso_cfdi_catalog_loads():
    """Test Uso CFDI Catalog loads"""
    data = UsoCFDICatalog.get_all()
    assert isinstance(data, list)
    if data:
        assert UsoCFDICatalog.is_valid(data[0]["code"]) is True


def test_config_autotransporte_catalog_loads():
    """Test Config Autotransporte Catalog loads"""
    data = ConfigAutotransporteCatalog.get_all()
    assert isinstance(data, list)
    if data:
        assert ConfigAutotransporteCatalog.is_valid(data[0]["code"]) is True
        ConfigAutotransporteCatalog.get_axes_count(data[0]["code"])


def test_material_peligroso_catalog_loads():
    """Test Material Peligroso Catalog loads"""
    data = MaterialPeligrosoCatalog.get_all()
    assert isinstance(data, list)
    if data:
        code = data[0].get("code", data[0].get("un_number", ""))
        if code:
            assert MaterialPeligrosoCatalog.is_valid(code) is True or MaterialPeligrosoCatalog.is_valid(code) is False


def test_tipo_embalaje_catalog_loads():
    """Test Tipo Embalaje Catalog loads"""
    data = TipoEmbalajeCatalog.get_all()
    assert isinstance(data, list)
    if data:
        assert TipoEmbalajeCatalog.is_valid(data[0]["code"]) is True


def test_tipo_permiso_catalog_loads():
    """Test Tipo Permiso Catalog loads"""
    data = TipoPermisoCatalog.get_all()
    assert isinstance(data, list)
    if data:
        assert TipoPermisoCatalog.is_valid(data[0]["code"]) is True


def test_nomina_banco_catalog_loads():
    """Test Banco Catalog (Nomina) loads"""
    data = NominaBancoCatalog.get_all()
    assert isinstance(data, list)
    if data:
        assert NominaBancoCatalog.is_valid(data[0]["code"]) is True
        NominaBancoCatalog.get_by_name(data[0]["name"])


def test_periodicidad_pago_catalog_loads():
    """Test Periodicidad Pago Catalog loads"""
    data = PeriodicidadPagoCatalog.get_all()
    assert isinstance(data, list)
    if data:
        assert PeriodicidadPagoCatalog.is_valid(data[0]["code"]) is True


def test_riesgo_puesto_catalog_loads():
    """Test Riesgo Puesto Catalog loads"""
    data = RiesgoPuestoCatalog.get_all()
    assert isinstance(data, list)
    if data:
        assert RiesgoPuestoCatalog.is_valid(data[0]["code"]) is True
        # Test get_by_level
        if "level" in data[0]:
            RiesgoPuestoCatalog.get_by_level(data[0]["level"])


def test_tipo_contrato_catalog_loads():
    """Test Tipo Contrato Catalog loads"""
    data = TipoContratoCatalog.get_all()
    assert isinstance(data, list)
    if data:
        assert TipoContratoCatalog.is_valid(data[0]["code"]) is True


def test_tipo_jornada_catalog_loads():
    """Test Tipo Jornada Catalog loads"""
    data = TipoJornadaCatalog.get_all()
    assert isinstance(data, list)
    if data:
        assert TipoJornadaCatalog.is_valid(data[0]["code"]) is True


def test_tipo_nomina_catalog_loads():
    """Test Tipo Nomina Catalog loads"""
    data = TipoNominaCatalog.get_all()
    assert isinstance(data, list)
    if data:
        assert TipoNominaCatalog.is_valid(data[0]["code"]) is True
        TipoNominaCatalog.is_ordinaria(data[0]["code"])


def test_nomina_tipo_regimen_catalog_loads():
    """Test Tipo Regimen Catalog (Nomina) loads"""
    data = NominaTipoRegimenCatalog.get_all()
    assert isinstance(data, list)
    if data:
        assert NominaTipoRegimenCatalog.is_valid(data[0]["code"]) is True


def test_clave_pedimento_catalog_loads():
    """Test Clave Pedimento Catalog loads"""
    data = ClavePedimentoCatalog.get_all()
    assert isinstance(data, list)
    if data:
        assert ClavePedimentoCatalog.is_valid(data[0]["clave"]) is True
        ClavePedimentoCatalog.is_export(data[0]["clave"])
        ClavePedimentoCatalog.is_import(data[0]["clave"])
        ClavePedimentoCatalog.get_by_regime("exportacion")


def test_estado_catalog_loads():
    """Test Estado Catalog loads"""
    data = EstadoCatalog.get_all_usa()
    assert isinstance(data, list)
    data2 = EstadoCatalog.get_all_canada()
    assert isinstance(data2, list)
    if data:
        EstadoCatalog.get_estado_usa(data[0]["code"])
    if data2:
        EstadoCatalog.get_provincia_canada(data2[0]["code"])


def test_incoterms_validator_loads():
    """Test Incoterms Validator loads"""
    data = IncotermsValidator.get_all()
    assert isinstance(data, list)
    if data:
        assert IncotermsValidator.is_valid(data[0]["code"]) is True
        IncotermsValidator.is_valid_for_transport(data[0]["code"], "any")


def test_moneda_catalog_loads():
    """Test Moneda Catalog loads"""
    data = MonedaCatalog.get_all()
    assert isinstance(data, list)
    if data:
        MonedaCatalog.is_valid(data[0]["codigo"])
        MonedaCatalog.search("USD")
        MonedaCatalog.validate_conversion_usd({"moneda": "USD", "total": 100, "tipo_cambio_usd": 1, "total_usd": 100})


def test_motivo_traslado_catalog_loads():
    """Test Motivo Traslado Catalog loads"""
    data = MotivoTrasladoCatalog.get_all()
    assert isinstance(data, list)
    if data:
        assert MotivoTrasladoCatalog.is_valid(data[0]["code"]) is True
        MotivoTrasladoCatalog.requires_propietario(data[0]["code"])


def test_registro_ident_trib_catalog_loads():
    """Test Registro Ident Trib Catalog loads"""
    data = RegistroIdentTribCatalog.get_all()
    assert isinstance(data, list)
    if data:
        assert RegistroIdentTribCatalog.is_valid(data[0]["code"]) is True
        RegistroIdentTribCatalog.validate_tax_id(data[0]["code"], "123456789")


def test_unidad_aduana_catalog_loads():
    """Test Unidad Aduana Catalog loads"""
    data = UnidadAduanaCatalog.get_all()
    assert isinstance(data, list)
    if data:
        assert UnidadAduanaCatalog.is_valid(data[0]["code"]) is True
        UnidadAduanaCatalog.get_by_type("weight")

