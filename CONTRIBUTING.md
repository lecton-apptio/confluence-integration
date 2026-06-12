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

## Code Review Process

All submissions require review. We use GitHub pull requests for this purpose. Reviewers will check:

- Code quality and style compliance
- Test coverage
- Documentation updates
- Backward compatibility
- Performance implications

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