#!/usr/bin/env python3
"""Plan and run catalog maintenance from the canonical registry.

The registry owns freshness policy. This tool turns ``max_age_days`` into a
maintenance cadence and deterministically spreads datasets across schedule
slots so GitHub Actions does not hit every upstream at once.

Adapters are deliberately explicit: an unknown dataset is reported as
``unconfigured`` instead of executing arbitrary commands from JSON metadata.
This keeps the registry declarative and avoids turning it into a shell script.
Adapters may update canonical repository data or build independently published
artifacts; the maintenance workflow handles those outputs after adapter runs.

Usage:
    python scripts/catalog_maintenance.py plan --cadence monthly --slot 0
    python scripts/catalog_maintenance.py plan --cadence monthly --slot 0 --json
    python scripts/catalog_maintenance.py run --cadence monthly --slot 0
    python scripts/catalog_maintenance.py run --dataset banxico.reference
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = REPO_ROOT / "packages" / "shared-data" / "catalog-registry.json"

CADENCES = ("daily", "weekly", "monthly", "quarterly", "semiannual", "annual")
SLOT_COUNTS = {
    "daily": 1,
    "weekly": 2,
    "monthly": 4,
    "quarterly": 2,
    "semiannual": 1,
    "annual": 1,
}

# Repository-maintained adapters only. Do not execute commands from registry JSON.
# Each adapter must be deterministic. Repository adapters update canonical files
# in-place; release adapters write a manifest and files below dist/catalog-artifacts.
ADAPTERS: dict[str, tuple[str, ...]] = {
    "banxico.reference": (sys.executable, "scripts/update_banxico_banks.py"),
    "inegi.ageeml": (
        sys.executable,
        "scripts/inegi/build_ageeml.py",
        "--output-dir",
        "dist/catalog-artifacts/inegi-ageeml",
    ),
    "sat.carta_porte": (
        sys.executable,
        "scripts/sat/build_carta_porte_31.py",
        "--output-dir",
        "dist/catalog-artifacts/sat-carta-porte-31",
    ),
    "sat.cfdi_4": (
        sys.executable,
        "scripts/sat/build_cfdi_40.py",
        "--output-dir",
        "dist/catalog-artifacts/sat-cfdi-40",
    ),
    "sat.comercio_exterior": (
        sys.executable,
        "scripts/sat/build_comercio_exterior_20.py",
        "--output-dir",
        "dist/catalog-artifacts/sat-comercio-exterior-20",
    ),
    "sat.nomina_1_2": (
        sys.executable,
        "scripts/sat/build_nomina_12.py",
        "--output-dir",
        "dist/catalog-artifacts/sat-nomina-12",
        "--compat-output-dir",
        "packages/shared-data/sat/nomina_1.2",
    ),
    "sepomex.codigos_postales": (
        sys.executable,
        "scripts/sepomex/build_postal_codes.py",
        "--output-dir",
        "dist/catalog-artifacts/sepomex-codigos-postales",
    ),
}


@dataclass(frozen=True)
class PlannedDataset:
    id: str
    cadence: str
    slot: int
    max_age_days: int
    adapter_configured: bool


@dataclass(frozen=True)
class RunResult:
    id: str
    status: str
    returncode: int | None = None


def load_registry(path: Path = DEFAULT_REGISTRY) -> dict[str, Any]:
    """Load the canonical registry."""
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict) or not isinstance(data.get("datasets"), list):
        raise ValueError("registry must contain a datasets list")
    return data


def cadence_for_dataset(dataset: dict[str, Any]) -> str | None:
    """Map the registry freshness SLA to an operational maintenance cadence."""
    if dataset.get("status") != "managed":
        return None

    freshness = dataset.get("freshness", {})
    mode = freshness.get("mode")
    if mode in {"pipeline", "event", "manual"}:
        return None
    if mode != "interval":
        return None

    max_age_days = freshness.get("max_age_days")
    if not isinstance(max_age_days, int) or max_age_days <= 0:
        return None
    if max_age_days <= 2:
        return "daily"
    if max_age_days <= 14:
        return "weekly"
    if max_age_days <= 45:
        return "monthly"
    if max_age_days <= 120:
        return "quarterly"
    if max_age_days <= 200:
        return "semiannual"
    return "annual"


def assign_slots(dataset_ids: Sequence[str], cadence: str) -> dict[str, int]:
    """Deterministically balance one cadence across its available schedule slots.

    IDs are sorted and assigned round-robin. This makes the plan reproducible
    while keeping each slot within one dataset of the others. Assignments may
    move when the set of datasets in a cadence changes, which is acceptable for
    operational staggering and avoids persisting schedule noise in the registry.
    """
    slot_count = SLOT_COUNTS[cadence]
    return {
        dataset_id: index % slot_count
        for index, dataset_id in enumerate(sorted(dataset_ids))
    }


def build_plan(
    registry: dict[str, Any], cadence: str, slot: int | None = None
) -> list[PlannedDataset]:
    """Build a deterministic and balanced maintenance plan for one cadence/slot."""
    if cadence not in CADENCES:
        raise ValueError(f"unsupported cadence: {cadence}")

    slot_count = SLOT_COUNTS[cadence]
    if slot is not None and not 0 <= slot < slot_count:
        raise ValueError(f"slot for {cadence} must be between 0 and {slot_count - 1}")

    eligible = [
        dataset
        for dataset in registry["datasets"]
        if cadence_for_dataset(dataset) == cadence
    ]
    assignments = assign_slots([dataset["id"] for dataset in eligible], cadence)

    plan: list[PlannedDataset] = []
    for dataset in eligible:
        dataset_slot = assignments[dataset["id"]]
        if slot is not None and dataset_slot != slot:
            continue
        plan.append(
            PlannedDataset(
                id=dataset["id"],
                cadence=cadence,
                slot=dataset_slot,
                max_age_days=dataset["freshness"]["max_age_days"],
                adapter_configured=dataset["id"] in ADAPTERS,
            )
        )
    return sorted(plan, key=lambda item: item.id)


def run_adapter(dataset_id: str) -> RunResult:
    """Run a trusted adapter or report that one is not configured."""
    command = ADAPTERS.get(dataset_id)
    if command is None:
        return RunResult(id=dataset_id, status="unconfigured")

    completed = subprocess.run(command, cwd=REPO_ROOT, check=False)  # noqa: S603
    status = "ok" if completed.returncode == 0 else "failed"
    return RunResult(id=dataset_id, status=status, returncode=completed.returncode)


def print_plan(plan: Sequence[PlannedDataset]) -> None:
    """Print a compact human-readable maintenance plan."""
    for item in plan:
        adapter = "adapter" if item.adapter_configured else "review"
        print(
            f"{item.id}\t{item.cadence}\tslot={item.slot}\t"
            f"sla={item.max_age_days}d\t{adapter}"
        )


def print_run_summary(results: Sequence[RunResult]) -> None:
    """Print adapter outcomes."""
    for result in results:
        suffix = "" if result.returncode is None else f" ({result.returncode})"
        print(f"{result.id}: {result.status}{suffix}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser(
        "plan", help="show datasets assigned to a schedule slot"
    )
    plan_parser.add_argument("--cadence", required=True, choices=CADENCES)
    plan_parser.add_argument("--slot", type=int)
    plan_parser.add_argument("--json", action="store_true")

    run_parser = subparsers.add_parser("run", help="run configured adapters")
    selector = run_parser.add_mutually_exclusive_group(required=True)
    selector.add_argument("--dataset")
    selector.add_argument("--cadence", choices=CADENCES)
    run_parser.add_argument("--slot", type=int)
    run_parser.add_argument("--strict-unconfigured", action="store_true")

    args = parser.parse_args(argv)
    registry = load_registry(args.registry)

    if args.command == "plan":
        plan = build_plan(registry, args.cadence, args.slot)
        if args.json:
            print(json.dumps([asdict(item) for item in plan], indent=2))
        else:
            print_plan(plan)
        return 0

    if args.dataset:
        dataset_ids = {dataset["id"] for dataset in registry["datasets"]}
        if args.dataset not in dataset_ids:
            parser.error(f"unknown dataset: {args.dataset}")
        results = [run_adapter(args.dataset)]
    else:
        plan = build_plan(registry, args.cadence, args.slot)
        results = [run_adapter(item.id) for item in plan]

    print_run_summary(results)
    if any(result.status == "failed" for result in results):
        return 1
    if args.strict_unconfigured and any(
        result.status == "unconfigured" for result in results
    ):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
