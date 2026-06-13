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
        description="Confluence Integration - Validate API permissions and read pages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate permissions (default command)
  python -m confluence_integration validate

  # Read pages from last 30 days (default)
  python -m confluence_integration read

  # Read pages with custom date range
  python -m confluence_integration read \\
    --start-date 2026-05-01 \\
    --end-date 2026-06-01

  # Read pages by specific authors
  python -m confluence_integration read \\
    --authors john.doe@company.com,jane.smith@company.com

  # Read pages with content included
  python -m confluence_integration read --include-content

Environment Variables:
  CONFLUENCE_URL          Confluence base URL
  CONFLUENCE_EMAIL        Atlassian account email
  CONFLUENCE_API_TOKEN    API token for authentication
  CONFLUENCE_SPACE_KEY    Confluence space key to test
        """,
    )

    # Add subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Validate command (default)
    validate_parser = subparsers.add_parser("validate", help="Validate Confluence API permissions")
    validate_parser.add_argument(
        "--url", help="Confluence base URL (e.g., https://your-domain.atlassian.net)"
    )
    validate_parser.add_argument("--email", help="Atlassian account email")
    validate_parser.add_argument("--token", help="API token for authentication")
    validate_parser.add_argument("--space", help="Confluence space key to test")
    validate_parser.add_argument("--env", type=Path, help="Path to .env file (default: ./.env)")
    validate_parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed test information"
    )

    # Read command
    read_parser = subparsers.add_parser("read", help="Read and filter Confluence pages")
    read_parser.add_argument(
        "--url", help="Confluence base URL (e.g., https://your-domain.atlassian.net)"
    )
    read_parser.add_argument("--email", help="Atlassian account email")
    read_parser.add_argument("--token", help="API token for authentication")
    read_parser.add_argument("--space", help="Confluence space key to read from")
    read_parser.add_argument("--env", type=Path, help="Path to .env file (default: ./.env)")
    read_parser.add_argument(
        "--start-date",
        help="Start date in YYYY-MM-DD format (default: 30 days ago)",
    )
    read_parser.add_argument("--end-date", help="End date in YYYY-MM-DD format (default: today)")
    read_parser.add_argument(
        "--authors",
        help="Comma-separated list of author usernames/emails (default: all)",
    )
    read_parser.add_argument(
        "--include-content",
        action="store_true",
        help="Include page content in output",
    )
    read_parser.add_argument(
        "--limit", type=int, default=100, help="Maximum pages per request (default: 100)"
    )
    read_parser.add_argument(
        "--output-dir",
        type=Path,
        help="Directory to save pages as Markdown files (optional)",
    )
    read_parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="markdown",
        help="Output format when saving to files (default: markdown)",
    )

    args = parser.parse_args()

    # Default to validate if no command specified
    if not args.command:
        args.command = "validate"
        # Set default values for validate command
        args.verbose = False
        args.env = None

    # Load environment variables
    load_env_file(args.env if hasattr(args, "env") else None)

    # Get configuration from args or environment
    url = (args.url if hasattr(args, "url") else None) or os.getenv("CONFLUENCE_URL")
    email = (args.email if hasattr(args, "email") else None) or os.getenv("CONFLUENCE_EMAIL")
    api_token = (args.token if hasattr(args, "token") else None) or os.getenv(
        "CONFLUENCE_API_TOKEN"
    )
    space_key = (args.space if hasattr(args, "space") else None) or os.getenv(
        "CONFLUENCE_SPACE_KEY"
    )

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

    # Type assertions - we've validated these are not None
    assert isinstance(url, str), "URL must be a string"
    assert isinstance(email, str), "Email must be a string"
    assert isinstance(api_token, str), "API token must be a string"
    assert isinstance(space_key, str), "Space key must be a string"

    # Route to appropriate command handler
    if args.command == "read":
        return handle_read_command(args, url, email, api_token, space_key)
    else:
        return handle_validate_command(args, url, email, api_token, space_key)


def handle_validate_command(
    args: argparse.Namespace, url: str, email: str, api_token: str, space_key: str
) -> int:
    """Handle the validate command."""
    from .permissions import ConfluencePermissions

    print("🔍 Confluence Integration - Permission Validator")
    print("=" * 70)
    print(f"URL: {url}")
    print(f"Email: {email}")
    print(f"Space: {space_key}")
    print("=" * 70)
    print()

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

        verbose = getattr(args, "verbose", False)
        if verbose:
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


def _save_pages_to_files(pages: list, output_dir: Path, output_format: str, space_key: str) -> None:
    """Save pages to files in the specified directory."""
    import json
    import re

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"💾 Saving {len(pages)} page(s) to {output_dir}")
    print()

    for page in pages:
        # Sanitize filename
        safe_title = re.sub(r'[<>:"/\\|?*]', "_", page.title)
        safe_title = safe_title[:100]  # Limit filename length

        if output_format == "json":
            filename = f"{safe_title}.json"
            filepath = output_dir / filename

            # Convert PageInfo to dict
            page_dict = {
                "page_id": page.page_id,
                "title": page.title,
                "space_key": page.space_key,
                "author": page.author,
                "author_display_name": page.author_display_name,
                "created_date": page.created_date.isoformat(),
                "modified_date": page.modified_date.isoformat(),
                "version": page.version,
                "url": page.url,
                "content": page.content,
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(page_dict, f, indent=2, ensure_ascii=False)

        else:  # markdown
            filename = f"{safe_title}.md"
            filepath = output_dir / filename

            # Convert HTML to Markdown (basic conversion)
            content_md = _html_to_markdown(page.content) if page.content else ""

            # Create markdown file with metadata
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {page.title}\n\n")
                f.write(f"**Author:** {page.author_display_name} ({page.author})  \n")
                f.write(f"**Created:** {page.created_date.strftime('%Y-%m-%d %H:%M:%S')}  \n")
                f.write(f"**Modified:** {page.modified_date.strftime('%Y-%m-%d %H:%M:%S')}  \n")
                f.write(f"**Version:** {page.version}  \n")
                f.write(f"**URL:** {page.url}  \n")
                f.write(f"**Space:** {space_key}  \n")
                f.write("\n---\n\n")
                f.write(content_md)

        print(f"  ✓ Saved: {filename}")

    print()
    print(f"📁 All pages saved to: {output_dir.absolute()}")


def _html_to_markdown(html: str) -> str:
    """Convert HTML to Markdown (basic conversion)."""
    import re

    if not html:
        return ""

    # Remove HTML comments
    text = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)

    # Convert headers
    text = re.sub(r"<h1[^>]*>(.*?)</h1>", r"# \1", text, flags=re.IGNORECASE)
    text = re.sub(r"<h2[^>]*>(.*?)</h2>", r"## \1", text, flags=re.IGNORECASE)
    text = re.sub(r"<h3[^>]*>(.*?)</h3>", r"### \1", text, flags=re.IGNORECASE)
    text = re.sub(r"<h4[^>]*>(.*?)</h4>", r"#### \1", text, flags=re.IGNORECASE)
    text = re.sub(r"<h5[^>]*>(.*?)</h5>", r"##### \1", text, flags=re.IGNORECASE)
    text = re.sub(r"<h6[^>]*>(.*?)</h6>", r"###### \1", text, flags=re.IGNORECASE)

    # Convert bold and italic
    text = re.sub(r"<strong[^>]*>(.*?)</strong>", r"**\1**", text, flags=re.IGNORECASE)
    text = re.sub(r"<b[^>]*>(.*?)</b>", r"**\1**", text, flags=re.IGNORECASE)
    text = re.sub(r"<em[^>]*>(.*?)</em>", r"*\1*", text, flags=re.IGNORECASE)
    text = re.sub(r"<i[^>]*>(.*?)</i>", r"*\1*", text, flags=re.IGNORECASE)

    # Convert code
    text = re.sub(r"<code[^>]*>(.*?)</code>", r"`\1`", text, flags=re.IGNORECASE)
    text = re.sub(r"<pre[^>]*>(.*?)</pre>", r"```\n\1\n```", text, flags=re.IGNORECASE | re.DOTALL)

    # Convert links
    text = re.sub(
        r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>',
        r"[\2](\1)",
        text,
        flags=re.IGNORECASE,
    )

    # Convert lists
    text = re.sub(r"<li[^>]*>(.*?)</li>", r"- \1", text, flags=re.IGNORECASE)
    text = re.sub(r"<ul[^>]*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"</ul>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<ol[^>]*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"</ol>", "\n", text, flags=re.IGNORECASE)

    # Convert paragraphs
    text = re.sub(r"<p[^>]*>(.*?)</p>", r"\1\n\n", text, flags=re.IGNORECASE | re.DOTALL)

    # Convert line breaks
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)

    # Remove remaining HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Clean up multiple newlines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Decode HTML entities
    text = text.replace("&nbsp;", " ")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&amp;", "&")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")

    return text.strip()


def handle_read_command(
    args: argparse.Namespace, url: str, email: str, api_token: str, space_key: str
) -> int:
    """Handle the read command."""
    from .reader import ConfluenceReader

    print("📖 Confluence Integration - Page Reader")
    print("=" * 70)
    print(f"URL: {url}")
    print(f"Email: {email}")
    print(f"Space: {space_key}")

    # Parse authors if provided
    authors = None
    if hasattr(args, "authors") and args.authors:
        authors = [a.strip() for a in args.authors.split(",")]
        print(f"Authors: {', '.join(authors)}")

    # Display date range
    start_date = getattr(args, "start_date", None)
    end_date = getattr(args, "end_date", None)
    if start_date:
        print(f"Start Date: {start_date}")
    else:
        print("Start Date: 30 days ago (default)")
    if end_date:
        print(f"End Date: {end_date}")
    else:
        print("End Date: today (default)")

    print("=" * 70)
    print()

    try:
        # Create reader
        reader = ConfluenceReader(
            url=url,
            email=email,
            api_token=api_token,
            space_key=space_key,
            start_date=start_date,
            end_date=end_date,
            authors=authors,
        )

        # Get space info
        space_info = reader.get_space_info()
        print(f"📁 Space: {space_info['name']} ({space_info['key']})")
        print()

        # Get pages
        output_dir = getattr(args, "output_dir", None)
        include_content = getattr(args, "include_content", False) or output_dir is not None
        limit = getattr(args, "limit", 100)

        print(f"🔍 Fetching pages (limit: {limit} per request)...")
        pages = reader.get_pages(include_content=include_content, limit=limit)

        print(f"✅ Found {len(pages)} page(s) matching filters")
        print()

        # Save to files if output directory specified
        if output_dir:
            output_format = getattr(args, "format", "markdown")
            _save_pages_to_files(pages, output_dir, output_format, space_key)
        else:
            # Display pages in terminal
            if pages:
                print("Pages:")
                print("-" * 70)
                for i, page in enumerate(pages, 1):
                    print(f"{i}. {page.title}")
                    print(f"   Author: {page.author_display_name} ({page.author})")
                    print(f"   Created: {page.created_date.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"   Modified: {page.modified_date.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"   Version: {page.version}")
                    print(f"   URL: {page.url}")

                    if include_content and page.content:
                        content_preview = (
                            page.content[:200] + "..." if len(page.content) > 200 else page.content
                        )
                        print(f"   Content: {content_preview}")

                    print()

        print("=" * 70)
        print(f"✅ Successfully read {len(pages)} page(s)")
        return 0

    except ValueError as e:
        print(f"❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
