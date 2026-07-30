import os
import pytest
from pathlib import Path

# Define the path to latest.html
# Option 1: Use the absolute path provided (not ideal for portability)
# LATEST_HTML_PATH = Path(r"C:\Users\david\citizen-compass\releases\latest.html")

# Option 2: More portable - assume test runs from project root or use environment variable
# Get project root from environment variable or relative to this file
PROJECT_ROOT = Path(os.environ.get("CITIZEN_COMPASS_ROOT", Path(__file__).parent.parent))
LATEST_HTML_PATH = PROJECT_ROOT / "releases" / "latest.html"

# Option 3: If you know the exact relative structure, use this:
# LATEST_HTML_PATH = Path(__file__).parent.parent / "releases" / "latest.html"


def test_latest_html_exists():
    """Test that the latest.html file exists."""
    assert LATEST_HTML_PATH.is_file(), f"File not found: {LATEST_HTML_PATH}"


def test_latest_html_not_empty():
    """Test that the latest.html file is not empty."""
    assert LATEST_HTML_PATH.stat().st_size > 0, f"File is empty: {LATEST_HTML_PATH}"


def test_latest_html_contains_html_tag():
    """Test that the file contains basic HTML structure."""
    content = LATEST_HTML_PATH.read_text(encoding="utf-8")
    # Check for html tag (case insensitive)
    assert "<html" in content.lower(), "No <html> tag found in latest.html"
    assert "</html>" in content.lower(), "No closing </html> tag found in latest.html"


def test_latest_html_has_expected_content():
    """
    Test that the file contains expected release information.
    CUSTOMIZE THIS TEST BASED ON WHAT SHOULD BE IN latest.html
    """
    content = LATEST_HTML_PATH.read_text(encoding="utf-8")

    # Example checks - adjust as needed for your project:
    # assert "Latest Release" in content, "Missing 'Latest Release' heading"
    # assert "Version" in content, "Missing version information"
    # assert "2026" in content, "Missing current year in release notes"

    # Placeholder - replace with actual expected content for your project
    # For now, just check it's not empty and has some text
    assert len(content.strip()) > 0, "File appears to be empty or whitespace only"


# Optional: If you want to test specific patterns (e.g., version numbers)
def test_latest_html_version_pattern():
    """Test that version number follows expected pattern (customize regex)."""
    content = LATEST_HTML_PATH.read_text(encoding="utf-8")
    # Example: look for something like "v1.2.3" or "Version 1.2.3"
    # import re
    # version_pattern = r'v\d+\.\d+\.\d+|Version\s+\d+\.\d+\.\d+'
    # assert re.search(version_pattern, content), f"No version pattern found in {LATEST_HTML_PATH}"
    pass  # Implement based on your versioning scheme


if __name__ == "__main__":
    # Allow running this test file directly for quick checks
    pytest.main([__file__, "-v"])