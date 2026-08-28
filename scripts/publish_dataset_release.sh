#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: publish_dataset_release.sh --manifest PATH --artifact PATH --channel TAG --target SHA

Publishes one complete artifact/manifest pair under an immutable content-addressed
GitHub release, verifies the remote bytes, then atomically advances a stable
release body containing only a JSON pointer to that immutable release.
EOF
  exit 2
}

manifest=""
artifact=""
channel=""
target=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --manifest) manifest="${2:-}"; shift 2 ;;
    --artifact) artifact="${2:-}"; shift 2 ;;
    --channel) channel="${2:-}"; shift 2 ;;
    --target) target="${2:-}"; shift 2 ;;
    *) usage ;;
  esac
done

[ -n "$manifest" ] || usage
[ -n "$artifact" ] || usage
[ -n "$channel" ] || usage
[ -n "$target" ] || usage
[ -n "${GITHUB_REPOSITORY:-}" ] || { echo "GITHUB_REPOSITORY is required" >&2; exit 1; }
[ -f "$manifest" ] || { echo "Manifest not found: $manifest" >&2; exit 1; }
[ -f "$artifact" ] || { echo "Artifact not found: $artifact" >&2; exit 1; }
[[ "$channel" =~ ^[A-Za-z0-9._-]+$ ]] || { echo "Unsafe release channel: $channel" >&2; exit 1; }
[[ "$target" =~ ^[0-9a-fA-F]{40}$ ]] || { echo "Target must be a full commit SHA" >&2; exit 1; }

for command in gh jq sha256sum cmp mktemp awk sed tr sort; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "Required command is unavailable: $command" >&2
    exit 1
  }
done

dataset_id=$(jq -er '.dataset_id | select(type == "string" and length > 0)' "$manifest")
version=$(jq -er '.dataset_version | tostring | select(length > 0)' "$manifest")
artifact_name=$(jq -er '.dataset.file | select(type == "string" and length > 0)' "$manifest")
content_sha=$(jq -er '.dataset.content_sha256 | select(type == "string" and test("^[0-9a-f]{64}$"))' "$manifest")
expected_file_sha=$(jq -er '.dataset.file_sha256 | select(type == "string" and test("^[0-9a-f]{64}$"))' "$manifest")
manifest_name=$(basename "$manifest")

if [ "$(basename "$artifact")" != "$artifact_name" ]; then
  echo "Manifest artifact filename does not match supplied artifact" >&2
  exit 1
fi
actual_file_sha=$(sha256sum "$artifact" | awk '{print $1}')
if [ "$actual_file_sha" != "$expected_file_sha" ]; then
  echo "Artifact SHA-256 does not match manifest" >&2
  exit 1
fi

