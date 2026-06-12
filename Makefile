.PHONY: help install install-dev clean format lint typecheck test test-cov build publish-test publish all-checks

help:  ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package
	pip install -e .

install-dev:  ## Install package with development dependencies
	pip install -e ".[dev]"

clean:  ## Remove build artifacts and cache files
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

format:  ## Format code with black
	black confluence_integration/

lint:  ## Lint code with ruff
	ruff check confluence_integration/

lint-fix:  ## Lint and auto-fix issues with ruff
	ruff check --fix confluence_integration/

typecheck:  ## Run type checking with mypy
	mypy confluence_integration/

test:  ## Run tests
	pytest

test-cov:  ## Run tests with coverage report
	pytest --cov=confluence_integration --cov-report=term-missing --cov-report=html

all-checks:  ## Run all quality checks (format, lint, typecheck, test)
	@echo "Running black..."
	black confluence_integration/
	@echo "\nRunning ruff..."
	ruff check confluence_integration/
	@echo "\nRunning mypy..."
	mypy confluence_integration/
	@echo "\nRunning tests..."
	pytest --cov=confluence_integration --cov-report=term-missing

build:  ## Build distribution packages
	python -m build

publish-test:  ## Publish to TestPyPI
	twine upload --repository testpypi dist/*

publish:  ## Publish to PyPI
	twine upload dist/*

run:  ## Run the CLI tool
	python -m confluence_integration

run-verbose:  ## Run the CLI tool with verbose output
	python -m confluence_integration --verbose
