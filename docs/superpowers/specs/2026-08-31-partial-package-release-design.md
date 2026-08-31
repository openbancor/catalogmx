# Partial Package Release Design

**Status:** Approved for implementation

## Goal

Publish catalogmx `0.7.0` to PyPI, npm, and pub.dev while leaving Maven Central explicitly pending, without allowing missing Maven credentials to block or falsely mark the three completed registries as a failed release.

The existing `v0.6.0` tag and its failed legacy workflow are historical and are not modified or republished by this change.

## Architecture

`.github/workflows/publish.yml` remains the single release workflow. Tag pushes default to the three non-Maven registries. A manual `workflow_dispatch` input named `publish_maven` enables the Maven job later, using the same tag and the existing immutable-artifact checks. The preflight job always builds and verifies all package artifacts, but Maven credentials are checked only by the Maven job when that job is enabled.

The GitHub Release is created after PyPI, npm, and pub.dev succeed, provided Maven either succeeds or is intentionally skipped. Its body reports the three published registries and says Maven is pending when skipped. A later manual run can update the same release after the Maven job succeeds, even when recovering an existing tag from the default branch.

## Workflow behavior

- `push` tags matching `v*.*.*` set `publish_maven=false`.
- `workflow_dispatch` exposes required `version` and `source_ref` inputs plus a required boolean `publish_maven`, defaulting to `false`; `source_ref` must be exactly `v${version}` and resolve to an existing tag. This supports recovering a failed existing tag without rewriting it or building bytes from a different branch.
- Preflight outputs the selected Maven mode and does not require Maven secrets.
- `publish-maven` runs only when the output is `true`, uses environment `maven`, and fails closed if any of the four Maven secrets is absent.
- `create-release` requires successful PyPI, npm, and pub.dev jobs plus either successful or skipped Maven. It writes an explicit Maven status to the release notes.
- Existing registry checks remain authoritative: an existing version with different bytes fails, while an exact match is skipped.

## Security and failure handling

OIDC remains the authentication mechanism for PyPI, npm, and pub.dev. Maven secrets are scoped to the `maven` environment and are not exposed to tag-triggered runs while Maven is deferred. A failure in any of the three requested registries prevents the GitHub Release. A skipped Maven job is not a failure, but is visible in the release notes and summary.

The npm publish path uses an explicit `./release/...tgz` path. Without the `./` prefix, npm interprets a relative string such as `release/catalogmx-0.7.0.tgz` as a GitHub package spec and attempts an SSH Git lookup.

Manual recovery checkouts use `source_ref` and archive `HEAD`, so all verified artifacts and the release metadata come from the same immutable tag commit.

## Verification

The change will be checked with YAML/actionlint validation where available, the repository's relevant CI checks, a verified review receipt for the exact commit, and a post-merge tag/workflow run. The tag is not pushed until the merged workflow and provider configuration are ready.
