#!/usr/bin/env python3
"""
CLI entry point for confluence-integration package.

This allows the package to be run as:
    python -m confluence_integration
"""
import argparse
import os
import sys
from pathlib import Path
from typing import Optional

from .permissions import ConfluencePermissions


def load_env_file(env_path: Optional[Path] = None) -> None:
    """Load environment variables from .env file."""
    if env_path is None:
        env_path = Path.cwd() / ".env"

    if not env_path.exists():
        return

    try:
        from dotenv import load_dotenv

        load_dotenv(env_path)
    except ImportError:
        # Manual loading if python-dotenv not installed
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Confluence Integration - Validate API permissions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using environment variables from .env file
  python -m confluence_integration

  # Using command line arguments
  python -m confluence_integration \\
    --url https://your-domain.atlassian.net \\
    --email your.email@company.com \\
    --token your_api_token \\
    --space YOUR_SPACE

  # Using custom .env file
  python -m confluence_integration --env /path/to/.env

Environment Variables:
  CONFLUENCE_URL          Confluence base URL
  CONFLUENCE_EMAIL        Atlassian account email
  CONFLUENCE_API_TOKEN    API token for authentication
  CONFLUENCE_SPACE_KEY    Confluence space key to test
        """,
    )

    parser.add_argument(
        "--url", help="Confluence base URL (e.g., https://your-domain.atlassian.net)"
    )
    parser.add_argument("--email", help="Atlassian account email")
    parser.add_argument("--token", help="API token for authentication")
    parser.add_argument("--space", help="Confluence space key to test")
    parser.add_argument("--env", type=Path, help="Path to .env file (default: ./.env)")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed test information"
    )

    args = parser.parse_args()

    # Load environment variables
    load_env_file(args.env)

    # Get configuration from args or environment
    url = args.url or os.getenv("CONFLUENCE_URL")
    email = args.email or os.getenv("CONFLUENCE_EMAIL")
    api_token = args.token or os.getenv("CONFLUENCE_API_TOKEN")
    space_key = args.space or os.getenv("CONFLUENCE_SPACE_KEY")

    # Validate configuration
    if not all([url, email, api_token, space_key]):
        print("❌ Missing required configuration:")
        print()
        if not url:
            print("   --url or CONFLUENCE_URL")
        if not email:
            print("   --email or CONFLUENCE_EMAIL")
        if not api_token:
            print("   --token or CONFLUENCE_API_TOKEN")
        if not space_key:
            print("   --space or CONFLUENCE_SPACE_KEY")
        print()
        print("Use --help for more information")
        sys.exit(1)

    print("🔍 Confluence Integration - Permission Validator")
    print("=" * 70)
    print(f"URL: {url}")
    print(f"Email: {email}")
    print(f"Space: {space_key}")
    print("=" * 70)
    print()

    # Type guard - ensure all required values are strings
    assert isinstance(url, str), "URL must be a string"
    assert isinstance(email, str), "Email must be a string"
    assert isinstance(api_token, str), "API token must be a string"
    assert isinstance(space_key, str), "Space key must be a string"

    # Run tests
    validator = ConfluencePermissions(
        url=url, email=email, api_token=api_token, space_key=space_key
    )

    results = validator.run_all_tests()

    # Print results
    print("Test Results:")
    print("-" * 70)
    for i, test in enumerate(results["tests"], 1):
        status = "✅ PASS" if test.passed else "❌ FAIL"
        print(f"{i}. {test.test_name:15} {status}")
        print(f"   {test.message}")

        if args.verbose:
            if test.error:
                print(f"   Error: {test.error}")
            if test.data:
                for key, value in test.data.items():
                    print(f"   {key}: {value}")
        elif test.error and not test.passed:
            print(f"   Error: {test.error}")

        print()

    print("=" * 70)
    summary = results["summary"]
    print(f"Summary: {summary['passed']}/{summary['total']} tests passed")
    print("=" * 70)
    print()

    if results["all_passed"]:
        print("🎉 SUCCESS! All permissions validated!")
        print()
        print("Your Confluence API access is fully configured:")
        print("✅ CREATE permission verified")
        print("✅ READ permission verified")
        print("✅ UPDATE permission verified")
        print("✅ DELETE permission verified")
        print()
        return 0
    else:
        print("❌ FAILED! Some permissions are missing or invalid.")
        print()
        print("Please check:")
        print("- API token is valid and not expired")
        print("- You have appropriate permissions in the Confluence space")
        print("- Space key is correct")
        print()
        print("Use --verbose flag for detailed error information")
        return 1


if __name__ == "__main__":
    sys.exit(main())
