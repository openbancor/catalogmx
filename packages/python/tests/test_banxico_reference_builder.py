"""Tests for the deterministic Banxico reference bundle builder."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "banxico" / "build_reference.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("banxico_reference_builder", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_source(source: Path) -> None:
    source.mkdir(parents=True)
    payloads = {
        "banks.json": [{"code": "002", "name": "BANAMEX"}],
        "codigos_plaza.json": {"plazas": [{"codigo": "001"}]},
        "instituciones_financieras.json": [{"code": "002"}],
        "monedas_divisas.json": [{"code": "MXN"}],
        "spei_institutions.json": [
            {"banxico_key": "40002", "code": "002", "name": "BANAMEX"}
        ],
    }
    for name, payload in payloads.items():
        (source / name).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def test_builder_is_byte_reproducible_and_manifest_verifies_members(tmp_path: Path):
    module = load_module()
    source = tmp_path / "source"
    write_source(source)

    artifact_a, _, manifest_a = module.build_from_directory(source, tmp_path / "a")
    artifact_b, _, manifest_b = module.build_from_directory(source, tmp_path / "b")

    assert artifact_a.read_bytes() == artifact_b.read_bytes()
    assert manifest_a["dataset_id"] == "banxico.reference"
    assert manifest_a["dataset_version"] == "1"
    assert manifest_a["dataset"]["file_sha256"] == module.sha256_file(artifact_a)
    assert manifest_a["dataset"]["content_sha256"] == manifest_b["dataset"]["content_sha256"]
    assert [item["path"] for item in manifest_a["dataset"]["files"]] == [
        "banxico/banks.json",
        "banxico/codigos_plaza.json",
        "banxico/instituciones_financieras.json",
        "banxico/monedas_divisas.json",
        "banxico/spei_institutions.json",
    ]


def test_semantic_hash_ignores_json_formatting_only_changes(tmp_path: Path):
    module = load_module()
    source = tmp_path / "source"
    write_source(source)
    _, _, first = module.build_from_directory(source, tmp_path / "first")

    banks = json.loads((source / "banks.json").read_text(encoding="utf-8"))
    (source / "banks.json").write_text(
        json.dumps(banks, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    _, _, second = module.build_from_directory(source, tmp_path / "second")

    assert first["dataset"]["content_sha256"] == second["dataset"]["content_sha256"]
    assert first["dataset"]["file_sha256"] != second["dataset"]["file_sha256"]


def test_builder_fails_closed_when_namespace_changes(tmp_path: Path):
    module = load_module()
    source = tmp_path / "source"
    write_source(source)
    (source / "banks.json").unlink()
    with pytest.raises(RuntimeError, match="namespace changed"):
        module.build_from_directory(source, tmp_path / "missing")

    write_source(source)
    (source / "future.json").write_text("[]\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="unexpected=future.json"):
        module.build_from_directory(source, tmp_path / "extra")
