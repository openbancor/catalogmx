#!/bin/bash
# Version management script for catalogmx
#
# Usage:
#   ./scripts/version.sh                    # Show current versions
#   ./scripts/version.sh patch              # Bump patch (0.4.0 -> 0.4.1)
#   ./scripts/version.sh minor              # Bump minor (0.4.0 -> 0.5.0)
#   ./scripts/version.sh major              # Bump major (0.4.0 -> 1.0.0)
#   ./scripts/version.sh 0.5.0              # Set specific version
#   ./scripts/version.sh --check            # Check version consistency
#
# All packages are updated together:
#   - packages/python/pyproject.toml
#   - packages/typescript/package.json
#   - packages/dart/pubspec.yaml
#   - packages/kotlin/build.gradle.kts

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# File paths
PYTHON_FILE="$PROJECT_ROOT/packages/python/pyproject.toml"
TS_FILE="$PROJECT_ROOT/packages/typescript/package.json"
DART_FILE="$PROJECT_ROOT/packages/dart/pubspec.yaml"
KOTLIN_FILE="$PROJECT_ROOT/packages/kotlin/build.gradle.kts"

# Get current versions
get_python_version() {
    grep '^version = ' "$PYTHON_FILE" | sed 's/version = "\(.*\)"/\1/'
}

get_ts_version() {
    node -p "require('$TS_FILE').version" 2>/dev/null || echo "unknown"
}

get_dart_version() {
    grep '^version:' "$DART_FILE" | awk '{print $2}'
}

get_kotlin_version() {
    grep '^version = ' "$KOTLIN_FILE" | sed 's/version = "\(.*\)"/\1/'
}

# Parse version components
parse_version() {
    local version="$1"
    MAJOR=$(echo "$version" | cut -d. -f1)
    MINOR=$(echo "$version" | cut -d. -f2)
    PATCH=$(echo "$version" | cut -d. -f3)
}

# Bump version
bump_version() {
    local version="$1"
    local type="$2"

    parse_version "$version"

    case "$type" in
        major)
            MAJOR=$((MAJOR + 1))
            MINOR=0
            PATCH=0
            ;;
        minor)
            MINOR=$((MINOR + 1))
            PATCH=0
            ;;
        patch)
            PATCH=$((PATCH + 1))
            ;;
    esac

    echo "$MAJOR.$MINOR.$PATCH"
}

# Update Python version
update_python() {
    local version="$1"
    sed -i '' "s/^version = \".*\"/version = \"$version\"/" "$PYTHON_FILE"
}

# Update TypeScript version
update_typescript() {
    local version="$1"
    # Use node to update JSON properly
    node -e "
        const fs = require('fs');
        const pkg = require('$TS_FILE');
        pkg.version = '$version';
        fs.writeFileSync('$TS_FILE', JSON.stringify(pkg, null, 2) + '\n');
    "
}

# Update Dart version
update_dart() {
    local version="$1"
    sed -i '' "s/^version: .*/version: $version/" "$DART_FILE"
}

# Update Kotlin version
update_kotlin() {
    local version="$1"
    sed -i '' "s/^version = \".*\"/version = \"$version\"/" "$KOTLIN_FILE"
}

# Show current versions
show_versions() {
    local py_ver=$(get_python_version)
    local ts_ver=$(get_ts_version)
    local dart_ver=$(get_dart_version)
    local kotlin_ver=$(get_kotlin_version)

    echo -e "${CYAN}📦 catalogmx versions${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "  Python:     ${BLUE}$py_ver${NC}"
    echo -e "  TypeScript: ${BLUE}$ts_ver${NC}"
    echo -e "  Dart:       ${BLUE}$dart_ver${NC}"
    echo -e "  Kotlin:     ${BLUE}$kotlin_ver${NC}"
    echo ""

    # Check consistency
    if [ "$py_ver" = "$ts_ver" ] && [ "$ts_ver" = "$dart_ver" ] && [ "$dart_ver" = "$kotlin_ver" ]; then
        echo -e "${GREEN}✓ All versions are in sync${NC}"
        return 0
    else
        echo -e "${RED}✗ Version mismatch detected!${NC}"
        return 1
    fi
}

