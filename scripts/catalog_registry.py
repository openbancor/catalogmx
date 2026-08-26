#!/usr/bin/env python3
"""Validate and audit catalogmx catalog metadata.

The catalog registry is intentionally separate from package releases. It tracks
what data is managed, where it comes from, how it is distributed, and whether
its upstream source needs review.

Usage:
    python scripts/catalog_registry.py validate
    python scripts/catalog_registry.py audit
    python scripts/catalog_registry.py audit --json
    python scripts/catalog_registry.py audit --fail-on-due
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = REPO_ROOT / "packages" / "shared-data" / "catalog-registry.json"

ALLOWED_KINDS = {
    "reference",
    "classification",
    "time_series",
    "derived",
    "regulatory_parameters",
}
ALLOWED_STATUSES = {"managed", "planned", "legacy"}
ALLOWED_DISTRIBUTIONS = {"embedded", "release", "optional", "mixed"}
ALLOWED_FRESHNESS_MODES = {"interval", "pipeline", "event", "manual"}
DATASET_ID_RE = re.compile(r"^[a-z0-9_.-]+$")


def load_registry(path: Path) -> dict[str, Any]:
    """Load a catalog registry JSON document."""
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("registry root must be a JSON object")
    return data


def parse_iso_date(value: str) -> date:
    """Parse an ISO date or datetime into a date."""
    try:
        return date.fromisoformat(value)
    except ValueError:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()


def validate_registry(
    registry: dict[str, Any], repo_root: Path = REPO_ROOT
) -> tuple[list[str], list[str]]:
    """Return structural errors and non-fatal provenance warnings."""
    errors: list[str] = []
    warnings: list[str] = []

    if registry.get("schema_version") != 1:
        errors.append("schema_version must be 1")

    datasets = registry.get("datasets")
    if not isinstance(datasets, list) or not datasets:
        errors.append("datasets must be a non-empty list")
        return errors, warnings

    seen_ids: set[str] = set()
    required = {
        "id",
        "title",
        "authority",
        "kind",
        "status",
        "distribution",
        "local_paths",
        "upstream",
        "freshness",
    }

    for index, dataset in enumerate(datasets):
        prefix = f"datasets[{index}]"
        if not isinstance(dataset, dict):
            errors.append(f"{prefix} must be an object")
            continue

        missing = sorted(required - dataset.keys())
        if missing:
            errors.append(f"{prefix} missing required fields: {', '.join(missing)}")
            continue

        dataset_id = dataset["id"]
        if not isinstance(dataset_id, str) or not DATASET_ID_RE.fullmatch(dataset_id):
            errors.append(f"{prefix}.id must use lowercase registry-safe characters")
            dataset_id = prefix
        elif dataset_id in seen_ids:
            errors.append(f"duplicate dataset id: {dataset_id}")
        else:
            seen_ids.add(dataset_id)

        if dataset["kind"] not in ALLOWED_KINDS:
            errors.append(f"{dataset_id}: unsupported kind {dataset['kind']!r}")
        if dataset["status"] not in ALLOWED_STATUSES:
            errors.append(f"{dataset_id}: unsupported status {dataset['status']!r}")
        if dataset["distribution"] not in ALLOWED_DISTRIBUTIONS:
            errors.append(
                f"{dataset_id}: unsupported distribution {dataset['distribution']!r}"
            )

        local_paths = dataset["local_paths"]
        if not isinstance(local_paths, list) or not all(
            isinstance(path, str) and path for path in local_paths
        ):
            errors.append(f"{dataset_id}: local_paths must be a list of non-empty strings")
            local_paths = []

        if dataset["status"] == "managed" and not local_paths:
            errors.append(f"{dataset_id}: managed datasets must declare local_paths")

        for local_path in local_paths:
            path = Path(local_path)
            if path.is_absolute() or ".." in path.parts:
                errors.append(f"{dataset_id}: unsafe local path {local_path!r}")
                continue
            if not (repo_root / path).exists():
                errors.append(f"{dataset_id}: local path does not exist: {local_path}")

        upstream = dataset["upstream"]
        if not isinstance(upstream, list):
            errors.append(f"{dataset_id}: upstream must be a list")
            upstream = []

        for source_index, source in enumerate(upstream):
            if not isinstance(source, dict):
                errors.append(f"{dataset_id}: upstream[{source_index}] must be an object")
                continue
            if not isinstance(source.get("url"), str) or not source["url"].startswith(
                ("https://", "http://")
            ):
                errors.append(f"{dataset_id}: upstream[{source_index}] requires an HTTP URL")

        if dataset["status"] == "managed" and not upstream:
            warnings.append(f"{dataset_id}: authoritative upstream source is not registered yet")

        freshness = dataset["freshness"]
        if not isinstance(freshness, dict):
            errors.append(f"{dataset_id}: freshness must be an object")
            continue

        mode = freshness.get("mode")
        if mode not in ALLOWED_FRESHNESS_MODES:
            errors.append(f"{dataset_id}: unsupported freshness mode {mode!r}")

        if mode in {"interval", "pipeline"}:
            max_age_days = freshness.get("max_age_days")
            if not isinstance(max_age_days, int) or max_age_days <= 0:
                errors.append(f"{dataset_id}: {mode} freshness requires max_age_days > 0")

        if mode == "pipeline":
            workflow = freshness.get("workflow")
            if not isinstance(workflow, str) or not workflow:
                errors.append(f"{dataset_id}: pipeline freshness requires workflow")
            elif not (repo_root / workflow).exists():
                errors.append(f"{dataset_id}: workflow does not exist: {workflow}")

        checked_at = freshness.get("upstream_checked_at")
        if checked_at is not None:
            if not isinstance(checked_at, str):
                errors.append(f"{dataset_id}: upstream_checked_at must be an ISO date or null")
            else:
                try:
                    parse_iso_date(checked_at)
                except ValueError:
                    errors.append(f"{dataset_id}: invalid upstream_checked_at: {checked_at}")

        if dataset["kind"] == "derived":
            derivation = dataset.get("derivation")
            if not isinstance(derivation, dict):
                errors.append(f"{dataset_id}: derived datasets require derivation metadata")
            else:
                filter_spec = derivation.get("filter_spec")
                if dataset["status"] == "managed" and not filter_spec:
                    errors.append(
                        f"{dataset_id}: managed filtered derivatives require a filter_spec"
                    )
                elif dataset["status"] == "planned" and not filter_spec:
                    warnings.append(
                        f"{dataset_id}: derivation is intentionally blocked until filter_spec is defined"
                    )

    return errors, warnings


def audit_dataset(dataset: dict[str, Any], today: date) -> dict[str, Any]:
    """Compute the freshness state for one structurally valid dataset."""
    freshness = dataset["freshness"]
    mode = freshness["mode"]
    checked_at = freshness.get("upstream_checked_at")

    if dataset["status"] == "planned":
        return {"id": dataset["id"], "state": "planned", "reason": "not materialized"}

    if mode == "pipeline":
        return {
            "id": dataset["id"],
            "state": "pipeline",
            "reason": freshness.get("workflow", "automated pipeline"),
        }

    if checked_at is None:
        state = "due" if mode in {"interval", "manual"} else "review"
        return {"id": dataset["id"], "state": state, "reason": "never checked in registry"}

    checked_date = parse_iso_date(checked_at)
    age_days = (today - checked_date).days

    if mode == "interval":
        max_age_days = freshness["max_age_days"]
        state = "due" if age_days > max_age_days else "current"
        return {
            "id": dataset["id"],
            "state": state,
            "reason": f"checked {age_days} days ago; SLA {max_age_days} days",
        }

    if mode == "event":
        return {
            "id": dataset["id"],
            "state": "current",
            "reason": f"event-driven; last reviewed {checked_date.isoformat()}",
        }

    return {
        "id": dataset["id"],
        "state": "review",
        "reason": f"manual review; last checked {checked_date.isoformat()}",
    }


def build_audit(registry: dict[str, Any], today: date | None = None) -> dict[str, Any]:
    """Build a machine-readable audit report."""
    today = today or date.today()
    states = [audit_dataset(dataset, today) for dataset in registry["datasets"]]
    counts: dict[str, int] = {}
    for item in states:
        counts[item["state"]] = counts.get(item["state"], 0) + 1
    return {
        "date": today.isoformat(),
        "registry_status": registry.get("registry_status"),
        "counts": counts,
        "datasets": states,
    }


def print_validation(errors: list[str], warnings: list[str]) -> None:
    """Print structural validation results."""
    for error in errors:
        print(f"ERROR: {error}")
    for warning in warnings:
        print(f"WARN: {warning}")

    if not errors:
        print(f"Registry structure valid ({len(warnings)} warning(s)).")


def print_audit(report: dict[str, Any]) -> None:
    """Print a concise human-readable freshness report."""
    print(f"Catalog registry audit for {report['date']}")
    print(f"Registry status: {report['registry_status']}")
    for item in report["datasets"]:
        print(f"{item['state'].upper():8} {item['id']}: {item['reason']}")
    counts = ", ".join(
        f"{state}={count}" for state, count in sorted(report["counts"].items())
    )
    print(f"Summary: {counts}")


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Validate and audit catalog registry metadata")
    parser.add_argument(
        "command",
        choices=["validate", "audit"],
        help="validate structure or audit freshness",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=DEFAULT_REGISTRY,
        help="path to catalog-registry.json",
    )
    parser.add_argument("--json", action="store_true", help="emit audit as JSON")
    parser.add_argument(
        "--fail-on-due",
        action="store_true",
        help="return a non-zero status when an audit contains due datasets",
    )
    args = parser.parse_args(argv)

    registry_path = args.registry
    if not registry_path.is_absolute():
        registry_path = (Path.cwd() / registry_path).resolve()

    try:
        registry = load_registry(registry_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot load registry: {exc}", file=sys.stderr)
        return 1

    errors, warnings = validate_registry(registry)
    if errors:
        print_validation(errors, warnings)
        return 1

    if args.command == "validate":
        print_validation(errors, warnings)
        return 0

    report = build_audit(registry)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print_validation(errors, warnings)
        print_audit(report)

    if args.fail_on_due and report["counts"].get("due", 0) > 0:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
