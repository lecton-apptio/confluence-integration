# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-06-13

### Added
- **ConfluenceReader class** for reading and filtering Confluence pages
- **PageInfo dataclass** to store page metadata (id, title, author, dates, version, URL, content)
- Date range filtering for pages with `--start-date` and `--end-date` CLI parameters (default: last 30 days)
- Author filtering with `--authors` CLI parameter (comma-separated list)
- File export functionality with `--output-dir` parameter
- Support for Markdown and JSON export formats via `--format` parameter
- HTML to Markdown conversion for readable page exports
- `read` subcommand to CLI for reading and exporting pages
- API methods:
  - `ConfluenceReader.get_pages()` - Fetch pages with filtering
  - `ConfluenceReader.get_page_count()` - Count matching pages
  - `ConfluenceReader.get_space_info()` - Get space metadata

### Changed
- Updated README with comprehensive documentation for new read functionality
- Enhanced CLI with additional subcommands and parameters

## [1.0.0] - 2026-06-12

### Added
- Initial release of confluence-integration library
- **ConfluencePermissions class** for validating Confluence API permissions
- **TestResult dataclass** for storing test results
- Comprehensive permission testing:
  - Space read access validation
  - Page creation capability testing
  - Page update capability testing
  - Page deletion capability testing
  - Comment creation capability testing
  - Attachment upload capability testing
- CLI tool with `validate` subcommand
- Environment variable support (.env file)
- Type hints and py.typed marker for type safety (PEP 561)
- Modern Python packaging with pyproject.toml (PEP 621)
- GitHub Actions CI/CD pipeline:
  - Code quality checks (black, ruff, mypy)
  - Python 3.9, 3.10, 3.11, 3.12 compatibility testing
- Comprehensive documentation:
  - README.md with usage examples
  - CONTRIBUTING.md with development guidelines
  - LICENSE (MIT)
  - PRODUCTION_GRADE_IMPROVEMENTS.md with enhancement roadmap
- Development tooling:
  - Makefile for common tasks
  - Pre-configured linting and formatting
  - Type checking with mypy

### Security
- Secure credential handling via environment variables
- API token-based authentication

[Unreleased]: https://github.com/yourusername/confluence-integration/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/yourusername/confluence-integration/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/yourusername/confluence-integration/releases/tag/v1.0.0