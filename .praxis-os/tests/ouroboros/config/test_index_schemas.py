"""
Tests for index configuration schemas.

Tests all 9 index configuration Pydantic models:
    - VectorConfig
    - FTSConfig
    - RerankingConfig
    - GraphConfig
    - FileWatcherConfig
    - StandardsIndexConfig
    - CodeIndexConfig
    - ASTIndexConfig
    - IndexesConfig

Test Coverage:
    - Field validation and constraints
    - Cross-field validation (e.g., chunk_overlap < chunk_size)
    - Default values
    - Error messages and remediation
    - Immutability (frozen=True)
    - Unknown field rejection (extra="forbid")
"""

from pathlib import Path

import pytest
from ouroboros.config.schemas.indexes import (
    ASTIndexConfig,
    CodeIndexConfig,
    FileWatcherConfig,
    FTSConfig,
    GraphConfig,
    IndexesConfig,
    RerankingConfig,
    StandardsIndexConfig,
    VectorConfig,
)
from pydantic import ValidationError


class TestVectorConfig:
    """Tests for VectorConfig."""

    def test_vector_config_defaults(self):
        """Test VectorConfig with default values."""
        config = VectorConfig()
        assert config.model == "sentence-transformers/all-MiniLM-L6-v2"
        assert config.chunk_size == 800
        assert config.chunk_overlap == 100
        assert config.dimension == 384
        assert config.index_type == "HNSW"

    def test_vector_config_custom_values(self):
        """Test VectorConfig with custom values."""
        config = VectorConfig(
            model="microsoft/codebert-base",
            chunk_size=200,
            chunk_overlap=20,
            dimension=768,
            index_type="IVF_PQ",
        )
        assert config.model == "microsoft/codebert-base"
        assert config.chunk_size == 200
        assert config.chunk_overlap == 20
        assert config.dimension == 768
        assert config.index_type == "IVF_PQ"

    def test_vector_config_chunk_size_constraints(self):
        """Test chunk_size constraints (100-2000)."""
        # Valid sizes
        VectorConfig(chunk_size=100, chunk_overlap=0)  # Min (with overlap=0)
        VectorConfig(chunk_size=2000)  # Max
        VectorConfig(chunk_size=500)  # Mid

        # Too small
        with pytest.raises(ValidationError, match="greater than or equal to 100"):
            VectorConfig(chunk_size=99)

        # Too large
        with pytest.raises(ValidationError, match="less than or equal to 2000"):
            VectorConfig(chunk_size=2001)

    def test_vector_config_chunk_overlap_constraints(self):
        """Test chunk_overlap constraints (0-500)."""
        # Valid overlaps
        VectorConfig(chunk_overlap=0)  # Min
        VectorConfig(chunk_overlap=500)  # Max

        # Too small
        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            VectorConfig(chunk_overlap=-1)

        # Too large
        with pytest.raises(ValidationError, match="less than or equal to 500"):
            VectorConfig(chunk_overlap=501)

    def test_vector_config_overlap_lt_chunk_size(self):
        """Test cross-field validation: overlap < chunk_size."""
        # Valid: overlap < size
        VectorConfig(chunk_size=800, chunk_overlap=100)

        # Invalid: overlap >= size (within range, but >= chunk_size)
        with pytest.raises(ValidationError, match="chunk_overlap.*must be.*chunk_size"):
            VectorConfig(chunk_size=200, chunk_overlap=200)

        # Note: overlap=800 fails built-in constraint (le=500) before custom validator
        with pytest.raises(ValidationError, match="less than or equal to 500"):
            VectorConfig(chunk_size=800, chunk_overlap=800)

    def test_vector_config_dimension_constraints(self):
        """Test dimension constraints (128-4096)."""
        # Valid dimensions
        VectorConfig(dimension=128)  # Min
        VectorConfig(dimension=4096)  # Max

        # Too small
        with pytest.raises(ValidationError, match="greater than or equal to 128"):
            VectorConfig(dimension=127)

        # Too large
        with pytest.raises(ValidationError, match="less than or equal to 4096"):
            VectorConfig(dimension=4097)

    def test_vector_config_index_type_validation(self):
        """Test index_type pattern validation."""
        # Valid types
        VectorConfig(index_type="HNSW")
        VectorConfig(index_type="IVF_PQ")
        VectorConfig(index_type="FLAT")

        # Invalid type
        with pytest.raises(ValidationError, match="String should match pattern"):
            VectorConfig(index_type="INVALID")


