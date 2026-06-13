#!/usr/bin/env python3
"""
Confluence Page Reader

A module for reading and filtering Confluence pages by date range and authors.
"""
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Optional

try:
    from atlassian import Confluence
except ImportError:
    print("❌ Required package not installed.")
    print("   Run: pip install atlassian-python-api")
    sys.exit(1)


@dataclass
class PageInfo:
    """Information about a Confluence page."""

    page_id: str
    title: str
    space_key: str
    author: str
    author_display_name: str
    created_date: datetime
    modified_date: datetime
    version: int
    url: str
    content: Optional[str] = None


class ConfluenceReader:
    """
    Read and filter Confluence pages by date range and authors.

    Features:
    - Filter pages by creation/modification date range
    - Filter pages by author(s)
    - Default: last 30 days, all authors
    """

    def __init__(
        self,
        url: str,
        email: str,
        api_token: str,
        space_key: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        authors: Optional[list[str]] = None,
    ):
        """
        Initialize Confluence page reader.

        Args:
            url: Confluence base URL (e.g., https://apptio.atlassian.net)
            email: Atlassian account email
            api_token: API token for authentication
            space_key: Confluence space key to read from
            start_date: Start date in YYYY-MM-DD format (default: 30 days ago)
            end_date: End date in YYYY-MM-DD format (default: today)
            authors: List of author usernames/emails to filter by (default: all)
        """
        self.url = url
        self.email = email
        self.api_token = api_token
        self.space_key = space_key
        self.confluence: Optional[Confluence] = None

        # Parse date range
        self.end_date = self._parse_date(end_date) if end_date else datetime.now()
        self.start_date = (
            self._parse_date(start_date) if start_date else self.end_date - timedelta(days=30)
        )

        # Normalize authors list
        self.authors = [a.strip().lower() for a in authors] if authors else None

    def _parse_date(self, date_str: str) -> datetime:
        """
        Parse date string in YYYY-MM-DD format.

        Args:
            date_str: Date string in YYYY-MM-DD format

        Returns:
            datetime object

        Raises:
            ValueError: If date format is invalid
        """
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(f"Invalid date format '{date_str}'. Expected YYYY-MM-DD") from e

    def _initialize_client(self) -> None:
        """Initialize Confluence client."""
        if self.confluence is None:
            self.confluence = Confluence(
                url=self.url, username=self.email, password=self.api_token, cloud=True
            )

    def _parse_confluence_date(self, date_str: str) -> datetime:
        """
        Parse Confluence date string to datetime.

        Confluence returns dates in ISO 8601 format like:
        "2026-06-12T18:09:24.000Z"

        Args:
            date_str: ISO 8601 date string from Confluence

        Returns:
            datetime object
        """
        # Remove milliseconds and Z suffix, parse as UTC
        if "." in date_str:
            date_str = date_str.split(".")[0]
        date_str = date_str.rstrip("Z")
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")

    def _matches_author_filter(self, author_username: str, author_email: str) -> bool:
        """
        Check if page author matches the author filter.

        Args:
            author_username: Author's username
            author_email: Author's email

        Returns:
            True if author matches filter or no filter is set
        """
        if self.authors is None:
            return True

        author_username_lower = author_username.lower()
        author_email_lower = author_email.lower()

        return any(
            author in author_username_lower or author in author_email_lower
            for author in self.authors
        )

    def _matches_date_filter(self, page_date: datetime) -> bool:
        """
        Check if page date is within the date range filter.

        Args:
            page_date: Page creation or modification date

        Returns:
            True if date is within range
        """
        return self.start_date <= page_date <= self.end_date

    def _extract_page_info(self, page: dict[str, Any]) -> PageInfo:
        """
        Extract page information from Confluence API response.

        Args:
            page: Page data from Confluence API

        Returns:
            PageInfo object
        """
        page_id = page["id"]
        title = page["title"]
        space_key = page["space"]["key"]

        # Extract author information
        author_data = page["history"]["createdBy"]
        author_username = author_data.get("username", author_data.get("accountId", ""))
        author_display_name = author_data.get("displayName", author_username)
        author_email = author_data.get("email", "")

        # Extract dates
        created_date = self._parse_confluence_date(page["history"]["createdDate"])
        modified_date = self._parse_confluence_date(page["version"]["when"])

        # Extract version
        version = page["version"]["number"]

        # Build page URL
        page_url = f"{self.url}/wiki/spaces/{space_key}/pages/{page_id}"

        # Extract content if available
        content = None
        if "body" in page and "storage" in page["body"]:
            content = page["body"]["storage"]["value"]

        return PageInfo(
            page_id=page_id,
            title=title,
            space_key=space_key,
            author=author_email or author_username,
            author_display_name=author_display_name,
            created_date=created_date,
            modified_date=modified_date,
            version=version,
            url=page_url,
            content=content,
        )

    def get_pages(self, include_content: bool = False, limit: int = 100) -> list[PageInfo]:
        """
        Get pages from Confluence filtered by date range and authors.

        Args:
            include_content: Whether to include page content (default: False)
            limit: Maximum number of pages to retrieve per request (default: 100)

        Returns:
            List of PageInfo objects matching the filters
        """
        self._initialize_client()
        assert self.confluence is not None

        filtered_pages: list[PageInfo] = []
        start = 0

        # Expand fields we need
        expand = "history.createdBy,version,space"
        if include_content:
            expand += ",body.storage"

        while True:
            # Get pages from space
            result = self.confluence.get_all_pages_from_space(
                space=self.space_key,
                start=start,
                limit=limit,
                expand=expand,
            )

            if not result:
                break

            for page in result:
                # Extract page info
                page_info = self._extract_page_info(page)

                # Apply date filter (check both created and modified dates)
                if not (
                    self._matches_date_filter(page_info.created_date)
                    or self._matches_date_filter(page_info.modified_date)
                ):
                    continue

                # Apply author filter
                if not self._matches_author_filter(page_info.author, page_info.author_display_name):
                    continue

                filtered_pages.append(page_info)

            # Check if we've retrieved all pages
            if len(result) < limit:
                break

            start += limit

        return filtered_pages

    def get_page_count(self) -> int:
        """
        Get count of pages matching the filters.

        Returns:
            Number of pages matching filters
        """
        return len(self.get_pages(include_content=False))

    def get_space_info(self) -> dict[str, Any]:
        """
        Get information about the Confluence space.

        Returns:
            Dictionary with space information
        """
        self._initialize_client()
        assert self.confluence is not None

        space = self.confluence.get_space(self.space_key)
        if space is None:
            raise ValueError(f"Space '{self.space_key}' not found")

        return {
            "id": space["id"],
            "key": space["key"],
            "name": space["name"],
            "type": space["type"],
        }


# Made with Bob
