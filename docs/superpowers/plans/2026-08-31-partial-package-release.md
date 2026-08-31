# Partial Package Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish catalogmx 0.7.0 to PyPI, npm, and pub.dev while making Maven Central an explicit, later opt-in step.

**Architecture:** Keep `.github/workflows/publish.yml` as the release pipeline. Tag pushes publish the three registries by default and skip Maven; a manual run against an existing version tag can explicitly skip an already-published PyPI version or opt into Maven. The GitHub Release is gated on npm/pub.dev plus the selected PyPI/Maven outcomes and records deferred Maven status.

**Tech Stack:** GitHub Actions YAML, GitHub Environments, PyPI/npm/pub.dev OIDC, Gradle Maven Central publishing, `gh`, `actionlint` when available.

---

### Task 1: Add explicit release modes

**Files:**
- Modify: `.github/workflows/publish.yml:3-15,90-105`

- [ ] **Step 1: Add manual PyPI/Maven inputs and preflight outputs.**

Add this trigger input after the existing tag trigger:

```yaml
  workflow_dispatch:
    inputs:
      version:
        description: Version to publish from the selected ref (for example, 0.7.0)
        required: true
        type: string
      source_ref:
        description: Existing version tag to build (for example, v0.7.0)
        required: true
        type: string
      publish_pypi:
        description: Publish PyPI for this existing version tag
        required: true
        default: false
        type: boolean
      publish_maven:
        description: Publish Maven Central for this existing version tag
        required: true
        default: false
        type: boolean
```

Add `publish_maven` to the preflight outputs and a step that emits `true` only for a manual run explicitly opting into Maven:

```yaml
    outputs:
      version: ${{ steps.get-version.outputs.version }}
      publish_pypi: ${{ steps.release-mode.outputs.publish_pypi }}
      publish_maven: ${{ steps.release-mode.outputs.publish_maven }}
```

```yaml
      - name: Select Maven release mode
        id: release-mode
        run: |
          if [[ "${{ github.event_name }}" == "workflow_dispatch" && "${{ inputs.publish_maven }}" == "true" ]]; then
            echo "publish_maven=true" >> "$GITHUB_OUTPUT"
          else
            echo "publish_maven=false" >> "$GITHUB_OUTPUT"
          fi
```

- [ ] **Step 2: Verify the existing PyPI version for skip-mode recovery.**

When `publish_pypi=false`, query PyPI metadata and fail unless the requested version exists. This prevents a release from claiming PyPI completion when the skip was accidental.

- [ ] **Step 3: Remove the Maven environment and credential gate from preflight.**

Delete `environment: maven` from `preflight` and delete the `Check Maven Central credentials` step. This keeps Maven secrets unavailable to normal tag runs while preserving all Maven build and artifact verification steps.

- [ ] **Step 4: Verify the trigger and preflight structure.**

Run:

```bash
git diff --check
rg -n "workflow_dispatch|publish_maven|environment: maven|Check Maven Central credentials" .github/workflows/publish.yml
```

Expected: the input, output, and mode step exist; `environment: maven` and the credential check appear only in the Maven job after Task 2.

- [ ] **Step 5: Commit the release-mode change.**

```bash
git add .github/workflows/publish.yml
git commit -m "ci(release): make Maven publication opt-in"
```

### Task 2: Gate Maven and describe partial completion

**Files:**
- Modify: `.github/workflows/publish.yml:500-620,617-690`

- [ ] **Step 1: Gate the Maven job on the preflight output.**

Add this job-level condition to `publish-maven`:

```yaml
    needs: [publish-pubdev, preflight]
    if: needs.preflight.outputs.publish_maven == 'true'
```

Keep `environment: maven` on that job and add the fail-closed credential check there, using exactly these variables:

```yaml
      - name: Check Maven Central credentials
        env:
          MAVEN_CENTRAL_USERNAME: ${{ secrets.MAVEN_CENTRAL_USERNAME }}
          MAVEN_CENTRAL_PASSWORD: ${{ secrets.MAVEN_CENTRAL_PASSWORD }}
          MAVEN_SIGNING_KEY: ${{ secrets.MAVEN_SIGNING_KEY }}
          MAVEN_SIGNING_PASSWORD: ${{ secrets.MAVEN_SIGNING_PASSWORD }}
        run: |
          for credential in MAVEN_CENTRAL_USERNAME MAVEN_CENTRAL_PASSWORD MAVEN_SIGNING_KEY MAVEN_SIGNING_PASSWORD; do
            if [ -z "${!credential}" ]; then
              echo "Missing required Maven Central credential: $credential" >&2
              exit 1
            fi
          done
```

- [ ] **Step 2: Allow the release job to accept skipped Maven.**

Replace the current `needs` declaration and add the fail-closed condition:

