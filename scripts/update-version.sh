#!/bin/bash
# Version update script for catalogmx
# Updates version across all three packages (Python, TypeScript, Dart)
# Usage: ./scripts/update-version.sh <new-version>

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${BLUE}ℹ${NC} $1"; }
success() { echo -e "${GREEN}✓${NC} $1"; }
warning() { echo -e "${YELLOW}⚠${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; exit 1; }

# Check arguments
if [ $# -ne 1 ]; then
    echo "Usage: $0 <version>"
    echo "Example: $0 0.5.0"
    exit 1
fi

NEW_VERSION=$1

# Validate version format (semver)
if ! [[ $NEW_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    error "Invalid version format. Use semantic versioning: MAJOR.MINOR.PATCH (e.g., 0.5.0)"
fi

info "Updating catalogmx to version $NEW_VERSION"

# Check if we're in the repository root
if [ ! -d "packages/python" ] || [ ! -d "packages/typescript" ] || [ ! -d "packages/dart" ]; then
    error "Must run from repository root"
fi

# Get current versions
PYTHON_VERSION=$(grep '^version = ' packages/python/pyproject.toml | sed 's/version = "\(.*\)"/\1/')
TS_VERSION=$(node -p "require('./packages/typescript/package.json').version" 2>/dev/null || echo "unknown")
DART_VERSION=$(grep '^version:' packages/dart/pubspec.yaml | awk '{print $2}')

info "Current versions:"
echo "  Python:     $PYTHON_VERSION"
echo "  TypeScript: $TS_VERSION"
echo "  Dart:       $DART_VERSION"
echo ""

# Update Python version
info "Updating Python package (packages/python/pyproject.toml)..."
sed -i.bak "s/^version = \".*\"/version = \"${NEW_VERSION}\"/" packages/python/pyproject.toml
rm -f packages/python/pyproject.toml.bak
success "Python: $PYTHON_VERSION → $NEW_VERSION"

# Update TypeScript version
info "Updating TypeScript package (packages/typescript/package.json)..."
cd packages/typescript
npm version $NEW_VERSION --no-git-tag-version --allow-same-version >/dev/null 2>&1
cd ../..
success "TypeScript: $TS_VERSION → $NEW_VERSION"

# Update Dart version
info "Updating Dart package (packages/dart/pubspec.yaml)..."
sed -i.bak "s/^version: .*/version: ${NEW_VERSION}/" packages/dart/pubspec.yaml
rm -f packages/dart/pubspec.yaml.bak
success "Dart: $DART_VERSION → $NEW_VERSION"

# Show changed files
info "Changed files:"
git diff --name-only packages/python/pyproject.toml packages/typescript/package.json packages/dart/pubspec.yaml 2>/dev/null || true

echo ""
success "Version updated to $NEW_VERSION across all packages!"
echo ""
warning "Next steps:"
echo "  1. Update CHANGELOG.md for each package"
echo "  2. Review changes: git diff"
echo "  3. Commit changes: git add -A && git commit -m 'chore: bump version to $NEW_VERSION'"
echo "  4. Create tag: git tag v$NEW_VERSION"
echo "  5. Publish: ./scripts/publish-all.sh $NEW_VERSION"
