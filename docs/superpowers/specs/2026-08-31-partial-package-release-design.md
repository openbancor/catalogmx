# Partial Package Release Design

**Status:** Approved for implementation

## Goal

Publish catalogmx `0.7.0` to PyPI, npm, and pub.dev while leaving Maven Central explicitly pending, without allowing missing Maven credentials to block or falsely mark the three completed registries as a failed release.

The existing `v0.6.0` tag and its failed legacy workflow are historical and are not modified or republished by this change.

## Architecture

`.github/workflows/publish.yml` remains the single release workflow. Tag pushes default to the three non-Maven registries. Manual `workflow_dispatch` inputs named `publish_pypi` and `publish_maven` control recovery of an existing tag: PyPI can be explicitly skipped after its artifacts are recovered from a successful tag-run and matched by SHA-256, while Maven can be enabled later using the same tag and immutable-artifact checks. The preflight job always builds and verifies all package artifacts, but registry credentials are checked only by the corresponding publication job when it is enabled.

The GitHub Release is created after PyPI, npm, and pub.dev succeed, provided Maven either succeeds or is intentionally skipped. Its body reports the three published registries and says Maven is pending when skipped. A later manual run can update the same release after the Maven job succeeds, even when recovering an existing tag from the default branch.

## Workflow behavior

- `push` tags matching `v*.*.*` set `publish_maven=false`.
- `workflow_dispatch` exposes required `version` and `source_ref` inputs plus required boolean `publish_pypi` and `publish_maven` inputs, both defaulting to `false`; `source_ref` must be exactly `v${version}` and resolve to an existing tag. When `publish_pypi=false`, `pypi_artifact_run_id` must identify a tag push at the same commit with a successful preflight. This supports recovering a failed existing tag without rewriting it or building bytes from a different branch.
- Preflight outputs the selected modes and the validated source SHA. When PyPI is disabled, it downloads the verified artifact from the identified tag run and requires every PyPI file and SHA-256 digest to match before allowing npm/pub.dev recovery to proceed. Downstream jobs check out that SHA rather than re-resolving the tag.
- `publish-maven` runs only when the output is `true`, uses environment `maven`, and fails closed if any of the four Maven secrets is absent.
- `publish-npm` and `publish-pubdev` can continue when PyPI is intentionally skipped, but not when preflight or any enabled upstream job fails. `create-release` requires successful npm and pub.dev plus successful or intentionally skipped PyPI/Maven. It writes explicit registry status to the release notes.
- Existing registry checks remain authoritative: an existing version with different or malformed bytes fails, while an exact match is skipped. A new PyPI upload is polled and rechecked against the verified distributions before the release job can proceed.

## Security and failure handling

OIDC remains the authentication mechanism for PyPI, npm, and pub.dev. Maven secrets are scoped to the `maven` environment and are not exposed to tag-triggered runs while Maven is deferred. A failure in any of the three requested registries prevents the GitHub Release. A skipped Maven job is not a failure, but is visible in the release notes and summary.

The npm publish path uses an explicit `./release/...tgz` path. Without the `./` prefix, npm interprets a relative string such as `release/catalogmx-0.7.0.tgz` as a GitHub package spec and attempts an SSH Git lookup. PyPI recovery is bound to a successful preflight artifact from the exact immutable tag. Maven Central publication polls until all files are visible and compares their SHA-256 digests with the verified build before reporting success.

Manual recovery preflight resolves `source_ref` once, validates its commit, and archives `HEAD`; downstream jobs use the emitted source SHA, so all verified artifacts and release metadata come from the same immutable tag commit even if a tag is later moved.

## Verification

The change will be checked with YAML/actionlint validation where available, the repository's relevant CI checks, a verified review receipt for the exact commit, and a post-merge tag/workflow run. The tag is not pushed until the merged workflow and provider configuration are ready.
