"""Regression coverage for partial Banxico transaction staging."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "update_banxico_banks.py"


def load_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("banxico_staging_cleanup", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_partial_staging_failure_removes_already_created_temp_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    module = load_module()
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    first.write_text("[]\n", encoding="utf-8")
    second.write_text("[]\n", encoding="utf-8")

    real_stage = module._stage_bytes
    calls = 0

    def fail_second_stage(destination: Path, payload: bytes) -> Path:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated staging failure")
        return real_stage(destination, payload)

    monkeypatch.setattr(module, "_stage_bytes", fail_second_stage)

    with pytest.raises(OSError, match="simulated staging failure"):
        module.write_json_transaction(
            [(first, [{"new": 1}]), (second, [{"new": 2}])]
        )

    assert first.read_text(encoding="utf-8") == "[]\n"
    assert second.read_text(encoding="utf-8") == "[]\n"
    assert list(tmp_path.glob(".*.tmp")) == []
