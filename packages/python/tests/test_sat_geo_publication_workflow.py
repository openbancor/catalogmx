"""Contract tests for SAT/geo push publication."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "publish-reference-data.yml"

EXPECTED_DATASETS = (
    "inegi.ageeml",
    "sat.carta_porte",
    "sat.cfdi_4",
    "sat.comercio_exterior",
    "sat.nomina_1_2",
    "sepomex.codigos_postales",
)


def test_reference_publication_matrix_covers_all_runtime_file_datasets():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "resolver-file-datasets:" in text
    assert "fail-fast: false" in text
    assert "max-parallel: 2" in text
    for dataset_id in EXPECTED_DATASETS:
        assert f"dataset_id: {dataset_id}" in text


def test_reference_publication_validates_contract_before_pointer_mutation():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "python scripts/render_dataset_contract.py --check" in text
    assert ".dataset.format == $format" in text
    assert ".dataset.mount_path == $mount" in text
    assert "reviewed_sha=$(git rev-parse HEAD)" in text
    assert "master_sha=$(git rev-parse origin/master)" in text
    assert 'if [ "$reviewed_sha" != "$master_sha" ]; then' in text
    assert "bash scripts/publish_dataset_release.sh" in text
    assert '--target "$reviewed_sha"' in text
    assert "gh release upload" not in text
    assert "--clobber" not in text
