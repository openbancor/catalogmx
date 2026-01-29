#!/bin/bash
# Version bump script for catalogmx
# Usage: ./scripts/bump-version.sh <new-version>
# Example: ./scripts/bump-version.sh 0.4.0

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ -z "$1" ]; then
    echo -e "${RED}Usage: $0 <new-version>${NC}"
    echo "Example: $0 0.4.0"
    exit 1
fi

NEW_VERSION="$1"

# Validate version format
if ! [[ "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${RED}Invalid version format. Use semver: X.Y.Z${NC}"
    exit 1
fi

echo -e "${YELLOW}📦 Bumping all packages to version $NEW_VERSION${NC}"
echo ""

# Current versions
PYTHON_VERSION=$(grep '^version = ' packages/python/pyproject.toml | sed 's/version = "\(.*\)"/\1/')
TS_VERSION=$(node -p "require('./packages/typescript/package.json').version" 2>/dev/null || echo "unknown")
DART_VERSION=$(grep '^version:' packages/dart/pubspec.yaml | awk '{print $2}')

echo "Current versions:"
echo "  Python:     $PYTHON_VERSION"
echo "  TypeScript: $TS_VERSION"
echo "  Dart:       $DART_VERSION"
echo ""
echo "New version: $NEW_VERSION"
echo ""

# Update Python version
echo "Updating packages/python/pyproject.toml..."
sed -i.bak "s/^version = \".*\"/version = \"$NEW_VERSION\"/" packages/python/pyproject.toml
rm -f packages/python/pyproject.toml.bak

# Update TypeScript version
echo "Updating packages/typescript/package.json..."
cd packages/typescript
npm version "$NEW_VERSION" --no-git-tag-version --allow-same-version
cd ../..

# Update Dart version
echo "Updating packages/dart/pubspec.yaml..."
sed -i.bak "s/^version: .*/version: $NEW_VERSION/" packages/dart/pubspec.yaml
rm -f packages/dart/pubspec.yaml.bak

# Verify
echo ""
echo "Verifying updates..."
NEW_PYTHON=$(grep '^version = ' packages/python/pyproject.toml | sed 's/version = "\(.*\)"/\1/')
NEW_TS=$(node -p "require('./packages/typescript/package.json').version")
NEW_DART=$(grep '^version:' packages/dart/pubspec.yaml | awk '{print $2}')

echo "  Python:     $NEW_PYTHON"
echo "  TypeScript: $NEW_TS"
echo "  Dart:       $NEW_DART"

if [ "$NEW_PYTHON" = "$NEW_VERSION" ] && [ "$NEW_TS" = "$NEW_VERSION" ] && [ "$NEW_DART" = "$NEW_VERSION" ]; then
    echo ""
    echo -e "${GREEN}✅ All packages updated to $NEW_VERSION${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review changes: git diff"
    echo "  2. Commit: git add -A && git commit -m 'chore: bump version to $NEW_VERSION'"
    echo "  3. Release: ./scripts/release.sh $NEW_VERSION"
else
    echo ""
    echo -e "${RED}❌ Version update failed${NC}"
    exit 1
fi
