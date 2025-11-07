# Unified Config System Design (Pydantic v2)

**Date:** 2025-11-03  
**Status:** Design Draft  
**Goal:** Single `config/mcp.yaml` file with full Pydantic v2 validation

---

## Problem Statement

**Current State:**
- Two separate config systems (`models/config.py` + `config/index_config.yaml`)
- No validation until runtime (fail during search, not startup)
- Manual dict access: `config["indexes"]["standards"]["vector"]["model"]`
- Guessing structure: "Is it `vector` or `embedding`?"
- No IDE autocomplete
- Poor error messages: "KeyError: 'model'" vs "model must be >= 100 chars"

**Goal:**
- Single config file: `config/mcp.yaml`
- Pydantic v2 schemas with full validation
- Type-safe access: `config.indexes.standards.vector.model`
- Fail-fast at startup with clear error messages
- Config-driven: zero code changes for supported behaviors
- IDE autocomplete everywhere

---

## Unified Config Structure

### File: `config/mcp.yaml`

```yaml
# ============================================================================
# prAxIs OS MCP Server Configuration
# ============================================================================
# Single source of truth for all MCP server behavior.
# Validated at startup - invalid config = clear error message, won't start.

version: "1.0"

# ============================================================================
# SERVER SETTINGS
# ============================================================================
server:
  # Transport configuration
  transport:
    mode: stdio  # stdio | http | dual
    http:
      host: "127.0.0.1"
      port: 4242
      path: "/mcp"
  
  # Tool configuration
  tools:
    max_tools_warning: 20
    enabled_groups:
      - rag
      - workflow
      - browser
  
  # Paths (relative to .praxis-os/)
  paths:
    standards: "standards/"
    workflows: "workflows/"
    specs: "workspace/specs/"
    cache: ".cache/"

# ============================================================================
# RAG / SEARCH CONFIGURATION
# ============================================================================
indexes:
  # ---------------------------------------------------------------------------
  # Standards Index (Markdown Documentation)
  # ---------------------------------------------------------------------------
  standards:
    enabled: true
    
    # What to index
    source_paths:
      - "standards/"
    file_patterns:
      - "*.md"
    
    # Vector search (semantic)
    vector:
      enabled: true
      model: "BAAI/bge-small-en-v1.5"  # or bge-base, bge-large
      chunk_size: 500        # tokens per chunk (100-2000)
      chunk_overlap: 50      # overlap tokens (0-500)
      batch_size: 32         # embedding batch size
      device: "cpu"          # cpu | cuda | mps
    
    # Full-text search (keyword)
    fts:
      enabled: true
      with_position: false
      stem: true
      remove_stop_words: true
      ascii_folding: true
      max_token_length: 40
    
    # Metadata extraction
    metadata:
      extract_frontmatter: true
      extract_headers: true
      extract_code_blocks: false
    
    # Cache settings
    cache:
      enabled: true
      ttl_seconds: 3600
  
  # ---------------------------------------------------------------------------
  # Code Index (Semantic Code Search)
  # ---------------------------------------------------------------------------
  code:
    enabled: true
    
    # What to index
    source_paths:
      - "mcp_server/"
      - "scripts/"
    file_patterns:
      - "*.py"
      - "*.ts"
      - "*.tsx"
      - "*.js"
      - "*.jsx"
    exclude_patterns:
      - "**/__pycache__/**"
      - "**/node_modules/**"
      - "**/.venv/**"
      - "**/dist/**"
    
    # Vector search for code
    vector:
      enabled: true
      model: "microsoft/codebert-base"  # Code-specific model
      chunk_size: 200       # Smaller chunks for code
      chunk_overlap: 20
      batch_size: 16
      device: "cpu"
    
    # Code-specific FTS
    fts:
      enabled: true
      with_position: true   # For code, position matters
      stem: false           # Don't stem code identifiers
      remove_stop_words: false
      ascii_folding: false
      max_token_length: 100
    
    cache:
      enabled: true
      ttl_seconds: 1800
  
  # ---------------------------------------------------------------------------
  # AST Index (Structural Code Search)
  # ---------------------------------------------------------------------------
  ast:
    enabled: true
    
    # Auto-install Tree-sitter parsers
    auto_install_parsers: true
    
    # Supported languages (auto-detect from file extensions)
    languages:
      python:
        enabled: true
        file_extensions: [".py"]
        parser: "tree-sitter-python"
      typescript:
        enabled: true
        file_extensions: [".ts", ".tsx"]
        parser: "tree-sitter-typescript"
      javascript:
        enabled: true
        file_extensions: [".js", ".jsx"]
        parser: "tree-sitter-javascript"
      rust:
        enabled: false
        file_extensions: [".rs"]
        parser: "tree-sitter-rust"
      go:
        enabled: false
        file_extensions: [".go"]
        parser: "tree-sitter-go"
    
    # What to index
    node_types:
      - function_definition
      - class_definition
      - method_definition
      - import_statement
      - decorator
    
    cache:
      enabled: true
      ttl_seconds: 3600

# ============================================================================
# RETRIEVAL / RANKING CONFIGURATION
# ============================================================================
retrieval:
  # Hybrid search (vector + FTS fusion)
  hybrid:
    enabled: true
    fusion_method: "rrf"  # rrf | linear | rank_based
    rrf_k: 60             # RRF parameter (30-100)
    vector_weight: 0.7    # If using linear fusion
    fts_weight: 0.3
  
  # Cross-encoder re-ranking
  rerank:
    enabled: true
    model: "cross-encoder/ms-marco-MiniLM-L-6-v2"
    top_n: 10             # Re-rank top N results
    batch_size: 16
    device: "cpu"
  
  # Query expansion
  query_expansion:
    enabled: false
    method: "synonyms"    # synonyms | embeddings | llm
    max_expansions: 3

# ============================================================================
# FILE WATCHER CONFIGURATION
# ============================================================================
file_watcher:
  enabled: true
  
  # What to watch (dynamic based on index configs)
  # Automatically watches all source_paths from enabled indexes
  auto_watch_indexes: true
  
  # Debouncing (prevent rebuild spam)
  debounce_seconds: 2.0
  
  # Batch updates
  batch_updates: true
  batch_window_seconds: 5.0
  
  # Custom watched paths (in addition to indexes)
  additional_paths:
    - "config/"  # Rebuild on config changes

# ============================================================================
# WORKFLOW ENGINE CONFIGURATION
# ============================================================================
workflows:
  enabled: true
  
  # Where workflows are stored
  workflows_path: "workflows/"
  
  # Validation
  validate_on_load: true
  strict_mode: true
  
  # State management
  state:
    persistence: true
    checkpoint_interval: 30  # seconds
    max_history: 100

# ============================================================================
# BROWSER AUTOMATION CONFIGURATION
# ============================================================================
browser:
  enabled: true
  
  # Session management
  session_timeout_seconds: 3600
  max_concurrent_sessions: 5
  
  # Browser options
  headless: true
  viewport:
    width: 1280
    height: 720
  
  # Network
  user_agent: "praxis-os-browser/1.0"

# ============================================================================
# QUERY GAMIFICATION (Behavioral Reinforcement)
# ============================================================================
gamification:
  enabled: true
  
  # Prepend settings
  prepends:
    enabled: true
    show_progress: true
    show_suggestions: true
    show_warnings: true
  
  # Thresholds
  thresholds:
    diverse_angles_target: 3  # Aim for 3+ query angles
    query_count_low: 3
    query_count_medium: 5
    query_count_high: 10

# ============================================================================
# LOGGING & OBSERVABILITY
# ============================================================================
logging:
  level: "INFO"  # DEBUG | INFO | WARNING | ERROR
  format: "json"  # json | text
  
  # Component-specific levels
  components:
    rag: "INFO"
    workflow: "INFO"
    browser: "WARNING"
    file_watcher: "INFO"
  
  # Output
  file: ".cache/logs/mcp-server.log"
  max_bytes: 10485760  # 10MB
  backup_count: 5

# ============================================================================
# PERFORMANCE & LIMITS
# ============================================================================
performance:
  # Threading
  max_workers: 4
  
  # Memory
  max_cache_size_mb: 500
  
  # Rate limiting (per tool)
  rate_limits:
    search: 100  # queries per minute
    workflow: 20
    browser: 10

# ============================================================================
# FEATURE FLAGS
# ============================================================================
features:
  experimental:
    code_semantic_search: true
    query_expansion: false
    multi_modal_search: false
  
  beta:
    ast_search: true
    hybrid_reranking: true
```

