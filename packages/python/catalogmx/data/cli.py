"""Click commands for independent CatalogMX dataset management."""

from __future__ import annotations

from pathlib import Path

import click

from catalogmx.data.resolver import DatasetResolver


def _echo_profile_status(profile: str) -> None:
    resolver = DatasetResolver()
    dataset_ids = resolver.dataset_ids_for_profile(profile)
    if not dataset_ids:
        click.echo(f"{profile}: no external datasets required")
        return
    for dataset_id in dataset_ids:
        state = resolver.cache_status(dataset_id)
        if not state["cached"]:
            click.echo(f"{dataset_id}: missing")
            continue
        freshness = "stale" if state["stale"] else "current"
        click.echo(
            f"{dataset_id}: {freshness} "
            f"content={state['content_sha256']} fetched={state['fetched_at']}"
        )


@click.group("data")
def data() -> None:
    """Fetch, verify and inspect independently versioned datasets."""


@data.command("status")
@click.option("--profile", default="payglobal", show_default=True)
def data_status(profile: str) -> None:
    """Show cache state for all datasets in a profile."""
    _echo_profile_status(profile)


@data.command("fetch")
@click.option("--profile", required=True)
@click.option(
    "--dest",
    type=click.Path(path_type=Path, file_okay=False),
    help="Materialize a shared-data root suitable for a read-only runtime mount.",
)
def data_fetch(profile: str, dest: Path | None) -> None:
    """Fetch a data profile and optionally materialize it to a shared root."""
    resolver = DatasetResolver()
    if dest is not None:
        root = resolver.materialize_profile(profile, dest)
        click.echo(f"Materialized {profile} at {root}")
        return

    fetched = resolver.fetch_profile(profile)
    if not fetched:
        click.echo(f"{profile}: no external datasets required")
        return
    for dataset_id, root in fetched.items():
        click.echo(f"{dataset_id}: {root}")


@data.command("update")
@click.option("--dataset", "dataset_id", required=True)
def data_update(dataset_id: str) -> None:
    """Force synchronization of one dataset release into the local cache."""
    resolver = DatasetResolver()
    if resolver.mode == "offline":
        raise click.ClickException(
            "dataset update is disabled while CATALOGMX_DATA_MODE=offline"
        )
    resolver.mode = "refresh"
    root = resolver.fetch_dataset(dataset_id)
    click.echo(f"{dataset_id}: {root}")


@data.command("verify")
@click.option("--profile", required=True)
def data_verify(profile: str) -> None:
    """Verify cached files against their release manifests."""
    resolver = DatasetResolver(mode="offline")
    results = resolver.verify_profile(profile)
    failed = []
    if not results:
        click.echo(f"{profile}: no external datasets required")
        return
    for dataset_id, valid in results.items():
        click.echo(f"{dataset_id}: {'ok' if valid else 'invalid-or-missing'}")
        if not valid:
            failed.append(dataset_id)
    if failed:
        raise click.ClickException(
            "dataset verification failed: " + ", ".join(sorted(failed))
        )


@data.group("cache")
def data_cache() -> None:
    """Inspect or clear the local content-addressed dataset cache."""


@data_cache.command("info")
@click.option("--profile", default="payglobal", show_default=True)
def data_cache_info(profile: str) -> None:
    """Show cache information for a profile."""
    _echo_profile_status(profile)


@data_cache.command("clear")
@click.option("--dataset", "dataset_id")
def data_cache_clear(dataset_id: str | None) -> None:
    """Clear one dataset cache or all dataset caches."""
    resolver = DatasetResolver(mode="offline")
    resolver.clear_cache(dataset_id)
    click.echo(f"Cleared {'all datasets' if dataset_id is None else dataset_id}")


__all__ = ["data"]
