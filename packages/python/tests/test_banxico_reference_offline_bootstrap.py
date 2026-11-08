"""Offline bootstrap for banxico.reference and BankCatalog cache invalidation."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from catalogmx.catalogs.banxico.banks import BankCatalog
from catalogmx.data import resolver as resolver_module
from catalogmx.data.resolver import (
    DatasetResolver,
    cached_dataset_signature,
    load_dataset_contract,
)

DATASET_ID = "banxico.reference"
PACKAGE_DIR = Path(resolver_module.__file__).resolve().parents[1] / "data" / "bootstrap" / "banxico"


@pytest.fixture(autouse=True)
def _no_local_shared_data(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    """Simulate an installed wheel: no repo/shared-data roots, empty cache."""
    monkeypatch.delenv("CATALOGMX_SHARED_DATA", raising=False)
    monkeypatch.setenv("CATALOGMX_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setattr("catalogmx.utils.shared_data._local_roots", lambda: [])
    monkeypatch.setattr(DatasetResolver, "_repo_root", lambda self, dataset: None)
    monkeypatch.setattr(DatasetResolver, "_package_root", lambda self, dataset: None)
    BankCatalog.reload()
    yield
    BankCatalog.reload()


def _offline_raises(url: str) -> bytes:
    raise OSError("offline")


def test_contract_declares_directory_bootstrap_with_hashes() -> None:
    bootstrap = load_dataset_contract()["datasets"][DATASET_ID]["bootstrap"]
    assert bootstrap["role"] == "offline-fallback"
    assert bootstrap["kind"] == "directory"
    assert bootstrap["package_path"] == "data/bootstrap/banxico"
    packaged = (PACKAGE_DIR / "banks.json").read_bytes()
    assert bootstrap["files"] == {"banks.json": hashlib.sha256(packaged).hexdigest()}


def test_offline_with_empty_cache_resolves_packaged_banks() -> None:
    resolver = DatasetResolver(mode="offline")
    path = resolver.get_dataset_path(DATASET_ID, "banks.json")
    assert path == PACKAGE_DIR / "banks.json"
    assert resolver.cache_status(DATASET_ID)["cached"] is False


def test_bank_catalog_works_offline_without_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CATALOGMX_DATA_MODE", "offline")
    assert BankCatalog.get_bank_by_code("002")["name"]
    assert BankCatalog.is_spei_participant("002") in (True, False)


def test_network_failure_falls_back_in_fetch_missing_and_refresh() -> None:
    for mode in ("fetch-missing", "refresh"):
        resolver = DatasetResolver(mode=mode, downloader=_offline_raises)
        assert resolver.get_dataset_path(DATASET_ID, "banks.json") == PACKAGE_DIR / "banks.json"
        assert resolver.cache_status(DATASET_ID)["cached"] is False


def test_bootstrap_never_suppresses_remote_resolution() -> None:
    calls: list[str] = []

    def downloader(url: str) -> bytes:
        calls.append(url)
        raise OSError("offline")

    DatasetResolver(mode="fetch-missing", downloader=downloader).resolve_dataset_root(DATASET_ID)
    assert calls, "remote resolution must still be attempted before falling back"


def test_http_errors_never_fall_back_to_bootstrap() -> None:
    from urllib.error import HTTPError

    def broken(url: str) -> bytes:
        raise HTTPError(url, 503, "unavailable", None, None)  # type: ignore[arg-type]

    resolver = DatasetResolver(mode="fetch-missing", downloader=broken)
    with pytest.raises(HTTPError):
        resolver.resolve_dataset_root(DATASET_ID)


def _contract_with_bootstrap(bootstrap: object) -> dict:
    contract = load_dataset_contract()
    contract["datasets"][DATASET_ID]["bootstrap"] = bootstrap
    return contract


def test_tampered_bootstrap_file_fails_closed(tmp_path: Path) -> None:
    contract = _contract_with_bootstrap(
        {
            "kind": "directory",
            "role": "offline-fallback",
            "package_path": "data/bootstrap/banxico",
            "files": {"banks.json": "0" * 64},
        }
    )
    resolver = DatasetResolver(mode="offline", contract=contract)
    with pytest.raises(RuntimeError, match="bootstrap file hash mismatch"):
        resolver.resolve_dataset_root(DATASET_ID)


@pytest.mark.parametrize(
    ("bootstrap", "message"),
    [
        (
            {
                "kind": "directory",
                "role": "offline-fallback",
                "package_path": "data/bootstrap/banxico",
            },
            "bootstrap files must be a non-empty",
        ),
        (
            {
                "kind": "directory",
                "role": "offline-fallback",
                "package_path": "data/bootstrap/banxico",
                "files": {"../x.json": "0" * 64},
            },
            "unsafe",
        ),
        (
            {
                "kind": "directory",
                "role": "offline-fallback",
                "package_path": "data/bootstrap/banxico",
                "files": {"banks.json": "nothex"},
            },
            "bootstrap file hash must be sha256",
        ),
        (
            {
                "kind": "directory",
                "role": "offline-fallback",
                "package_path": "data/bootstrap/banxico",
                "files": {"missing.json": "0" * 64},
            },
            "bootstrap file is missing",
        ),
    ],
)
def test_invalid_directory_bootstrap_contract_fails_closed(bootstrap: dict, message: str) -> None:
    resolver = DatasetResolver(mode="offline", contract=_contract_with_bootstrap(bootstrap))
    with pytest.raises(RuntimeError, match=message):
        resolver.resolve_dataset_root(DATASET_ID)


def test_missing_bootstrap_directory_keeps_offline_failure() -> None:
    contract = _contract_with_bootstrap(
        {
            "kind": "directory",
            "role": "offline-fallback",
            "package_path": "data/bootstrap/nonexistent",
            "files": {"banks.json": "0" * 64},
        }
    )
    resolver = DatasetResolver(mode="offline", contract=contract)
    with pytest.raises(FileNotFoundError):
        resolver.resolve_dataset_root(DATASET_ID)


def test_directory_bootstrap_requires_archive_artifact() -> None:
    contract = _contract_with_bootstrap(
        {
            "kind": "directory",
            "role": "offline-fallback",
            "package_path": "data/bootstrap/banxico",
            "files": {"banks.json": "0" * 64},
        }
    )
    contract["datasets"][DATASET_ID]["artifact"]["format"] = "file"
    with pytest.raises(RuntimeError, match="directory bootstrap requires"):
        DatasetResolver(mode="offline", contract=contract).resolve_dataset_root(DATASET_ID)


def test_corrupt_bootstrap_not_checked_when_remote_succeeds_is_not_needed() -> None:
    """Hash is verified only when the bootstrap is actually used."""
    contract = _contract_with_bootstrap(
        {
            "kind": "directory",
            "role": "offline-fallback",
            "package_path": "data/bootstrap/banxico",
            "files": {"banks.json": "0" * 64},
        }
    )
    resolver = DatasetResolver(mode="fetch-missing", contract=contract, downloader=_offline_raises)
    with pytest.raises(RuntimeError, match="bootstrap file hash mismatch"):
        resolver.resolve_dataset_root(DATASET_ID)


def test_packaged_banks_json_is_valid_and_complete() -> None:
    banks = json.loads((PACKAGE_DIR / "banks.json").read_text(encoding="utf-8"))
    codes = {bank["code"] for bank in banks}
    assert {"002", "012", "014"} <= codes


def test_pyproject_ships_bootstrap_directory() -> None:
    root = Path(__file__).resolve().parents[1]
    assert '"data/bootstrap/banxico/*.json"' in (root / "pyproject.toml").read_text(
        encoding="utf-8"
    )


# --- BankCatalog invalidation -------------------------------------------------


def _write_cache(cache: Path, content_sha: str) -> None:
    dataset_dir = cache / "datasets" / DATASET_ID
    dataset_dir.mkdir(parents=True, exist_ok=True)
    (dataset_dir / "current.json").write_text(
        json.dumps({"dataset_id": DATASET_ID, "content_sha256": content_sha}), encoding="utf-8"
    )


def test_cached_dataset_signature_tracks_state(tmp_path: Path) -> None:
    assert cached_dataset_signature(DATASET_ID) is None
    _write_cache(tmp_path / "cache", "a" * 64)
    assert cached_dataset_signature(DATASET_ID) == "a" * 64
    _write_cache(tmp_path / "cache", "b" * 64)
    assert cached_dataset_signature(DATASET_ID) == "b" * 64


@pytest.mark.parametrize("payload", ["{not json", "[]", json.dumps({"content_sha256": "bad"})])
def test_cached_dataset_signature_ignores_corrupt_state(tmp_path: Path, payload: str) -> None:
    dataset_dir = tmp_path / "cache" / "datasets" / DATASET_ID
    dataset_dir.mkdir(parents=True)
    (dataset_dir / "current.json").write_text(payload, encoding="utf-8")
    assert cached_dataset_signature(DATASET_ID) is None


def test_bank_catalog_reload_clears_all_indexes() -> None:
    BankCatalog.get_bank_by_code("002")
    assert BankCatalog._data is not None
    BankCatalog.reload()
    assert BankCatalog._data is None
    assert BankCatalog._bank_by_code is None
    assert BankCatalog._bank_by_spei_code is None
    assert BankCatalog._bank_by_name is None
    assert BankCatalog._bank_by_name_normalized is None


def test_bank_catalog_picks_up_cache_refresh_in_same_process(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    loads: list[str] = []
    root_a = tmp_path / "a"
    root_b = tmp_path / "b"
    for root, name in ((root_a, "BANCO A"), (root_b, "BANCO B")):
        root.mkdir()
        (root / "banks.json").write_text(
            json.dumps([{"code": "999", "name": name, "spei_code": None}]), encoding="utf-8"
        )

    current = {"root": root_a}

    def fake_path(*parts: str) -> Path:
        loads.append("load")
        return current["root"].joinpath(*parts[1:])

    monkeypatch.setattr("catalogmx.catalogs.banxico.banks.get_shared_data_path", fake_path)

    assert BankCatalog.get_bank_by_code("999")["name"] == "BANCO A"
    BankCatalog.get_bank_by_code("999")
    assert len(loads) == 1, "no reload while the verified cache did not change"

    current["root"] = root_b
    assert BankCatalog.get_bank_by_code("999")["name"] == "BANCO A", "stale until cache changes"

    _write_cache(tmp_path / "cache", "c" * 64)
    assert BankCatalog.get_bank_by_code("999")["name"] == "BANCO B"
    assert len(loads) == 2


def test_bank_catalog_query_path_never_downloads(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    def forbidden(url: str) -> bytes:  # pragma: no cover - must never run
        raise AssertionError("query path must not download")

    monkeypatch.setattr(resolver_module, "_default_downloader", forbidden)
    monkeypatch.setenv("CATALOGMX_DATA_MODE", "offline")
    BankCatalog.get_bank_by_code("002")
    _write_cache(tmp_path / "cache", "d" * 64)  # signature change, cache object absent
    assert BankCatalog.get_bank_by_code("002") is not None


@pytest.mark.parametrize(
    ("bootstrap", "message"),
    [
        ("nope", "must be an object"),
        (
            {"kind": "directory", "role": "other", "package_path": "x"},
            "unsupported dataset bootstrap role",
        ),
        (
            {"kind": "zip", "role": "offline-fallback", "package_path": "x"},
            "unsupported dataset bootstrap kind",
        ),
        (
            {"kind": "directory", "role": "offline-fallback", "package_path": ""},
            "package_path must be",
        ),
        (
            {"kind": "file", "role": "offline-fallback", "package_path": "data/x.bin"},
            "file bootstrap requires a file artifact",
        ),
    ],
)
def test_malformed_bootstrap_contract_fails_closed(bootstrap: object, message: str) -> None:
    resolver = DatasetResolver(mode="offline", contract=_contract_with_bootstrap(bootstrap))
    with pytest.raises(RuntimeError, match=message):
        resolver.resolve_dataset_root(DATASET_ID)


def test_file_bootstrap_filename_mismatch_fails_closed() -> None:
    contract = _contract_with_bootstrap(
        {"kind": "file", "role": "offline-fallback", "package_path": "data/x.bin"}
    )
    contract["datasets"][DATASET_ID]["artifact"]["format"] = "file"
    contract["datasets"][DATASET_ID]["artifact"]["file"] = "other.bin"
    with pytest.raises(RuntimeError, match="filename mismatch"):
        DatasetResolver(mode="offline", contract=contract).resolve_dataset_root(DATASET_ID)