# Check version consistency
check_versions() {
    local py_ver=$(get_python_version)
    local ts_ver=$(get_ts_version)
    local dart_ver=$(get_dart_version)
    local kotlin_ver=$(get_kotlin_version)

    if [ "$py_ver" = "$ts_ver" ] && [ "$ts_ver" = "$dart_ver" ] && [ "$dart_ver" = "$kotlin_ver" ]; then
        echo -e "${GREEN}✓ All versions are in sync: $py_ver${NC}"
        exit 0
    else
        echo -e "${RED}✗ Version mismatch:${NC}"
        echo "  Python:     $py_ver"
        echo "  TypeScript: $ts_ver"
        echo "  Dart:       $dart_ver"
        echo "  Kotlin:     $kotlin_ver"
        exit 1
    fi
}

# Update all versions
update_all() {
    local new_version="$1"
    local current=$(get_python_version)

    echo -e "${YELLOW}Updating versions: $current → $new_version${NC}"
    echo ""

    echo -n "  Updating Python...     "
    update_python "$new_version"
    echo -e "${GREEN}✓${NC}"

    echo -n "  Updating TypeScript... "
    update_typescript "$new_version"
    echo -e "${GREEN}✓${NC}"

    echo -n "  Updating Dart...       "
    update_dart "$new_version"
    echo -e "${GREEN}✓${NC}"

    echo -n "  Updating Kotlin...     "
    update_kotlin "$new_version"
    echo -e "${GREEN}✓${NC}"

    echo ""
    echo -e "${GREEN}✓ All packages updated to $new_version${NC}"
    echo ""
    echo "Files modified:"
    echo "  - packages/python/pyproject.toml"
    echo "  - packages/typescript/package.json"
    echo "  - packages/dart/pubspec.yaml"
    echo "  - packages/kotlin/build.gradle.kts"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Review changes: git diff"
    echo "  2. Commit: git commit -am \"chore: bump version to $new_version\""
    echo "  3. Release: ./scripts/release.sh"
}

# Validate version format
validate_version() {
    local version="$1"
    if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo -e "${RED}Error: Invalid version format '$version'${NC}"
        echo "Expected format: MAJOR.MINOR.PATCH (e.g., 1.2.3)"
        exit 1
    fi
}

# Main
main() {
    cd "$PROJECT_ROOT"

    case "${1:-}" in
        ""|show)
            show_versions
            ;;
        --check|-c|check)
            check_versions
            ;;
        major|minor|patch)
            current=$(get_python_version)
            new_version=$(bump_version "$current" "$1")
            update_all "$new_version"
            ;;
        --help|-h|help)
            echo "Usage: $(basename "$0") [command]"
            echo ""
            echo "Commands:"
            echo "  (none)      Show current versions"
            echo "  patch       Bump patch version (0.4.0 → 0.4.1)"
            echo "  minor       Bump minor version (0.4.0 → 0.5.0)"
            echo "  major       Bump major version (0.4.0 → 1.0.0)"
            echo "  X.Y.Z       Set specific version"
            echo "  --check     Check version consistency"
            echo "  --help      Show this help"
            echo ""
            echo "Examples:"
            echo "  $(basename "$0")              # Show versions"
            echo "  $(basename "$0") patch        # 0.4.0 → 0.4.1"
            echo "  $(basename "$0") minor        # 0.4.0 → 0.5.0"
            echo "  $(basename "$0") 1.0.0        # Set to 1.0.0"
            ;;
        *)
            # Assume it's a version number
            validate_version "$1"
            update_all "$1"
            ;;
    esac
}

main "$@"
