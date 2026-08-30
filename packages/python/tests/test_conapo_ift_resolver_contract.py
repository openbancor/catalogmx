"""Runtime resolver coverage for reviewed CONAPO and IFT snapshots."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from catalogmx.catalogs.conapo.sistema_urbano_nacional import (
    SistemaUrbanoNacionalCatalog,
)
from catalogmx.catalogs.conapo.zonas_metropolitanas import ZonasMetropolitanasCatalog
from catalogmx.catalogs.ift.codigos_lada import CodigosLADACatalog
from catalogmx.catalogs.ift.operadores_moviles import OperadoresMovilesCatalog

REPO_ROOT = Path(__file__).resolve().parents[3]
REGISTRY = REPO_ROOT / "packages" / "shared-data" / "catalog-registry.json"


def reset_catalogs() -> None:
    SistemaUrbanoNacionalCatalog._data = None
    SistemaUrbanoNacionalCatalog._by_clave = None
    ZonasMetropolitanasCatalog._data = None
    ZonasMetropolitanasCatalog._by_clave = None
    ZonasMetropolitanasCatalog._by_municipio = None
    ZonasMetropolitanasCatalog._metropolis = None
    CodigosLADACatalog._data = None
    CodigosLADACatalog._by_lada = None
    CodigosLADACatalog._by_municipio = None
    CodigosLADACatalog._by_entidad = None
    CodigosLADACatalog._zm_lookup = None
    OperadoresMovilesCatalog._data = None
    OperadoresMovilesCatalog._by_nombre = None


def test_registry_exposes_conapo_and_ift_runtime_artifacts():
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    datasets = {item["id"]: item for item in registry["datasets"]}

    conapo = datasets["conapo.territorial"]
    assert conapo["distribution"] == "mixed"
    assert conapo["source_subpath"] == "conapo"
    assert conapo["implementation"]["status"] == "resolver_ready"
    assert conapo["implementation"]["publish_from_reviewed_master"] is True
    assert conapo["artifact"] == {
        "version": "2020",
        "channel": "data-conapo-territorial-2020-latest",
        "file": "conapo_territorial.tar.gz",
        "manifest": "conapo_territorial.manifest.json",
        "format": "tar.gz",
        "mount_path": "conapo",
        "discovery": "release-pointer",
    }

    ift = datasets["ift.numbering"]
    assert ift["distribution"] == "mixed"
    assert ift["source_subpath"] == "ift"
    assert ift["freshness"]["upstream_checked_at"] == "2026-08-28"
    assert ift["implementation"]["status"] == "resolver_ready"
    assert ift["implementation"]["publish_from_reviewed_master"] is True
    assert ift["artifact"] == {
        "version": "1",
        "channel": "data-ift-numbering-1-latest",
        "file": "ift_numbering.tar.gz",
        "manifest": "ift_numbering.manifest.json",
        "format": "tar.gz",
        "mount_path": "ift",
        "discovery": "release-pointer",
    }

    assert "conapo.territorial" in registry["profiles"]["mexico-geo"]["datasets"]
    assert registry["profiles"]["mexico-telecom"]["datasets"] == ["ift.numbering"]


def test_conapo_and_ift_catalogs_honor_shared_data_override(
    tmp_path: Path, monkeypatch
):
    root = tmp_path / "shared-data"
    conapo = root / "conapo"
    ift = root / "ift"
    conapo.mkdir(parents=True)
    ift.mkdir(parents=True)

    (conapo / "sun_2020.csv").write_text(
        "cve_cd,nom_cd,pob_2020\n99.01,Ciudad Prueba,12345\n", encoding="utf-8"
    )
    metropolis_fields = [
        "clave_metropoli",
        "tipo",
        "nombre",
        "clave_entidad",
        "entidad",
        "clave_municipio",
        "clave_compuesta_municipio",
        "municipio",
        "centrales_conurbacion_fisica",
        "centrales_integracion_funcional",
        "centrales_capital_200khab",
        "centrales_0100khab",
        "centrales_50khab",
        "exteriores_integracion_funcional",
        "exteriores_continuidad_geografica",
        "entidad_etq",
    ]
    with (conapo / "municipios_tipologia.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=metropolis_fields)
        writer.writeheader()
        writer.writerow(
            {
                "clave_metropoli": "99.1.01",
                "tipo": "Zona metropolitana",
                "nombre": "Metrópoli Prueba",
                "clave_entidad": "99",
                "entidad": "Entidad Prueba",
                "clave_municipio": "1",
                "clave_compuesta_municipio": "99001",
                "municipio": "Municipio Prueba",
                "centrales_conurbacion_fisica": "True",
                "centrales_integracion_funcional": "False",
                "centrales_capital_200khab": "False",
                "centrales_0100khab": "False",
                "centrales_50khab": "False",
                "exteriores_integracion_funcional": "False",
                "exteriores_continuidad_geografica": "False",
                "entidad_etq": "Entidad Prueba",
            }
        )

    (ift / "codigos_lada.json").write_text(
        json.dumps(
            {
                "codigos": [
                    {
                        "lada": "999",
                        "ciudad": "Ciudad Prueba",
                        "estado": "Estado Prueba",
                        "tipo": "normal",
                        "region": "prueba",
                        "cve_entidad": "99",
                        "cve_municipio": "001",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    (ift / "operadores_moviles.json").write_text(
        json.dumps(
            {
                "operadores": [
                    {
                        "nombre_comercial": "Operador Prueba",
                        "razon_social": "Operador Prueba, S.A.",
                        "tipo": "OMV",
                        "grupo_empresarial": "Prueba",
                        "tecnologias": ["4G"],
                        "cobertura": "nacional",
                        "servicios": ["datos"],
                        "market_share_aprox": 0.0,
                        "fecha_inicio_operaciones": "2026-01-01",
                        "activo": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    # The bundle namespace includes this reviewed compatibility snapshot even
    # though current Python APIs do not expose it directly.
    (ift / "operadores_pnn.json").write_text("{}\n", encoding="utf-8")

    monkeypatch.setenv("CATALOGMX_SHARED_DATA", str(root))
    reset_catalogs()
    try:
        assert (
            SistemaUrbanoNacionalCatalog.get_por_clave("99.01")["nombre"]
            == "Ciudad Prueba"
        )
        assert (
            ZonasMetropolitanasCatalog.buscar_por_municipio("99", "1")[
                "nombre_metropoli"
            ]
            == "Metrópoli Prueba"
        )
        assert CodigosLADACatalog.buscar_por_lada("999")["ciudad"] == "Ciudad Prueba"
        assert (
            OperadoresMovilesCatalog.buscar_por_nombre("Operador Prueba")[
                "razon_social"
            ]
            == "Operador Prueba, S.A."
        )
    finally:
        reset_catalogs()
