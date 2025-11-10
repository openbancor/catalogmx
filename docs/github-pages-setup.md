# GitHub Pages Setup for Coverage Reports

This guide explains how to set up GitHub Pages to display your test coverage reports.

## Quick Setup

### 1. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** → **Pages**
3. Under "Source", select:
   - **Deploy from a branch**
   - Branch: `gh-pages`
   - Folder: `/ (root)`
4. Click **Save**

### 2. Add Coverage Workflow

The workflow file `.github/workflows/coverage-report.yml` is already configured to:
- Run tests with coverage on every push to `main`
- Generate HTML coverage reports
- Deploy to `gh-pages` branch automatically

### 3. View Coverage Reports

After the workflow runs successfully, coverage reports will be available at:

- **Python Coverage**: `https://openbancor.github.io/catalogmx/coverage/python/`
- **TypeScript Coverage**: `https://openbancor.github.io/catalogmx/coverage/typescript/`

### 4. Add Badge to README

Update your README.md with a live coverage badge:

```markdown
[![Coverage](https://codecov.io/gh/openbancor/catalogmx/branch/main/graph/badge.svg)](https://codecov.io/gh/openbancor/catalogmx)
```

Or use a static badge:

```markdown
[![Coverage](https://img.shields.io/badge/coverage-93.78%25-brightgreen)](https://openbancor.github.io/catalogmx/coverage/python/)
```

## Advanced Configuration

### Custom Domain

To use a custom domain for GitHub Pages:

1. Create a `CNAME` file in your `gh-pages` branch root:
   ```
   docs.catalogmx.com
   ```

2. Configure DNS:
   - Add a CNAME record pointing to `openbancor.github.io`

3. Update repository Settings → Pages → Custom domain

### Coverage Badge Automation

To automatically update the coverage badge:

1. Use Codecov for dynamic badges:
   - Sign up at https://codecov.io
   - Add your repository
   - Get the badge markdown from Codecov dashboard

2. Or use GitHub Actions to update a badge in README:
   ```yaml
   - name: Update README badge
     run: |
       COVERAGE=$(cat packages/python/coverage.xml | grep -oP 'line-rate="\K[^"]+' | head -1)
       COVERAGE_PCT=$(echo "$COVERAGE * 100" | bc -l | xargs printf "%.2f")
       sed -i "s/coverage-[0-9.]*%25/coverage-${COVERAGE_PCT}%25/g" README.md
   ```

## Codecov Integration

For richer coverage insights, integrate with Codecov:

### Setup Codecov

1. Go to https://codecov.io
2. Sign in with GitHub
3. Add the `catalogmx` repository
4. Copy the upload token
5. Add token to repository secrets:
   - Settings → Secrets → Actions
   - New secret: `CODECOV_TOKEN` = `your-token`

### Add codecov.yml

Create `.codecov.yml` in repository root:

```yaml
codecov:
  require_ci_to_pass: yes

coverage:
  precision: 2
  round: down
  range: "80...100"
  
  status:
    project:
      default:
        target: 90%
        threshold: 1%
    patch:
      default:
        target: 80%

comment:
  layout: "reach,diff,flags,tree"
  behavior: default
  require_changes: false
```

## Monitoring Coverage

### GitHub Actions Summary

After each workflow run:
1. Go to Actions tab
2. Click on the workflow run
3. View coverage summary in the job output
4. Download coverage artifacts

### Coverage Trends

Track coverage over time:
- **Codecov Dashboard**: Visual graphs and trends
- **GitHub Pages**: Historical HTML reports (if archived)
- **PR Comments**: Automated coverage comparisons

## Troubleshooting

### GitHub Pages Not Updating

1. Check Actions tab for workflow errors
2. Ensure `gh-pages` branch exists
3. Verify GitHub Pages is enabled in Settings
4. Check repository visibility (public repos preferred)

### Coverage Reports Not Generating

1. Verify pytest-cov is installed
2. Check `pyproject.toml` coverage configuration
3. Ensure tests are in correct directory
4. Run locally first: `pytest --cov=catalogmx --cov-report=html`

### Badge Not Showing

1. Ensure URL is correct
2. Check badge markdown syntax
3. Clear browser cache
4. Verify repository is public (for shields.io badges)

## Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Codecov Documentation](https://docs.codecov.com/)
- [uv Documentation](https://github.com/astral-sh/uv)
- [Python Packaging Guide](https://packaging.python.org/en/latest/)

