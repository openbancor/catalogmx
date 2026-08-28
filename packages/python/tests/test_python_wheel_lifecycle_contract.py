"""Static guards for the Python code-wheel/data lifecycle boundary."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PYPROJECT = ROOT / "packages" / "python" / "pyproject.toml"
WHEEL_WORKFLOW = ROOT / ".github" / "workflows" / "python-wheel-data.yml"
CONTRACT = ROOT / "packages" / "python" / "catalogmx" / "data" / "dataset_contract.json"
PACKAGE_DYNAMIC_DB = ROOT / "packages" / "python" / "catalogmx" / "data" / "mexico_dynamic.sqlite3"


def test_dynamic_sqlite_is_declared_noncanonical_bootstrap_package_data() -> None:
    assert PACKAGE_DYNAMIC_DB.is_file()
    pyproject = PYPROJECT.read_text(encoding="utf-8")
    assert '"data/*.sqlite3"' in pyproject
    assert '"data/*.db"' not in pyproject

    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    dynamic = contract["datasets"]["banxico.sie_dynamic"]
    assert dynamic["bootstrap"] == {
        "kind": "file",
        "package_path": "data/mexico_dynamic.sqlite3",
        "role": "offline-fallback",
    }


def test_clean_wheel_gate_proves_bootstrap_precedence() -> None:
    workflow = WHEEL_WORKFLOW.read_text(encoding="utf-8")
    assert "catalogmx/data/mexico_dynamic.sqlite3" in workflow
    assert "Use packaged bootstrap in clean offline wheel" in workflow
    assert "Prefer verified dynamic release over packaged bootstrap" in workflow
    assert "Reuse verified dynamic cache offline" in workflow
