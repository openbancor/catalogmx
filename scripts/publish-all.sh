#!/bin/bash
# Unified publishing script for catalogmx across all platforms
# Publishes to PyPI, NPM, and pub.dev
# Usage: ./scripts/publish-all.sh <version>

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Helper functions
info() { echo -e "${BLUE}ℹ${NC} $1"; }
success() { echo -e "${GREEN}✓${NC} $1"; }
warning() { echo -e "${YELLOW}⚠${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; exit 1; }
banner() { echo -e "${MAGENTA}╔═══════════════════════════════════════════════════════════╗${NC}"; echo -e "${MAGENTA}║${NC} $1"; echo -e "${MAGENTA}╚═══════════════════════════════════════════════════════════╝${NC}"; }

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

banner "📦 catalogmx Unified Publishing - v${NEW_VERSION}"

# Check if we're in the repository root
if [ ! -d "packages/python" ] || [ ! -d "packages/typescript" ] || [ ! -d "packages/dart" ]; then
    error "Must run from repository root"
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    warning "You have uncommitted changes!"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        error "Aborted by user"
    fi
fi

# ============================================================================
# STEP 1: Update versions in all packages
# ============================================================================

banner "Step 1: Updating versions"

info "Updating Python package version..."
sed -i "s/^version = \".*\"/version = \"${NEW_VERSION}\"/" packages/python/pyproject.toml
success "Python: $NEW_VERSION"

info "Updating TypeScript package version..."
cd packages/typescript
npm version $NEW_VERSION --no-git-tag-version
cd ../..
success "TypeScript: $NEW_VERSION"

info "Updating Dart package version..."
sed -i "s/^version: .*/version: ${NEW_VERSION}/" packages/dart/pubspec.yaml
success "Dart: $NEW_VERSION"

# ============================================================================
# STEP 2: Run preflight checks
# ============================================================================

banner "Step 2: Preflight checks"

# Python checks
info "Checking Python package..."
cd packages/python
if ! pytest tests/ -q --tb=no; then
    error "Python tests failed!"
fi
success "Python tests passed"
cd ../..

# TypeScript checks
info "Checking TypeScript package..."
cd packages/typescript
npm install --silent
if ! npm test --silent; then
    error "TypeScript tests failed!"
fi
if ! npm run build --silent; then
    error "TypeScript build failed!"
fi
success "TypeScript tests and build passed"
cd ../..

# Dart checks
info "Checking Dart package..."
cd packages/dart
dart pub get --quiet
if ! dart analyze --quiet; then
    error "Dart analysis failed!"
fi
if ! dart test; then
    error "Dart tests failed!"
fi
success "Dart tests passed"
cd ../..

success "All preflight checks passed!"

# ============================================================================
# STEP 3: Commit version changes
# ============================================================================

banner "Step 3: Committing version changes"

git add packages/python/pyproject.toml
git add packages/typescript/package.json
git add packages/typescript/package-lock.json
git add packages/dart/pubspec.yaml

if ! git diff --cached --quiet; then
    git commit -m "chore: bump version to ${NEW_VERSION}"
    success "Version changes committed"
else
    info "No version changes to commit"
fi

# ============================================================================
# STEP 4: Create git tag
# ============================================================================

banner "Step 4: Creating git tag"

TAG_NAME="v${NEW_VERSION}"

if git rev-parse "$TAG_NAME" >/dev/null 2>&1; then
    warning "Tag $TAG_NAME already exists"
else
    git tag -a "$TAG_NAME" -m "Release version ${NEW_VERSION}"
    success "Created tag: $TAG_NAME"
fi

# ============================================================================
# STEP 5: Publish to PyPI
# ============================================================================

banner "Step 5: Publishing to PyPI"

read -p "Publish to PyPI? (Y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    warning "Skipping PyPI publication"
else
    info "Publishing to PyPI..."
    if ./scripts/publish-python.sh; then
        success "Published to PyPI successfully"
    else
        error "PyPI publication failed!"
    fi
fi

# ============================================================================
# STEP 6: Publish to NPM
# ============================================================================

banner "Step 6: Publishing to NPM"

read -p "Publish to NPM? (Y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    warning "Skipping NPM publication"
else
    info "Publishing to NPM..."
    if ./scripts/publish-typescript.sh; then
        success "Published to NPM successfully"
    else
        error "NPM publication failed!"
    fi
fi

# ============================================================================
# STEP 7: Publish to pub.dev
# ============================================================================

banner "Step 7: Publishing to pub.dev"

read -p "Publish to pub.dev? (Y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    warning "Skipping pub.dev publication"
else
    info "Publishing to pub.dev..."
    if ./scripts/publish-dart.sh; then
        success "Published to pub.dev successfully"
    else
        error "pub.dev publication failed!"
    fi
fi

# ============================================================================
# STEP 8: Push to GitHub
# ============================================================================

banner "Step 8: Pushing to GitHub"

read -p "Push commits and tags to GitHub? (Y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    warning "Skipping GitHub push"
    info "Remember to push manually: git push && git push --tags"
else
    info "Pushing to GitHub..."
    git push
    git push --tags
    success "Pushed to GitHub"
fi

# ============================================================================
# COMPLETION
# ============================================================================

banner "🎉 Publication Complete!"

echo ""
echo -e "${GREEN}Successfully published catalogmx v${NEW_VERSION} to:${NC}"
echo -e "  ${CYAN}•${NC} PyPI:    https://pypi.org/project/catalogmx/${NEW_VERSION}/"
echo -e "  ${CYAN}•${NC} NPM:     https://www.npmjs.com/package/catalogmx/v/${NEW_VERSION}"
echo -e "  ${CYAN}•${NC} pub.dev: https://pub.dev/packages/catalogmx/versions/${NEW_VERSION}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  1. Create GitHub Release: https://github.com/openbancor/catalogmx/releases/new"
echo "  2. Verify installations work:"
echo "     • pip install catalogmx==${NEW_VERSION}"
echo "     • npm install catalogmx@${NEW_VERSION}"
echo "     • flutter pub add catalogmx:${NEW_VERSION}"
echo "  3. Update documentation if needed"
echo "  4. Announce release"
echo ""

success "All done! 🚀"
