# Confluence Integration

[![PyPI version](https://badge.fury.io/py/confluence-integration.svg)](https://badge.fury.io/py/confluence-integration)
[![Python Support](https://img.shields.io/pypi/pyversions/confluence-integration.svg)](https://pypi.org/project/confluence-integration/)
[![CI](https://github.com/yourusername/confluence-integration/workflows/CI/badge.svg)](https://github.com/yourusername/confluence-integration/actions)
[![codecov](https://codecov.io/gh/yourusername/confluence-integration/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/confluence-integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A production-grade Python library for validating Confluence API permissions through comprehensive testing. This package performs 6 distinct tests to verify Create, Read, Update, and Delete (CRUD) permissions on your Confluence space.

## Features

- ✅ **6 Comprehensive Tests**: CREATE, READ, UPDATE, READ_VERIFY, DELETE, DELETE_VERIFY
- 🔐 **Secure Authentication**: Uses Atlassian API tokens
- 📦 **Easy Integration**: Use as a library or CLI tool
- 🎯 **Detailed Results**: Get specific feedback on each permission test
- 🧹 **Auto Cleanup**: Automatically removes test pages after validation

## Installation

### From PyPI (Recommended)

```bash
pip install confluence-integration
```

### From Source (Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/confluence-integration.git
cd confluence-integration

# Install in editable mode with development dependencies
pip install -e ".[dev]"

# Or just the package
pip install -e .
```

### Verify Installation

```bash
# Check version
python -c "import confluence_integration; print(confluence_integration.__version__)"

# Run help
python -m confluence_integration --help
```

## Quick Start

### 1. Get Your Confluence API Token

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **Create API token**
3. Name it (e.g., "Confluence Integration Test")
4. Copy the token (save it securely)

### 2. Set Up Environment Variables

Create a `.env` file in your project directory:

```bash
CONFLUENCE_URL=https://your-domain.atlassian.net
CONFLUENCE_EMAIL=your.email@company.com
CONFLUENCE_API_TOKEN=your_api_token_here
CONFLUENCE_SPACE_KEY=YOUR_SPACE
```

### 3. Run the Tests

#### As a CLI Tool

```bash
# Using .env file
python -m confluence_integration

# Using command line arguments
python -m confluence_integration \
  --url https://your-domain.atlassian.net \
  --email your.email@company.com \
  --token your_api_token \
  --space YOUR_SPACE

# With verbose output
python -m confluence_integration --verbose
```

#### As a Python Library

```python
from confluence_integration import ConfluencePermissions

# Initialize validator
validator = ConfluencePermissions(
    url="https://your-domain.atlassian.net",
    email="your.email@company.com",
    api_token="your_api_token",
    space_key="YOUR_SPACE"
)

# Run all tests
results = validator.run_all_tests()

# Check results
if results["all_passed"]:
    print("✅ All permissions validated!")
    for test in results["tests"]:
        print(f"{test.test_name}: {test.message}")
else:
    print("❌ Some tests failed")
    print(f"Passed: {results['summary']['passed']}/{results['summary']['total']}")
```

## The 6 Permission Tests

### 1. CREATE Test
Creates a new test page in your Confluence space with original content marker.

**Validates**: Write permission to create new pages

### 2. READ Test
Reads the created page and verifies the content marker is present.

**Validates**: Read permission and content integrity

### 3. UPDATE Test
Updates the test page with new content and a different marker.

**Validates**: Edit/update permission on existing pages

### 4. READ_VERIFY Test
Reads the page again and confirms:
- Updated content marker is present
- Original content marker is removed
- Version number increased

**Validates**: Update was successful and readable

### 5. DELETE Test
Deletes the test page from Confluence.

**Validates**: Delete permission

### 6. DELETE_VERIFY Test
Attempts to read the deleted page (should fail with 404).

**Validates**: Page was actually deleted

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `CONFLUENCE_URL` | Yes | Confluence base URL (e.g., https://your-domain.atlassian.net) |
| `CONFLUENCE_EMAIL` | Yes | Your Atlassian account email |
| `CONFLUENCE_API_TOKEN` | Yes | API token for authentication |
| `CONFLUENCE_SPACE_KEY` | Yes | Confluence space key to test (e.g., "TEAM") |

### Command Line Arguments

```bash
python -m confluence_integration --help
```

Options:
- `--url URL` - Confluence base URL
- `--email EMAIL` - Atlassian account email
- `--token TOKEN` - API token
- `--space SPACE` - Confluence space key
- `--env PATH` - Path to custom .env file
- `--verbose, -v` - Show detailed test information

## Usage Examples

### Example 1: Basic Library Usage

```python
from confluence_integration import ConfluencePermissions

validator = ConfluencePermissions(
    url="https://apptio.atlassian.net",
    email="john.doe@apptio.com",
    api_token="ATATT3xFfGF0...",
    space_key="ENGINEERING"
)

results = validator.run_all_tests()

# Access individual test results
for test in results["tests"]:
    print(f"{test.test_name}: {'PASS' if test.passed else 'FAIL'}")
    if test.data:
        print(f"  Data: {test.data}")
```

### Example 2: Run Specific Tests

```python
from confluence_integration import ConfluencePermissions

validator = ConfluencePermissions(
    url="https://apptio.atlassian.net",
    email="john.doe@apptio.com",
    api_token="ATATT3xFfGF0...",
    space_key="ENGINEERING"
)

# Initialize connection
init_result = validator._initialize_client()
if not init_result.passed:
    print(f"Connection failed: {init_result.error}")
    exit(1)

# Run individual tests
create_result = validator.test_1_create_page()
print(f"CREATE: {create_result.message}")

read_result = validator.test_2_read_page()
print(f"READ: {read_result.message}")

# Clean up
validator.test_5_delete_page()
```

### Example 3: CLI with Custom .env File

```bash
# Use a specific .env file
python -m confluence_integration --env /path/to/production.env

# Override specific values
python -m confluence_integration \
  --env /path/to/.env \
  --space DIFFERENT_SPACE \
  --verbose
```

### Example 4: Integration in CI/CD

```python
import sys
from confluence_integration import ConfluencePermissions

def validate_confluence_access():
    """Validate Confluence access in CI/CD pipeline."""
    validator = ConfluencePermissions(
        url=os.environ["CONFLUENCE_URL"],
        email=os.environ["CONFLUENCE_EMAIL"],
        api_token=os.environ["CONFLUENCE_API_TOKEN"],
        space_key=os.environ["CONFLUENCE_SPACE_KEY"]
    )
    
    results = validator.run_all_tests()
    
    if not results["all_passed"]:
        print("❌ Confluence permission validation failed!")
        for test in results["tests"]:
            if not test.passed:
                print(f"  {test.test_name}: {test.error}")
        sys.exit(1)
    
    print("✅ Confluence permissions validated successfully")
    return True

if __name__ == "__main__":
    validate_confluence_access()
```

## Test Output

### Successful Run

```
🔍 Confluence Integration - Permission Validator
======================================================================
URL: https://your-domain.atlassian.net
Email: your.email@company.com
Space: YOUR_SPACE
======================================================================

Test Results:
----------------------------------------------------------------------
1. CREATE          ✅ PASS
   Successfully created page '[PERMISSION TEST] 2026-06-12 16:30:00'

2. READ            ✅ PASS
   Successfully read page (version 1)

3. UPDATE          ✅ PASS
   Successfully updated page to version 2

4. READ_VERIFY     ✅ PASS
   Successfully verified update (version 2)

5. DELETE          ✅ PASS
   Successfully deleted page '[PERMISSION TEST] 2026-06-12 16:30:00'

6. DELETE_VERIFY   ✅ PASS
   Successfully verified page deletion (page not found)

======================================================================
Summary: 6/6 tests passed
======================================================================

🎉 SUCCESS! All permissions validated!

Your Confluence API access is fully configured:
✅ CREATE permission verified
✅ READ permission verified
✅ UPDATE permission verified
✅ DELETE permission verified
```

### Failed Run

```
Test Results:
----------------------------------------------------------------------
1. CREATE          ❌ FAIL
   Failed to create page
   Error: 403 FORBIDDEN "Request rejected because caller cannot access Confluence"

======================================================================
Summary: 0/1 tests passed
======================================================================

❌ FAILED! Some permissions are missing or invalid.

Please check:
- API token is valid and not expired
- You have appropriate permissions in the Confluence space
- Space key is correct

Use --verbose flag for detailed error information
```

## Troubleshooting

### 403 FORBIDDEN Error

**Problem**: `403 FORBIDDEN "Request rejected because caller cannot access Confluence"`

**Solutions**:
1. Generate a new API token at https://id.atlassian.com/manage-profile/security/api-tokens
2. Verify you're using the correct email address (the one you log into Confluence with)
3. Check that you have access to the specified Confluence space
4. Ensure the space key is correct (case-sensitive)

### 404 Not Found Error

**Problem**: Space or page not found

**Solutions**:
1. Verify the space key is correct (check in Confluence URL)
2. Ensure you have permission to view the space
3. Check that the Confluence URL is correct

### Connection Timeout

**Problem**: Cannot connect to Confluence

**Solutions**:
1. Check your internet connection
2. Verify the Confluence URL is correct and accessible
3. Check if there's a firewall blocking the connection
4. Ensure you're using `https://` in the URL

## API Reference

### ConfluencePermissions Class

```python
class ConfluencePermissions:
    def __init__(self, url: str, email: str, api_token: str, space_key: str)
    def run_all_tests(self) -> Dict[str, Any]
    def test_1_create_page(self) -> TestResult
    def test_2_read_page(self) -> TestResult
    def test_3_update_page(self) -> TestResult
    def test_4_read_verify(self) -> TestResult
    def test_5_delete_page(self) -> TestResult
    def test_6_delete_verify(self) -> TestResult
```

### TestResult Dataclass

```python
@dataclass
class TestResult:
    test_name: str              # Name of the test
    passed: bool                # Whether the test passed
    message: str                # Human-readable message
    error: Optional[str]        # Error message if failed
    data: Optional[Dict]        # Additional test data
```

### Results Dictionary

```python
{
    "all_passed": bool,         # True if all tests passed
    "tests": List[TestResult],  # List of test results
    "summary": {
        "passed": int,          # Number of passed tests
        "failed": int,          # Number of failed tests
        "total": int            # Total number of tests
    }
}
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/confluence-integration.git
cd confluence-integration

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Code Quality Tools

```bash
# Format code with black
black confluence_integration/

# Lint with ruff
ruff check confluence_integration/

# Type checking with mypy
mypy confluence_integration/

# Run all checks
black confluence_integration/ && ruff check confluence_integration/ && mypy confluence_integration/
```

### Run Tests

```bash
# Run the validator
python -m confluence_integration

# Run with verbose output
python -m confluence_integration --verbose

# Run unit tests (when available)
pytest

# Run with coverage
pytest --cov=confluence_integration --cov-report=html
```

### Building and Publishing

```bash
# Build distribution packages
python -m build

# Check distribution
twine check dist/*

# Upload to PyPI (requires credentials)
twine upload dist/*
```

## Requirements

- Python >= 3.9
- atlassian-python-api >= 3.41.0

### Development Dependencies

- python-dotenv >= 1.0.0 (for .env file support)
- pytest >= 7.0.0 (testing framework)
- pytest-cov >= 4.0.0 (code coverage)
- black >= 23.0.0 (code formatter)
- ruff >= 0.1.0 (fast linter)
- mypy >= 1.0.0 (static type checker)
- types-requests >= 2.31.0 (type stubs)

All dependencies are managed in [`pyproject.toml`](pyproject.toml:1) following PEP 621 standards.

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details on:

- Setting up your development environment
- Code quality standards (Black, Ruff, MyPy)
- Running tests and coverage
- Submitting pull requests

Quick start for contributors:

```bash
# Clone and setup
git clone https://github.com/yourusername/confluence-integration.git
cd confluence-integration
pip install -e ".[dev]"

# Run all quality checks
make all-checks
```

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or contributions, please visit:
https://github.com/yourusername/confluence-integration/issues

## Changelog

### Version 1.0.0 (2026-06-12)

- Initial release
- 6 comprehensive permission tests
- CLI and library interfaces
- Environment variable and argument support
- Detailed test results and error messages
- Auto-cleanup of test pages

---

**Made with ❤️ for the Confluence community**