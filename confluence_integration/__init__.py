"""
Confluence Integration Library

A Python library for validating Confluence API permissions and reading pages.

Usage:
    # Validate permissions
    from confluence_integration import ConfluencePermissions, TestResult

    validator = ConfluencePermissions(
        url="https://your-domain.atlassian.net",
        email="your.email@company.com",
        api_token="your_api_token",
        space_key="YOUR_SPACE"
    )

    results = validator.run_all_tests()
    if results["all_passed"]:
        print("All permissions validated!")

    # Read and filter pages
    from confluence_integration import ConfluenceReader, PageInfo

    reader = ConfluenceReader(
        url="https://your-domain.atlassian.net",
        email="your.email@company.com",
        api_token="your_api_token",
        space_key="YOUR_SPACE",
        start_date="2026-05-01",
        end_date="2026-06-01",
        authors=["john.doe@company.com"]
    )

    pages = reader.get_pages(include_content=True)
    for page in pages:
        print(f"{page.title} by {page.author_display_name}")
"""

from .permissions import ConfluencePermissions, TestResult
from .reader import ConfluenceReader, PageInfo

__version__ = "1.0.0"
__all__ = ["ConfluencePermissions", "TestResult", "ConfluenceReader", "PageInfo"]
