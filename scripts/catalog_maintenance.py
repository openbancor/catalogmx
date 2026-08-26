#!/usr/bin/env python3
"""Plan and run catalog maintenance from the canonical registry.

The registry owns freshness policy. This tool turns ``max_age_days`` into a
maintenance cadence and deterministically spreads datasets across schedule
slots so GitHub Actions does not hit every upstream at once.

Adapters are deliberately explicit: an unknown dataset is reported as
``unconfigured`` instead of executing arbitrary commands from JSON metadata.
This keeps the registry declarative and avoids turning it into a shell script.

Usage:
    python scripts/catalog_maintenance.py plan --cadence monthly --slot 0
    python scripts/catalog_maintenance.py plan --cadence monthly --slot 0 --json
    python scripts/catalog_maintenance.py run --cadence monthly --slot 0
    python scripts/catalog_maintenance.py run --dataset banxico.reference
"""

from __future__ import annotations

import argparse
import hashlib
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
# Each adapter should be deterministic: update canonical files in-place and let
# git diff decide whether a PR is necessary.
ADAPTERS: dict[str, tuple[str, ...]] = {
    "banxico.reference": (sys.executable, "scripts/update_banxico_banks.py"),
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


def slot_for_dataset(dataset_id: str, cadence: str) -> int:
    """Assign a stable slot without storing scheduling noise in the registry."""
    slot_count = SLOT_COUNTS[cadence]
    digest = hashlib.sha256(dataset_id.encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") % slot_count


def build_plan(
    registry: dict[str, Any], cadence: str, slot: int | None = None
) -> list[PlannedDataset]:
    """Build a deterministic maintenance plan for one cadence/slot."""
    if cadence not in CADENCES:
        raise ValueError(f"unsupported cadence: {cadence}")

    slot_count = SLOT_COUNTS[cadence]
    if slot is not None and not 0 <= slot < slot_count:
        raise ValueError(f"slot for {cadence} must be between 0 and {slot_count - 1}")

    plan: list[PlannedDataset] = []
    for dataset in registry["datasets"]:
        dataset_cadence = cadence_for_dataset(dataset)
        if dataset_cadence != cadence:
            continue
        dataset_slot = slot_for_dataset(dataset["id"], cadence)
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
    """Run a trusted repository adapter or report that one is not configured."""
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
