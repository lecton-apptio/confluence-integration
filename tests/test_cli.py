"""Tests for CLI functionality."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from confluence_integration.__main__ import (
    handle_read_command,
    handle_validate_command,
    load_env_file,
    main,
)


class TestLoadEnvFile:
    """Tests for load_env_file function."""

    def test_load_env_file_success(self, temp_env_file: str, clean_env: None) -> None:
        """Test loading environment variables from file."""
        load_env_file(Path(temp_env_file))
        assert os.environ["CONFLUENCE_URL"] == "https://test.atlassian.net"
        assert os.environ["CONFLUENCE_EMAIL"] == "test@example.com"
        assert os.environ["CONFLUENCE_API_TOKEN"] == "test_token_12345678"
        assert os.environ["CONFLUENCE_SPACE_KEY"] == "TEST"

    def test_load_env_file_nonexistent(self, clean_env: None) -> None:
        """Test loading from nonexistent file does nothing."""
        load_env_file(Path("nonexistent.env"))
        assert "CONFLUENCE_URL" not in os.environ

    def test_load_env_file_default_path(self) -> None:
        """Test loading with default path when file doesn't exist."""
        # Don't use clean_env since we're testing the default behavior
        # Just verify it doesn't raise an error
        load_env_file(Path("nonexistent_default.env"))
        # Should not raise error, just silently skip