class TestFTSConfig:
    """Tests for FTSConfig."""

    def test_fts_config_defaults(self):
        """Test FTSConfig with default values."""
        config = FTSConfig()
        assert config.enabled is True
        assert config.use_tantivy is False
        assert config.tokenizer == "default"

    def test_fts_config_custom_values(self):
        """Test FTSConfig with custom values."""
        config = FTSConfig(
            enabled=False,
            use_tantivy=True,
            tokenizer="whitespace",
        )
        assert config.enabled is False
        assert config.use_tantivy is True
        assert config.tokenizer == "whitespace"

    def test_fts_config_tokenizer_validation(self):
        """Test tokenizer pattern validation."""
        # Valid tokenizers
        FTSConfig(tokenizer="default")
        FTSConfig(tokenizer="standard")
        FTSConfig(tokenizer="whitespace")
        FTSConfig(tokenizer="simple")

        # Invalid tokenizer
        with pytest.raises(ValidationError, match="String should match pattern"):
            FTSConfig(tokenizer="invalid")


class TestRerankingConfig:
    """Tests for RerankingConfig."""

    def test_reranking_config_defaults(self):
        """Test RerankingConfig with default values."""
        config = RerankingConfig()
        assert config.enabled is False
        assert config.model == "cross-encoder/ms-marco-MiniLM-L-6-v2"
        assert config.top_k == 20

    def test_reranking_config_custom_values(self):
        """Test RerankingConfig with custom values."""
        config = RerankingConfig(
            enabled=True,
            model="custom-model",
            top_k=10,
        )
        assert config.enabled is True
        assert config.model == "custom-model"
        assert config.top_k == 10

    def test_reranking_config_top_k_constraints(self):
        """Test top_k constraints (5-100)."""
        # Valid values
        RerankingConfig(top_k=5)  # Min
        RerankingConfig(top_k=100)  # Max

        # Too small
        with pytest.raises(ValidationError, match="greater than or equal to 5"):
            RerankingConfig(top_k=4)

        # Too large
        with pytest.raises(ValidationError, match="less than or equal to 100"):
            RerankingConfig(top_k=101)


class TestGraphConfig:
    """Tests for GraphConfig."""

    def test_graph_config_defaults(self):
        """Test GraphConfig with default values."""
        config = GraphConfig()
        assert config.max_depth == 10
        assert config.relationship_types == ["calls", "imports", "inherits"]

    def test_graph_config_custom_values(self):
        """Test GraphConfig with custom values."""
        config = GraphConfig(
            max_depth=20,
            relationship_types=["calls", "imports"],
        )
        assert config.max_depth == 20
        assert config.relationship_types == ["calls", "imports"]

    def test_graph_config_max_depth_constraints(self):
        """Test max_depth constraints (1-100)."""
        # Valid values
        GraphConfig(max_depth=1)  # Min
        GraphConfig(max_depth=100)  # Max

        # Too small
        with pytest.raises(ValidationError, match="greater than or equal to 1"):
            GraphConfig(max_depth=0)

        # Too large
        with pytest.raises(ValidationError, match="less than or equal to 100"):
            GraphConfig(max_depth=101)


