"""Regression coverage for the generic dataset release publication protocol."""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PUBLISHER = REPO_ROOT / "scripts" / "publish_dataset_release.sh"
REFERENCE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "publish-reference-data.yml"
MAINTENANCE_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "catalog-maintenance.yml"


def test_generic_publisher_has_valid_shell_syntax_and_no_live_asset_clobber():
    subprocess.run(["bash", "-n", str(PUBLISHER)], check=True)
    text = PUBLISHER.read_text(encoding="utf-8")

    assert "--clobber" not in text
    assert text.count("--latest=false") >= 3
    assert 'cmp "$artifact" "$verify_dir/immutable/$artifact_name"' in text
    assert 'cmp "$manifest" "$verify_dir/immutable/$manifest_name"' in text
    assert 'expected_pointer=$(printf \'%s\' "$pointer" | jq -ceS \'.\')' in text
    assert "release_count()" in text
    assert "jq -sc 'length'" in text
    assert "validate_pointer_body()" in text
    assert '.release_tag == ($release_prefix + .content_sha256)' in text
    assert "verify_legacy_channel()" in text
    assert '"Automated CatalogMX data artifact. Source mirror release:"*' in text
    assert "cleanup_channel_assets()" in text
    assert 'releases/assets/${asset_id}' in text


def test_banxico_and_catalog_maintenance_share_one_publisher():
    reference = REFERENCE_WORKFLOW.read_text(encoding="utf-8")
    maintenance = MAINTENANCE_WORKFLOW.read_text(encoding="utf-8")

    invocation = "bash scripts/publish_dataset_release.sh"
    assert invocation in reference
    assert invocation in maintenance
    assert "\n          scripts/publish_dataset_release.sh" not in reference
    assert "\n            scripts/publish_dataset_release.sh" not in maintenance
    assert "gh release upload" not in reference
    assert "gh release upload" not in maintenance
    assert "--clobber" not in reference
    assert "--clobber" not in maintenance


def test_scheduled_publication_is_pinned_to_checked_out_master():
    text = MAINTENANCE_WORKFLOW.read_text(encoding="utf-8")

    assert "ref: master" in text
    assert "reviewed_sha=$(git rev-parse HEAD)" in text
    assert "master_sha=$(git rev-parse origin/master)" in text
    assert '--target "$reviewed_sha"' in text
    assert '--target "${GITHUB_SHA}"' not in text
