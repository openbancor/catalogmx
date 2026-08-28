"""Regression coverage for reviewed reference-data publication boundaries."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "publish-reference-data.yml"


def test_reference_data_publication_is_pinned_to_reviewed_master():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "branches: [master]" in text
    assert "ref: master" in text
    assert "reviewed_sha=$(git rev-parse HEAD)" in text
    assert "master_sha=$(git rev-parse origin/master)" in text
    assert '--target "$reviewed_sha"' in text
    assert '--target "${GITHUB_SHA}"' not in text
