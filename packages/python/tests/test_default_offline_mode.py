"""The default data mode is offline: nothing downloads unless explicitly requested."""

from __future__ import annotations

import importlib
import socket
from pathlib import Path

import pytest

from catalogmx.data import resolver as resolver_module
from catalogmx.data import updater as updater_module
from catalogmx.data.resolver import DEFAULT_DATA_MODE, DatasetResolver

BANXICO = "banxico.reference"
NO_FALLBACK = "sat.cfdi_4"


@pytest.fixture(autouse=True)
def _clean_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    for name in ("CATALOGMX_DATA_MODE", "CATALOGMX_SHARED_DATA", "CATALOGMX_AUTO_UPDATE"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("CATALOGMX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr("catalogmx.utils.shared_data._local_roots", lambda: [])
    monkeypatch.setattr(DatasetResolver, "_repo_root", lambda self, dataset: None)
    monkeypatch.setattr(DatasetResolver, "_package_root", lambda self, dataset: None)


@pytest.fixture
def no_network(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    attempts: list[str] = []

    def forbid(*args: object, **kwargs: object):
        attempts.append("network")
        raise AssertionError("network access attempted in default mode")

    monkeypatch.setattr(socket.socket, "connect", forbid)
    monkeypatch.setattr(socket, "create_connection", forbid)
    monkeypatch.setattr(resolver_module, "urlopen", forbid)
    return attempts


def test_default_mode_constant_is_offline() -> None:
    assert DEFAULT_DATA_MODE == "offline"


def test_resolver_without_environment_is_offline() -> None:
    assert DatasetResolver().mode == "offline"


@pytest.mark.parametrize("mode", ["fetch-missing", "refresh"])
def test_environment_still_enables_download_modes(
    monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    monkeypatch.setenv("CATALOGMX_DATA_MODE", mode)
    assert DatasetResolver().mode == mode


def test_default_uses_verified_packaged_fallback_without_network(no_network: list[str]) -> None:
    resolver = DatasetResolver()
    path = resolver.get_dataset_path(BANXICO, "banks.json")
    assert path.name == "banks.json"
    assert "bootstrap" in path.parts
    assert no_network == []


def test_default_fails_closed_without_fallback_and_explains_how_to_enable(
    no_network: list[str],
) -> None:
    with pytest.raises(FileNotFoundError) as excinfo:
        DatasetResolver().resolve_dataset_root(NO_FALLBACK)
    message = str(excinfo.value)
    assert NO_FALLBACK in message
    assert "CATALOGMX_DATA_MODE=fetch-missing" in message
    assert "refresh" in message
    assert no_network == []


def test_default_never_calls_injected_downloader() -> None:
    def downloader(url: str) -> bytes:
        raise AssertionError(f"unexpected download: {url}")

    resolver = DatasetResolver(downloader=downloader)
    with pytest.raises(FileNotFoundError):
        resolver.resolve_dataset_root(NO_FALLBACK)


def test_explicit_fetch_missing_still_downloads() -> None:
    calls: list[str] = []

    def downloader(url: str) -> bytes:
        calls.append(url)
        raise OSError("offline")

    resolver = DatasetResolver(mode="fetch-missing", downloader=downloader)
    with pytest.raises(RuntimeError, match="transport unavailable"):
        resolver.resolve_dataset_root(NO_FALLBACK)
    assert calls


def test_legacy_auto_update_flag_is_opt_in(monkeypatch: pytest.MonkeyPatch) -> None:
    try:
        assert importlib.reload(updater_module).AUTO_UPDATE_ENABLED is False
        monkeypatch.setenv("CATALOGMX_AUTO_UPDATE", "true")
        assert importlib.reload(updater_module).AUTO_UPDATE_ENABLED is True
    finally:
        monkeypatch.delenv("CATALOGMX_AUTO_UPDATE", raising=False)
        importlib.reload(updater_module)


def test_default_downloader_is_used_only_when_a_download_mode_is_requested(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: dict[str, object] = {}

    class _Response:
        def __enter__(self) -> _Response:
            return self

        def __exit__(self, *exc: object) -> None:
            return None

        def read(self) -> bytes:
            return b"payload"

    def fake_urlopen(request: object, timeout: int) -> _Response:
        seen["url"] = request.full_url  # type: ignore[attr-defined]
        seen["timeout"] = timeout
        return _Response()

    monkeypatch.setattr(resolver_module, "urlopen", fake_urlopen)
    assert resolver_module._default_downloader("https://example.invalid/x") == b"payload"
    assert seen == {"url": "https://example.invalid/x", "timeout": 30}


def test_refresh_returns_fresh_verified_cache_without_download(tmp_path: Path) -> None:
    from test_dataset_resolver import contract, mapped_downloader, release_fixture

    _, manifest_payload, artifact_payload = release_fixture()
    download, _ = mapped_downloader(manifest_payload, artifact_payload)
    kwargs = {
        "cache_dir": tmp_path / "cache",
        "contract": contract(),
        "release_base_url": "https://example.invalid/releases/download",
    }
    root = DatasetResolver(mode="fetch-missing", downloader=download, **kwargs).fetch_dataset(
        "banxico.reference"
    )

    def fail_network(url: str) -> bytes:
        raise AssertionError(f"fresh cache must not trigger a download: {url}")

    refreshed = DatasetResolver(mode="refresh", downloader=fail_network, **kwargs)
    assert refreshed.resolve_dataset_root("banxico.reference") == root
