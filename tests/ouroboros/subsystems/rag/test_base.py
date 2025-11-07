"""Tests for RAG base types and interfaces."""

import pytest
from ouroboros.subsystems.rag.base import HealthStatus, SearchResult


class TestSearchResult:
    """Tests for SearchResult model."""

    def test_create_search_result(self):
        """Test creating a basic SearchResult."""
        result = SearchResult(
            content="Example content",
            file_path="standards/test.md",
            relevance_score=0.95,
            content_type="standard",
            metadata={"domain": "testing"},
        )

        assert result.content == "Example content"
        assert result.file_path == "standards/test.md"
        assert result.relevance_score == 0.95
        assert result.content_type == "standard"
        assert result.metadata == {"domain": "testing"}
        assert result.chunk_id is None
        assert result.line_range is None
        assert result.section is None

    def test_search_result_with_optional_fields(self):
        """Test SearchResult with all optional fields."""
        result = SearchResult(
            content="Code snippet",
            file_path="src/main.py",
            relevance_score=0.85,
            content_type="code",
            metadata={"language": "python"},
            chunk_id="abc123",
            line_range=(10, 25),
            section="Functions",
        )

        assert result.chunk_id == "abc123"
        assert result.line_range == (10, 25)
        assert result.section == "Functions"

    def test_search_result_immutable(self):
        """Test that SearchResult is immutable."""
        result = SearchResult(
            content="Test",
            file_path="test.md",
            relevance_score=0.5,
            content_type="standard",
            metadata={},
        )

        with pytest.raises(
            Exception
        ):  # Pydantic raises ValidationError for frozen models
            result.content = "Modified"

    def test_search_result_relevance_score_bounds(self):
        """Test that relevance_score is bounded to [0, 1]."""
        # Valid scores
        SearchResult(
            content="Test",
            file_path="test.md",
            relevance_score=0.0,
            content_type="standard",
            metadata={},
        )
        SearchResult(
            content="Test",
            file_path="test.md",
            relevance_score=1.0,
            content_type="standard",
            metadata={},
        )

        # Invalid scores
        with pytest.raises(Exception):
            SearchResult(
                content="Test",
                file_path="test.md",
                relevance_score=-0.1,
                content_type="standard",
                metadata={},
            )

        with pytest.raises(Exception):
            SearchResult(
                content="Test",
                file_path="test.md",
                relevance_score=1.1,
                content_type="standard",
                metadata={},
            )

    def test_search_result_forbids_extra_fields(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(Exception):
            SearchResult(
                content="Test",
                file_path="test.md",
                relevance_score=0.5,
                content_type="standard",
                metadata={},
                extra_field="not allowed",
            )


class TestHealthStatus:
    """Tests for HealthStatus model."""

    def test_create_health_status_healthy(self):
        """Test creating a healthy status."""
        status = HealthStatus(
            healthy=True, message="Index operational", details={"chunk_count": 100}
        )

        assert status.healthy is True
        assert status.message == "Index operational"
        assert status.details == {"chunk_count": 100}
        assert status.last_updated is None

    def test_create_health_status_unhealthy(self):
        """Test creating an unhealthy status."""
        status = HealthStatus(
            healthy=False,
            message="Index not built",
            details={"error": "Table does not exist"},
        )

        assert status.healthy is False
        assert status.message == "Index not built"
        assert status.details == {"error": "Table does not exist"}

    def test_health_status_with_timestamp(self):
        """Test HealthStatus with last_updated timestamp."""
        status = HealthStatus(
            healthy=True,
            message="Recently updated",
            details={},
            last_updated="2025-11-04T10:00:00Z",
        )

        assert status.last_updated == "2025-11-04T10:00:00Z"

    def test_health_status_immutable(self):
        """Test that HealthStatus is immutable."""
        status = HealthStatus(healthy=True, message="Test", details={})

        with pytest.raises(Exception):
            status.healthy = False

    def test_health_status_forbids_extra_fields(self):
        """Test that extra fields are forbidden."""
        with pytest.raises(Exception):
            HealthStatus(healthy=True, message="Test", details={}, extra="not allowed")