---

## Pydantic v2 Schema Implementation

### File Structure:

```
mcp_server/
├── models/
│   ├── __init__.py
│   ├── config/              # NEW: Config schemas
│   │   ├── __init__.py
│   │   ├── base.py          # Base classes, enums
│   │   ├── server.py        # Server settings
│   │   ├── indexes.py       # Index configurations
│   │   ├── retrieval.py     # Retrieval settings
│   │   ├── monitoring.py    # Logging, performance
│   │   └── mcp_config.py    # Root MCPConfig class
```

---

### File: `mcp_server/models/config/base.py`

```python
"""Base configuration models and shared types."""

from enum import Enum
from pydantic import BaseModel, ConfigDict


class TransportMode(str, Enum):
    """MCP transport mode."""
    STDIO = "stdio"
    HTTP = "http"
    DUAL = "dual"


class LogLevel(str, Enum):
    """Logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class Device(str, Enum):
    """Compute device for embeddings."""
    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"  # Apple Silicon


class FusionMethod(str, Enum):
    """Hybrid search fusion method."""
    RRF = "rrf"  # Reciprocal Rank Fusion
    LINEAR = "linear"
    RANK_BASED = "rank_based"


class BaseConfig(BaseModel):
    """Base configuration with common settings."""
    
    model_config = ConfigDict(
        frozen=False,  # Mutable for testing, frozen in production
        validate_assignment=True,
        extra="forbid",  # Reject unknown fields
        str_strip_whitespace=True,
        use_enum_values=True
    )
```

