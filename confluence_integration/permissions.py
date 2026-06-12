#!/usr/bin/env python3
"""
Confluence Permissions Validator

A comprehensive library to validate Confluence API permissions through
6 distinct tests: create, read, update, read-verify, delete, and delete-verify.
"""
import contextlib
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

try:
    from atlassian import Confluence
except ImportError:
    print("❌ Required package not installed.")
    print("   Run: pip install atlassian-python-api")
    sys.exit(1)


@dataclass
class TestResult:
    """Result of a single permission test."""

    test_name: str
    passed: bool
    message: str
    error: Optional[str] = None
    data: Optional[dict[str, Any]] = None


class ConfluencePermissions:
    """
    Validates Confluence API permissions through comprehensive testing.

    Tests performed:
    1. CREATE - Write a new page
    2. READ - Read the written page
    3. UPDATE - Edit the page
    4. READ_VERIFY - Read again and validate the edit
    5. DELETE - Delete the page
    6. DELETE_VERIFY - Validate the page is deleted
    """

    def __init__(self, url: str, email: str, api_token: str, space_key: str):
        """
        Initialize Confluence permissions validator.

        Args:
            url: Confluence base URL (e.g., https://apptio.atlassian.net)
            email: Atlassian account email
            api_token: API token for authentication
            space_key: Confluence space key to test in
        """
        self.url = url
        self.email = email
        self.api_token = api_token
        self.space_key = space_key
        self.confluence: Optional[Confluence] = None
        self.test_page_id: Optional[str] = None
        self.test_page_title: str = ""
        self.original_content: str = ""
        self.updated_content: str = ""

    def _initialize_client(self) -> TestResult:
        """Initialize Confluence client."""
        try:
            self.confluence = Confluence(
                url=self.url, username=self.email, password=self.api_token, cloud=True
            )
            # Test connection by getting space
            space = self.confluence.get_space(self.space_key)
            return TestResult(
                test_name="INITIALIZE",
                passed=True,
                message=f"Connected to space '{space['name']}'",
                data={"space_id": space["id"], "space_key": space["key"]},
            )
        except Exception as e:
            return TestResult(
                test_name="INITIALIZE",
                passed=False,
                message="Failed to initialize Confluence client",
                error=str(e),
            )

    def test_1_create_page(self) -> TestResult:
        """
        Test 1: CREATE - Write a new page.

        Returns:
            TestResult with page creation details
        """
        if not self.confluence:
            return TestResult(
                test_name="CREATE",
                passed=False,
                message="Confluence client not initialized",
                error="Client is None",
            )

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.test_page_title = f"[PERMISSION TEST] {timestamp}"
        self.original_content = f"""
<h2>Confluence Permissions Test Page</h2>
<p><strong>Created:</strong> {timestamp}</p>
<p>This is the <strong>original content</strong> of the test page.</p>
<p>Test marker: <code>ORIGINAL_CONTENT_v1</code></p>
"""

        try:
            result = self.confluence.create_page(
                space=self.space_key,
                title=self.test_page_title,
                body=self.original_content,
                type="page",
                representation="storage",
            )
            self.test_page_id = result["id"]
            page_url = f"{self.url}/wiki/spaces/{self.space_key}/pages/{self.test_page_id}"

            return TestResult(
                test_name="CREATE",
                passed=True,
                message=f"Successfully created page '{self.test_page_title}'",
                data={
                    "page_id": self.test_page_id,
                    "page_url": page_url,
                    "title": self.test_page_title,
                },
            )
        except Exception as e:
            return TestResult(
                test_name="CREATE", passed=False, message="Failed to create page", error=str(e)
            )

    def test_2_read_page(self) -> TestResult:
        """
        Test 2: READ - Read the written page.

        Returns:
            TestResult with page read details
        """
        if not self.confluence or not self.test_page_id:
            return TestResult(
                test_name="READ",
                passed=False,
                message="Cannot read page - page not created",
                error="Missing page_id",
            )

        try:
            page = self.confluence.get_page_by_id(
                page_id=self.test_page_id, expand="body.storage,version"
            )

            content = page["body"]["storage"]["value"]
            version = page["version"]["number"]

            # Verify we can read the content
            if "ORIGINAL_CONTENT_v1" in content:
                return TestResult(
                    test_name="READ",
                    passed=True,
                    message=f"Successfully read page (version {version})",
                    data={
                        "page_id": self.test_page_id,
                        "title": page["title"],
                        "version": version,
                        "content_length": len(content),
                        "content_verified": True,
                    },
                )
            else:
                return TestResult(
                    test_name="READ",
                    passed=False,
                    message="Page read but content verification failed",
                    error="Original content marker not found",
                )
        except Exception as e:
            return TestResult(
                test_name="READ", passed=False, message="Failed to read page", error=str(e)
            )

    def test_3_update_page(self) -> TestResult:
        """
        Test 3: UPDATE - Edit the page.

        Returns:
            TestResult with page update details
        """
        if not self.confluence or not self.test_page_id:
            return TestResult(
                test_name="UPDATE",
                passed=False,
                message="Cannot update page - page not created",
                error="Missing page_id",
            )

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.updated_content = f"""
<h2>Confluence Permissions Test Page</h2>
<p><strong>Created:</strong> {timestamp}</p>
<p>This is the <strong>UPDATED content</strong> of the test page.</p>
<p>Test marker: <code>UPDATED_CONTENT_v2</code></p>
<p><em>Last updated: {timestamp}</em></p>
"""

        try:
            result = self.confluence.update_page(
                page_id=self.test_page_id,
                title=self.test_page_title,
                body=self.updated_content,
                type="page",
                representation="storage",
            )

            new_version = result["version"]["number"]

            return TestResult(
                test_name="UPDATE",
                passed=True,
                message=f"Successfully updated page to version {new_version}",
                data={
                    "page_id": self.test_page_id,
                    "new_version": new_version,
                    "title": self.test_page_title,
                },
            )
        except Exception as e:
            return TestResult(
                test_name="UPDATE", passed=False, message="Failed to update page", error=str(e)
            )

    def test_4_read_verify(self) -> TestResult:
        """
        Test 4: READ_VERIFY - Read again and validate the edit.

        Returns:
            TestResult with verification details
        """
        if not self.confluence or not self.test_page_id:
            return TestResult(
                test_name="READ_VERIFY",
                passed=False,
                message="Cannot verify page - page not created",
                error="Missing page_id",
            )

        try:
            page = self.confluence.get_page_by_id(
                page_id=self.test_page_id, expand="body.storage,version"
            )

            content = page["body"]["storage"]["value"]
            version = page["version"]["number"]

            # Verify the update was successful
            has_updated_marker = "UPDATED_CONTENT_v2" in content
            no_original_marker = "ORIGINAL_CONTENT_v1" not in content
            version_increased = version >= 2

            if has_updated_marker and no_original_marker and version_increased:
                return TestResult(
                    test_name="READ_VERIFY",
                    passed=True,
                    message=f"Successfully verified update (version {version})",
                    data={
                        "page_id": self.test_page_id,
                        "version": version,
                        "has_updated_content": has_updated_marker,
                        "original_content_removed": no_original_marker,
                        "content_length": len(content),
                    },
                )
            else:
                return TestResult(
                    test_name="READ_VERIFY",
                    passed=False,
                    message="Page read but update verification failed",
                    error=f"Updated marker: {has_updated_marker}, Original removed: {no_original_marker}, Version: {version}",
                )
        except Exception as e:
            return TestResult(
                test_name="READ_VERIFY",
                passed=False,
                message="Failed to verify page update",
                error=str(e),
            )

    def test_5_delete_page(self) -> TestResult:
        """
        Test 5: DELETE - Delete the page.

        Returns:
            TestResult with deletion details
        """
        if not self.confluence or not self.test_page_id:
            return TestResult(
                test_name="DELETE",
                passed=False,
                message="Cannot delete page - page not created",
                error="Missing page_id",
            )

        try:
            self.confluence.remove_page(self.test_page_id)

            return TestResult(
                test_name="DELETE",
                passed=True,
                message=f"Successfully deleted page '{self.test_page_title}'",
                data={"page_id": self.test_page_id, "title": self.test_page_title},
            )
        except Exception as e:
            return TestResult(
                test_name="DELETE", passed=False, message="Failed to delete page", error=str(e)
            )

    def test_6_delete_verify(self) -> TestResult:
        """
        Test 6: DELETE_VERIFY - Validate the page is deleted.

        Returns:
            TestResult with deletion verification details
        """
        if not self.confluence or not self.test_page_id:
            return TestResult(
                test_name="DELETE_VERIFY",
                passed=False,
                message="Cannot verify deletion - page not created",
                error="Missing page_id",
            )

        try:
            # Try to read the page - should fail
            self.confluence.get_page_by_id(page_id=self.test_page_id, expand="body.storage")

            # If we get here, the page still exists
            return TestResult(
                test_name="DELETE_VERIFY",
                passed=False,
                message="Page still exists after deletion",
                error=f"Page {self.test_page_id} was not deleted",
            )
        except Exception as e:
            # Expected: page should not exist
            error_msg = str(e).lower()
            # Check for various "not found" or "no permission" messages that indicate deletion
            deletion_indicators = [
                "404",
                "not found",
                "does not exist",
                "no content with the given id",
                "calling user does not have permission to view",
            ]

            if any(indicator in error_msg for indicator in deletion_indicators):
                return TestResult(
                    test_name="DELETE_VERIFY",
                    passed=True,
                    message="Successfully verified page deletion (page not found)",
                    data={
                        "page_id": self.test_page_id,
                        "verified_deleted": True,
                        "error_message": str(e),
                    },
                )
            else:
                return TestResult(
                    test_name="DELETE_VERIFY",
                    passed=False,
                    message="Unexpected error during deletion verification",
                    error=str(e),
                )

    def run_all_tests(self) -> dict[str, Any]:
        """
        Run all 6 permission tests in sequence.

        Returns:
            Dictionary containing:
                - all_passed: bool
                - tests: List of TestResult objects
                - summary: Dict with pass/fail counts
        """
        results = []

        # Initialize
        init_result = self._initialize_client()
        if not init_result.passed:
            return {
                "all_passed": False,
                "tests": [init_result],
                "summary": {"passed": 0, "failed": 1, "total": 1},
                "error": "Failed to initialize Confluence client",
            }

        # Run all 6 tests
        test_methods = [
            self.test_1_create_page,
            self.test_2_read_page,
            self.test_3_update_page,
            self.test_4_read_verify,
            self.test_5_delete_page,
            self.test_6_delete_verify,
        ]

        for test_method in test_methods:
            result = test_method()
            results.append(result)

            # Stop if a test fails (except for cleanup tests)
            if not result.passed and result.test_name not in ["DELETE", "DELETE_VERIFY"]:
                # Try to cleanup if we created a page
                if self.test_page_id and self.confluence:
                    with contextlib.suppress(BaseException):
                        self.confluence.remove_page(self.test_page_id)
                break

        passed = sum(1 for r in results if r.passed)
        failed = sum(1 for r in results if not r.passed)
        all_passed = all(r.passed for r in results)

        return {
            "all_passed": all_passed,
            "tests": results,
            "summary": {"passed": passed, "failed": failed, "total": len(results)},
        }
