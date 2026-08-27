"""Registry/runtime-contract consistency tests."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

from catalogmx.data.resolver import load_dataset_contract

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "render_dataset_contract.py"
REGISTRY_PATH = REPO_ROOT / "packages" / "shared-data" / "catalog-registry.json"
CONTRACT_PATH = REPO_ROOT / "packages" / "python" / "catalogmx" / "data" / "dataset_contract.json"


def load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("dataset_contract_renderer", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_checked_in_runtime_contract_is_exact_registry_projection():
    module = load_script()
    registry = module.load_registry(REGISTRY_PATH)
    rendered = module.serialize_contract(module.render_contract(registry))
    assert CONTRACT_PATH.read_text(encoding="utf-8") == rendered


def test_payglobal_profiles_resolve_only_banxico_reference():
    contract = load_dataset_contract()
    assert contract["profiles"]["core"]["datasets"] == []
    assert contract["profiles"]["payglobal"]["datasets"] == ["banxico.reference"]
    assert contract["profiles"]["payglobal-e2e"]["datasets"] == [
        "banxico.reference"
    ]

    banxico = contract["datasets"]["banxico.reference"]
    assert banxico["artifact"] == {
        "channel": "data-banxico-reference-1-latest",
        "file": "banxico_reference.tar.gz",
        "format": "tar.gz",
        "manifest": "banxico_reference.manifest.json",
        "mount_path": "banxico",
        "version": "1",
    }
    assert banxico["source_subpath"] == "banxico"
