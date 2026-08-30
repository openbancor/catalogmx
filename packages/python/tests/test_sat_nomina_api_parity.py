"""Cross-catalog API coverage for all 13 SAT Nómina 1.2 catalogs."""

from catalogmx.catalogs.sat.nomina import (
    BancoCatalog,
    OrigenRecursoCatalog,
    PeriodicidadPagoCatalog,
    RiesgoPuestoCatalog,
    TipoContratoCatalog,
    TipoDeduccionCatalog,
    TipoHorasCatalog,
    TipoIncapacidadCatalog,
    TipoJornadaCatalog,
    TipoNominaCatalog,
    TipoOtroPagoCatalog,
    TipoPercepcionCatalog,
    TipoRegimenCatalog,
)


def test_all_thirteen_nomina_catalogs_load_and_lookup():
    samples = [
        (BancoCatalog, "002"),
        (OrigenRecursoCatalog, "IP"),
        (PeriodicidadPagoCatalog, "04"),
        (RiesgoPuestoCatalog, "99"),
        (TipoContratoCatalog, "10"),
        (TipoDeduccionCatalog, "115"),
        (TipoHorasCatalog, "01"),
        (TipoIncapacidadCatalog, "04"),
        (TipoJornadaCatalog, "08"),
        (TipoNominaCatalog, "O"),
        (TipoOtroPagoCatalog, "999"),
        (TipoPercepcionCatalog, "057"),
        (TipoRegimenCatalog, "13"),
    ]
    assert len(samples) == 13
    for catalog, code in samples:
        catalog.reload()
        assert catalog.get_all()
        assert catalog.is_valid(code)
        item = catalog.get_by_code(code)
        assert item is not None
        assert item["code"] == code
        assert item["clave"] == code


def test_aliases_and_regulatory_edges_are_consistent():
    contrato = TipoContratoCatalog.get_by_code("10")
    assert contrato is not None
    assert contrato["description"] == contrato["descripcion"]

    banco = BancoCatalog.get_banco("002")
    assert banco is not None
    assert banco["full_name"] == banco["razon_social"]
    assert BancoCatalog.get_by_name("Banamex")

    assert TipoJornadaCatalog.is_valid("08")
    assert RiesgoPuestoCatalog.is_valid("99")
    assert RiesgoPuestoCatalog.get_prima_media("99") is None
    assert RiesgoPuestoCatalog.validate_prima("99", 1.0) is False
    assert RiesgoPuestoCatalog.validate_prima("1", 0.55) is True
    assert TipoNominaCatalog.is_ordinaria("O") is True
    assert TipoNominaCatalog.is_ordinaria("E") is False
    assert TipoNominaCatalog.is_extraordinaria("E") is True
