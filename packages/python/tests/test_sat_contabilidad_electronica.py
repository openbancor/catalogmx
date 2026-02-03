"""Tests for SAT electronic accounting catalogs (Anexo 24)."""

from catalogmx.catalogs.sat.contabilidad_electronica import CodigoAgrupadorSATCatalog


def test_codigo_agrupador_get_all_default():
    items = CodigoAgrupadorSATCatalog.get_all()
    assert len(items) > 1000


def test_codigo_agrupador_get_by_codigo():
    item = CodigoAgrupadorSATCatalog.get_by_codigo("100")
    assert item is not None
    assert item["nombre"].lower() == "activo"


def test_codigo_agrupador_is_valid():
    assert CodigoAgrupadorSATCatalog.is_valid("101.01") is True
    assert CodigoAgrupadorSATCatalog.is_valid("999.99") is False


def test_codigo_agrupador_versions():
    versions = CodigoAgrupadorSATCatalog.get_versions()
    assert "2024-01-22" in versions
    assert "2026-01-13" in versions
    assert CodigoAgrupadorSATCatalog.get_default_version() == "2026-01-13"


def test_codigo_agrupador_diff():
    diff = CodigoAgrupadorSATCatalog.get_diff_2024_2026()
    assert "added" in diff
    assert diff["_meta"]["counts"]["added"] > 0
