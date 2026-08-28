"""Runtime tests for resolver-backed SAT Nómina public catalogs."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from catalogmx.catalogs.sat._sqlite import read_dataset_table
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

CATALOGS = (
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


def _create_nomina_database(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            "CREATE TABLE nomina_bancos ("
            "id TEXT PRIMARY KEY, texto TEXT NOT NULL, razon_social TEXT NOT NULL, "
            "vigencia_desde TEXT NOT NULL, vigencia_hasta TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT INTO nomina_bancos VALUES (?, ?, ?, ?, ?)",
            ("002", "BANAMEX", "Banco Nacional de México, S.A.", "2017-01-01", ""),
        )

        two_column_rows = {
            "nomina_origenes_recursos": [("IP", "Ingresos propios.")],
            "nomina_tipos_contratos": [("10", "Jubilación, pensión, retiro.")],
            "nomina_tipos_horas": [("01", "Dobles")],
            "nomina_tipos_incapacidades": [("04", "Licencia por cuidados médicos")],
            "nomina_tipos_jornadas": [("08", "Por hora")],
            "nomina_tipos_nominas": [
                ("E", "Nómina extraordinaria"),
                ("O", "Nómina ordinaria"),
            ],
        }
        for table, rows in two_column_rows.items():
            connection.execute(
                f'CREATE TABLE "{table}" (id TEXT PRIMARY KEY, texto TEXT NOT NULL)'
            )
            connection.executemany(f'INSERT INTO "{table}" VALUES (?, ?)', rows)

        four_column_rows = {
            "nomina_periodicidades_pagos": [("04", "Quincenal", "2016-11-01", "")],
            "nomina_riesgos_puestos": [
                ("1", "Clase I", "2017-01-01", ""),
                ("99", "No aplica", "2017-08-13", ""),
            ],
            "nomina_tipos_deducciones": [("115", "Deducción revision E", "2026-01-01", "")],
            "nomina_tipos_otros_pagos": [("999", "Pagos distintos", "2017-01-01", "")],
            "nomina_tipos_percepciones": [("057", "Percepción revision E", "2026-01-01", "")],
            "nomina_tipos_regimenes": [("13", "Indemnización o separación", "2017-01-01", "")],
        }
        for table, rows in four_column_rows.items():
            connection.execute(
                f'CREATE TABLE "{table}" ('
                "id TEXT PRIMARY KEY, texto TEXT NOT NULL, "
                "vigencia_desde TEXT NOT NULL, vigencia_hasta TEXT NOT NULL)"
            )
            connection.executemany(f'INSERT INTO "{table}" VALUES (?, ?, ?, ?)', rows)
        connection.commit()
    finally:
        connection.close()


@pytest.fixture
def nomina_shared_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    shared = tmp_path / "shared"
    database = shared / "sat" / "nomina_1.2" / "sat_nomina_12.sqlite3"
    _create_nomina_database(database)
    monkeypatch.setenv("CATALOGMX_SHARED_DATA", str(shared))
    for catalog in CATALOGS:
        catalog.reload()
    try:
        yield database
    finally:
        for catalog in CATALOGS:
            catalog.reload()


def test_all_thirteen_public_catalogs_use_resolver_sqlite(nomina_shared_data: Path) -> None:
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
    for catalog, code in samples:
        item = catalog.get_by_code(code)
        assert item is not None
        assert item["code"] == code
        assert item["clave"] == code

    banco = BancoCatalog.get_banco("002")
    assert banco is not None
    assert banco["name"] == "BANAMEX"
    assert banco["full_name"] == banco["razon_social"]

    assert PeriodicidadPagoCatalog.get_days("04") == 15
    assert RiesgoPuestoCatalog.get_prima_media("1") == 0.54355
    assert RiesgoPuestoCatalog.get_prima_media("99") is None
    assert RiesgoPuestoCatalog.validate_prima("1", 0.55) is True
    assert RiesgoPuestoCatalog.validate_prima("99", 1.0) is False
    assert TipoNominaCatalog.is_ordinaria("O") is True
    assert TipoNominaCatalog.is_extraordinaria("E") is True


def test_reader_uses_shared_mount_and_preserves_null_vigencia(
    nomina_shared_data: Path,
) -> None:
    rows = read_dataset_table(
        "sat.nomina_1_2", "sat_nomina_12.sqlite3", "nomina_periodicidades_pagos"
    )
    assert rows == [
        {
            "id": "04",
            "texto": "Quincenal",
            "vigencia_desde": "2016-11-01",
            "vigencia_hasta": "",
        }
    ]
    item = PeriodicidadPagoCatalog.get_by_code("04")
    assert item is not None
    assert item["valid_from"] == "2016-11-01"
    assert item["valid_to"] is None


def test_reader_fails_closed_for_missing_or_unsafe_table(
    nomina_shared_data: Path,
) -> None:
    with pytest.raises(RuntimeError, match="canonical SQLite table is missing"):
        read_dataset_table("sat.nomina_1_2", "sat_nomina_12.sqlite3", "missing_table")
    with pytest.raises(ValueError, match="unsafe SQLite identifier"):
        read_dataset_table(
            "sat.nomina_1_2", "sat_nomina_12.sqlite3", 'nomina_bancos; DROP TABLE x'
        )
