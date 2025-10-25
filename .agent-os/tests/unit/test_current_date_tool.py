"""
Unit tests for current_date MCP tool logic.

Tests the date formatting and structure without requiring full MCP server setup.
"""

from datetime import datetime
from typing import Any, Dict

import pytest


def mock_current_date_implementation() -> Dict[str, Any]:
    """
    Mock implementation matching the actual current_date tool.

    This mirrors the logic in agent_os_rag.py without requiring
    the full MCP server infrastructure and dependencies.
    """
    now = datetime.now()

    return {
        "iso_date": now.strftime("%Y-%m-%d"),
        "iso_datetime": now.isoformat(),
        "day_of_week": now.strftime("%A"),
        "month": now.strftime("%B"),
        "year": now.year,
        "unix_timestamp": int(now.timestamp()),
        "formatted": {
            "spec_directory": f"{now.strftime('%Y-%m-%d')}-",
            "header": f"**Date**: {now.strftime('%Y-%m-%d')}",
            "readable": now.strftime("%B %d, %Y"),
        },
        "usage_note": "Use 'iso_date' (YYYY-MM-DD) for all specifications, directories, and headers per Agent OS date policy",
    }


class TestCurrentDateTool:
    """Test suite for current_date tool logic."""

    def test_current_date_returns_required_fields(self):
        """Verify current_date returns all required fields."""
        result = mock_current_date_implementation()

        # Verify required fields exist
        assert "iso_date" in result
        assert "iso_datetime" in result
        assert "day_of_week" in result
        assert "month" in result
        assert "year" in result
        assert "unix_timestamp" in result
        assert "formatted" in result
        assert "usage_note" in result

        # Verify formatted sub-fields
        assert "spec_directory" in result["formatted"]
        assert "header" in result["formatted"]
        assert "readable" in result["formatted"]

    def test_current_date_iso_format(self):
        """Verify iso_date follows YYYY-MM-DD format."""
        result = mock_current_date_implementation()

        # Verify ISO 8601 format
        iso_date = result["iso_date"]

        # Should match YYYY-MM-DD pattern
        parts = iso_date.split("-")
        assert len(parts) == 3, f"Expected 3 parts in {iso_date}"

        year, month, day = parts
        assert len(year) == 4, f"Year should be 4 digits: {year}"
        assert len(month) == 2, f"Month should be 2 digits: {month}"
        assert len(day) == 2, f"Day should be 2 digits: {day}"

        # Verify it's actually today's date
        today = datetime.now().strftime("%Y-%m-%d")
        assert iso_date == today, f"Expected {today}, got {iso_date}"

    def test_current_date_formatted_outputs(self):
        """Verify formatted outputs are correct."""
        result = mock_current_date_implementation()

        iso_date = result["iso_date"]

        # Verify spec_directory format
        assert result["formatted"]["spec_directory"] == f"{iso_date}-"

        # Verify header format
        assert result["formatted"]["header"] == f"**Date**: {iso_date}"

        # Verify readable format exists and has content
        assert len(result["formatted"]["readable"]) > 0

        # Verify readable matches expected pattern (Month DD, YYYY)
        readable = result["formatted"]["readable"]
        now = datetime.now()
        expected = now.strftime("%B %d, %Y")
        assert readable == expected

    def test_current_date_consistency(self):
        """Verify multiple calls return consistent results (within same second)."""
        result1 = mock_current_date_implementation()
        result2 = mock_current_date_implementation()

        # Should return same date (assuming test runs in <1 second)
        assert result1["iso_date"] == result2["iso_date"]
        assert result1["day_of_week"] == result2["day_of_week"]
        assert result1["month"] == result2["month"]
        assert result1["year"] == result2["year"]

    def test_current_date_types(self):
        """Verify field types are correct."""
        result = mock_current_date_implementation()

        # Verify types
        assert isinstance(result["iso_date"], str)
        assert isinstance(result["iso_datetime"], str)
        assert isinstance(result["day_of_week"], str)
        assert isinstance(result["month"], str)
        assert isinstance(result["year"], int)
        assert isinstance(result["unix_timestamp"], int)
        assert isinstance(result["formatted"], dict)
        assert isinstance(result["usage_note"], str)

    def test_current_date_iso_datetime_format(self):
        """Verify iso_datetime is valid ISO 8601 with time."""
        result = mock_current_date_implementation()

        iso_datetime = result["iso_datetime"]

        # Should be parseable as datetime
        parsed = datetime.fromisoformat(iso_datetime)
        assert parsed is not None

        # Should contain 'T' separator
        assert "T" in iso_datetime

    def test_current_date_unix_timestamp(self):
        """Verify unix_timestamp is reasonable."""
        result = mock_current_date_implementation()

        unix_ts = result["unix_timestamp"]

        # Should be positive
        assert unix_ts > 0

        # Should be recent (after 2020-01-01)
        assert unix_ts > 1577836800  # 2020-01-01 00:00:00 UTC

        # Should be before 2030-01-01 (sanity check)
        assert unix_ts < 1893456000  # 2030-01-01 00:00:00 UTC

    def test_current_date_day_of_week(self):
        """Verify day_of_week is valid."""
        result = mock_current_date_implementation()

        day_of_week = result["day_of_week"]

        valid_days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        assert day_of_week in valid_days

    def test_current_date_month(self):
        """Verify month is valid."""
        result = mock_current_date_implementation()

        month = result["month"]

        valid_months = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        assert month in valid_months
