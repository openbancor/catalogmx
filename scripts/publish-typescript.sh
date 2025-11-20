#!/bin/bash
# Publishing script for catalogmx TypeScript package to NPM
# Usage: ./scripts/publish-typescript.sh

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
if [ ! -f "packages/typescript/package.json" ]; then
    error "Must run from repository root"
fi

info "Starting TypeScript package publication to NPM..."

# Navigate to TypeScript package
cd packages/typescript

# Get current version
VERSION=$(node -p "require('./package.json').version")
info "Publishing version: $VERSION"

# Check if logged in to NPM
if ! npm whoami >/dev/null 2>&1; then
    warning "Not logged in to NPM"
    info "Please login to NPM..."
    npm login
fi

LOGGED_IN_USER=$(npm whoami)
success "Logged in as: $LOGGED_IN_USER"

# Step 1: Clean previous builds
info "Cleaning previous builds..."
npm run clean || rm -rf dist/
success "Cleaned"

# Step 2: Install dependencies
info "Installing dependencies..."
if ! npm install; then
    error "Dependency installation failed!"
fi
success "Dependencies installed"

# Step 3: Run linter
info "Running linter..."
if ! npm run lint; then
    warning "Linting issues found"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        error "Aborted by user"
    fi
fi
success "Linting passed"

# Step 4: Type checking
info "Running type checker..."
if ! npm run typecheck; then
    error "Type checking failed!"
fi
success "Type checking passed"

# Step 5: Run tests
info "Running tests..."
if ! npm test; then
    error "Tests failed! Fix tests before publishing."
fi
success "All tests passed"

# Step 6: Build package
info "Building package..."
if ! npm run build; then
    error "Build failed!"
fi
success "Package built successfully"

# Step 7: Check build output
info "Checking build output..."
if [ ! -d "dist" ]; then
    error "dist/ directory not found!"
fi
success "Build output verified"

# Step 8: Dry run npm pack
info "Running npm pack (dry-run)..."
npm pack --dry-run

# Step 9: Show package contents
info "Package contents:"
ls -lh dist/ | head -20

# Step 10: Confirm publication
warning "Ready to publish catalogmx v${VERSION} to NPM"
echo ""
echo "Files to be published:"
npm pack --dry-run 2>/dev/null | tail -n +2 | head -20
echo ""
read -p "Proceed with publication? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    error "Publication cancelled by user"
fi

# Step 11: Publish to NPM
info "Publishing to NPM..."
if ! npm publish; then
    error "Publication to NPM failed!"
fi

success "Successfully published catalogmx v${VERSION} to NPM! 🎉"
info "Verify at: https://www.npmjs.com/package/catalogmx/v/${VERSION}"

# Return to repo root
cd ../..

success "TypeScript package publication complete!"
