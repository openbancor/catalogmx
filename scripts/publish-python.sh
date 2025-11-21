#!/bin/bash
# Publishing script for catalogmx Python package to PyPI
# Usage: ./scripts/publish-python.sh

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

# Check if we're in the repository root
if [ ! -f "packages/python/pyproject.toml" ]; then
    error "Must run from repository root"
fi

info "Starting Python package publication to PyPI..."

# Navigate to Python package
cd packages/python

# Get current version
VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
info "Publishing version: $VERSION"

# Step 1: Clean previous builds
info "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info catalogmx.egg-info
success "Cleaned"

# Step 2: Run tests
info "Running tests..."
if ! pytest tests/ --cov=catalogmx --cov-branch -q; then
    error "Tests failed! Fix tests before publishing."
fi
success "All tests passed"

# Step 3: Check code coverage
info "Checking coverage..."
COVERAGE=$(pytest tests/ --cov=catalogmx --cov-branch --cov-report=term | grep "TOTAL" | awk '{print $NF}' | sed 's/%//')
if [ -n "$COVERAGE" ] && [ "${COVERAGE%.*}" -lt 90 ]; then
    warning "Coverage is below 90% (${COVERAGE}%)"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        error "Aborted by user"
    fi
fi
success "Coverage check passed"

# Step 4: Format check
info "Checking code format..."
if ! black --check catalogmx/ >/dev/null 2>&1; then
    warning "Code is not formatted. Running black..."
    black catalogmx/
fi
success "Code format OK"

# Step 5: Lint check
info "Running linter..."
if ! ruff check catalogmx/ --quiet; then
    warning "Linting issues found. Fix them and try again."
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        error "Aborted by user"
    fi
fi
success "Linting passed"

# Step 6: Build package
info "Building package..."
if ! python -m build; then
    error "Build failed!"
fi
success "Package built successfully"

# Step 7: Check package
info "Checking package integrity..."
if ! python -m twine check dist/*; then
    error "Package check failed!"
fi
success "Package check passed"

# Step 8: Show package contents
info "Package contents:"
ls -lh dist/

# Step 9: Confirm publication
warning "Ready to publish catalogmx v${VERSION} to PyPI"
echo "Package files:"
ls -1 dist/
echo ""
read -p "Proceed with publication? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    error "Publication cancelled by user"
fi

# Step 10: Upload to PyPI
info "Uploading to PyPI..."
if ! python -m twine upload dist/*; then
    error "Upload to PyPI failed!"
fi

success "Successfully published catalogmx v${VERSION} to PyPI! 🎉"
info "Verify at: https://pypi.org/project/catalogmx/${VERSION}/"

# Return to repo root
cd ../..

success "Python package publication complete!"
