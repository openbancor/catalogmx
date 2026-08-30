"""Runtime coverage for resolver-backed Python CFDI 4.0 catalog APIs."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from catalogmx.catalogs.sat.cfdi_4 import (
    ClaveUnidadCatalog,
    EstadoCfdiCatalog,
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
from catalogmx.catalogs.sat.cfdi_4.meses import Meses
from catalogmx.catalogs.sat.cfdi_4.periodicidad import Periodicidad
from catalogmx.catalogs.sat.cfdi_4.tasa_o_cuota import TasaOCuota
from catalogmx.catalogs.sat.cfdi_4.tipo_factor import TipoFactor

MIGRATED_MODULES = (
    "clave_unidad.py",
    "exportacion.py",
    "forma_pago.py",
    "impuesto.py",
    "meses.py",
    "metodo_pago.py",
    "objeto_imp.py",
    "periodicidad.py",
    "regimen_fiscal.py",
    "tasa_o_cuota.py",
    "tipo_comprobante.py",
    "tipo_factor.py",
    "tipo_relacion.py",
    "uso_cfdi.py",
)


def _create_cfdi_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        simple = {
            "cfdi_40_exportaciones": [("01", "No aplica")],
            "cfdi_40_estados": [("CMX", "Ciudad de México")],
            "cfdi_40_formas_pago": [("01", "Efectivo")],
            "cfdi_40_metodos_pago": [("PUE", "Pago en una sola exhibición")],
            "cfdi_40_objetos_impuestos": [("01", "No objeto de impuesto.")],
            "cfdi_40_tipos_relaciones": [
                ("01", "Nota de crédito de los documentos relacionados")
            ],
            "cfdi_40_tipos_comprobantes": [("I", "Ingreso")],
            "cfdi_40_meses": [("01", "Enero")],
            "cfdi_40_periodicidades": [("01", "Diario")],
        }
        for table, rows in simple.items():
            connection.execute(
                f'CREATE TABLE "{table}" (id TEXT PRIMARY KEY, texto TEXT NOT NULL)'
            )
            connection.executemany(f'INSERT INTO "{table}" VALUES (?, ?)', rows)

        connection.execute("CREATE TABLE cfdi_40_tipos_factores (id TEXT PRIMARY KEY)")
        connection.execute("INSERT INTO cfdi_40_tipos_factores VALUES ('Tasa')")

        connection.execute(
            "CREATE TABLE cfdi_40_impuestos ("
            "id TEXT PRIMARY KEY, texto TEXT NOT NULL, "
            "retencion INTEGER, traslado INTEGER)"
        )
        connection.executemany(
            "INSERT INTO cfdi_40_impuestos VALUES (?, ?, ?, ?)",
            [
                ("001", "ISR", 1, 0),
                ("002", "IVA", 1, 1),
            ],
        )

        connection.execute(
            "CREATE TABLE cfdi_40_regimenes_fiscales ("
            "id TEXT PRIMARY KEY, texto TEXT NOT NULL, "
            "aplica_fisica INTEGER, aplica_moral INTEGER)"
        )
        connection.executemany(
            "INSERT INTO cfdi_40_regimenes_fiscales VALUES (?, ?, ?, ?)",
            [
                ("601", "General de Ley Personas Morales", 0, 1),
                ("605", "Sueldos y Salarios e Ingresos Asimilados a Salarios", 1, 0),
            ],
        )

        connection.execute(
            "CREATE TABLE cfdi_40_usos_cfdi ("
            "id TEXT PRIMARY KEY, texto TEXT NOT NULL, "
            "aplica_fisica INTEGER, aplica_moral INTEGER)"
        )
        connection.executemany(
            "INSERT INTO cfdi_40_usos_cfdi VALUES (?, ?, ?, ?)",
            [
                ("G01", "Adquisición de mercancías.", 1, 1),
                ("D01", "Honorarios médicos, dentales y gastos hospitalarios.", 1, 0),
            ],
        )

        connection.execute(
            "CREATE TABLE cfdi_40_claves_unidades ("
            "id TEXT PRIMARY KEY, texto TEXT NOT NULL, descripcion TEXT, notas TEXT, "
            "vigencia_desde TEXT, vigencia_hasta TEXT, simbolo TEXT)"
        )
        connection.executemany(
            "INSERT INTO cfdi_40_claves_unidades VALUES (?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    "KGM",
                    "Kilogramo",
                    "",
                    "Unidad de masa",
                    "2022-01-01",
                    "",
                    "kg",
                ),
                (
                    "OLD",
                    "Unidad obsoleta",
                    "",
                    "",
                    "2022-01-01",
                    "2025-12-31",
                    "",
                ),
            ],
        )

        connection.execute(
            "CREATE TABLE cfdi_40_reglas_tasa_cuota ("
            "tipo TEXT NOT NULL, minimo TEXT, valor TEXT, impuesto TEXT NOT NULL, "
            "factor TEXT NOT NULL, traslado INTEGER, retencion INTEGER, "
            "vigencia_desde TEXT, vigencia_hasta TEXT)"
        )
        connection.executemany(
            "INSERT INTO cfdi_40_reglas_tasa_cuota VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            [
                ("Fijo", "", "0.160000", "IVA", "Tasa", 1, 0, "2022-01-01", ""),
                (
                    "Rango",
                    "0.000000",
                    "0.160000",
                    "IVA",
                    "Tasa",
                    0,
                    1,
                    "2022-01-01",
                    "",
                ),
            ],
        )
        connection.commit()
    finally:
        connection.close()


def _reset_caches() -> None:
    for catalog in (
        ExportacionCatalog,
        EstadoCfdiCatalog,
        FormaPagoCatalog,
        ImpuestoCatalog,
        MetodoPagoCatalog,
        ObjetoImpCatalog,
        RegimenFiscalCatalog,
        TipoComprobanteCatalog,
        TipoRelacionCatalog,
        UsoCFDICatalog,
    ):
        catalog._data = None
        catalog._by_code = None
    ClaveUnidadCatalog._data = None
    ClaveUnidadCatalog._by_id = None
    Meses._data = None
    Periodicidad._data = None
    TasaOCuota._data = None
    TipoFactor._data = None


@pytest.fixture
def cfdi_shared_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    shared = tmp_path / "shared"
    database = shared / "sat" / "cfdi_4.0" / "sat_cfdi_40.sqlite3"
    _create_cfdi_database(database)
    monkeypatch.setenv("CATALOGMX_SHARED_DATA", str(shared))
    _reset_caches()
    try:
        yield database
    finally:
        _reset_caches()


def test_simple_code_description_catalogs_preserve_public_shape(
    cfdi_shared_data: Path,
) -> None:
    cases = [
        (ExportacionCatalog.get_exportacion, "01", "No aplica"),
        (FormaPagoCatalog.get_forma_pago, "01", "Efectivo"),
        (MetodoPagoCatalog.get_metodo, "pue", "Pago en una sola exhibición"),
        (ObjetoImpCatalog.get_objeto, "01", "No objeto de impuesto"),
        (
            TipoRelacionCatalog.get_tipo,
            "01",
            "Nota de crédito de los documentos relacionados",
        ),
        (TipoComprobanteCatalog.get_tipo, "i", "Ingreso"),
    ]
    for getter, code, description in cases:
        item = getter(code)
        assert item == {
            "code": code.upper() if code.isalpha() else code,
            "description": description,
        }

    assert EstadoCfdiCatalog.get_estado("cmx") == {"code": "CMX"}
    assert EstadoCfdiCatalog.get_estado("DIF") == {"code": "DIF"}
    assert len(EstadoCfdiCatalog.get_all()) == 96


def test_boolean_and_catalogmx_enriched_projections_match_legacy_api(
    cfdi_shared_data: Path,
) -> None:
    isr = ImpuestoCatalog.get_impuesto("001")
    assert isr == {
        "code": "001",
        "description": "ISR",
        "name": "Impuesto Sobre la Renta",
        "retention": True,
        "transfer": False,
    }
    assert ImpuestoCatalog.supports_retention("001") is True
    assert ImpuestoCatalog.supports_transfer("001") is False
    assert ImpuestoCatalog.supports_transfer("002") is True

    moral = RegimenFiscalCatalog.get_regimen("601")
    assert moral == {
        "code": "601",
        "description": "General de Ley Personas Morales",
        "fisica": False,
        "moral": True,
    }
    assert RegimenFiscalCatalog.is_valid_for_persona_fisica("601") is False
    assert RegimenFiscalCatalog.is_valid_for_persona_moral("601") is True
    assert RegimenFiscalCatalog.is_valid_for_persona_fisica("605") is True

    both = UsoCFDICatalog.get_uso("g01")
    assert both == {
        "code": "G01",
        "description": "Adquisición de mercancías",
        "fisica": True,
        "moral": True,
        "applies_to": "both",
    }
    fisica = UsoCFDICatalog.get_uso("D01")
    assert fisica is not None
    assert fisica["applies_to"] == "fisica"
    assert fisica["description"].endswith("hospitalarios")


def test_value_catalogs_preserve_historical_valor_shape(cfdi_shared_data: Path) -> None:
    assert Meses.get_by_id("01") == {"valor": "01"}
    assert Periodicidad.get_by_id("01") == {"valor": "01"}
    assert TipoFactor.get_by_id("Tasa") == {"valor": "Tasa"}
    assert Meses.is_valid("01") is True
    assert Periodicidad.is_valid("99") is False
    assert TipoFactor.is_valid("Tasa") is True


def test_tasa_o_cuota_uses_normalized_canonical_rules(cfdi_shared_data: Path) -> None:
    data = TasaOCuota.get_data()
    assert data[0]["valor_mínimo"] is None
    assert data[0]["valor_máximo"] == "0.160000"

    fixed = TasaOCuota.get_by_range_and_tax(None, 0.16, "002", "tasa", True, False)
    assert len(fixed) == 1
    assert fixed[0]["tipo"] == "Fijo"

    retained_range = TasaOCuota.get_by_range_and_tax(
        0, "0.160000", "IVA", "Tasa", False, True
    )
    assert len(retained_range) == 1
    assert retained_range[0]["tipo"] == "Rango"


def test_clave_unidad_preserves_keys_and_date_format_while_using_canonical_values(
    cfdi_shared_data: Path,
) -> None:
    kilogramo = ClaveUnidadCatalog.get_unidad("KGM")
    assert kilogramo == {
        "id": "KGM",
        "nombre": "Kilogramo",
        "descripcion": "",
        "nota": "Unidad de masa",
        "fechaDeInicioDeVigencia": "01-01-2022",
        "fechaDeFinDeVigencia": "",
        "simbolo": "kg",
    }
    assert ClaveUnidadCatalog.is_valid("KGM") is True
    assert ClaveUnidadCatalog.search_by_symbol("KG") == [kilogramo]
    assert kilogramo in ClaveUnidadCatalog.get_vigentes()

    obsoleta = ClaveUnidadCatalog.get_unidad("OLD")
    assert obsoleta is not None
    assert obsoleta["fechaDeFinDeVigencia"] == "31-12-2025"
    assert obsoleta in ClaveUnidadCatalog.get_obsoletas()


def test_migrated_modules_have_no_runtime_json_fallback() -> None:
    root = (
        Path(__file__).resolve().parents[1]
        / "catalogmx"
        / "catalogs"
        / "sat"
        / "cfdi_4"
    )
    for filename in MIGRATED_MODULES:
        source = (root / filename).read_text(encoding="utf-8")
        assert "get_shared_data_path" not in source, filename
        assert "json.load" not in source, filename