---

### File: `mcp_server/models/config/indexes.py`

```python
"""Index configuration schemas."""

from pathlib import Path
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator, model_validator

from .base import BaseConfig, Device


class VectorConfig(BaseConfig):
    """Vector search configuration."""
    
    enabled: bool = Field(
        default=True,
        description="Enable vector similarity search"
    )
    
    model: str = Field(
        default="BAAI/bge-small-en-v1.5",
        description="Embedding model (HuggingFace identifier)",
        examples=["BAAI/bge-small-en-v1.5", "BAAI/bge-base-en-v1.5"]
    )
    
    chunk_size: int = Field(
        default=500,
        ge=100,
        le=2000,
        description="Chunk size in tokens"
    )
    
    chunk_overlap: int = Field(
        default=50,
        ge=0,
        le=500,
        description="Overlap between chunks in tokens"
    )
    
    batch_size: int = Field(
        default=32,
        ge=1,
        le=128,
        description="Batch size for embedding generation"
    )
    
    device: Device = Field(
        default=Device.CPU,
        description="Compute device"
    )
    
    @field_validator('chunk_overlap')
    @classmethod
    def overlap_less_than_size(cls, v: int, info) -> int:
        """Validate overlap < chunk_size."""
        chunk_size = info.data.get('chunk_size', 500)
        if v >= chunk_size:
            raise ValueError(
                f"chunk_overlap ({v}) must be < chunk_size ({chunk_size})"
            )
        return v


class FTSConfig(BaseConfig):
    """Full-text search configuration."""
    
    enabled: bool = Field(default=True)
    with_position: bool = Field(
        default=False,
        description="Enable positional indexing for phrase queries"
    )
    stem: bool = Field(
        default=True,
        description="Enable stemming (running → run)"
    )
    remove_stop_words: bool = Field(
        default=True,
        description="Remove common stop words (the, a, is)"
    )
    ascii_folding: bool = Field(
        default=True,
        description="Normalize accents (café → cafe)"
    )
    max_token_length: int = Field(
        default=40,
        ge=10,
        le=200,
        description="Maximum token length (filters base64, URLs)"
    )


class CacheConfig(BaseConfig):
    """Query cache configuration."""
    
    enabled: bool = Field(default=True)
    ttl_seconds: int = Field(
        default=3600,
        ge=60,
        le=86400,
        description="Cache TTL in seconds (1min - 24hrs)"
    )


class MetadataConfig(BaseConfig):
    """Metadata extraction configuration."""
    
    extract_frontmatter: bool = Field(default=True)
    extract_headers: bool = Field(default=True)
    extract_code_blocks: bool = Field(default=False)


class StandardsIndexConfig(BaseConfig):
    """Standards (markdown) index configuration."""
    
    enabled: bool = Field(default=True)
    source_paths: List[str] = Field(
        default_factory=lambda: ["standards/"],
        min_length=1,
        description="Paths to index (relative to .praxis-os/)"
    )
    file_patterns: List[str] = Field(
        default_factory=lambda: ["*.md"],
        min_length=1,
        description="File glob patterns"
    )
    
    vector: VectorConfig = Field(default_factory=VectorConfig)
    fts: FTSConfig = Field(default_factory=FTSConfig)
    metadata: MetadataConfig = Field(default_factory=MetadataConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    
    @field_validator('source_paths', mode='after')
    @classmethod
    def validate_paths_not_empty(cls, v: List[str]) -> List[str]:
        """Ensure no empty paths."""
        if any(not p.strip() for p in v):
            raise ValueError("source_paths cannot contain empty strings")
        return v


class CodeIndexConfig(BaseConfig):
    """Code (semantic) index configuration."""
    
    enabled: bool = Field(default=True)
    source_paths: List[str] = Field(default_factory=lambda: ["mcp_server/"])
    file_patterns: List[str] = Field(
        default_factory=lambda: ["*.py", "*.ts", "*.tsx", "*.js", "*.jsx"]
    )
    exclude_patterns: List[str] = Field(
        default_factory=lambda: [
            "**/__pycache__/**",
            "**/node_modules/**",
            "**/.venv/**",
            "**/dist/**"
        ]
    )
    
    vector: VectorConfig = Field(
        default_factory=lambda: VectorConfig(
            model="microsoft/codebert-base",
            chunk_size=200,
            chunk_overlap=20
        )
    )
    fts: FTSConfig = Field(
        default_factory=lambda: FTSConfig(
            with_position=True,
            stem=False,
            remove_stop_words=False
        )
    )
    cache: CacheConfig = Field(
        default_factory=lambda: CacheConfig(ttl_seconds=1800)
    )


class LanguageConfig(BaseConfig):
    """Tree-sitter language configuration."""
    
    enabled: bool = Field(default=True)
    file_extensions: List[str] = Field(min_length=1)
    parser: str = Field(description="Tree-sitter parser package name")


class ASTIndexConfig(BaseConfig):
    """AST (structural code) index configuration."""
    
    enabled: bool = Field(default=True)
    auto_install_parsers: bool = Field(
        default=True,
        description="Auto-install missing Tree-sitter parsers"
    )
    
    languages: dict[str, LanguageConfig] = Field(
        default_factory=lambda: {
            "python": LanguageConfig(
                enabled=True,
                file_extensions=[".py"],
                parser="tree-sitter-python"
            ),
            "typescript": LanguageConfig(
                enabled=True,
                file_extensions=[".ts", ".tsx"],
                parser="tree-sitter-typescript"
            ),
            "javascript": LanguageConfig(
                enabled=True,
                file_extensions=[".js", ".jsx"],
                parser="tree-sitter-javascript"
            )
        }
    )
    
    node_types: List[str] = Field(
        default_factory=lambda: [
            "function_definition",
            "class_definition",
            "method_definition",
            "import_statement",
            "decorator"
        ]
    )
    
    cache: CacheConfig = Field(default_factory=CacheConfig)


class IndexesConfig(BaseConfig):
    """All index configurations."""
    
    standards: StandardsIndexConfig = Field(
        default_factory=StandardsIndexConfig
    )
    code: CodeIndexConfig = Field(
        default_factory=CodeIndexConfig
    )
    ast: ASTIndexConfig = Field(
        default_factory=ASTIndexConfig
    )
```

