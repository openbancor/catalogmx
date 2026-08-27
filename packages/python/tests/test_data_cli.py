"""CLI tests for dataset profile management."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from catalogmx.data import cli as data_cli


class FakeResolver:
    instances: list["FakeResolver"] = []

    def __init__(self, mode: str | None = None):
        self.mode = mode
        self.cleared: str | None | object = object()
        type(self).instances.append(self)

    def dataset_ids_for_profile(self, profile: str) -> list[str]:
        return [] if profile == "core" else ["banxico.reference"]

    def cache_status(self, dataset_id: str) -> dict:
        assert dataset_id == "banxico.reference"
        return {
            "cached": True,
            "stale": False,
            "content_sha256": "a" * 64,
            "fetched_at": "2026-08-27T12:00:00+00:00",
        }

    def fetch_profile(self, profile: str) -> dict[str, Path]:
        assert profile == "payglobal"
        return {"banxico.reference": Path("/cache/banxico")}

    def materialize_profile(self, profile: str, destination: Path) -> Path:
        assert profile == "payglobal"
        return destination.resolve()

    def fetch_dataset(self, dataset_id: str) -> Path:
        assert dataset_id == "banxico.reference"
        return Path("/cache/banxico")

    def verify_profile(self, profile: str) -> dict[str, bool]:
        if profile == "broken":
            return {"banxico.reference": False}
        return {"banxico.reference": True}

    def clear_cache(self, dataset_id: str | None = None) -> None:
        self.cleared = dataset_id


def test_status_and_cache_info(monkeypatch):
    FakeResolver.instances.clear()
    monkeypatch.setattr(data_cli, "DatasetResolver", FakeResolver)
    runner = CliRunner()

    result = runner.invoke(data_cli.data, ["status", "--profile", "core"])
    assert result.exit_code == 0
    assert "no external datasets required" in result.output

    result = runner.invoke(data_cli.data, ["cache", "info", "--profile", "payglobal"])
    assert result.exit_code == 0
    assert "banxico.reference: current" in result.output


def test_fetch_update_verify_and_clear(monkeypatch, tmp_path: Path):
    FakeResolver.instances.clear()
    monkeypatch.setattr(data_cli, "DatasetResolver", FakeResolver)
    runner = CliRunner()

    result = runner.invoke(data_cli.data, ["fetch", "--profile", "payglobal"])
    assert result.exit_code == 0
    assert "banxico.reference" in result.output

    destination = tmp_path / "shared"
    result = runner.invoke(
        data_cli.data,
        ["fetch", "--profile", "payglobal", "--dest", str(destination)],
    )
    assert result.exit_code == 0
    assert str(destination.resolve()) in result.output

    result = runner.invoke(
        data_cli.data,
        ["update", "--dataset", "banxico.reference"],
    )
    assert result.exit_code == 0
    assert FakeResolver.instances[-1].mode == "refresh"

    result = runner.invoke(data_cli.data, ["verify", "--profile", "payglobal"])
    assert result.exit_code == 0
    assert "banxico.reference: ok" in result.output
    assert FakeResolver.instances[-1].mode == "offline"

    result = runner.invoke(data_cli.data, ["verify", "--profile", "broken"])
    assert result.exit_code != 0
    assert "dataset verification failed" in result.output

    result = runner.invoke(
        data_cli.data,
        ["cache", "clear", "--dataset", "banxico.reference"],
    )
    assert result.exit_code == 0
    assert FakeResolver.instances[-1].cleared == "banxico.reference"