```yaml
    needs: [publish-pypi, publish-npm, publish-pubdev, publish-maven]
    if: >-
      always() &&
      needs.publish-pypi.result == 'success' &&
      needs.publish-npm.result == 'success' &&
      needs.publish-pubdev.result == 'success' &&
      (needs.publish-maven.result == 'success' || needs.publish-maven.result == 'skipped')
```

- [ ] **Step 3: Make the release body and summary truthful.**

Before the release action, write the Maven status to `changelog.txt` after the existing changelog extraction:

```bash
if [ "${{ needs.publish-maven.result }}" = "skipped" ]; then
  printf '\n\nMaven Central: pending separate opt-in publication.\n' >> changelog.txt
else
  printf '\n\nMaven Central: published and verified.\n' >> changelog.txt
fi
```

Replace the unconditional Maven success line in `Post-release summary` with a conditional shell block that prints either `pending` or `published`, while retaining the PyPI, npm, pub.dev, and GitHub URLs.

- [ ] **Step 4: Commit the gating and status change.**

```bash
git add .github/workflows/publish.yml
git commit -m "ci(release): report Maven as pending when deferred"
```

- [ ] **Step 5: Add post-publication Maven Central verification.**

After a new Maven upload, poll Central until the JAR, sources, javadoc, POM, and module metadata are visible, then compare their SHA-256 digests with the verified build outputs. An existing matching release remains a skip.

### Task 3: Make failed-tag recovery safe

**Files:**
- Modify: `.github/workflows/publish.yml:5-55,375-400,520-535,640-660`

- [ ] **Step 1: Accept an explicit version for manual runs.**

For `workflow_dispatch`, read `inputs.version`, validate `^[0-9]+\\.[0-9]+\\.[0-9]+$`, require `inputs.source_ref == v${version}`, verify that the tag exists, and check that the checkout commit equals that tag. Tag pushes continue to derive the version from `GITHUB_REF`.

- [ ] **Step 2: Use the verified version output in downstream jobs.**

The Maven job and GitHub Release job must use the version output from preflight/pub.dev instead of parsing `GITHUB_REF`, and all manual-run checkouts must use `inputs.source_ref`, so a run started from `master` can recover the existing `v0.7.0` tag without changing it or using a different commit.

- [ ] **Step 3: Fix npm tarball path resolution.**

Set `npm_package="./release/catalogmx-${VERSION}.tgz"` and assert `test -f "$npm_package"` before calculating its digest or publishing. The explicit `./` prevents npm from treating the path as a GitHub package spec.

- [ ] **Step 4: Commit the recovery fix.**

```bash
git add .github/workflows/publish.yml docs/superpowers/specs/2026-08-31-partial-package-release-design.md docs/superpowers/plans/2026-08-31-partial-package-release.md
git commit -m "fix(release): recover existing tags with verified npm artifact"
```

### Task 4: Validate, review, merge, and publish

**Files:**
- Test: `.github/workflows/publish.yml`
- Review: exact release workflow commit and resulting PR head

- [ ] **Step 1: Run local workflow validation.**

Run:

```bash
if command -v actionlint >/dev/null 2>&1; then actionlint .github/workflows/publish.yml; fi
git diff --check origin/master...HEAD
```

Expected: no YAML/actionlint errors and no whitespace errors.

- [ ] **Step 2: Run the existing release-equivalent package checks.**

Run the repository's Python, TypeScript, Dart, and Kotlin checks from `AGENTS.md`, recording all results. The workflow-only change must not alter package source or versions.

- [ ] **Step 3: Create and verify the review receipt.**

Use `reviewctl` with the project policy and a bounded workflow excerpt; verify the persisted receipt against the exact commit. A missing or unavailable receipt is not approval.

- [ ] **Step 4: Push the branch and create the PR.**

```bash
git push -u origin codex/partial-publish
gh pr create --base master --head codex/partial-publish --title "ci(release): publish non-Maven registries independently" --body-file <reviewed-body-file>
```

- [ ] **Step 5: Merge only after exact-head CI and substantive review are green.**

Record the merged commit SHA, fetch `origin/master`, and confirm it contains both workflow commits.

- [ ] **Step 6: Create and push `v0.7.0`, then monitor the run.**

For a new release, create and push the tag only after merge:

```bash
git tag -a v0.7.0 <merged-sha> -m "Release v0.7.0"
git push origin v0.7.0
gh run list --workflow publish.yml --limit 1
```

For the already-existing `v0.7.0` tag, run the merged workflow from the `master` ref with `version=0.7.0`, `source_ref=v0.7.0`, and `publish_maven=false`; do not force-update the tag:

```bash
gh workflow run publish.yml --ref master -f version=0.7.0 -f source_ref=v0.7.0 -f publish_maven=false
```

Expected: PyPI, npm, and pub.dev succeed; Maven is `skipped`; the GitHub Release says Maven is pending. Do not run the Maven opt-in until its four secrets and Central Portal namespace are ready.