---

### File: `mcp_server/models/config/mcp_config.py`

```python
"""Root MCP configuration model."""

from pathlib import Path
from typing import Dict, Any
from pydantic import Field, field_validator

import yaml

from .base import BaseConfig
from .server import ServerConfig
from .indexes import IndexesConfig
from .retrieval import RetrievalConfig
from .monitoring import MonitoringConfig


class MCPConfig(BaseConfig):
    """Complete MCP server configuration.
    
    Single source of truth loaded from config/mcp.yaml.
    All settings validated at startup.
    
    Example:
        >>> config = MCPConfig.from_yaml(Path("config/mcp.yaml"))
        >>> model = config.indexes.standards.vector.model
        >>> print(config.model_dump_json(indent=2))
    """
    
    version: str = Field(
        default="1.0",
        pattern=r"^\d+\.\d+$",
        description="Config schema version"
    )
    
    server: ServerConfig = Field(default_factory=ServerConfig)
    indexes: IndexesConfig = Field(default_factory=IndexesConfig)
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    
    @classmethod
    def from_yaml(cls, path: Path) -> "MCPConfig":
        """Load and validate configuration from YAML file.
        
        Args:
            path: Path to mcp.yaml configuration file
            
        Returns:
            Validated MCPConfig instance
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If YAML is invalid
            pydantic.ValidationError: If config is invalid
            
        Example:
            >>> config = MCPConfig.from_yaml(Path(".praxis-os/config/mcp.yaml"))
        """
        if not path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {path}\n"
                f"Expected mcp.yaml at this location."
            )
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Validate and return
        return cls.model_validate(data)
    
    def to_yaml(self, path: Path) -> None:
        """Save configuration to YAML file.
        
        Args:
            path: Output path for mcp.yaml
        """
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(
                self.model_dump(mode='json', exclude_none=True),
                f,
                default_flow_style=False,
                sort_keys=False
            )
    
    @field_validator('version')
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate config version matches supported versions."""
        supported = ["1.0"]
        if v not in supported:
            raise ValueError(
                f"Config version {v} not supported. "
                f"Supported versions: {supported}"
            )
        return v
```

