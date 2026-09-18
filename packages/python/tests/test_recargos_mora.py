from decimal import Decimal

from catalogmx.catalogs.mexico.recargos_mora import RecargosMoraCatalog


def test_exposes_effective_mora_rate_for_supported_fiscal_years():
    assert RecargosMoraCatalog.get_tasa_mensual(2024) == Decimal("0.0147")
    assert RecargosMoraCatalog.get_tasa_mensual(2025) == Decimal("0.0147")
    assert RecargosMoraCatalog.get_tasa_mensual(2026) == Decimal("0.0207")


def test_records_include_vigency_and_normative_provenance():
    record = RecargosMoraCatalog.get_por_anio(2026)

    assert record is not None
    assert record["vigencia_inicio"] == "2026-01-01"
    assert record["vigencia_fin"] == "2026-12-31"
    assert record["tasa_base_lif"] == "0.0138"
    assert record["fuente_normativa"]
    assert record["url_fuente"].startswith("https://")


def test_unknown_year_returns_none():
    assert RecargosMoraCatalog.get_por_anio(1900) is None
    assert RecargosMoraCatalog.get_tasa_mensual(1900) is None


def test_get_data_returns_defensive_records():
    records = RecargosMoraCatalog.get_data()
    records[0]["tasa_mora_mensual"] = "0"

    assert RecargosMoraCatalog.get_tasa_mensual(2024) == Decimal("0.0147")
