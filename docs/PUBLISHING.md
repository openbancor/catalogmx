# Publishing Guide - catalogmx

Complete guide for publishing **catalogmx** to PyPI, NPM, and pub.dev.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Publishing to PyPI (Python)](#publishing-to-pypi-python)
4. [Publishing to NPM (TypeScript)](#publishing-to-npm-typescript)
5. [Publishing to pub.dev (Dart/Flutter)](#publishing-to-pubdev-dartflutter)
6. [Unified Publishing Workflow](#unified-publishing-workflow)
7. [Version Management](#version-management)
8. [CI/CD Automation](#cicd-automation)
9. [Troubleshooting](#troubleshooting)

---

## Overview

**catalogmx** is published to three package repositories:

| Platform | Repository | Package URL | Current Version |
|----------|-----------|-------------|-----------------|
| Python | PyPI | https://pypi.org/project/catalogmx/ | 0.3.0 |
| TypeScript | NPM | https://www.npmjs.com/package/catalogmx | 0.3.0 |
| Dart/Flutter | pub.dev | https://pub.dev/packages/catalogmx | 0.4.0 |

**Important**: All three packages must maintain version parity and identical APIs.

---

## Prerequisites

### Required Accounts

1. **PyPI Account**: https://pypi.org/account/register/
2. **NPM Account**: https://www.npmjs.com/signup
3. **pub.dev Account**: Uses Google account via https://pub.dev/

### Required Tools

```bash
# Python publishing tools
pip install build twine

# Node.js and NPM (for TypeScript)
# Download from: https://nodejs.org/

# Dart SDK (for Flutter package)
# Download from: https://dart.dev/get-dart
```

### API Tokens Setup

#### PyPI Token
```bash
# Create token at: https://pypi.org/manage/account/token/
# Save to ~/.pypirc
cat > ~/.pypirc << 'EOF'
[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...YOUR_TOKEN_HERE
EOF
chmod 600 ~/.pypirc
```

#### NPM Token
```bash
# Login to NPM
npm login

# Or use token
npm config set //registry.npmjs.org/:_authToken YOUR_TOKEN_HERE
```

#### pub.dev Authentication
```bash
# First-time publishing requires interactive login
dart pub login
```

---

## Publishing to PyPI (Python)

### Pre-Publication Checklist

- [ ] Version updated in `packages/python/pyproject.toml`
- [ ] CHANGELOG updated with new version
- [ ] All tests passing: `pytest tests/ --cov=catalogmx --cov-branch`
- [ ] Coverage >= 90%
- [ ] Code formatted: `black catalogmx/` and `ruff check catalogmx/`
- [ ] Documentation updated
- [ ] Git tag created

### Manual Publishing Steps

```bash
cd packages/python

# 1. Clean previous builds
rm -rf dist/ build/ *.egg-info

# 2. Run tests
pytest tests/ --cov=catalogmx --cov-branch --cov-report=term-missing

# 3. Build package
python -m build

# 4. Check package
python -m twine check dist/*

# 5. Test upload (optional - uses test.pypi.org)
python -m twine upload --repository testpypi dist/*

# 6. Production upload
python -m twine upload dist/*
```

### Using the Script

```bash
# From repository root
./scripts/publish-python.sh
```

### Verify Publication

```bash
# Install from PyPI
pip install catalogmx --upgrade

# Test import
python -c "from catalogmx import validate_rfc; print(validate_rfc('XAXX010101000'))"
```

---

## Publishing to NPM (TypeScript)

### Pre-Publication Checklist

- [ ] Version updated in `packages/typescript/package.json`
- [ ] CHANGELOG updated
- [ ] All tests passing: `npm test`
- [ ] Build successful: `npm run build`
- [ ] Linting passed: `npm run lint`
- [ ] Type checking passed: `npm run typecheck`
- [ ] Documentation updated
- [ ] Git tag created

### Manual Publishing Steps

```bash
cd packages/typescript

# 1. Clean previous builds
npm run clean

# 2. Install dependencies
npm install

# 3. Run tests
npm test

# 4. Build package
npm run build

# 5. Check package contents
npm pack --dry-run

# 6. Publish to NPM
npm publish
```

### Using the Script

```bash
# From repository root
./scripts/publish-typescript.sh
```

### Verify Publication

```bash
# Install from NPM
npm install catalogmx@latest

# Test import
node -e "const {validateRFC} = require('catalogmx'); console.log(validateRFC('XAXX010101000'));"
```

---

## Publishing to pub.dev (Dart/Flutter)

### Pre-Publication Checklist

- [ ] Version updated in `packages/dart/pubspec.yaml`
- [ ] CHANGELOG.md updated with new version
- [ ] All tests passing: `dart test`
- [ ] Analysis passed: `dart analyze`
- [ ] Format checked: `dart format --set-exit-if-changed .`
- [ ] Documentation complete
- [ ] Example works
- [ ] Git tag created

### Manual Publishing Steps

```bash
cd packages/dart

# 1. Run pub.dev publication checks
dart pub publish --dry-run

# 2. Review output carefully
# Check for:
# - All files included
# - No sensitive files (tokens, keys)
# - Correct version
# - Valid dependencies

# 3. Publish (requires confirmation)
dart pub publish
```

### Using the Script

```bash
# From repository root
./scripts/publish-dart.sh
```

### Verify Publication

```bash
# Install from pub.dev
flutter pub add catalogmx

# Or for Dart
dart pub add catalogmx

# Test import
dart -e "import 'package:catalogmx/catalogmx.dart'; void main() { print(validateRFC('XAXX010101000')); }"
```

---

## Unified Publishing Workflow

### Complete Release Process

Use the unified script to publish to all platforms:

```bash
# From repository root
./scripts/publish-all.sh <version>
```

Example:
```bash
./scripts/publish-all.sh 0.5.0
```

This script will:
1. ✅ Validate version format
2. ✅ Check all pre-publication requirements
3. ✅ Update versions in all packages
4. ✅ Run all tests
5. ✅ Build all packages
6. ✅ Create git tag
7. ✅ Publish to PyPI, NPM, and pub.dev
8. ✅ Push tags to GitHub

---

## Version Management

### Version Numbering

We follow **Semantic Versioning** (SemVer):

```
MAJOR.MINOR.PATCH

Example: 0.4.0
- MAJOR: Breaking changes (0 = initial development)
- MINOR: New features (backward compatible)
- PATCH: Bug fixes
```

### Updating Versions

All three packages must have the same version:

```bash
# Use the version update script
./scripts/update-version.sh 0.5.0
```

This updates:
- `packages/python/pyproject.toml`
- `packages/typescript/package.json`
- `packages/dart/pubspec.yaml`

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.4.0 | 2024-11-20 | Full catalog parity (58+ catalogs) |
| 0.3.0 | 2024-11-20 | Initial multi-platform release |

---

## CI/CD Automation

### GitHub Actions Workflows

We provide automated publishing via GitHub Actions:

#### 1. Manual Publish (workflow_dispatch)

```bash
# Trigger from GitHub UI:
# Actions → Publish Package → Run workflow
```

#### 2. Tag-based Auto-publish

```bash
# Create and push tag
git tag v0.5.0
git push origin v0.5.0

# Automatically triggers publishing
```

### Required GitHub Secrets

Configure in: **Settings → Secrets and variables → Actions**

```yaml
PYPI_API_TOKEN: pypi-AgEIcHlwaS5vcmc...
NPM_TOKEN: npm_1234567890abcdef...
```

Note: pub.dev publishing requires manual approval on first publish.

---

## Troubleshooting

### PyPI Issues

**Problem**: `twine` upload fails with 403 error
```bash
# Solution: Check token permissions
# Regenerate token at: https://pypi.org/manage/account/token/
```

**Problem**: Version already exists
```bash
# Solution: Cannot re-upload same version
# Increment version and rebuild
./scripts/update-version.sh 0.5.1
```

### NPM Issues

**Problem**: `npm publish` fails with authentication error
```bash
# Solution: Re-login
npm logout
npm login
```

**Problem**: Package name already taken
```bash
# Solution: Use scoped package
# Update package.json: "@yourorg/catalogmx"
```

### pub.dev Issues

**Problem**: First-time publishing requires verification
```bash
# Solution: Follow interactive prompts
dart pub publish
# Opens browser for Google authentication
```

**Problem**: Package validation fails
```bash
# Solution: Run dry-run and fix issues
dart pub publish --dry-run
```

### Common Issues

**Problem**: Tests failing before publish
```bash
# Python
cd packages/python && pytest tests/

# TypeScript
cd packages/typescript && npm test

# Dart
cd packages/dart && dart test
```

**Problem**: Version mismatch across packages
```bash
# Solution: Use version update script
./scripts/update-version.sh 0.5.0
```

---

## Best Practices

### Before Every Release

1. **Test Everything**
   ```bash
   # Python
   cd packages/python && pytest tests/ --cov=catalogmx

   # TypeScript
   cd packages/typescript && npm test

   # Dart
   cd packages/dart && dart test
   ```

2. **Update Documentation**
   - CHANGELOG.md (all packages)
   - README.md (if API changed)
   - Version numbers

3. **Review Changes**
   ```bash
   git log --oneline v0.3.0..HEAD
   ```

4. **Create Release Notes**
   - GitHub Release with changelog
   - Highlight breaking changes
   - Migration guide (if needed)

### After Release

1. **Verify Installation**
   ```bash
   # Test in clean environments
   pip install catalogmx
   npm install catalogmx
   flutter pub add catalogmx
   ```

2. **Update Documentation Sites**
   - GitHub README
   - Official documentation
   - Examples

3. **Announce Release**
   - GitHub Releases
   - Twitter/Social media
   - Community forums

---

## Quick Reference

### Publishing Commands

```bash
# Python
cd packages/python && python -m build && python -m twine upload dist/*

# TypeScript
cd packages/typescript && npm run build && npm publish

# Dart
cd packages/dart && dart pub publish

# All platforms
./scripts/publish-all.sh <version>
```

### Version Update

```bash
./scripts/update-version.sh 0.5.0
```

### Pre-flight Checks

```bash
./scripts/preflight-check.sh
```

---

## Support

- **Issues**: https://github.com/openbancor/catalogmx/issues
- **Discussions**: https://github.com/openbancor/catalogmx/discussions
- **Email**: luisfernando@informind.com

---

## License

BSD-2-Clause License. See [LICENSE](../LICENSE) for details.
