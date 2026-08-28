"""Runtime-contract coverage for SAT and Mexico geographic release datasets."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from catalogmx.data.resolver import DatasetResolver

REPO_ROOT = Path(__file__).resolve().parents[3]
CONTRACT_PATH = REPO_ROOT / "packages" / "python" / "catalogmx" / "data" / "dataset_contract.json"

EXPECTED_ARTIFACTS = {
    "inegi.ageeml": {
        "version": "1",
        "channel": "data-inegi-ageeml-1-latest",
        "file": "inegi_ageeml.sqlite3",
        "manifest": "inegi_ageeml.manifest.json",
        "mount_path": "inegi/ageeml",
        "builder": "scripts/inegi/build_ageeml.py",
    },
    "sat.carta_porte": {
        "version": "3.1",
        "channel": "data-sat-carta-porte-3-1-latest",
        "file": "sat_carta_porte_31.sqlite3",
        "manifest": "sat_carta_porte_31.manifest.json",
        "mount_path": "sat/carta_porte_3.1",
        "builder": "scripts/sat/build_carta_porte_31.py",
    },
    "sat.cfdi_4": {
        "version": "4.0",
        "channel": "data-sat-cfdi-4-4-0-latest",
        "file": "sat_cfdi_40.sqlite3",
        "manifest": "sat_cfdi_40.manifest.json",
        "mount_path": "sat/cfdi_4.0",
        "builder": "scripts/sat/build_cfdi_40.py",
    },
    "sat.comercio_exterior": {
        "version": "2.0",
        "channel": "data-sat-comercio-exterior-2-0-latest",
        "file": "sat_comercio_exterior_20.sqlite3",
        "manifest": "sat_comercio_exterior_20.manifest.json",
        "mount_path": "sat/comercio_exterior_2.0",
        "builder": "scripts/sat/build_comercio_exterior_20.py",
    },
    "sat.nomina_1_2": {
        "version": "1.2-revision-e",
        "channel": "data-sat-nomina-1-2-1-2-revision-e-latest",
        "file": "sat_nomina_12.sqlite3",
        "manifest": "sat_nomina_12.manifest.json",
        "mount_path": "sat/nomina_1.2",
        "builder": "scripts/sat/build_nomina_12.py",
    },
    "sepomex.codigos_postales": {
        "version": "1",
        "channel": "data-sepomex-codigos-postales-1-latest",
        "file": "sepomex_codigos_postales.sqlite3",
        "manifest": "sepomex_codigos_postales.manifest.json",
        "mount_path": "sepomex",
        "builder": "scripts/sepomex/build_postal_codes.py",
    },
}


def load_contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def test_sat_and_geo_profiles_capture_runtime_boundaries_and_dependencies():
    profiles = load_contract()["profiles"]

    assert profiles["sat-cfdi"]["datasets"] == ["sat.cfdi_4"]
    assert profiles["sat-carta-porte"]["datasets"] == ["sat.carta_porte"]
    assert profiles["sat-comercio-exterior"]["datasets"] == [
        "sat.cfdi_4",
        "sat.comercio_exterior",
    ]
    assert profiles["sat-nomina"]["datasets"] == ["sat.nomina_1_2"]
    assert profiles["mexico-geo"]["datasets"] == [
        "inegi.ageeml",
        "sepomex.codigos_postales",
        "conapo.territorial",
    ]
    assert profiles["mexico-telecom"]["datasets"] == ["ift.numbering"]


def test_runtime_contract_matches_builder_release_contracts():
    contract = load_contract()

    assert set(EXPECTED_ARTIFACTS).issubset(contract["datasets"])
    for dataset_id, expected in EXPECTED_ARTIFACTS.items():
        artifact = contract["datasets"][dataset_id]["artifact"]
        assert artifact == {
            "channel": expected["channel"],
            "discovery": "release-pointer",
            "file": expected["file"],
            "format": "file",
            "manifest": expected["manifest"],
            "mount_path": expected["mount_path"],
            "version": expected["version"],
        }

        builder = (REPO_ROOT / expected["builder"]).read_text(encoding="utf-8")
        assert 'ARTIFACT_FORMAT = "file"' in builder
        assert f'MOUNT_PATH = "{expected["mount_path"]}"' in builder
        assert '"format": ARTIFACT_FORMAT' in builder
        assert '"mount_path": MOUNT_PATH' in builder


@pytest.mark.parametrize("dataset_id", sorted(EXPECTED_ARTIFACTS))
def test_resolver_fetches_each_sat_geo_file_dataset(tmp_path: Path, dataset_id: str):
    contract = load_contract()
    artifact = contract["datasets"][dataset_id]["artifact"]
    payload = f"SQLite fixture for {dataset_id}".encode()
    file_sha = hashlib.sha256(payload).hexdigest()
    content_sha = hashlib.sha256(f"semantic:{dataset_id}".encode()).hexdigest()
    release_tag = f"data-test-{content_sha}"

    pointer = {
        "schema_version": 1,
        "dataset_id": dataset_id,
        "dataset_version": artifact["version"],
        "release_tag": release_tag,
        "content_sha256": content_sha,
        "artifact": artifact["file"],
        "manifest": artifact["manifest"],
    }
    manifest = {
        "schema_version": 1,
        "dataset_id": dataset_id,
        "dataset_version": artifact["version"],
        "dataset": {
            "file": artifact["file"],
            "format": "file",
            "mount_path": artifact["mount_path"],
            "file_sha256": file_sha,
            "content_sha256": content_sha,
        },
    }

    release_base = "https://example.invalid/releases"
    metadata_base = "https://example.invalid/releases/tags"
    responses = {
        f"{metadata_base}/{artifact['channel']}": json.dumps(
            {"tag_name": artifact["channel"], "body": json.dumps(pointer)}
        ).encode(),
        f"{release_base}/{release_tag}/{artifact['manifest']}": json.dumps(
            manifest
        ).encode(),
        f"{release_base}/{release_tag}/{artifact['file']}": payload,
    }

    resolver = DatasetResolver(
        cache_dir=tmp_path / dataset_id.replace(".", "-"),
        mode="fetch-missing",
        contract=contract,
        downloader=lambda url: responses[url],
        release_base_url=release_base,
        release_metadata_base_url=metadata_base,
    )

    root = resolver.fetch_dataset(dataset_id)
    assert (root / artifact["file"]).read_bytes() == payload
    assert resolver.verify_cached_dataset(dataset_id)
    assert resolver.cache_status(dataset_id)["release_tag"] == release_tag
