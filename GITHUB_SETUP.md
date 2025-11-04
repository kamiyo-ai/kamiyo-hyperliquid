# GitHub Repository Setup Guide
## Creating the Dual Repository Structure for kamiyo.ai

This guide walks through setting up the GitHub organization and repositories for the open source + commercial dual-use strategy.

---

## Overview

We're creating two repositories:
1. **Public:** `kamiyo-ai/kamiyo-hyperliquid` (open source)
2. **Private:** `kamiyo-ai/kamiyo-platform` (commercial features)

---

## Step 1: Create GitHub Organization

### Option A: Create New Organization

1. Go to https://github.com/organizations/new
2. Organization account name: `kamiyo-ai`
3. Contact email: `hello@kamiyo.ai`
4. Organization plan: **Free** (upgrade later if needed)
5. Click "Create organization"

### Option B: Use Existing Organization

If you already have a GitHub organization, you can use that instead.

---

## Step 2: Create Public Repository

### Via GitHub Web Interface

1. Go to https://github.com/organizations/kamiyo-ai/repositories/new
2. Repository name: `kamiyo-hyperliquid`
3. Description: `Open source real-time exploit detection for Hyperliquid DEX`
4. Visibility: **Public**
5. Initialize: **Do NOT initialize** (we'll push existing code)
6. Click "Create repository"

### Via GitHub CLI

```bash
# Install GitHub CLI if not already installed
# https://cli.github.com/

# Login to GitHub
gh auth login

# Create public repository
gh repo create kamiyo-ai/kamiyo-hyperliquid \
  --public \
  --description "Open source real-time exploit detection for Hyperliquid DEX" \
  --homepage "https://kamiyo.ai"
```

---

## Step 3: Push Code to Public Repository

```bash
# Navigate to your local kamiyo-hyperliquid directory
cd /Users/dennisgoslar/Projekter/kamiyo-hyperliquid

# Verify you're on the main branch
git branch

# Check current remotes
git remote -v

# Add the new public repository as a remote
git remote add origin-public git@github.com:kamiyo-ai/kamiyo-hyperliquid.git

# Or use HTTPS if you prefer:
# git remote add origin-public https://github.com/kamiyo-ai/kamiyo-hyperliquid.git

# Push to the public repository
git push origin-public main

# Set upstream tracking
git branch --set-upstream-to=origin-public/main main

# Verify push was successful
git remote show origin-public
```

---

## Step 4: Configure Public Repository Settings

### Repository Settings

1. Go to https://github.com/kamiyo-ai/kamiyo-hyperliquid/settings

**General:**
- Features:
  - ✅ Issues
  - ✅ Discussions
  - ✅ Projects
  - ✅ Wiki (optional)
- Pull Requests:
  - ✅ Allow squash merging
  - ✅ Automatically delete head branches

**Branches:**
- Branch protection rule for `main`:
  - ✅ Require pull request reviews (1 approval)
  - ✅ Require status checks to pass
  - ✅ Require branches to be up to date
  - ✅ Include administrators

**Actions:**
- ✅ Allow all actions and reusable workflows

### Repository Topics

Add topics to help people discover your repository:
- `defi`
- `security`
- `monitoring`
- `hyperliquid`
- `exploit-detection`
- `blockchain`
- `python`
- `fastapi`
- `docker`
- `machine-learning`

### About Section

Edit the "About" section on the main repo page:
- Description: `Open source real-time exploit detection for Hyperliquid DEX`
- Website: `https://kamiyo.ai`
- Topics: (add the topics listed above)

---

## Step 5: Create Private Repository

### Via GitHub Web Interface

1. Go to https://github.com/organizations/kamiyo-ai/repositories/new
2. Repository name: `kamiyo-platform`
3. Description: `kamiyo.ai commercial platform - multi-protocol monitoring`
4. Visibility: **Private**
5. Initialize: ✅ Initialize with README
6. Click "Create repository"

### Via GitHub CLI

```bash
# Create private repository
gh repo create kamiyo-ai/kamiyo-platform \
  --private \
  --description "kamiyo.ai commercial platform - multi-protocol monitoring" \
  --add-readme
```

---

## Step 6: Set Up Private Repository Structure

```bash
# Clone the private repository
git clone git@github.com:kamiyo-ai/kamiyo-platform.git
cd kamiyo-platform

# Create directory structure for commercial platform
mkdir -p platform
mkdir -p aggregators
mkdir -p ml_models_advanced
mkdir -p frontend/{dashboard,admin,analytics}
mkdir -p infrastructure/{kubernetes,terraform,helm}

# Create initial README
cat > README-INTERNAL.md << 'EOF'
# kamiyo.ai Platform (Private)

**⚠️ CONFIDENTIAL - Internal Use Only**

This repository contains the proprietary commercial platform code for kamiyo.ai.

## What's Here

- **platform/** - Multi-tenant infrastructure, billing, auth
- **aggregators/** - Proprietary protocol aggregators (20+ protocols)
- **ml_models_advanced/** - Advanced ML models and trained weights
- **frontend/** - Web dashboard and admin interface
- **infrastructure/** - Kubernetes, Terraform, Helm configs

## What's Open Source

The Hyperliquid monitoring core is open source at:
https://github.com/kamiyo-ai/kamiyo-hyperliquid

## Development Setup

See DEVELOPMENT.md for setup instructions.

## License

Proprietary - All Rights Reserved
Copyright © 2025 kamiyo.ai
EOF

# Create placeholder files
touch platform/__init__.py
touch platform/config.py
touch platform/billing.py
touch platform/auth.py
touch platform/multi_tenant.py

touch aggregators/__init__.py
touch aggregators/registry.py

touch requirements-platform.txt

# Commit initial structure
git add .
git commit -m "Initial platform repository structure"
git push origin main
```

---

## Step 7: Set Up CI/CD (Public Repository)

Create GitHub Actions workflow for the public repository:

```bash
cd /Users/dennisgoslar/Projekter/kamiyo-hyperliquid

# Create .github/workflows directory
mkdir -p .github/workflows

# Create CI workflow
cat > .github/workflows/ci.yml << 'EOF'
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11']

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Cache dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov black flake8

    - name: Run linters
      run: |
        black . --check --line-length 100
        flake8 . --max-line-length=100 --ignore=E203,W503 --exclude=venv,__pycache__

    - name: Run tests
      run: |
        pytest tests/ -v --cov=. --cov-report=xml --cov-report=term

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: false

  docker:
    runs-on: ubuntu-latest
    needs: test

    steps:
    - uses: actions/checkout@v3

    - name: Build Docker image
      run: |
        docker build -t kamiyo-hyperliquid:${{ github.sha }} .

    - name: Test Docker image
      run: |
        docker run --rm kamiyo-hyperliquid:${{ github.sha }} python -c "import api.main"
EOF

# Commit and push
git add .github/workflows/ci.yml
git commit -m "Add GitHub Actions CI workflow"
git push origin-public main
```

---

## Step 8: Configure Repository Secrets

For the public repository, add these secrets:

1. Go to https://github.com/kamiyo-ai/kamiyo-hyperliquid/settings/secrets/actions
2. Click "New repository secret"

**Required secrets:**
- `CODECOV_TOKEN` (optional, for coverage reporting)
- Any API keys needed for tests (if applicable)

**Note:** Don't store production credentials in the public repo!

---

## Step 9: Set Up Issue Templates

```bash
cd /Users/dennisgoslar/Projekter/kamiyo-hyperliquid

# Create .github/ISSUE_TEMPLATE directory
mkdir -p .github/ISSUE_TEMPLATE

# Create bug report template
cat > .github/ISSUE_TEMPLATE/bug_report.md << 'EOF'
---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

## Describe the Bug
A clear and concise description of what the bug is.

## To Reproduce
Steps to reproduce the behavior:
1. Go to '...'
2. Run command '...'
3. See error

## Expected Behavior
A clear and concise description of what you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g. Ubuntu 22.04]
- Python Version: [e.g. 3.10.8]
- Docker Version: [e.g. 24.0.5]
- Installation Method: [Docker Compose / Manual]

## Logs
```
Paste relevant logs here
```

## Additional Context
Add any other context about the problem here.
EOF

# Create feature request template
cat > .github/ISSUE_TEMPLATE/feature_request.md << 'EOF'
---
name: Feature Request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

## Is your feature request related to a problem?
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

## Describe the solution you'd like
A clear and concise description of what you want to happen.

## Describe alternatives you've considered
A clear and concise description of any alternative solutions or features you've considered.

## Additional Context
Add any other context or screenshots about the feature request here.

## Would you like to work on this?
- [ ] Yes, I'd like to implement this feature
- [ ] No, I'm just suggesting it
EOF

# Create pull request template
cat > .github/PULL_REQUEST_TEMPLATE.md << 'EOF'
## Description
Brief description of what this PR does.

## Related Issue
Closes #(issue number)

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Code refactoring
- [ ] Performance improvement

## How Has This Been Tested?
Describe the tests you ran to verify your changes.

- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
- [ ] Any dependent changes have been merged and published

## Screenshots (if applicable)
Add screenshots to help explain your changes.
EOF

# Commit and push
git add .github/
git commit -m "Add issue and PR templates"
git push origin-public main
```

---

## Step 10: Enable GitHub Discussions

1. Go to https://github.com/kamiyo-ai/kamiyo-hyperliquid/settings
2. Scroll down to "Features"
3. Check ✅ "Discussions"
4. Click "Set up discussions"
5. Create categories:
   - **General** - General discussions
   - **Q&A** - Questions and answers
   - **Ideas** - Feature requests and ideas
   - **Show and tell** - Share your setup/usage
   - **Announcements** - Project updates

---

## Step 11: Configure Dependabot (Security)

Create `.github/dependabot.yml`:

```bash
cat > .github/dependabot.yml << 'EOF'
version: 2
updates:
  # Python dependencies
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
    commit-message:
      prefix: "deps"
      include: "scope"

  # Docker dependencies
  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
EOF

git add .github/dependabot.yml
git commit -m "Configure Dependabot for security updates"
git push origin-public main
```

---

## Step 12: Add Social Preview Image

1. Create a 1280x640px image for your repository
2. Go to https://github.com/kamiyo-ai/kamiyo-hyperliquid/settings
3. Scroll to "Social preview"
4. Upload your image

**Design suggestions:**
- Project name: "Hyperliquid Security Monitor"
- Tagline: "Detect exploits 100x faster"
- kamiyo.ai branding
- Security/monitoring theme

---

## Step 13: Update Remote Origins (Local Setup)

After creating the repositories, update your local git configuration:

```bash
cd /Users/dennisgoslar/Projekter/kamiyo-hyperliquid

# List current remotes
git remote -v

# Rename origin to origin-old (if needed)
git remote rename origin origin-old

# Set the public repo as the primary origin
git remote add origin git@github.com:kamiyo-ai/kamiyo-hyperliquid.git

# Set upstream tracking
git branch --set-upstream-to=origin/main main

# Verify
git remote -v
git remote show origin
```

---

## Step 14: Verify Setup

Run these checks to ensure everything is configured correctly:

```bash
# 1. Check remote configuration
git remote -v
# Should show:
# origin    git@github.com:kamiyo-ai/kamiyo-hyperliquid.git (fetch)
# origin    git@github.com:kamiyo-ai/kamiyo-hyperliquid.git (push)

# 2. Check you can push
git push origin main

# 3. Check GitHub Actions
# Visit: https://github.com/kamiyo-ai/kamiyo-hyperliquid/actions
# Verify CI workflow runs successfully

# 4. Check repository visibility
# Public repo: https://github.com/kamiyo-ai/kamiyo-hyperliquid
# Private repo: https://github.com/kamiyo-ai/kamiyo-platform

# 5. Check branch protection
# Visit: https://github.com/kamiyo-ai/kamiyo-hyperliquid/settings/branches
# Verify main branch is protected
```

---

## Next Steps

After completing the GitHub setup:

1. **Update Documentation Links**
   - Replace all `mizuki-tamaki/kamiyo-hyperliquid` references with `kamiyo-ai/kamiyo-hyperliquid`
   - Update URLs in README, docs, CONTRIBUTING.md

2. **Set Up Domain & Website**
   - Register `kamiyo.ai` domain (if not already registered)
   - Set up landing page at https://kamiyo.ai
   - Configure docs subdomain: https://docs.kamiyo.ai

3. **Create Social Accounts**
   - Twitter: @kamiyo_ai
   - Discord: discord.gg/kamiyo
   - Email: hello@kamiyo.ai, support@kamiyo.ai, licensing@kamiyo.ai

4. **Begin Day 2 of Integration Plan**
   - Implement billing system (Stripe)
   - Create multi-protocol aggregator registry
   - Build advanced ML models

---

## Troubleshooting

### Issue: Permission Denied when pushing

```bash
# Ensure SSH key is added to GitHub
ssh -T git@github.com

# If using HTTPS, configure credentials
git config --global credential.helper store
```

### Issue: Branch protection prevents push

```bash
# Create a branch and PR instead
git checkout -b feature/your-change
git push origin feature/your-change
# Then create PR on GitHub
```

### Issue: GitHub Actions failing

1. Check the Actions tab: https://github.com/kamiyo-ai/kamiyo-hyperliquid/actions
2. Review the error logs
3. Ensure all required secrets are configured
4. Verify Python version compatibility

---

## Checklist

Use this checklist to track your progress:

- [ ] GitHub organization created (`kamiyo-ai`)
- [ ] Public repository created (`kamiyo-hyperliquid`)
- [ ] Code pushed to public repository
- [ ] Repository settings configured (branch protection, features)
- [ ] Repository topics added
- [ ] Private repository created (`kamiyo-platform`)
- [ ] Private repository structure initialized
- [ ] CI/CD workflow configured
- [ ] Issue templates created
- [ ] PR template created
- [ ] GitHub Discussions enabled
- [ ] Dependabot configured
- [ ] Local git remotes updated
- [ ] All checks passing

---

## Resources

- GitHub CLI: https://cli.github.com/
- GitHub Actions: https://docs.github.com/en/actions
- Branch Protection: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches
- Dependabot: https://docs.github.com/en/code-security/dependabot

---

**Setup complete! You're now ready to continue with Day 2 of the integration plan.**

[Back to Integration Plan](KAMIYO_INTEGRATION_PLAN.md) • [README](README.md)