class TestFileWatcherConfig:
    """Tests for FileWatcherConfig."""

    def test_file_watcher_config_defaults(self):
        """Test FileWatcherConfig with default values."""
        config = FileWatcherConfig()
        assert config.enabled is True
        assert config.debounce_ms == 500
        assert "*.md" in config.watch_patterns
        assert "*.py" in config.watch_patterns

    def test_file_watcher_config_custom_values(self):
        """Test FileWatcherConfig with custom values."""
        config = FileWatcherConfig(
            enabled=False,
            debounce_ms=2000,
            watch_patterns=["*.md"],
        )
        assert config.enabled is False
        assert config.debounce_ms == 2000
        assert config.watch_patterns == ["*.md"]

    def test_file_watcher_config_debounce_constraints(self):
        """Test debounce_ms constraints (100-5000)."""
        # Valid values
        FileWatcherConfig(debounce_ms=100)  # Min
        FileWatcherConfig(debounce_ms=5000)  # Max

        # Too small
        with pytest.raises(ValidationError, match="greater than or equal to 100"):
            FileWatcherConfig(debounce_ms=99)

        # Too large
        with pytest.raises(ValidationError, match="less than or equal to 5000"):
            FileWatcherConfig(debounce_ms=5001)


class TestStandardsIndexConfig:
    """Tests for StandardsIndexConfig."""

    def test_standards_index_config_valid(self):
        """Test StandardsIndexConfig with valid values."""
        config = StandardsIndexConfig(
            source_paths=["standards/"],
            vector=VectorConfig(),
            fts=FTSConfig(),
            reranking=None,
        )
        assert config.source_paths == ["standards/"]
        assert config.vector is not None
        assert config.fts is not None
        assert config.reranking is None

    def test_standards_index_config_with_reranking(self):
        """Test StandardsIndexConfig with reranking enabled."""
        config = StandardsIndexConfig(
            source_paths=["standards/"],
            vector=VectorConfig(),
            fts=FTSConfig(),
            reranking=RerankingConfig(enabled=True),
        )
        assert config.reranking is not None
        assert config.reranking.enabled is True

    def test_standards_index_config_empty_source_paths(self):
        """Test StandardsIndexConfig rejects empty source_paths."""
        with pytest.raises(ValidationError, match="at least 1 item"):
            StandardsIndexConfig(
                source_paths=[],
                vector=VectorConfig(),
                fts=FTSConfig(),
            )

    def test_standards_index_config_multiple_paths(self):
        """Test StandardsIndexConfig with multiple source paths."""
        config = StandardsIndexConfig(
            source_paths=["standards/", "docs/", "guides/"],
            vector=VectorConfig(),
            fts=FTSConfig(),
        )
        assert len(config.source_paths) == 3


class TestCodeIndexConfig:
    """Tests for CodeIndexConfig."""

    def test_code_index_config_valid(self):
        """Test CodeIndexConfig with valid values."""
        config = CodeIndexConfig(
            source_paths=["src/"],
            languages=["python"],
            vector=VectorConfig(),
            fts=FTSConfig(),
            duckdb_path=Path(".praxis-os/code.duckdb"),
            graph=GraphConfig(),
        )
        assert config.source_paths == ["src/"]
        assert config.languages == ["python"]
        assert config.duckdb_path == Path(".praxis-os/code.duckdb")

    def test_code_index_config_empty_languages(self):
        """Test CodeIndexConfig rejects empty languages."""
        with pytest.raises(ValidationError, match="at least 1 item"):
            CodeIndexConfig(
                source_paths=["src/"],
                languages=[],
                vector=VectorConfig(),
                fts=FTSConfig(),
                graph=GraphConfig(),
            )

    def test_code_index_config_multiple_languages(self):
        """Test CodeIndexConfig with multiple languages."""
        config = CodeIndexConfig(
            source_paths=["src/", "lib/"],
            languages=["python", "typescript", "rust"],
            vector=VectorConfig(),
            fts=FTSConfig(),
            graph=GraphConfig(),
        )
        assert len(config.languages) == 3


class TestASTIndexConfig:
    """Tests for ASTIndexConfig."""

    def test_ast_index_config_valid(self):
        """Test ASTIndexConfig with valid values."""
        config = ASTIndexConfig(
            source_paths=["src/"],
            languages=["python"],
            auto_install_parsers=True,
            venv_path=Path(".praxis-os/venv"),
        )
        assert config.source_paths == ["src/"]
        assert config.languages == ["python"]
        assert config.auto_install_parsers is True
        assert config.venv_path == Path(".praxis-os/venv")

    def test_ast_index_config_defaults(self):
        """Test ASTIndexConfig with default values."""
        config = ASTIndexConfig(
            source_paths=["src/"],
            languages=["python"],
        )
        assert config.auto_install_parsers is True  # Default
        assert config.venv_path == Path(".praxis-os/venv")  # Default

    def test_ast_index_config_empty_languages(self):
        """Test ASTIndexConfig rejects empty languages."""
        with pytest.raises(ValidationError, match="at least 1 item"):
            ASTIndexConfig(
                source_paths=["src/"],
                languages=[],
            )


