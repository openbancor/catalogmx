"""Tests for the repository-level catalog registry maintenance tool."""

from __future__ import annotations

import importlib.util
from copy import deepcopy
from datetime import date
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "catalog_registry.py"
REGISTRY_PATH = REPO_ROOT / "packages" / "shared-data" / "catalog-registry.json"


def load_registry_module() -> ModuleType:
    """Load the maintenance script as a module without making scripts a package."""
    spec = importlib.util.spec_from_file_location("catalog_registry_tool", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bootstrap_registry_is_structurally_valid():
    """The committed registry must reference real managed artifacts."""
    module = load_registry_module()
    registry = module.load_registry(REGISTRY_PATH)

    errors, warnings = module.validate_registry(registry, REPO_ROOT)

    assert errors == []
    assert any("authoritative upstream source" in warning for warning in warnings)


def test_audit_marks_unknown_interval_sources_due_without_guessing_freshness():
    """Unknown source verification dates are due, not silently treated as current."""
    module = load_registry_module()
    registry = module.load_registry(REGISTRY_PATH)

    report = module.build_audit(registry, today=date(2026, 8, 25))
    states = {item["id"]: item["state"] for item in report["datasets"]}

    assert states["cnbv.reference"] == "due"
    assert states["banxico.sie_dynamic"] == "pipeline"
    assert states["inegi.denue.filtered"] == "planned"


def test_managed_filtered_derivative_requires_reproducible_filter_spec():
    """A derived view cannot become managed before its filter is specified."""
    module = load_registry_module()
    registry = module.load_registry(REGISTRY_PATH)
    modified = deepcopy(registry)

    denue = next(
        dataset for dataset in modified["datasets"] if dataset["id"] == "inegi.denue.filtered"
    )
    denue["status"] = "managed"
    denue["local_paths"] = ["packages/shared-data/inegi"]

    errors, _ = module.validate_registry(modified, REPO_ROOT)

    assert any("managed filtered derivatives require a filter_spec" in error for error in errors)