slug=$(printf '%s-%s' "$dataset_id" "$version" \
  | tr '[:upper:]' '[:lower:]' \
  | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//')
[ -n "$slug" ] || { echo "Cannot derive immutable release slug" >&2; exit 1; }
immutable="data-${slug}-${content_sha}"
verify_dir=$(mktemp -d)
trap 'rm -rf "$verify_dir"' EXIT

pointer=$(jq -cn \
  --arg dataset_id "$dataset_id" \
  --arg dataset_version "$version" \
  --arg release_tag "$immutable" \
  --arg content_sha256 "$content_sha" \
  --arg artifact "$artifact_name" \
  --arg manifest "$manifest_name" \
  '{
    schema_version: 1,
    dataset_id: $dataset_id,
    dataset_version: $dataset_version,
    release_tag: $release_tag,
    content_sha256: $content_sha256,
    artifact: $artifact,
    manifest: $manifest
  }')
expected_pointer=$(printf '%s' "$pointer" | jq -ceS '.')

find_release() {
  local tag="$1"
  gh api --paginate \
    "repos/${GITHUB_REPOSITORY}/releases?per_page=100" \
    --jq ".[] | select(.tag_name == \"$tag\") | {id: .id, draft: .draft, body: .body, assets: [.assets[] | {id: .id, name: .name}]}"
}

release_count() {
  local payload="$1"
  if [ -z "$payload" ]; then
    printf '0\n'
    return
  fi
  printf '%s\n' "$payload" | jq -sc 'length'
}

delete_release_record() {
  local release_json="$1"
  local tag="$2"
  local release_id
  release_id=$(printf '%s' "$release_json" | jq -r '.id')
  gh api --method DELETE "repos/${GITHUB_REPOSITORY}/releases/${release_id}"
  gh api --method DELETE "repos/${GITHUB_REPOSITORY}/git/refs/tags/${tag}" \
    >/dev/null 2>&1 || true
}

verify_legacy_channel() {
  local release_json="$1"
  local body="$2"
  case "$body" in
    "Automated CatalogMX data artifact. Source mirror release:"*) ;;
    *) return 1 ;;
  esac

  local asset_count
  asset_count=$(printf '%s' "$release_json" | jq -r '.assets | length')
  [ "$asset_count" -eq 2 ] || return 1

  local actual_names expected_names
  actual_names=$(printf '%s' "$release_json" | jq -r '.assets[].name' | sort)
  expected_names=$(printf '%s\n%s\n' "$artifact_name" "$manifest_name" | sort)
  [ "$actual_names" = "$expected_names" ] || return 1

  local legacy_dir="$verify_dir/legacy-channel"
  mkdir -p "$legacy_dir"
  gh release download "$channel" \
    --pattern "$artifact_name" \
    --pattern "$manifest_name" \
    --dir "$legacy_dir" >/dev/null

  local legacy_manifest="$legacy_dir/$manifest_name"
  local legacy_artifact="$legacy_dir/$artifact_name"
  [ -f "$legacy_manifest" ] || return 1
  [ -f "$legacy_artifact" ] || return 1
  [ "$(jq -er '.schema_version' "$legacy_manifest")" = "1" ] || return 1
  [ "$(jq -er '.dataset_id' "$legacy_manifest")" = "$dataset_id" ] || return 1
  [ "$(jq -er '.dataset_version | tostring' "$legacy_manifest")" = "$version" ] || return 1
  [ "$(jq -er '.dataset.file' "$legacy_manifest")" = "$artifact_name" ] || return 1

  local legacy_file_sha legacy_content_sha legacy_actual_sha
  legacy_file_sha=$(jq -er '.dataset.file_sha256 | select(type == "string" and test("^[0-9a-f]{64}$"))' "$legacy_manifest") || return 1
  legacy_content_sha=$(jq -er '.dataset.content_sha256 | select(type == "string" and test("^[0-9a-f]{64}$"))' "$legacy_manifest") || return 1
  [ -n "$legacy_content_sha" ] || return 1
  legacy_actual_sha=$(sha256sum "$legacy_artifact" | awk '{print $1}')
  [ "$legacy_actual_sha" = "$legacy_file_sha" ]
}

cleanup_channel_assets() {
  local release_json="$1"
  local asset_id
  while IFS= read -r asset_id; do
    [ -n "$asset_id" ] || continue
    gh api --method DELETE "repos/${GITHUB_REPOSITORY}/releases/assets/${asset_id}"
  done < <(printf '%s' "$release_json" | jq -r '.assets[]?.id')
}

previous_pointer=""
previous_release_tag=""
legacy_channel=false
channel_release=$(find_release "$channel")
channel_count=$(release_count "$channel_release")
if [ "$channel_count" -gt 1 ]; then
  echo "Expected at most one live channel release for $channel" >&2
  exit 1
fi
if [ "$channel_count" -eq 1 ]; then
  channel_draft=$(printf '%s' "$channel_release" | jq -r '.draft')
  if [ "$channel_draft" = "true" ]; then
    echo "Stable channel exists only as a draft release; refusing publication" >&2
    exit 1
  fi
  previous_body=$(printf '%s' "$channel_release" | jq -r '.body // empty')
  if previous_pointer=$(printf '%s' "$previous_body" | jq -ceS '.' 2>/dev/null); then
    previous_release_tag=$(printf '%s' "$previous_pointer" | jq -r '.release_tag // empty')
  elif verify_legacy_channel "$channel_release" "$previous_body"; then
    legacy_channel=true
    previous_pointer=""
  else
    echo "Stable channel is neither a valid pointer nor a verified legacy CatalogMX release" >&2
    exit 1
  fi
