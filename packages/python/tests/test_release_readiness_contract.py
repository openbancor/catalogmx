"""Release-readiness contracts that must stay enforced in source control."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_packed_typescript_contract_is_blocking_ci() -> None:
    checker = REPO_ROOT / "scripts" / "check_typescript_package.mjs"
    workflow = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text()

    assert checker.is_file()
    assert "catalogmx/catalogs" in checker.read_text()
    assert "catalogmx/cfdi" in checker.read_text()
    assert "node --test scripts/process_shutdown.test.mjs" in workflow
    assert "node scripts/check_typescript_package.mjs" in workflow
    assert "api-worker-tests" in workflow


def test_python_uv_lock_is_real_and_checked() -> None:
    lock = (REPO_ROOT / "packages" / "python" / "uv.lock").read_text()
    workflow = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text()

    assert lock.startswith("version = 1\n")
    assert "uv lock --check --project packages/python" in workflow


def test_v07_migration_guide_covers_fiscal_boundaries() -> None:
    guide = (REPO_ROOT / "docs" / "guides" / "v0.7-fiscal-migration.md").read_text()

    for required_text in (
        "ultimo_sbc_mensual",
        "ultimoSbcMensual",
        'zona="general"',
        "zona: 'frontera'",
        "get_ceav_patron_rate",
        "getCEAVPatronRate",
        "1 de febrero",
        "Modalidad 10",
        "legacy_unverified",
        "#97",
    ):
        assert required_text in guide
