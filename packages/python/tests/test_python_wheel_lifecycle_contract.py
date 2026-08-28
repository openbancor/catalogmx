"""Static guards for the Python code-wheel/data lifecycle boundary."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PYPROJECT = ROOT / "packages" / "python" / "pyproject.toml"
WHEEL_WORKFLOW = ROOT / ".github" / "workflows" / "python-wheel-data.yml"
PACKAGE_DYNAMIC_DB = ROOT / "packages" / "python" / "catalogmx" / "data" / "mexico_dynamic.sqlite3"


def test_dynamic_sqlite_is_not_tracked_as_python_package_data() -> None:
    assert not PACKAGE_DYNAMIC_DB.exists()
    pyproject = PYPROJECT.read_text(encoding="utf-8")
    assert '"data/*.sqlite3"' not in pyproject
    assert '"data/*.db"' not in pyproject


def test_clean_wheel_gate_rejects_embedded_dynamic_database() -> None:
    workflow = WHEEL_WORKFLOW.read_text(encoding="utf-8")
    assert "catalogmx/data/mexico_dynamic.sqlite3" in workflow
    assert "Dynamic runtime data must not be embedded in the code wheel" in workflow
