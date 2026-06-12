"""
Confluence Integration Library

A Python library for validating Confluence API permissions through comprehensive testing.

Usage:
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
"""

from .permissions import ConfluencePermissions, TestResult

__version__ = "1.0.0"
__all__ = ["ConfluencePermissions", "TestResult"]