---

## Usage Examples

### 1. Load Config (Startup)

```python
# mcp_server/__main__.py

from pathlib import Path
from .models.config import MCPConfig

def main():
    # Load config (fails fast with clear errors)
    try:
        config_path = Path(".praxis-os/config/mcp.yaml")
        config = MCPConfig.from_yaml(config_path)
    except FileNotFoundError as e:
        print(f"❌ Config file not found: {e}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML syntax: {e}")
        sys.exit(1)
    except ValidationError as e:
        print(f"❌ Invalid configuration:")
        for error in e.errors():
            loc = " → ".join(str(x) for x in error['loc'])
            msg = error['msg']
            print(f"   {loc}: {msg}")
        sys.exit(1)
    
    # Config is validated! Safe to use
    print(f"✅ Config loaded: {len(config.indexes)} indexes enabled")
    
    # Type-safe access with IDE autocomplete
    if config.indexes.standards.enabled:
        model = config.indexes.standards.vector.model
        print(f"✅ Standards index using model: {model}")
```

**Error output example:**
```
❌ Invalid configuration:
   indexes → standards → vector → chunk_size: Input should be greater than or equal to 100
   indexes → code → vector → model: String should match pattern '^[a-zA-Z0-9/_-]+$'
   retrieval → rerank → top_n: Input should be less than or equal to 100
```

