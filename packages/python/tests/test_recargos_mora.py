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


def test_records_separate_lif_base_mora_rate_and_official_source():
    expected = {
        2024: (
            "0.0098",
            "https://sidof.segob.gob.mx/notas/docFuente/5708368",
        ),
        2025: (
            "0.0098",
            "https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/documentos2025/rmf/rmf/RMF_2025-30122024.pdf",
        ),
        2026: (
            "0.0138",
            "https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/documentos2026/rmf/rmf/RMF_2026-DOF-28122025.pdf",
        ),
    }

    for anio, (tasa_base_lif, url_fuente) in expected.items():
        record = RecargosMoraCatalog.get_por_anio(anio)

        assert record is not None
        assert record["tasa_base_lif"] == tasa_base_lif
        assert record["fuente_normativa"]
        assert record["url_fuente"] == url_fuente
        assert "tasa_parcialidades" not in record
        assert "no es la tasa de pagos a plazos" in record["nota"]


def test_unknown_year_returns_none():
    assert RecargosMoraCatalog.get_por_anio(1900) is None
    assert RecargosMoraCatalog.get_tasa_mensual(1900) is None


def test_get_data_returns_defensive_records():
    records = RecargosMoraCatalog.get_data()
    records[0]["tasa_mora_mensual"] = "0"

    assert RecargosMoraCatalog.get_tasa_mensual(2024) == Decimal("0.0147")


def test_uses_configured_shared_data_root(monkeypatch, tmp_path):
    shared_data = tmp_path / "mexico"
    shared_data.mkdir()
    (shared_data / "recargos_mora.json").write_text(
        '[{"ejercicio": 2099, "tasa_mora_mensual": "0.1234"}]',
        encoding="utf-8",
    )
    monkeypatch.setenv("CATALOGMX_SHARED_DATA", str(tmp_path))
    monkeypatch.setattr(RecargosMoraCatalog, "_data", None)

    assert RecargosMoraCatalog.get_tasa_mensual(2099) == Decimal("0.1234")