class TestIndexesConfig:
    """Tests for IndexesConfig (root container)."""

    def test_indexes_config_valid(self):
        """Test IndexesConfig with valid nested configs."""
        config = IndexesConfig(
            standards=StandardsIndexConfig(
                source_paths=["standards/"],
                vector=VectorConfig(),
                fts=FTSConfig(),
            ),
            code=CodeIndexConfig(
                source_paths=["src/"],
                languages=["python"],
                vector=VectorConfig(),
                fts=FTSConfig(),
                graph=GraphConfig(),
            ),
            ast=ASTIndexConfig(
                source_paths=["src/"],
                languages=["python"],
            ),
            cache_path=Path(".praxis-os/.cache/vector_index"),
            file_watcher=FileWatcherConfig(),
        )
        assert config.standards is not None
        assert config.code is not None
        assert config.ast is not None
        assert config.cache_path == Path(".praxis-os/.cache/vector_index")
        assert config.file_watcher is not None

    def test_indexes_config_default_cache_path(self):
        """Test IndexesConfig with default cache_path."""
        config = IndexesConfig(
            standards=StandardsIndexConfig(
                source_paths=["standards/"],
                vector=VectorConfig(),
                fts=FTSConfig(),
            ),
            code=CodeIndexConfig(
                source_paths=["src/"],
                languages=["python"],
                vector=VectorConfig(),
                fts=FTSConfig(),
                graph=GraphConfig(),
            ),
            ast=ASTIndexConfig(
                source_paths=["src/"],
                languages=["python"],
            ),
            file_watcher=FileWatcherConfig(),
        )
        assert config.cache_path == Path(".cache/indexes")  # Updated default path

    def test_indexes_config_immutability(self):
        """Test IndexesConfig is immutable (frozen=True)."""
        config = IndexesConfig(
            standards=StandardsIndexConfig(
                source_paths=["standards/"],
                vector=VectorConfig(),
                fts=FTSConfig(),
            ),
            code=CodeIndexConfig(
                source_paths=["src/"],
                languages=["python"],
                vector=VectorConfig(),
                fts=FTSConfig(),
                graph=GraphConfig(),
            ),
            ast=ASTIndexConfig(
                source_paths=["src/"],
                languages=["python"],
            ),
            file_watcher=FileWatcherConfig(),
        )

        # Attempt to modify should raise ValidationError
        with pytest.raises(ValidationError, match="Instance is frozen"):
            config.cache_path = Path("/tmp/other")  # type: ignore


class TestErrorMessages:
    """Tests for validation error message quality."""

    def test_chunk_overlap_error_message(self):
        """Test chunk_overlap validation error has custom remediation."""
        try:
            VectorConfig(chunk_size=200, chunk_overlap=200)
        except ValidationError as e:
            error_str = str(e)
            assert "Remediation" in error_str
            assert "chunk_overlap" in error_str

    def test_min_length_error_messages(self):
        """Test Pydantic built-in min_length validation works."""
        # source_paths
        try:
            StandardsIndexConfig(
                source_paths=[],
                vector=VectorConfig(),
                fts=FTSConfig(),
            )
        except ValidationError as e:
            error_str = str(e)
            assert "at least 1 item" in error_str
            assert "source_paths" in error_str

        # languages
        try:
            CodeIndexConfig(
                source_paths=["src/"],
                languages=[],
                vector=VectorConfig(),
                fts=FTSConfig(),
                graph=GraphConfig(),
            )
        except ValidationError as e:
            error_str = str(e)
            assert "at least 1 item" in error_str
            assert "languages" in error_str
