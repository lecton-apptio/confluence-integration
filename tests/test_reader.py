"""Tests for ConfluenceReader class."""

from datetime import datetime, timedelta
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from confluence_integration.reader import ConfluenceReader, PageInfo


class TestPageInfo:
    """Tests for PageInfo dataclass."""

    def test_init(self) -> None:
        """Test PageInfo initialization."""
        created = datetime(2026, 6, 1, 10, 0, 0)
        modified = datetime(2026, 6, 2, 10, 0, 0)

        page_info = PageInfo(
            page_id="12345",
            title="Test Page",
            space_key="TEST",
            author="test@example.com",
            author_display_name="Test User",
            created_date=created,
            modified_date=modified,
            version=1,
            url="https://test.atlassian.net/wiki/spaces/TEST/pages/12345",
            content="<p>Test content</p>",
        )

        assert page_info.page_id == "12345"
        assert page_info.title == "Test Page"
        assert page_info.space_key == "TEST"
        assert page_info.author == "test@example.com"
        assert page_info.author_display_name == "Test User"
        assert page_info.created_date == created
        assert page_info.modified_date == modified
        assert page_info.version == 1
        assert page_info.url == "https://test.atlassian.net/wiki/spaces/TEST/pages/12345"
        assert page_info.content == "<p>Test content</p>"


