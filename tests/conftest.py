"""Pytest configuration and fixtures for confluence-integration tests."""

import os
import tempfile
from collections.abc import Generator
from datetime import datetime
from typing import Any
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def temp_env_file() -> Generator[str, None, None]:
    """Create a temporary .env file for testing.

    Yields:
        Path to the temporary .env file
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write("CONFLUENCE_URL=https://test.atlassian.net\n")
        f.write("CONFLUENCE_EMAIL=test@example.com\n")
        f.write("CONFLUENCE_API_TOKEN=test_token_12345678\n")
        f.write("CONFLUENCE_SPACE_KEY=TEST\n")
        f.write("# Comment line\n")
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def clean_env() -> Generator[None, None, None]:
    """Clean environment variables before and after test.

    Yields:
        None
    """
    # Store original values
    original_env = {}
    confluence_keys = [
        "CONFLUENCE_URL",
        "CONFLUENCE_EMAIL",
        "CONFLUENCE_API_TOKEN",
        "CONFLUENCE_SPACE_KEY",
    ]

    for key in confluence_keys:
        if key in os.environ:
            original_env[key] = os.environ[key]
            del os.environ[key]

    yield

    # Restore original values
    for key in confluence_keys:
        if key in os.environ:
            del os.environ[key]
    for key, value in original_env.items():
        os.environ[key] = value


@pytest.fixture
def mock_confluence_url() -> str:
    """Return a mock Confluence URL for testing.

    Returns:
        Mock Confluence URL string
    """
    return "https://test.atlassian.net"


@pytest.fixture
def mock_confluence_email() -> str:
    """Return a mock Confluence email for testing.

    Returns:
        Mock email string
    """
    return "test@example.com"


@pytest.fixture
def mock_confluence_token() -> str:
    """Return a mock Confluence API token for testing.

    Returns:
        Mock API token string
    """
    return "test_token_1234567890abcdef"


@pytest.fixture
def mock_confluence_space() -> str:
    """Return a mock Confluence space key for testing.

    Returns:
        Mock space key string
    """
    return "TEST"


@pytest.fixture
def mock_confluence_client() -> MagicMock:
    """Create a mock Confluence client for testing.

    Returns:
        Mock Confluence client
    """
    mock_client = MagicMock()

    # Mock space data
    mock_client.get_space.return_value = {
        "id": "12345",
        "key": "TEST",
        "name": "Test Space",
        "type": "global",
    }

    # Mock page creation
    mock_client.create_page.return_value = {
        "id": "67890",
        "title": "[PERMISSION TEST] 2026-06-13 10:00:00",
        "version": {"number": 1},
    }

    # Mock page read
    mock_client.get_page_by_id.return_value = {
        "id": "67890",
        "title": "[PERMISSION TEST] 2026-06-13 10:00:00",
        "body": {
            "storage": {
                "value": "<p>Test marker: <code>ORIGINAL_CONTENT_v1</code></p>"
            }
        },
        "version": {"number": 1},
    }

    # Mock page update
    mock_client.update_page.return_value = {
        "id": "67890",
        "title": "[PERMISSION TEST] 2026-06-13 10:00:00",
        "version": {"number": 2},
    }

    # Mock page deletion (no return value)
    mock_client.remove_page.return_value = None

    return mock_client


@pytest.fixture
def mock_page_data() -> dict[str, Any]:
    """Create mock page data for testing.

    Returns:
        Mock page data dictionary
    """
    return {
        "id": "12345",
        "title": "Test Page",
        "space": {"key": "TEST", "name": "Test Space"},
        "history": {
            "createdBy": {
                "username": "testuser",
                "displayName": "Test User",
                "email": "test@example.com",
                "accountId": "account123",
            },
            "createdDate": "2026-06-01T10:00:00.000Z",
        },
        "version": {
            "number": 1,
            "when": "2026-06-01T10:00:00.000Z",
        },
        "body": {
            "storage": {
                "value": "<h2>Test Content</h2><p>This is a test page.</p>"
            }
        },
    }


@pytest.fixture
def mock_pages_list(mock_page_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Create a list of mock pages for testing.

    Args:
        mock_page_data: Mock page data fixture

    Returns:
        List of mock page data dictionaries
    """
    pages = []
    for i in range(5):
        page = mock_page_data.copy()
        page["id"] = f"page_{i}"
        page["title"] = f"Test Page {i}"
        page["history"] = {
            "createdBy": {
                "username": f"user{i}",
                "displayName": f"User {i}",
                "email": f"user{i}@example.com",
                "accountId": f"account{i}",
            },
            "createdDate": f"2026-06-{i+1:02d}T10:00:00.000Z",
        }
        page["version"] = {
            "number": 1,
            "when": f"2026-06-{i+1:02d}T10:00:00.000Z",
        }
        pages.append(page)
    return pages


# Made with Bob