class TestHandleValidateCommand:
    """Tests for handle_validate_command function."""

    @patch("confluence_integration.permissions.ConfluencePermissions")
    @patch("builtins.print")
    def test_validate_command_success(
        self,
        mock_print: MagicMock,
        mock_permissions_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test successful validate command."""
        from confluence_integration.permissions import TestResult

        mock_validator = MagicMock()
        mock_validator.run_all_tests.return_value = {
            "all_passed": True,
            "tests": [
                TestResult(
                    test_name="CREATE",
                    passed=True,
                    message="Successfully created page",
                    data={"page_id": "12345"},
                )
            ],
            "summary": {"passed": 1, "failed": 0, "total": 1},
        }
        mock_permissions_class.return_value = mock_validator

        args = MagicMock()
        args.verbose = False

        result = handle_validate_command(
            args,
            mock_confluence_url,
            mock_confluence_email,
            mock_confluence_token,
            mock_confluence_space,
        )

        assert result == 0
        mock_validator.run_all_tests.assert_called_once()

    @patch("confluence_integration.permissions.ConfluencePermissions")
    @patch("builtins.print")
    def test_validate_command_failure(
        self,
        mock_print: MagicMock,
        mock_permissions_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test failed validate command."""
        from confluence_integration.permissions import TestResult

        mock_validator = MagicMock()
        mock_validator.run_all_tests.return_value = {
            "all_passed": False,
            "tests": [
                TestResult(
                    test_name="CREATE",
                    passed=False,
                    message="Failed to create page",
                    error="Permission denied",
                )
            ],
            "summary": {"passed": 0, "failed": 1, "total": 1},
        }
        mock_permissions_class.return_value = mock_validator

        args = MagicMock()
        args.verbose = False

        result = handle_validate_command(
            args,
            mock_confluence_url,
            mock_confluence_email,
            mock_confluence_token,
            mock_confluence_space,
        )

        assert result == 1

    @patch("confluence_integration.permissions.ConfluencePermissions")
    @patch("builtins.print")
    def test_validate_command_verbose(
        self,
        mock_print: MagicMock,
        mock_permissions_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test validate command with verbose output."""
        from confluence_integration.permissions import TestResult

        mock_validator = MagicMock()
        mock_validator.run_all_tests.return_value = {
            "all_passed": True,
            "tests": [
                TestResult(
                    test_name="CREATE",
                    passed=True,
                    message="Successfully created page",
                    data={"page_id": "12345", "page_url": "https://test.atlassian.net/..."},
                )
            ],
            "summary": {"passed": 1, "failed": 0, "total": 1},
        }
        mock_permissions_class.return_value = mock_validator

        args = MagicMock()
        args.verbose = True

        result = handle_validate_command(
            args,
            mock_confluence_url,
            mock_confluence_email,
            mock_confluence_token,
            mock_confluence_space,
        )

        assert result == 0


class TestHandleReadCommand:
    """Tests for handle_read_command function."""

    @patch("confluence_integration.reader.ConfluenceReader")
    @patch("builtins.print")
    def test_read_command_success(
        self,
        mock_print: MagicMock,
        mock_reader_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test successful read command."""
        from datetime import datetime

        from confluence_integration.reader import PageInfo

        mock_reader = MagicMock()
        mock_reader.get_space_info.return_value = {
            "id": "12345",
            "key": "TEST",
            "name": "Test Space",
            "type": "global",
        }
        mock_reader.get_pages.return_value = [
            PageInfo(
                page_id="12345",
                title="Test Page",
                space_key="TEST",
                author="test@example.com",
                author_display_name="Test User",
                created_date=datetime(2026, 6, 1, 10, 0, 0),
                modified_date=datetime(2026, 6, 2, 10, 0, 0),
                version=1,
                url="https://test.atlassian.net/wiki/spaces/TEST/pages/12345",
            )
        ]
        mock_reader_class.return_value = mock_reader

        args = MagicMock()
        args.start_date = None
        args.end_date = None
        args.authors = None
        args.include_content = False
        args.limit = 100
        args.output_dir = None

        result = handle_read_command(
            args,
            mock_confluence_url,
            mock_confluence_email,
            mock_confluence_token,
            mock_confluence_space,
        )

        assert result == 0
        mock_reader.get_pages.assert_called_once()

    @patch("confluence_integration.reader.ConfluenceReader")
    @patch("builtins.print")
    def test_read_command_with_authors(
        self,
        mock_print: MagicMock,
        mock_reader_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test read command with author filtering."""
        mock_reader = MagicMock()
        mock_reader.get_space_info.return_value = {
            "id": "12345",
            "key": "TEST",
            "name": "Test Space",
            "type": "global",
        }
        mock_reader.get_pages.return_value = []
        mock_reader_class.return_value = mock_reader

        args = MagicMock()
        args.start_date = None
        args.end_date = None
        args.authors = "user1@example.com,user2@example.com"
        args.include_content = False
        args.limit = 100
        args.output_dir = None

        result = handle_read_command(
            args,
            mock_confluence_url,
            mock_confluence_email,
            mock_confluence_token,
            mock_confluence_space,
        )

        assert result == 0
        # Verify authors were parsed correctly
        call_kwargs = mock_reader_class.call_args[1]
        assert call_kwargs["authors"] == ["user1@example.com", "user2@example.com"]

    @patch("confluence_integration.reader.ConfluenceReader")
    @patch("builtins.print")
    def test_read_command_with_dates(
        self,
        mock_print: MagicMock,
        mock_reader_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test read command with date filtering."""
        mock_reader = MagicMock()
        mock_reader.get_space_info.return_value = {
            "id": "12345",
            "key": "TEST",
            "name": "Test Space",
            "type": "global",
        }
        mock_reader.get_pages.return_value = []
        mock_reader_class.return_value = mock_reader

        args = MagicMock()
        args.start_date = "2026-05-01"
        args.end_date = "2026-06-01"
        args.authors = None
        args.include_content = False
        args.limit = 100
        args.output_dir = None

        result = handle_read_command(
            args,
            mock_confluence_url,
            mock_confluence_email,
            mock_confluence_token,
            mock_confluence_space,
        )

        assert result == 0
        # Verify dates were passed correctly
        call_kwargs = mock_reader_class.call_args[1]
        assert call_kwargs["start_date"] == "2026-05-01"
        assert call_kwargs["end_date"] == "2026-06-01"

    @patch("confluence_integration.reader.ConfluenceReader")
    @patch("builtins.print")
    def test_read_command_with_content(
        self,
        mock_print: MagicMock,
        mock_reader_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test read command with content included."""
        from datetime import datetime

        from confluence_integration.reader import PageInfo

        mock_reader = MagicMock()
        mock_reader.get_space_info.return_value = {
            "id": "12345",
            "key": "TEST",
            "name": "Test Space",
            "type": "global",
        }
        mock_reader.get_pages.return_value = [
            PageInfo(
                page_id="12345",
                title="Test Page",
                space_key="TEST",
                author="test@example.com",
                author_display_name="Test User",
                created_date=datetime(2026, 6, 1, 10, 0, 0),
                modified_date=datetime(2026, 6, 2, 10, 0, 0),
                version=1,
                url="https://test.atlassian.net/wiki/spaces/TEST/pages/12345",
                content="<p>Test content</p>",
            )
        ]
        mock_reader_class.return_value = mock_reader

        args = MagicMock()
        args.start_date = None
        args.end_date = None
        args.authors = None
        args.include_content = True
        args.limit = 100
        args.output_dir = None

        result = handle_read_command(
            args,
            mock_confluence_url,
            mock_confluence_email,
            mock_confluence_token,
            mock_confluence_space,
        )

        assert result == 0
        # Verify include_content was passed
        call_args = mock_reader.get_pages.call_args
        assert call_args[1]["include_content"] is True

    @patch("confluence_integration.reader.ConfluenceReader")
    @patch("builtins.print")
    def test_read_command_error(
        self,
        mock_print: MagicMock,
        mock_reader_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test read command with error."""
        mock_reader_class.side_effect = ValueError("Invalid date format")

        args = MagicMock()
        args.start_date = "invalid-date"
        args.end_date = None
        args.authors = None
        args.include_content = False
        args.limit = 100
        args.output_dir = None

        result = handle_read_command(
            args,
            mock_confluence_url,
            mock_confluence_email,
            mock_confluence_token,
            mock_confluence_space,
        )

        assert result == 1


class TestMain:
    """Tests for main CLI function."""

    @patch("confluence_integration.__main__.load_env_file")
    @patch("confluence_integration.__main__.handle_validate_command")
    @patch("sys.argv", ["confluence-integration", "validate"])
    def test_main_validate_command(
        self,
        mock_handle_validate: MagicMock,
        mock_load_env: MagicMock,
        clean_env: None,
    ) -> None:
        """Test main with validate command."""
        os.environ["CONFLUENCE_URL"] = "https://test.atlassian.net"
        os.environ["CONFLUENCE_EMAIL"] = "test@example.com"
        os.environ["CONFLUENCE_API_TOKEN"] = "test_token"
        os.environ["CONFLUENCE_SPACE_KEY"] = "TEST"

        mock_handle_validate.return_value = 0

        result = main()

        assert result == 0
        mock_handle_validate.assert_called_once()

    @patch("confluence_integration.__main__.load_env_file")
    @patch("confluence_integration.__main__.handle_read_command")
    @patch("sys.argv", ["confluence-integration", "read"])
    def test_main_read_command(
        self,
        mock_handle_read: MagicMock,
        mock_load_env: MagicMock,
        clean_env: None,
    ) -> None:
        """Test main with read command."""
        os.environ["CONFLUENCE_URL"] = "https://test.atlassian.net"
        os.environ["CONFLUENCE_EMAIL"] = "test@example.com"
        os.environ["CONFLUENCE_API_TOKEN"] = "test_token"
        os.environ["CONFLUENCE_SPACE_KEY"] = "TEST"

        mock_handle_read.return_value = 0

        result = main()

        assert result == 0
        mock_handle_read.assert_called_once()

    @patch("confluence_integration.__main__.load_env_file")
    @patch("sys.argv", ["confluence-integration", "validate"])
    def test_main_missing_config(
        self,
        mock_load_env: MagicMock,
        clean_env: None,
    ) -> None:
        """Test main with missing configuration."""
        # Don't set any environment variables
        with pytest.raises(SystemExit) as exc_info:
            main()

        # Should exit with code 1
        assert exc_info.value.code == 1

    @patch("confluence_integration.__main__.load_env_file")
    @patch("confluence_integration.__main__.handle_validate_command")
    @patch("sys.argv", ["confluence-integration"])
    def test_main_default_command(
        self,
        mock_handle_validate: MagicMock,
        mock_load_env: MagicMock,
        clean_env: None,
    ) -> None:
        """Test main with no command (defaults to validate)."""
        os.environ["CONFLUENCE_URL"] = "https://test.atlassian.net"
        os.environ["CONFLUENCE_EMAIL"] = "test@example.com"
        os.environ["CONFLUENCE_API_TOKEN"] = "test_token"
        os.environ["CONFLUENCE_SPACE_KEY"] = "TEST"

        mock_handle_validate.return_value = 0

        result = main()

        assert result == 0
        mock_handle_validate.assert_called_once()

    @patch("confluence_integration.__main__.load_env_file")
    @patch("confluence_integration.__main__.handle_validate_command")
    @patch(
        "sys.argv",
        [
            "confluence-integration",
            "validate",
            "--url",
            "https://custom.atlassian.net",
            "--email",
            "custom@example.com",
            "--token",
            "custom_token",
            "--space",
            "CUSTOM",
        ],
    )
    def test_main_with_cli_args(
        self,
        mock_handle_validate: MagicMock,
        mock_load_env: MagicMock,
        clean_env: None,
    ) -> None:
        """Test main with CLI arguments overriding environment."""
        os.environ["CONFLUENCE_URL"] = "https://env.atlassian.net"
        os.environ["CONFLUENCE_EMAIL"] = "env@example.com"
        os.environ["CONFLUENCE_API_TOKEN"] = "env_token"
        os.environ["CONFLUENCE_SPACE_KEY"] = "ENV"

        mock_handle_validate.return_value = 0

        result = main()

        assert result == 0
        # Verify CLI args were used
        call_args = mock_handle_validate.call_args[0]
        assert call_args[1] == "https://custom.atlassian.net"
        assert call_args[2] == "custom@example.com"
        assert call_args[3] == "custom_token"
        assert call_args[4] == "CUSTOM"


# Made with Bob