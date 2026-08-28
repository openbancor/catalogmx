"""Contract tests for the daily dynamic-data publication workflow."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "update-dynamic-data.yml"


def test_dynamic_workflow_fails_closed_and_publishes_verified_pointer():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "ref: master" in text
    assert "cancel-in-progress: false" in text
    assert "Refusing to publish a partial refresh" in text
    assert "build_dynamic_manifest.py" in text
    assert "data-banxico-sie-dynamic-1-latest" in text
    assert 'immutable="data-banxico-sie-dynamic-1-${content_sha}"' in text
    assert 'cmp "$database" "$verify_dir/$database"' in text
    assert 'cmp "$manifest" "$verify_dir/$manifest"' in text
    assert '--latest=false' in text
    assert "reviewed_sha=$(git rev-parse HEAD)" in text
    assert "master_sha=$(git rev-parse origin/master)" in text
    assert 'if [ "$reviewed_sha" != "$master_sha" ]; then' in text


def test_dynamic_workflow_distinguishes_empty_windows_from_real_failures():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert "run_updater()" in text
    assert "[fetch] No new records" in text
    assert "[fetch] ERROR" in text
    assert "reported a partial source failure" in text
    assert (
        "run_updater Salarios python scripts/fetch_salarios_minimos_banxico.py" in text
    )


def test_dynamic_workflow_preserves_and_repairs_compatibility_channels():
    text = WORKFLOW.read_text(encoding="utf-8")

    assert 'release_matches latest' in text
    assert 'release_matches "$archive_tag"' in text
    assert 'gh release upload latest "$database" "$manifest" --clobber' in text
    assert 'gh release create latest "$database" "$manifest"' in text
    assert 'verify_release_assets latest' in text
    assert 'archive_tag="data-${data_version}"' in text
    assert 'verify_release_assets "$archive_tag"' in text

    compatibility = text.index(
        "# Compatibility channel for existing DataUpdater clients"
    )
    archive = text.index("# Human-readable dated archive")
    pointer = text.index("# Commit the resolver pointer last")
    assert compatibility < archive < pointer
