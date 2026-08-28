#!/usr/bin/env python3
"""Render the package runtime dataset contract from the canonical registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = REPO_ROOT / "packages" / "shared-data" / "catalog-registry.json"
DEFAULT_OUTPUT = (
    REPO_ROOT / "packages" / "python" / "catalogmx" / "data" / "dataset_contract.json"
)


def load_registry(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        registry = json.load(handle)
    if not isinstance(registry, dict):
        raise ValueError("registry must be a JSON object")
    return registry


def render_contract(registry: dict[str, Any]) -> dict[str, Any]:
    """Project runtime-relevant registry metadata into a package-local contract."""
    profiles = registry.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise ValueError("registry must declare data profiles")

    datasets = registry.get("datasets")
    if not isinstance(datasets, list):
        raise ValueError("registry must declare datasets")
    by_id = {
        dataset["id"]: dataset
        for dataset in datasets
        if isinstance(dataset, dict) and isinstance(dataset.get("id"), str)
    }

    referenced: set[str] = set()
    for profile_name, profile in profiles.items():
        if not isinstance(profile, dict):
            raise ValueError(f"profile {profile_name!r} must be an object")
        dataset_ids = profile.get("datasets")
        if not isinstance(dataset_ids, list) or not all(
            isinstance(dataset_id, str) for dataset_id in dataset_ids
        ):
            raise ValueError(f"profile {profile_name!r} requires a datasets list")
        for dataset_id in dataset_ids:
            if dataset_id not in by_id:
                raise ValueError(
                    f"profile {profile_name!r} references unknown dataset {dataset_id!r}"
                )
            referenced.add(dataset_id)

    runtime_datasets: dict[str, Any] = {}
    for dataset_id in sorted(referenced):
        dataset = by_id[dataset_id]
        artifact = dataset.get("artifact")
        if not isinstance(artifact, dict):
            raise ValueError(
                f"profile dataset {dataset_id!r} has no runtime artifact contract"
            )

        runtime_artifact = dict(artifact)
        implementation = dataset.get("implementation")
        if (
            isinstance(implementation, dict)
            and implementation.get("publish_from_reviewed_master") is True
        ):
            # Reviewed-master publishers expose a stable release as a metadata
            # pointer to one complete immutable artifact/manifest release.
            runtime_artifact["discovery"] = "release-pointer"

        projected: dict[str, Any] = {
            "artifact": runtime_artifact,
            "freshness": dataset.get("freshness", {}),
        }
        source_subpath = dataset.get("source_subpath")
        if source_subpath is not None:
            if not isinstance(source_subpath, str) or not source_subpath:
                raise ValueError(f"invalid source_subpath for {dataset_id!r}")
            projected["source_subpath"] = source_subpath

        bootstrap = dataset.get("bootstrap")
        if bootstrap is not None:
            if not isinstance(bootstrap, dict):
                raise ValueError(f"invalid bootstrap contract for {dataset_id!r}")
            package_path = bootstrap.get("package_path")
            if not isinstance(package_path, str) or not package_path:
                raise ValueError(f"invalid bootstrap package_path for {dataset_id!r}")
            projected["bootstrap"] = dict(bootstrap)
        runtime_datasets[dataset_id] = projected

    return {
        "schema_version": 1,
        "profiles": profiles,
        "datasets": runtime_datasets,
    }


def serialize_contract(contract: dict[str, Any]) -> str:
    return json.dumps(contract, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when the checked-in package contract is not current",
    )
    args = parser.parse_args(argv)

    rendered = serialize_contract(render_contract(load_registry(args.registry)))
    if args.check:
        try:
            current = args.output.read_text(encoding="utf-8")
        except OSError:
            current = ""
        if current != rendered:
            print(f"Dataset contract is stale: {args.output}")
            return 1
        print(f"Dataset contract is current: {args.output}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    print(f"Rendered dataset contract: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
