import os
from pathlib import Path

import pytest

from catalogmx.utils import shared_data as sd


def test_shared_data_env_override(tmp_path, monkeypatch):
    target = tmp_path / "custom_shared"
    target.mkdir()
    monkeypatch.setenv("CATALOGMX_SHARED_DATA", str(target))
    assert sd.get_shared_data_root() == target.resolve()


def test_shared_data_default_package_location(monkeypatch):
    monkeypatch.delenv("CATALOGMX_SHARED_DATA", raising=False)
    root = sd.get_shared_data_root()
    expected = Path(sd.__file__).resolve().parents[1] / "shared-data"
    assert root == expected
    assert root.exists()


def test_shared_data_missing_raises(monkeypatch):
    monkeypatch.delenv("CATALOGMX_SHARED_DATA", raising=False)

    def _always_false(self):
        return False

    monkeypatch.setattr(sd.Path, "exists", _always_false, raising=True)
    with pytest.raises(FileNotFoundError):
        sd.get_shared_data_root()
