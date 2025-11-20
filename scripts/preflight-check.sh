#!/bin/bash
# Pre-publication check script for catalogmx
# Runs all tests and checks before publishing
# Usage: ./scripts/preflight-check.sh

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

info() { echo -e "${BLUE}ℹ${NC} $1"; }
success() { echo -e "${GREEN}✓${NC} $1"; }
warning() { echo -e "${YELLOW}⚠${NC} $1"; }
error() { echo -e "${RED}✗${NC} $1"; }
section() { echo -e "\n${CYAN}━━━ $1 ━━━${NC}\n"; }

ERRORS=0
WARNINGS=0

# Check if we're in the repository root
if [ ! -d "packages/python" ] || [ ! -d "packages/typescript" ] || [ ! -d "packages/dart" ]; then
    error "Must run from repository root"
    exit 1
fi

section "Preflight Checks for catalogmx"

# ============================================================================
# 1. Version Consistency Check
# ============================================================================

section "1. Version Consistency"

PYTHON_VERSION=$(grep '^version = ' packages/python/pyproject.toml | sed 's/version = "\(.*\)"/\1/')
TS_VERSION=$(node -p "require('./packages/typescript/package.json').version" 2>/dev/null)
DART_VERSION=$(grep '^version:' packages/dart/pubspec.yaml | awk '{print $2}')

info "Python:     $PYTHON_VERSION"
info "TypeScript: $TS_VERSION"
info "Dart:       $DART_VERSION"

if [ "$PYTHON_VERSION" = "$TS_VERSION" ] && [ "$TS_VERSION" = "$DART_VERSION" ]; then
    success "Versions are consistent: $PYTHON_VERSION"
else
    error "Version mismatch! Run: ./scripts/update-version.sh <version>"
    ((ERRORS++))
fi

# ============================================================================
# 2. Git Status Check
# ============================================================================

section "2. Git Status"

if ! git diff-index --quiet HEAD --; then
    warning "You have uncommitted changes"
    git status --short
    ((WARNINGS++))
else
    success "Working directory is clean"
fi

# ============================================================================
# 3. Python Package Checks
# ============================================================================

section "3. Python Package"

cd packages/python

# Tests
info "Running Python tests..."
if pytest tests/ --cov=catalogmx --cov-branch -q --tb=line; then
    success "Python tests passed"

    # Coverage
    COVERAGE=$(pytest tests/ --cov=catalogmx --cov-branch --cov-report=term 2>/dev/null | grep "TOTAL" | awk '{print $NF}' | sed 's/%//')
    if [ -n "$COVERAGE" ]; then
        if [ "${COVERAGE%.*}" -ge 90 ]; then
            success "Coverage: ${COVERAGE}% (>= 90%)"
        else
            warning "Coverage: ${COVERAGE}% (< 90%)"
            ((WARNINGS++))
        fi
    fi
else
    error "Python tests failed"
    ((ERRORS++))
fi

# Code quality
info "Checking Python code quality..."
if black --check catalogmx/ >/dev/null 2>&1; then
    success "Code formatting OK (black)"
else
    warning "Code needs formatting (run: black catalogmx/)"
    ((WARNINGS++))
fi

if ruff check catalogmx/ --quiet 2>/dev/null; then
    success "Linting OK (ruff)"
else
    warning "Linting issues found (run: ruff check catalogmx/)"
    ((WARNINGS++))
fi

cd ../..

# ============================================================================
# 4. TypeScript Package Checks
# ============================================================================

section "4. TypeScript Package"

cd packages/typescript

# Dependencies
info "Installing TypeScript dependencies..."
if npm install --silent; then
    success "Dependencies installed"
else
    error "Dependency installation failed"
    ((ERRORS++))
fi

# Build
info "Building TypeScript package..."
if npm run build --silent; then
    success "Build successful"
else
    error "Build failed"
    ((ERRORS++))
fi

# Tests
info "Running TypeScript tests..."
if npm test --silent; then
    success "TypeScript tests passed"
else
    error "TypeScript tests failed"
    ((ERRORS++))
fi

# Linting
info "Checking TypeScript code quality..."
if npm run lint --silent; then
    success "Linting OK"
else
    warning "Linting issues found"
    ((WARNINGS++))
fi

# Type checking
info "Type checking..."
if npm run typecheck --silent; then
    success "Type checking passed"
else
    error "Type checking failed"
    ((ERRORS++))
fi

cd ../..

# ============================================================================
# 5. Dart Package Checks
# ============================================================================

section "5. Dart/Flutter Package"

cd packages/dart

# Dependencies
info "Getting Dart dependencies..."
if dart pub get --quiet; then
    success "Dependencies retrieved"
else
    error "Failed to get dependencies"
    ((ERRORS++))
fi

# Analysis
info "Running dart analyze..."
if dart analyze --quiet; then
    success "Code analysis passed"
else
    error "Code analysis failed"
    ((ERRORS++))
fi

# Format
info "Checking Dart code format..."
if dart format --set-exit-if-changed . >/dev/null 2>&1; then
    success "Code formatting OK"
else
    warning "Code needs formatting (run: dart format .)"
    ((WARNINGS++))
fi

# Tests
info "Running Dart tests..."
if dart test; then
    success "Dart tests passed"
else
    error "Dart tests failed"
    ((ERRORS++))
fi

# Dry run
info "Running pub.dev dry-run..."
if dart pub publish --dry-run >/dev/null 2>&1; then
    success "pub.dev dry-run passed"
else
    warning "pub.dev dry-run has warnings"
    ((WARNINGS++))
fi

cd ../..

# ============================================================================
# 6. Documentation Checks
# ============================================================================

section "6. Documentation"

# Check for required files
REQUIRED_FILES=(
    "README.md"
    "LICENSE"
    "packages/python/README.md"
    "packages/typescript/README.md"
    "packages/dart/README.md"
    "packages/python/pyproject.toml"
    "packages/typescript/package.json"
    "packages/dart/pubspec.yaml"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        success "$file exists"
    else
        error "$file is missing"
        ((ERRORS++))
    fi
done

# ============================================================================
# Summary
# ============================================================================

section "Summary"

echo ""
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    success "All checks passed! Ready to publish. 🎉"
    echo ""
    info "To publish, run: ./scripts/publish-all.sh $PYTHON_VERSION"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    warning "$WARNINGS warning(s) found. Review and proceed with caution."
    echo ""
    info "To publish anyway, run: ./scripts/publish-all.sh $PYTHON_VERSION"
    exit 0
else
    error "$ERRORS error(s) and $WARNINGS warning(s) found. Fix errors before publishing."
    echo ""
    exit 1
fi
