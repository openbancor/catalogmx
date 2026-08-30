"""Independent CatalogMX data distribution and update helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from catalogmx.data.resolver import DatasetResolver, get_dataset_path, get_dataset_root

if TYPE_CHECKING:
    from catalogmx.data.updater import DataUpdater


def __getattr__(name: str) -> Any:
    """Keep the legacy dynamic updater lazy so importing data has no cache side effects."""
    if name == "DataUpdater":
        from catalogmx.data.updater import DataUpdater

        return DataUpdater
    raise AttributeError(name)


__all__ = [
    "DataUpdater",
    "DatasetResolver",
    "get_dataset_path",
    "get_dataset_root",
]
