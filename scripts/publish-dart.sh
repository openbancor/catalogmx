#!/bin/bash
# Publishing script for catalogmx Dart/Flutter package to pub.dev
# Usage: ./scripts/publish-dart.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
info() { echo -e "${BLUE}ℹ${NC} $1"; }
success() { echo -e "${GREEN}✓${NC} $1"; }
warning() { echo -e "${YELLOW}⚠${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; exit 1; }

# Check if dart is installed
if ! command -v dart &> /dev/null; then
    error "Dart SDK not found. Install from: https://dart.dev/get-dart"
fi

# Check if we're in the repository root
if [ ! -f "packages/dart/pubspec.yaml" ]; then
    error "Must run from repository root"
fi

info "Starting Dart/Flutter package publication to pub.dev..."

# Navigate to Dart package
cd packages/dart

# Get current version
VERSION=$(grep '^version:' pubspec.yaml | awk '{print $2}')
info "Publishing version: $VERSION"

# Step 1: Get dependencies
info "Getting dependencies..."
if ! dart pub get; then
    error "Failed to get dependencies!"
fi
success "Dependencies retrieved"

# Step 2: Run analysis
info "Running dart analyze..."
if ! dart analyze; then
    error "Code analysis failed! Fix issues before publishing."
fi
success "Code analysis passed"

# Step 3: Format check
info "Checking code format..."
if ! dart format --set-exit-if-changed . >/dev/null 2>&1; then
    warning "Code is not formatted"
    info "Running dart format..."
    dart format .
fi
success "Code format OK"

# Step 4: Run tests
info "Running tests..."
if ! dart test; then
    error "Tests failed! Fix tests before publishing."
fi
success "All tests passed"

# Step 5: Dry run publication
info "Running publication dry-run..."
echo ""
if ! dart pub publish --dry-run; then
    error "Dry-run failed! Review the output above."
fi
echo ""
success "Dry-run passed"

# Step 6: Review package contents
info "Package will include these files:"
dart pub publish --dry-run 2>&1 | grep "^|" || true

# Step 7: Important checks
warning "Pre-publication checklist:"
echo "  ✓ Version updated in pubspec.yaml: $VERSION"
echo "  ✓ CHANGELOG.md updated"
echo "  ✓ All tests passing"
echo "  ✓ Code analysis clean"
echo "  ✓ No sensitive files included"
echo ""

# Step 8: Confirm publication
warning "Ready to publish catalogmx v${VERSION} to pub.dev"
echo ""
echo "IMPORTANT: This action cannot be undone!"
echo "Once published, you cannot remove a package version."
echo ""
read -p "Proceed with publication? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    error "Publication cancelled by user"
fi

# Step 9: Publish to pub.dev
info "Publishing to pub.dev..."
echo ""
info "You may be prompted to authenticate with Google..."
echo ""

if ! dart pub publish; then
    error "Publication to pub.dev failed!"
fi

success "Successfully published catalogmx v${VERSION} to pub.dev! 🎉"
info "Verify at: https://pub.dev/packages/catalogmx/versions/${VERSION}"

# Return to repo root
cd ../..

success "Dart/Flutter package publication complete!"
