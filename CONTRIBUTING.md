# Contributing to Confluence Integration

Thank you for your interest in contributing to Confluence Integration! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- pip

### Setting Up Your Development Environment

1. **Fork and clone the repository**

```bash
git clone https://github.com/yourusername/confluence-integration.git
cd confluence-integration
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install development dependencies**

```bash
pip install -e ".[dev]"
```

## Code Quality Standards

This project follows strict code quality standards to ensure maintainability and reliability.

### Code Formatting

We use **Black** for consistent code formatting:

```bash
black confluence_integration/
```

### Linting

We use **Ruff** for fast, comprehensive linting:

```bash
# Check for issues
ruff check confluence_integration/

# Auto-fix issues where possible
ruff check --fix confluence_integration/
```

### Type Checking

We use **MyPy** for static type checking:

```bash
mypy confluence_integration/
```

### Running All Checks

Before submitting a PR, run all quality checks:

```bash
black confluence_integration/ && \
ruff check confluence_integration/ && \
mypy confluence_integration/
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=confluence_integration --cov-report=html

# Run specific test file
pytest tests/test_permissions.py
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files with `test_` prefix
- Use descriptive test function names
- Include docstrings explaining what each test validates

## Pull Request Process

1. **Create a feature branch**

```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes**
   - Write clear, concise commit messages
   - Follow the existing code style
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks**

```bash
black confluence_integration/
ruff check confluence_integration/
mypy confluence_integration/
pytest
```

4. **Commit your changes**

```bash
git add .
git commit -m "feat: add your feature description"
```

5. **Push to your fork**

```bash
git push origin feature/your-feature-name
```

6. **Create a Pull Request**
   - Provide a clear description of the changes
   - Reference any related issues
   - Ensure all CI checks pass

## Commit Message Guidelines

We follow conventional commit format:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:
```
feat: add support for custom page templates
fix: handle 404 errors in delete verification
docs: update installation instructions
```

## Versioning and Releases

This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html):

- **MAJOR** version (X.0.0): Incompatible API changes
- **MINOR** version (0.X.0): New functionality in a backward compatible manner
- **PATCH** version (0.0.X): Backward compatible bug fixes

### Version Bumping Guidelines

When making changes, determine the appropriate version bump:

1. **Breaking Changes** → MAJOR version
   - Removing or renaming public APIs
   - Changing function signatures
   - Removing CLI parameters
   - Changing default behavior in incompatible ways

2. **New Features** → MINOR version
   - Adding new classes, methods, or functions
   - Adding new CLI commands or parameters
   - Adding new optional parameters (with defaults)
   - Enhancing existing functionality without breaking changes

3. **Bug Fixes** → PATCH version
   - Fixing bugs without changing APIs
   - Documentation updates
   - Performance improvements
   - Internal refactoring

### Updating Version Numbers

When bumping versions, update in **three places**:

1. `pyproject.toml` - line 7: `version = "X.Y.Z"`
2. `confluence_integration/__init__.py` - line 42: `__version__ = "X.Y.Z"`
3. `CHANGELOG.md` - Add new version section at the top

### Changelog Maintenance

All notable changes must be documented in `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes in existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security fixes
```

**Important**: Update the changelog in the same PR as your changes, not in a separate commit.

## Code Review Process

All submissions require review. We use GitHub pull requests for this purpose. Reviewers will check:

- Code quality and style compliance
- Test coverage
- Documentation updates
- Backward compatibility
- Performance implications
- Version number updates (if applicable)
- Changelog updates (if applicable)

## Reporting Issues

When reporting issues, please include:

- Python version
- Operating system
- Confluence version (if applicable)
- Steps to reproduce
- Expected vs actual behavior
- Error messages and stack traces

## Questions?

Feel free to open an issue for questions or discussions about contributing.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.