class TestConfluenceReader:
    """Tests for ConfluenceReader class."""

    def test_init_with_defaults(
        self,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test ConfluenceReader initialization with defaults."""
        reader = ConfluenceReader(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )

        assert reader.url == mock_confluence_url
        assert reader.email == mock_confluence_email
        assert reader.api_token == mock_confluence_token
        assert reader.space_key == mock_confluence_space
        assert reader.confluence is None
        assert reader.authors is None
        # Default date range: last 30 days
        assert reader.start_date <= reader.end_date
        assert (reader.end_date - reader.start_date).days <= 30

    def test_init_with_custom_dates(
        self,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test ConfluenceReader initialization with custom dates."""
        reader = ConfluenceReader(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
            start_date="2026-05-01",
            end_date="2026-06-01",
        )

        assert reader.start_date == datetime(2026, 5, 1)
        assert reader.end_date == datetime(2026, 6, 1)

    def test_init_with_authors(
        self,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test ConfluenceReader initialization with authors."""
        reader = ConfluenceReader(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
            authors=["user1@example.com", "User2"],
        )

        assert reader.authors == ["user1@example.com", "user2"]

    def test_parse_date_valid(
        self,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test parsing valid date string."""
        reader = ConfluenceReader(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )

        date = reader._parse_date("2026-06-13")
        assert date == datetime(2026, 6, 13)

    def test_parse_date_invalid(
        self,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test parsing invalid date string."""
        reader = ConfluenceReader(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )

        with pytest.raises(ValueError, match="Invalid date format"):
            reader._parse_date("2026/06/13")

    def test_parse_confluence_date(
        self,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test parsing Confluence date string."""
        reader = ConfluenceReader(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )

        date = reader._parse_confluence_date("2026-06-13T10:30:45.123Z")
        assert date == datetime(2026, 6, 13, 10, 30, 45)

    def test_matches_author_filter_no_filter(
        self,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test author filter matching with no filter set."""
        reader = ConfluenceReader(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )

        assert reader._matches_author_filter("anyuser", "any@example.com") is True

    def test_matches_author_filter_with_filter(
        self,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test author filter matching with filter set."""
        reader = ConfluenceReader(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
            authors=["testuser", "admin@example.com"],
        )

        assert reader._matches_author_filter("testuser", "test@example.com") is True
        assert reader._matches_author_filter("otheruser", "admin@example.com") is True
        assert reader._matches_author_filter("otheruser", "other@example.com") is False

    def test_matches_date_filter(
        self,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test date filter matching."""
        reader = ConfluenceReader(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
            start_date="2026-06-01",
            end_date="2026-06-30",
        )

        assert reader._matches_date_filter(datetime(2026, 6, 15)) is True
        assert reader._matches_date_filter(datetime(2026, 6, 1)) is True
        assert reader._matches_date_filter(datetime(2026, 6, 30)) is True
        assert reader._matches_date_filter(datetime(2026, 5, 31)) is False
        assert reader._matches_date_filter(datetime(2026, 7, 1)) is False

    def test_extract_page_info(
        self,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
        mock_page_data: dict[str, Any],
    ) -> None:
        """Test extracting page information."""
        reader = ConfluenceReader(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )

        page_info = reader._extract_page_info(mock_page_data)

        assert page_info.page_id == "12345"
        assert page_info.title == "Test Page"
        assert page_info.space_key == "TEST"
        assert page_info.author == "test@example.com"
        assert page_info.author_display_name == "Test User"
        assert page_info.version == 1
        assert page_info.content == "<h2>Test Content</h2><p>This is a test page.</p>"

    @patch("confluence_integration.reader.Confluence")
    def test_initialize_client(
        self,
        mock_confluence_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test client initialization."""
        mock_client = MagicMock()
        mock_confluence_class.return_value = mock_client

        reader = ConfluenceReader(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )

        reader._initialize_client()

        assert reader.confluence is not None
        mock_confluence_class.assert_called_once_with(
            url=mock_confluence_url,
            username=mock_confluence_email,
            password=mock_confluence_token,
            cloud=True,
        )

    @patch("confluence_integration.reader.Confluence")
    def test_get_pages_empty_result(
        self,
        mock_confluence_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test getting pages with empty result."""
        mock_client = MagicMock()
        mock_client.get_all_pages_from_space.return_value = []
        mock_confluence_class.return_value = mock_client

        reader = ConfluenceReader(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )

        pages = reader.get_pages()

        assert len(pages) == 0

    @patch("confluence_integration.reader.Confluence")
    def test_get_pages_with_filtering(
        self,
        mock_confluence_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
        mock_pages_list: list[dict[str, Any]],
    ) -> None:
        """Test getting pages with date and author filtering."""
        mock_client = MagicMock()
        mock_client.get_all_pages_from_space.return_value = mock_pages_list
        mock_confluence_class.return_value = mock_client

        reader = ConfluenceReader(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
            start_date="2026-06-01",
            end_date="2026-06-03",
            authors=["user0", "user1"],
        )

        pages = reader.get_pages()

        # Should only get pages from user0 and user1 within date range
        assert len(pages) <= 3
        for page in pages:
            assert page.author in ["user0@example.com", "user1@example.com"]

    @patch("confluence_integration.reader.Confluence")
    def test_get_pages_with_content(
        self,
        mock_confluence_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
        mock_pages_list: list[dict[str, Any]],
    ) -> None:
        """Test getting pages with content included."""
        mock_client = MagicMock()
        mock_client.get_all_pages_from_space.return_value = mock_pages_list
        mock_confluence_class.return_value = mock_client

        reader = ConfluenceReader(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )

        pages = reader.get_pages(include_content=True)

        # Verify expand parameter includes body.storage
        call_args = mock_client.get_all_pages_from_space.call_args
        assert "body.storage" in call_args[1]["expand"]

    @patch("confluence_integration.reader.Confluence")
    def test_get_pages_pagination(
        self,
        mock_confluence_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
        mock_pages_list: list[dict[str, Any]],
    ) -> None:
        """Test getting pages with pagination."""
        mock_client = MagicMock()
        # Simulate pagination: first call returns 3 pages, second call returns 2 pages
        mock_client.get_all_pages_from_space.side_effect = [
            mock_pages_list[:3],
            mock_pages_list[3:],
        ]
        mock_confluence_class.return_value = mock_client

        reader = ConfluenceReader(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )

        pages = reader.get_pages(limit=3)

        # Should have made two calls
        assert mock_client.get_all_pages_from_space.call_count == 2

    @patch("confluence_integration.reader.Confluence")
    def test_get_page_count(
        self,
        mock_confluence_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
        mock_pages_list: list[dict[str, Any]],
    ) -> None:
        """Test getting page count."""
        mock_client = MagicMock()
        mock_client.get_all_pages_from_space.return_value = mock_pages_list
        mock_confluence_class.return_value = mock_client

        reader = ConfluenceReader(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )

        count = reader.get_page_count()

        assert count == len(mock_pages_list)

    @patch("confluence_integration.reader.Confluence")
    def test_get_space_info(
        self,
        mock_confluence_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test getting space information."""
        mock_client = MagicMock()
        mock_client.get_space.return_value = {
            "id": "12345",
            "key": "TEST",
            "name": "Test Space",
            "type": "global",
        }
        mock_confluence_class.return_value = mock_client

        reader = ConfluenceReader(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )

        space_info = reader.get_space_info()

        assert space_info["id"] == "12345"
        assert space_info["key"] == "TEST"
        assert space_info["name"] == "Test Space"
        assert space_info["type"] == "global"

    @patch("confluence_integration.reader.Confluence")
    def test_get_space_info_not_found(
        self,
        mock_confluence_class: MagicMock,
        mock_confluence_url: str,
        mock_confluence_email: str,
        mock_confluence_token: str,
        mock_confluence_space: str,
    ) -> None:
        """Test getting space information when space not found."""
        mock_client = MagicMock()
        mock_client.get_space.return_value = None
        mock_confluence_class.return_value = mock_client

        reader = ConfluenceReader(
            url=mock_confluence_url,
            email=mock_confluence_email,
            api_token=mock_confluence_token,
            space_key=mock_confluence_space,
        )

        with pytest.raises(ValueError, match="Space .* not found"):
            reader.get_space_info()


# Made with Bob