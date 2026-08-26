"""Tests for registry-driven catalog maintenance scheduling."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "catalog_maintenance.py"
REGISTRY_PATH = REPO_ROOT / "packages" / "shared-data" / "catalog-registry.json"


def load_module() -> ModuleType:
    """Load the maintenance script without making scripts a package."""
    spec = importlib.util.spec_from_file_location("catalog_maintenance_tool", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cadence_is_derived_from_freshness_sla():
    module = load_module()

    def dataset(days: int):
        return {
            "status": "managed",
            "freshness": {"mode": "interval", "max_age_days": days},
        }

    assert module.cadence_for_dataset(dataset(2)) == "daily"
    assert module.cadence_for_dataset(dataset(7)) == "weekly"
    assert module.cadence_for_dataset(dataset(31)) == "monthly"
    assert module.cadence_for_dataset(dataset(90)) == "quarterly"
    assert module.cadence_for_dataset(dataset(180)) == "semiannual"
    assert module.cadence_for_dataset(dataset(365)) == "annual"


def test_pipeline_event_and_planned_datasets_are_not_double_scheduled():
    module = load_module()

    pipeline = {
        "status": "managed",
        "freshness": {"mode": "pipeline", "max_age_days": 2},
    }
    event = {"status": "managed", "freshness": {"mode": "event"}}
    planned = {
        "status": "planned",
        "freshness": {"mode": "interval", "max_age_days": 31},
    }

    assert module.cadence_for_dataset(pipeline) is None
    assert module.cadence_for_dataset(event) is None
    assert module.cadence_for_dataset(planned) is None


def test_current_registry_schedules_reference_data_but_not_dynamic_pipeline():
    module = load_module()
    registry = module.load_registry(REGISTRY_PATH)

    monthly = module.build_plan(registry, "monthly")
    monthly_ids = {item.id for item in monthly}
    all_scheduled_ids = {
        item.id
        for cadence in module.CADENCES
        for item in module.build_plan(registry, cadence)
    }

    assert "banxico.reference" in monthly_ids
    assert "banxico.sie_dynamic" not in all_scheduled_ids


def test_slots_are_stable_and_partition_a_cadence():
    module = load_module()
    registry = module.load_registry(REGISTRY_PATH)

    complete = module.build_plan(registry, "monthly")
    by_slot = [
        module.build_plan(registry, "monthly", slot)
        for slot in range(module.SLOT_COUNTS["monthly"])
    ]

    flattened = [item.id for slot_plan in by_slot for item in slot_plan]
    assert sorted(flattened) == sorted(item.id for item in complete)
    assert len(flattened) == len(set(flattened))

    for item in complete:
        assert module.slot_for_dataset(item.id, "monthly") == item.slot


def test_unconfigured_adapter_is_reported_without_execution():
    module = load_module()
    result = module.run_adapter("sat.cfdi_4")

    assert result.id == "sat.cfdi_4"
    assert result.status == "unconfigured"
    assert result.returncode is None