fi

notes="CatalogMX data artifact for ${dataset_id} ${version}. Semantic content SHA-256: ${content_sha}. The manifest records authority/provenance and integrity metadata. This data release is independent from library package versions."

verify_immutable() {
  rm -rf "$verify_dir/immutable"
  mkdir -p "$verify_dir/immutable"
  if ! gh release download "$immutable" \
    --pattern "$artifact_name" \
    --pattern "$manifest_name" \
    --dir "$verify_dir/immutable"; then
    return 1
  fi
  [ -f "$verify_dir/immutable/$artifact_name" ] || return 1
  [ -f "$verify_dir/immutable/$manifest_name" ] || return 1
  cmp "$artifact" "$verify_dir/immutable/$artifact_name" || return 1
  cmp "$manifest" "$verify_dir/immutable/$manifest_name" || return 1
  remote_sha=$(jq -r '.dataset.content_sha256 // empty' "$verify_dir/immutable/$manifest_name")
  [ "$remote_sha" = "$content_sha" ]
}

create_immutable() {
  gh release create "$immutable" "$artifact" "$manifest" \
    --title "$dataset_id $version $content_sha" \
    --notes "$notes" \
    --target "$target" \
    --latest=false
}

immutable_release=$(find_release "$immutable")
immutable_count=$(release_count "$immutable_release")
if [ "$immutable_count" -gt 1 ]; then
  echo "Expected at most one immutable release for $immutable" >&2
  exit 1
fi
if [ "$immutable_count" -eq 1 ]; then
  immutable_draft=$(printf '%s' "$immutable_release" | jq -r '.draft')
  if [ "$immutable_draft" = "true" ]; then
    if [ "$previous_release_tag" = "$immutable" ]; then
      echo "Stable channel points to a draft immutable release; refusing mutation" >&2
      exit 1
    fi
    delete_release_record "$immutable_release" "$immutable"
    create_immutable
  elif ! verify_immutable; then
    if [ "$previous_release_tag" = "$immutable" ]; then
      echo "Live immutable release is incomplete; refusing to mutate the current channel target" >&2
      exit 1
    fi
    delete_release_record "$immutable_release" "$immutable"
    create_immutable
  fi
else
  create_immutable
fi

if ! verify_immutable; then
  echo "Immutable release is incomplete or does not match the built artifact" >&2
  exit 1
fi

pointer_already_current=false
if [ "$previous_pointer" = "$expected_pointer" ]; then
  pointer_already_current=true
elif [ "$channel_count" -eq 1 ]; then
  gh release edit "$channel" \
    --title "$dataset_id $version (latest)" \
    --notes "$pointer" \
    --target "$target" \
    --latest=false
else
  gh release create "$channel" \
    --title "$dataset_id $version (latest)" \
    --notes "$pointer" \
    --target "$target" \
    --latest=false
fi

# Stable channels are metadata pointers only. Legacy publishers stored the
# artifact and manifest on the channel itself; remove those assets only after a
# verified immutable release exists and the pointer is current, so migration is
# failure-safe. The same cleanup repairs any later accidental channel assets.
if [ "$channel_count" -eq 1 ]; then
  cleanup_channel_assets "$channel_release"
fi

if [ "$pointer_already_current" = "true" ]; then
  echo "$dataset_id unchanged and verified: $content_sha"
  exit 0
fi
if [ "$legacy_channel" = "true" ]; then
  echo "$dataset_id legacy channel migrated to verified pointer: $content_sha"
fi

if [ -n "${GITHUB_STEP_SUMMARY:-}" ]; then
  {
    echo "## Dataset publication"
    echo
    echo "- Dataset: \`$dataset_id\` $version"
    echo "- Target SHA: \`$target\`"
    echo "- Content SHA-256: \`$content_sha\`"
    echo "- Immutable tag: \`$immutable\`"
    echo "- Channel tag: \`$channel\`"
    echo "- Channel publication: metadata pointer only"
  } >> "$GITHUB_STEP_SUMMARY"
fi
