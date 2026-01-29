#!/bin/bash
# Release script for catalogmx
# Usage: ./scripts/release.sh [version]
# Example: ./scripts/release.sh 0.3.0

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get version from argument or current package versions
if [ -n "$1" ]; then
    VERSION="$1"
else
    VERSION=$(grep '^version = ' packages/python/pyproject.toml | sed 's/version = "\(.*\)"/\1/')
fi

echo -e "${YELLOW}📦 catalogmx Release Script${NC}"
echo "========================================"
echo ""

# Check current versions
PYTHON_VERSION=$(grep '^version = ' packages/python/pyproject.toml | sed 's/version = "\(.*\)"/\1/')
TS_VERSION=$(node -p "require('./packages/typescript/package.json').version" 2>/dev/null || echo "unknown")
DART_VERSION=$(grep '^version:' packages/dart/pubspec.yaml | awk '{print $2}')

echo "Current package versions:"
echo "  Python:     $PYTHON_VERSION"
echo "  TypeScript: $TS_VERSION"
echo "  Dart:       $DART_VERSION"
echo ""

# Check version consistency
if [ "$PYTHON_VERSION" != "$TS_VERSION" ] || [ "$TS_VERSION" != "$DART_VERSION" ]; then
    echo -e "${RED}❌ ERROR: Version mismatch detected!${NC}"
    echo ""
    echo "All packages must have the same version before releasing."
    echo "Please update the following files:"
    echo "  - packages/python/pyproject.toml"
    echo "  - packages/typescript/package.json"
    echo "  - packages/dart/pubspec.yaml"
    exit 1
fi

if [ "$VERSION" != "$PYTHON_VERSION" ]; then
    echo -e "${YELLOW}⚠️  Target version ($VERSION) differs from current ($PYTHON_VERSION)${NC}"
    echo ""
    echo "To update versions, modify:"
    echo "  - packages/python/pyproject.toml: version = \"$VERSION\""
    echo "  - packages/typescript/package.json: \"version\": \"$VERSION\""
    echo "  - packages/dart/pubspec.yaml: version: $VERSION"
    echo ""
    read -p "Do you want to continue with current version $PYTHON_VERSION? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    VERSION=$PYTHON_VERSION
fi

echo -e "${GREEN}✅ All versions consistent: $VERSION${NC}"
echo ""

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "${RED}❌ ERROR: You have uncommitted changes${NC}"
    echo ""
    git status --short
    echo ""
    echo "Please commit or stash your changes before releasing."
    exit 1
fi

# Check if tag already exists
if git rev-parse "v$VERSION" >/dev/null 2>&1; then
    echo -e "${RED}❌ ERROR: Tag v$VERSION already exists${NC}"
    echo ""
    echo "Existing tags:"
    git tag -l 'v*' | tail -5
    exit 1
fi

# Run tests
echo "Running tests..."
echo ""

echo "  🐍 Python tests..."
cd packages/python
if python -m pytest tests/ -q --tb=no 2>&1 | tail -1 | grep -q "passed"; then
    echo -e "  ${GREEN}✅ Python tests passed${NC}"
else
    echo -e "  ${RED}❌ Python tests failed${NC}"
    exit 1
fi
cd ../..

echo "  📘 TypeScript tests..."
cd packages/typescript
if npm test 2>&1 | grep -q "passed"; then
    echo -e "  ${GREEN}✅ TypeScript tests passed${NC}"
else
    echo -e "  ${RED}❌ TypeScript tests failed${NC}"
    exit 1
fi
cd ../..

echo "  🎯 Dart tests..."
cd packages/dart
if dart test 2>&1 | grep -q "All tests passed"; then
    echo -e "  ${GREEN}✅ Dart tests passed${NC}"
else
    echo -e "  ${RED}❌ Dart tests failed${NC}"
    exit 1
fi
cd ../..

echo ""
echo -e "${GREEN}All tests passed!${NC}"
echo ""

# Confirm release
echo "Ready to create release tag v$VERSION"
echo ""
echo "This will:"
echo "  1. Create tag v$VERSION"
echo "  2. Push tag to origin (triggers publish workflow)"
echo ""
read -p "Proceed with release? (y/N) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Release cancelled."
    exit 0
fi

# Create and push tag
echo ""
echo "Creating tag v$VERSION..."
git tag -a "v$VERSION" -m "Release v$VERSION

catalogmx version $VERSION

Packages:
- PyPI: https://pypi.org/project/catalogmx/$VERSION/
- NPM: https://www.npmjs.com/package/catalogmx/v/$VERSION
- pub.dev: https://pub.dev/packages/catalogmx/versions/$VERSION"

echo "Pushing tag to origin..."
git push origin "v$VERSION"

echo ""
echo -e "${GREEN}🎉 Release v$VERSION created successfully!${NC}"
echo ""
echo "The publish workflow will now run automatically."
echo "Monitor progress at: https://github.com/openbancor/catalogmx/actions"
echo ""
echo "Package URLs (after publish completes):"
echo "  - PyPI: https://pypi.org/project/catalogmx/"
echo "  - NPM: https://www.npmjs.com/package/catalogmx"
echo "  - pub.dev: https://pub.dev/packages/catalogmx"
