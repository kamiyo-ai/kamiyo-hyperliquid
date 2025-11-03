# Contributing to KAMIYO Hyperliquid

Thank you for your interest in contributing to KAMIYO Hyperliquid! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)
- [Community](#community)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Basic understanding of FastAPI and async Python
- Familiarity with Hyperliquid ecosystem

### First-Time Contributors

Look for issues tagged with `good first issue` or `help wanted`:
- [Good First Issues](https://github.com/mizuki-tamaki/kamiyo-hyperliquid/labels/good%20first%20issue)
- [Help Wanted](https://github.com/mizuki-tamaki/kamiyo-hyperliquid/labels/help%20wanted)

## Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/kamiyo-hyperliquid.git
cd kamiyo-hyperliquid
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 5. Run Tests

```bash
pytest tests/ -v
```

### 6. Start Development Server

```bash
python api/main.py
```

## How to Contribute

### Types of Contributions

We welcome the following contributions:

1. **Bug Fixes**: Fix issues in existing code
2. **New Features**: Add new aggregators, endpoints, or functionality
3. **Documentation**: Improve README, add examples, write guides
4. **Tests**: Add or improve test coverage
5. **Performance**: Optimize existing code
6. **Refactoring**: Improve code quality and structure

### Contribution Workflow

1. **Find or Create an Issue**
   - Check existing issues
   - Create new issue if needed
   - Discuss approach before starting work

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

3. **Make Changes**
   - Write code following our standards
   - Add tests for new functionality
   - Update documentation

4. **Test Your Changes**
   ```bash
   pytest tests/ -v
   python -m pylint aggregators/ api/
   python -m black aggregators/ api/
   ```

5. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

6. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line Length**: 100 characters maximum
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Single quotes for strings, double for docstrings
- **Imports**: Grouped and sorted (stdlib, third-party, local)

### Code Formatting

We use `black` for code formatting:

```bash
black aggregators/ api/ tests/
```

### Linting

We use `pylint` for linting:

```bash
pylint aggregators/ api/ tests/
```

### Type Hints

Use type hints for all function signatures:

```python
from typing import List, Dict, Any, Optional

def fetch_exploits(limit: int = 100) -> List[Dict[str, Any]]:
    """Fetch exploits with type hints."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def process_exploit(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process raw exploit data into normalized format.

    Args:
        data: Raw exploit data from source

    Returns:
        Normalized exploit dictionary

    Raises:
        ValueError: If data is invalid
    """
    pass
```

### Naming Conventions

- **Classes**: PascalCase (e.g., `HyperliquidAPIAggregator`)
- **Functions**: snake_case (e.g., `fetch_exploits`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `MAX_RETRIES`)
- **Private**: Prefix with underscore (e.g., `_internal_method`)

## Testing Guidelines

### Test Structure

```
tests/
├── test_aggregators.py
├── test_api.py
├── test_integration.py
└── fixtures/
    └── sample_data.json
```

### Writing Tests

Use `pytest` for all tests:

```python
import pytest
from aggregators import HyperliquidAPIAggregator

def test_fetch_exploits():
    """Test exploit fetching."""
    agg = HyperliquidAPIAggregator(use_testnet=True)
    exploits = agg.fetch_exploits()

    assert isinstance(exploits, list)
    assert len(exploits) >= 0
```

### Test Coverage

- Aim for >80% code coverage
- All new features must include tests
- Bug fixes should include regression tests

```bash
pytest --cov=aggregators --cov=api tests/
```

### Integration Tests

Test the full stack:

```python
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_get_exploits_endpoint():
    """Test /exploits endpoint."""
    response = client.get("/exploits?limit=10")
    assert response.status_code == 200
    assert "exploits" in response.json()
```

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No merge conflicts

### PR Title Format

```
<type>: <description>

Types:
- feat: New feature
- fix: Bug fix
- docs: Documentation only
- style: Code style (formatting, missing semi-colons, etc.)
- refactor: Code refactoring
- test: Adding or updating tests
- chore: Maintenance tasks
```

Examples:
- `feat: Add CoinGlass liquidation aggregator`
- `fix: Correct timestamp parsing in GitHub aggregator`
- `docs: Update API documentation with examples`

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How has this been tested?

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix/feature works
- [ ] New and existing unit tests pass locally
- [ ] Any dependent changes have been merged

## Screenshots (if applicable)
Add screenshots here
```

### Review Process

1. **Automated Checks**
   - CI/CD pipeline runs tests
   - Linting and formatting checks
   - Security vulnerability scan

2. **Code Review**
   - At least one approval required
   - Address all review comments
   - Keep discussion professional

3. **Merge**
   - Squash commits for features
   - Merge commits for releases
   - Delete branch after merge

## Reporting Bugs

### Before Reporting

1. Check existing issues
2. Try latest version
3. Gather debug information

### Bug Report Template

```markdown
**Describe the bug**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen

**Screenshots**
If applicable, add screenshots

**Environment:**
 - OS: [e.g. Ubuntu 22.04]
 - Python Version: [e.g. 3.11.0]
 - KAMIYO Version: [e.g. 1.0.0]

**Additional context**
Any other relevant information
```

## Suggesting Enhancements

### Enhancement Template

```markdown
**Is your feature request related to a problem?**
Clear description of the problem

**Describe the solution you'd like**
What you want to happen

**Describe alternatives you've considered**
Other solutions you've thought about

**Additional context**
Screenshots, mockups, or examples
```

## Adding New Aggregators

### Aggregator Checklist

When adding a new data source aggregator:

1. **Create Aggregator Class**
   ```python
   from aggregators.base import BaseAggregator

   class NewSourceAggregator(BaseAggregator):
       def __init__(self):
           super().__init__("new_source")

       def fetch_exploits(self) -> List[Dict[str, Any]]:
           # Implementation
           pass
   ```

2. **Add Tests**
   - Unit tests for parsing
   - Integration tests for API calls
   - Mock external dependencies

3. **Update Documentation**
   - Add to README data sources table
   - Document any required API keys
   - Add usage examples

4. **Register Aggregator**
   - Add to `aggregators/__init__.py`
   - Update orchestrator configuration

## Development Tips

### Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing API Locally

```bash
# Start server with hot reload
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Test endpoint
curl http://localhost:8000/exploits?limit=5
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Add new field"

# Apply migration
alembic upgrade head
```

## Community

### Getting Help

- **GitHub Discussions**: Ask questions and discuss ideas
- **Issues**: Report bugs and request features
- **Email**: info@kamiyo.ai for private inquiries

### Communication Guidelines

- Be respectful and inclusive
- Provide context and examples
- Search before asking
- Follow up on your issues/PRs

## Recognition

Contributors will be recognized in:
- README.md Contributors section
- Release notes
- Project website (when available)

Thank you for contributing to KAMIYO Hyperliquid!
