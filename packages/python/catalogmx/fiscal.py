"""Read-only access to CatalogMX's generated fiscal data manifest."""

from __future__ import annotations

import json
from copy import deepcopy
from importlib import resources
from typing import Literal, TypeAlias, TypedDict, cast

from catalogmx._fiscal_ids import FiscalDatasetId

FiscalDataStatus: TypeAlias = Literal["verified", "pending_review", "legacy_unverified"]
JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


class FiscalSource(TypedDict, total=False):
    """Authority metadata for a fiscal data source."""

    authority: str
    title: str
    published_at: str
    url: str


class _FiscalManifestEntryRequired(TypedDict):
    exercise: int
    status: FiscalDataStatus
    valid_from: str | None
    valid_to: str | None
    source_ids: list[str]
    values: JsonValue
    sha256: str


class FiscalManifestEntry(_FiscalManifestEntryRequired, total=False):
    """One fiscal dataset version for a declared exercise."""

    notes: str


class FiscalDatasetManifest(TypedDict):
    """A fiscal dataset and its exercise-indexed entries."""

    owner: str
    kind: str
    entries: dict[str, FiscalManifestEntry]


class _FiscalManifestRequired(TypedDict):
    schema_version: int
    manifest_id: str
    content_sha256: str
    policy: dict[FiscalDataStatus, str]
    sources: dict[str, FiscalSource]
    datasets: dict[FiscalDatasetId, FiscalDatasetManifest]


class FiscalManifest(_FiscalManifestRequired):
    """The provenance-bearing fiscal manifest generated at release time."""


class FiscalManifestForExercise(TypedDict):
    """All available fiscal dataset entries for one exercise."""

    exercise: int
    content_sha256: str
    entries: dict[FiscalDatasetId, FiscalManifestEntry]


class FiscalSourceReference(TypedDict):
    """A source identifier and its resolved manifest metadata, if available."""

    id: str
    source: FiscalSource | None


_MANIFEST: FiscalManifest | None = None


def _load_manifest() -> FiscalManifest:
    """Load the package-local generated manifest once per process."""
    global _MANIFEST
    if _MANIFEST is None:
        resource = resources.files("catalogmx.data").joinpath("fiscal-manifest.json")
        _MANIFEST = cast(
            FiscalManifest, json.loads(resource.read_text(encoding="utf-8"))
        )
    return _MANIFEST


def fiscal_manifest() -> FiscalManifest:
    """Return a defensive copy of the complete generated fiscal manifest."""
    return deepcopy(_load_manifest())


def fiscal_entry(
    dataset_id: FiscalDatasetId, exercise: int
) -> FiscalManifestEntry | None:
    """Return one fiscal dataset entry for an exercise, if it exists."""
    entry = _load_manifest()["datasets"][dataset_id]["entries"].get(str(exercise))
    return deepcopy(entry) if entry is not None else None


def fiscal_manifest_for_exercise(exercise: int) -> FiscalManifestForExercise:
    """Return the entries available for one exercise without collapsing history."""
    manifest = _load_manifest()
    entries: dict[FiscalDatasetId, FiscalManifestEntry] = {}
    for dataset_id in manifest["datasets"]:
        entry = fiscal_entry(dataset_id, exercise)
        if entry is not None:
            entries[dataset_id] = entry
    return {
        "exercise": exercise,
        "content_sha256": manifest["content_sha256"],
        "entries": entries,
    }


def fiscal_sources(
    dataset_id: FiscalDatasetId, exercise: int
) -> list[FiscalSourceReference]:
    """Resolve the provenance records referenced by a fiscal entry."""
    entry = fiscal_entry(dataset_id, exercise)
    if entry is None:
        return []
    sources = _load_manifest()["sources"]
    return [
        {"id": source_id, "source": deepcopy(sources.get(source_id))}
        for source_id in entry["source_ids"]
    ]


def assert_fiscal_data_verified(
    dataset_id: FiscalDatasetId, exercise: int
) -> FiscalManifestEntry:
    """Require source-audited fiscal data for an exercise."""
    entry = fiscal_entry(dataset_id, exercise)
    if entry is None:
        raise ValueError(f"No fiscal data for {dataset_id} exercise {exercise}")
    if entry["status"] != "verified":
        raise ValueError(
            f"Fiscal data {dataset_id} exercise {exercise} is {entry['status']}, not verified"
        )
    return entry


__all__ = [
    "FiscalDataStatus",
    "FiscalDatasetId",
    "FiscalDatasetManifest",
    "FiscalManifest",
    "FiscalManifestEntry",
    "FiscalManifestForExercise",
    "FiscalSource",
    "FiscalSourceReference",
    "JsonValue",
    "assert_fiscal_data_verified",
    "fiscal_entry",
    "fiscal_manifest",
    "fiscal_manifest_for_exercise",
    "fiscal_sources",
]
