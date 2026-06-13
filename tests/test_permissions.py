"""Tests for ConfluencePermissions class."""

from unittest.mock import MagicMock, patch

import pytest

from confluence_integration.permissions import ConfluencePermissions, TestResult


class TestTestResult:
    """Tests for TestResult dataclass."""

    def test_init_success(self) -> None:
        """Test TestResult initialization with success."""
        result = TestResult(
            test_name="CREATE",
            passed=True,
            message="Successfully created page",
            data={"page_id": "12345"},
        )
        assert result.test_name == "CREATE"
        assert result.passed is True
        assert result.message == "Successfully created page"
        assert result.data == {"page_id": "12345"}
        assert result.error is None

    def test_init_error(self) -> None:
        """Test TestResult initialization with error."""
        result = TestResult(
            test_name="CREATE",
            passed=False,
            message="Failed to create page",
            error="Permission denied",
        )
        assert result.test_name == "CREATE"
        assert result.passed is False
        assert result.message == "Failed to create page"
        assert result.error == "Permission denied"
        assert result.data is None


class TestConfluencePermissions:
    """Tests for ConfluencePermissions class."""

    def test_init(
        self,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test ConfluencePermissions initialization."""
        validator = ConfluencePermissions(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )
        assert validator.url == mock_confluence_url
        assert validator.email == mock_confluence_email
        assert validator.api_token == mock_confluence_token
        assert validator.space_key == mock_confluence_space
        assert validator.confluence is None
        assert validator.test_page_id is None

    @patch("confluence_integration.permissions.Confluence")
    def test_initialize_client_success(
        self,
        mock_confluence_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test successful client initialization."""
        mock_client = MagicMock()
        mock_client.get_space.return_value = {
            "id": "12345",
            "key": "TEST",
            "name": "Test Space",
        }
        mock_confluence_class.return_value = mock_client

        validator = ConfluencePermissions(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )

        result = validator._initialize_client()

        assert result.passed is True
        assert result.test_name == "INITIALIZE"
        assert "Connected to space" in result.message
        assert result.data is not None
        assert result.data["space_key"] == "TEST"

    @patch("confluence_integration.permissions.Confluence")
    def test_initialize_client_failure(
        self,
        mock_confluence_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test client initialization failure."""
        mock_confluence_class.side_effect = Exception("Connection failed")

        validator = ConfluencePermissions(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )

        result = validator._initialize_client()

        assert result.passed is False
        assert result.test_name == "INITIALIZE"
        assert "Failed to initialize" in result.message
        assert result.error == "Connection failed"

    @patch("confluence_integration.permissions.Confluence")
    def test_1_create_page_success(
        self,
        mock_confluence_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test successful page creation."""
        mock_client = MagicMock()
        mock_client.create_page.return_value = {
            "id": "67890",
            "title": "[PERMISSION TEST] 2026-06-13 10:00:00",
        }
        mock_confluence_class.return_value = mock_client

        validator = ConfluencePermissions(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )
        validator.confluence = mock_client

        result = validator.test_1_create_page()

        assert result.passed is True
        assert result.test_name == "CREATE"
        assert "Successfully created page" in result.message
        assert result.data is not None
        assert result.data["page_id"] == "67890"
        assert validator.test_page_id == "67890"

    def test_1_create_page_no_client(
        self,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test page creation without initialized client."""
        validator = ConfluencePermissions(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )

        result = validator.test_1_create_page()

        assert result.passed is False
        assert result.test_name == "CREATE"
        assert "not initialized" in result.message

    @patch("confluence_integration.permissions.Confluence")
    def test_1_create_page_failure(
        self,
        mock_confluence_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test page creation failure."""
        mock_client = MagicMock()
        mock_client.create_page.side_effect = Exception("Permission denied")
        mock_confluence_class.return_value = mock_client

        validator = ConfluencePermissions(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )
        validator.confluence = mock_client

        result = validator.test_1_create_page()

        assert result.passed is False
        assert result.test_name == "CREATE"
        assert "Failed to create page" in result.message
        assert result.error == "Permission denied"

    @patch("confluence_integration.permissions.Confluence")
    def test_2_read_page_success(
        self,
        mock_confluence_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test successful page read."""
        mock_client = MagicMock()
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
        mock_confluence_class.return_value = mock_client

        validator = ConfluencePermissions(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )
        validator.confluence = mock_client
        validator.test_page_id = "67890"

        result = validator.test_2_read_page()

        assert result.passed is True
        assert result.test_name == "READ"
        assert "Successfully read page" in result.message
        assert result.data is not None
        assert result.data["content_verified"] is True

    def test_2_read_page_no_page_id(
        self,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test page read without page ID."""
        validator = ConfluencePermissions(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )
        validator.confluence = MagicMock()

        result = validator.test_2_read_page()

        assert result.passed is False
        assert result.test_name == "READ"
        assert "page not created" in result.message

    @patch("confluence_integration.permissions.Confluence")
    def test_2_read_page_content_verification_failed(
        self,
        mock_confluence_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test page read with content verification failure."""
        mock_client = MagicMock()
        mock_client.get_page_by_id.return_value = {
            "id": "67890",
            "title": "[PERMISSION TEST] 2026-06-13 10:00:00",
            "body": {"storage": {"value": "<p>Wrong content</p>"}},
            "version": {"number": 1},
        }
        mock_confluence_class.return_value = mock_client

        validator = ConfluencePermissions(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )
        validator.confluence = mock_client
        validator.test_page_id = "67890"

        result = validator.test_2_read_page()

        assert result.passed is False
        assert result.test_name == "READ"
        assert "content verification failed" in result.message

    @patch("confluence_integration.permissions.Confluence")
    def test_3_update_page_success(
        self,
        mock_confluence_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test successful page update."""
        mock_client = MagicMock()
        mock_client.update_page.return_value = {
            "id": "67890",
            "version": {"number": 2},
        }
        mock_confluence_class.return_value = mock_client

        validator = ConfluencePermissions(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )
        validator.confluence = mock_client
        validator.test_page_id = "67890"
        validator.test_page_title = "[PERMISSION TEST] 2026-06-13 10:00:00"

        result = validator.test_3_update_page()

        assert result.passed is True
        assert result.test_name == "UPDATE"
        assert "Successfully updated page" in result.message
        assert result.data is not None
        assert result.data["new_version"] == 2

    def test_3_update_page_no_page_id(
        self,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test page update without page ID."""
        validator = ConfluencePermissions(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )
        validator.confluence = MagicMock()

        result = validator.test_3_update_page()

        assert result.passed is False
        assert result.test_name == "UPDATE"
        assert "page not created" in result.message

    @patch("confluence_integration.permissions.Confluence")
    def test_4_read_verify_success(
        self,
        mock_confluence_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test successful read verification."""
        mock_client = MagicMock()
        mock_client.get_page_by_id.return_value = {
            "id": "67890",
            "title": "[PERMISSION TEST] 2026-06-13 10:00:00",
            "body": {
                "storage": {
                    "value": "<p>Test marker: <code>UPDATED_CONTENT_v2</code></p>"
                }
            },
            "version": {"number": 2},
        }
        mock_confluence_class.return_value = mock_client

        validator = ConfluencePermissions(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )
        validator.confluence = mock_client
        validator.test_page_id = "67890"

        result = validator.test_4_read_verify()

        assert result.passed is True
        assert result.test_name == "READ_VERIFY"
        assert "Successfully verified update" in result.message
        assert result.data is not None
        assert result.data["has_updated_content"] is True

    def test_4_read_verify_no_page_id(
        self,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test read verification without page ID."""
        validator = ConfluencePermissions(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )
        validator.confluence = MagicMock()

        result = validator.test_4_read_verify()

        assert result.passed is False
        assert result.test_name == "READ_VERIFY"
        assert "page not created" in result.message

    @patch("confluence_integration.permissions.Confluence")
    def test_5_delete_page_success(
        self,
        mock_confluence_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test successful page deletion."""
        mock_client = MagicMock()
        mock_client.remove_page.return_value = None
        mock_confluence_class.return_value = mock_client

        validator = ConfluencePermissions(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )
        validator.confluence = mock_client
        validator.test_page_id = "67890"
        validator.test_page_title = "[PERMISSION TEST] 2026-06-13 10:00:00"

        result = validator.test_5_delete_page()

        assert result.passed is True
        assert result.test_name == "DELETE"
        assert "Successfully deleted page" in result.message
        assert result.data is not None
        assert result.data["page_id"] == "67890"

    def test_5_delete_page_no_page_id(
        self,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test page deletion without page ID."""
        validator = ConfluencePermissions(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )
        validator.confluence = MagicMock()

        result = validator.test_5_delete_page()

        assert result.passed is False
        assert result.test_name == "DELETE"
        assert "page not created" in result.message

    @patch("confluence_integration.permissions.Confluence")
    def test_6_delete_verify_success(
        self,
        mock_confluence_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test successful deletion verification."""
        mock_client = MagicMock()
        mock_client.get_page_by_id.side_effect = Exception("404 - Page not found")
        mock_confluence_class.return_value = mock_client

        validator = ConfluencePermissions(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )
        validator.confluence = mock_client
        validator.test_page_id = "67890"

        result = validator.test_6_delete_verify()

        assert result.passed is True
        assert result.test_name == "DELETE_VERIFY"
        assert "Successfully verified page deletion" in result.message
        assert result.data is not None
        assert result.data["verified_deleted"] is True

    def test_6_delete_verify_no_page_id(
        self,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test deletion verification without page ID."""
        validator = ConfluencePermissions(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )
        validator.confluence = MagicMock()

        result = validator.test_6_delete_verify()

        assert result.passed is False
        assert result.test_name == "DELETE_VERIFY"
        assert "page not created" in result.message

    @patch("confluence_integration.permissions.Confluence")
    def test_6_delete_verify_page_still_exists(
        self,
        mock_confluence_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test deletion verification when page still exists."""
        mock_client = MagicMock()
        mock_client.get_page_by_id.return_value = {
            "id": "67890",
            "title": "[PERMISSION TEST] 2026-06-13 10:00:00",
        }
        mock_confluence_class.return_value = mock_client

        validator = ConfluencePermissions(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )
        validator.confluence = mock_client
        validator.test_page_id = "67890"

        result = validator.test_6_delete_verify()

        assert result.passed is False
        assert result.test_name == "DELETE_VERIFY"
        assert "Page still exists" in result.message

    @patch("confluence_integration.permissions.Confluence")
    def test_run_all_tests_success(
        self,
        mock_confluence_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test running all tests successfully."""
        mock_client = MagicMock()
        mock_client.get_space.return_value = {
            "id": "12345",
            "key": "TEST",
            "name": "Test Space",
        }
        mock_client.create_page.return_value = {
            "id": "67890",
            "title": "[PERMISSION TEST] 2026-06-13 10:00:00",
        }
        mock_client.get_page_by_id.side_effect = [
            # First read
            {
                "id": "67890",
                "title": "[PERMISSION TEST] 2026-06-13 10:00:00",
                "body": {
                    "storage": {
                        "value": "<p>Test marker: <code>ORIGINAL_CONTENT_v1</code></p>"
                    }
                },
                "version": {"number": 1},
            },
            # Read verify
            {
                "id": "67890",
                "title": "[PERMISSION TEST] 2026-06-13 10:00:00",
                "body": {
                    "storage": {
                        "value": "<p>Test marker: <code>UPDATED_CONTENT_v2</code></p>"
                    }
                },
                "version": {"number": 2},
            },
            # Delete verify
            Exception("404 - Page not found"),
        ]
        mock_client.update_page.return_value = {
            "id": "67890",
            "version": {"number": 2},
        }
        mock_client.remove_page.return_value = None
        mock_confluence_class.return_value = mock_client

        validator = ConfluencePermissions(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )

        results = validator.run_all_tests()

        assert results["all_passed"] is True
        assert results["summary"]["passed"] == 6
        assert results["summary"]["failed"] == 0
        assert results["summary"]["total"] == 6
        assert len(results["tests"]) == 6

    @patch("confluence_integration.permissions.Confluence")
    def test_run_all_tests_init_failure(
        self,
        mock_confluence_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test running all tests with initialization failure."""
        mock_confluence_class.side_effect = Exception("Connection failed")

        validator = ConfluencePermissions(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )

        results = validator.run_all_tests()

        assert results["all_passed"] is False
        assert results["summary"]["passed"] == 0
        assert results["summary"]["failed"] == 1
        assert results["summary"]["total"] == 1
        assert "error" in results
        assert "Failed to initialize" in results["error"]

    @patch("confluence_integration.permissions.Confluence")
    def test_run_all_tests_create_failure(
        self,
        mock_confluence_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test running all tests with create failure."""
        mock_client = MagicMock()
        mock_client.get_space.return_value = {
            "id": "12345",
            "key": "TEST",
            "name": "Test Space",
        }
        mock_client.create_page.side_effect = Exception("Permission denied")
        mock_confluence_class.return_value = mock_client

        validator = ConfluencePermissions(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )

        results = validator.run_all_tests()

        assert results["all_passed"] is False
        assert results["summary"]["failed"] >= 1
        # Should stop after create failure
        assert len(results["tests"]) == 1


# Made with Bob