### 2. Type-Safe Access (No More Dict Guessing)

```python
# Before (dict hell):
model = config.get("indexes", {}).get("standards", {}).get("vector", {}).get("model", "default")
# ❌ No autocomplete, runtime KeyError, no validation

# After (type-safe):
model = config.indexes.standards.vector.model
# ✅ IDE autocomplete, compile-time checks, validated at load
```

### 3. IndexManager Integration

```python
# mcp_server/server/indexes/index_manager.py

from ...models.config import MCPConfig, StandardsIndexConfig

class IndexManager:
    def __init__(self, base_path: Path, config: MCPConfig):
        """Initialize with validated config."""
        self.base_path = base_path
        self.config = config
        self.indexes = self._init_indexes()
    
    def _init_indexes(self) -> dict[str, BaseIndex]:
        """Initialize indexes from validated config."""
        indexes = {}
        
        # Standards index
        if self.config.indexes.standards.enabled:
            indexes["standards"] = StandardsIndex(
                cache_path=self.base_path / "vector_index",
                config=self.config.indexes.standards  # ← Pydantic model!
            )
        
        # Code index
        if self.config.indexes.code.enabled:
            indexes["code"] = CodeIndex(
                cache_path=self.base_path / "code_index",
                config=self.config.indexes.code
            )
        
        return indexes
```

### 4. StandardsIndex Integration

```python
# mcp_server/server/indexes/standards_index.py

from ...models.config import StandardsIndexConfig

class StandardsIndex(BaseIndex):
    def __init__(self, cache_path: Path, config: StandardsIndexConfig):
        """Initialize with validated config model."""
        self.cache_path = cache_path
        self.config = config  # ← Pydantic model, not dict!
        
        # Type-safe access
        self.embedding_model = config.vector.model
        self.chunk_size = config.vector.chunk_size
        self.chunk_overlap = config.vector.chunk_overlap
        self.fts_enabled = config.fts.enabled
        
        # No .get(), no KeyError, all validated!
```

---

## Migration Path

### Phase 1: Add Pydantic Models (Parallel)
- ✅ Add `pydantic>=2.0` to requirements
- ✅ Create `models/config/` schemas
- ✅ Keep old dict-based loading working

### Phase 2: Update Consumers
- ✅ Update `IndexManager` to accept `MCPConfig`
- ✅ Update `StandardsIndex` to accept `StandardsIndexConfig`
- ✅ Update `ServerFactory` to load unified config

### Phase 3: Remove Old System
- ✅ Delete `models/config.py` (old dataclasses)
- ✅ Deprecate `index_config.yaml`
- ✅ Single `config/mcp.yaml`

---

## Benefits Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Config files** | 2 files (`.py` + `.yaml`) | 1 file (`mcp.yaml`) |
| **Validation** | Runtime (during search) | Startup (fail-fast) |
| **Error messages** | "KeyError: 'model'" | "chunk_size must be >= 100" |
| **Type safety** | None (dict access) | Full (Pydantic models) |
| **IDE support** | No autocomplete | Full autocomplete |
| **Documentation** | Comments in YAML | Auto-generated from schema |
| **Adding new field** | Update 5+ places | Update schema + YAML |
| **Config changes** | Code change required | YAML edit only |

---

## Next: Language Choice Analysis

Now that we have the config design, let me analyze whether Python is the right language for this MCP server...

(See next document: `language-choice-analysis.md`)

