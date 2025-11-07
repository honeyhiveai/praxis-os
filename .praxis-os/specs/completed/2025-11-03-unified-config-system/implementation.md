# Implementation Approach

**Project:** Unified Configuration System with Pydantic v2  
**Date:** 2025-11-03

---

## 1. Implementation Philosophy

**Core Principles:**
1. **Test-Driven Development** - Write tests alongside implementation
2. **Fail-Fast** - Validate at startup, not runtime
3. **Type Safety** - No dict access, use Pydantic models everywhere
4. **Incremental Delivery** - Phase 1 is parallel-safe (non-breaking)
5. **Code Review Required** - All changes reviewed before merge

---

## 2. Implementation Order

Follow the 4-phase plan from `tasks.md`:

1. **Phase 1: Create Pydantic Schemas** (8-10 hours)
   - Parallel-safe: Old config continues working
   - Create all models, write tests
   - Milestone: Pydantic models exist and validate

2. **Phase 2: Update Consumers** (6-8 hours)
   - Refactor components to accept Pydantic models
   - Type-safe config access throughout
   - Milestone: No dict["key"] access remains

3. **Phase 3: Remove Old System** (3-4 hours)
   - Delete old dataclasses
   - Create migration script
   - Milestone: Single config/mcp.yaml

4. **Phase 4: Testing & Validation** (4-6 hours)
   - Integration, performance, security tests
   - Validate all requirements
   - Milestone: Production-ready

---

## 3. Code Patterns

### Pattern 1: Pydantic Model Definition

**Purpose:** Define configuration schemas with validation

**Good Example:**
```python
# ouroboros/models/config/indexes.py

from pydantic import BaseModel, Field, field_validator
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
        ge=100,      # Constraint: must be >= 100
        le=2000,     # Constraint: must be <= 2000
        description="Chunk size in tokens"
    )
    
    chunk_overlap: int = Field(
        default=50,
        ge=0,
        le=500,
        description="Overlap between chunks in tokens"
    )
    
    @field_validator('chunk_overlap')
    @classmethod
    def overlap_less_than_size(cls, v: int, info) -> int:
        """Validate overlap < chunk_size (cross-field validation)."""
        chunk_size = info.data.get('chunk_size', 500)
        if v >= chunk_size:
            raise ValueError(
                f"chunk_overlap ({v}) must be < chunk_size ({chunk_size})"
            )
        return v
```

**Key Points:**
- Inherit from `BaseConfig` (sets frozen=True, extra="forbid", etc.)
- Use `Field()` for validation constraints (ge, le, pattern)
- Add descriptions (auto-documentation)
- Use `@field_validator` for cross-field validation
- Type hint everything

**Anti-Pattern:**
```python
# ❌ DON'T: No validation, mutable, no descriptions
class VectorConfig:
    def __init__(self):
        self.model = "BAAI/bge-small-en-v1.5"
        self.chunk_size = 500  # No constraints!
```

---

### Pattern 2: Config Loading with Error Handling

**Purpose:** Load and validate config at startup with user-friendly errors

**Good Example:**
```python
# ouroboros/__main__.py

from pathlib import Path
from pydantic import ValidationError
import yaml
import sys

from .models.config import MCPConfig

def main():
    """Load config with comprehensive error handling."""
    config_path = Path(".praxis-os/config/mcp.yaml")
    
    try:
        # Load and validate (single call, fails fast)
        config = MCPConfig.from_yaml(config_path)
        
    except FileNotFoundError as e:
        print(f"❌ Config file not found: {config_path}")
        print("💡 Run 'praxis-os init' to create default config")
        sys.exit(1)
        
    except yaml.YAMLError as e:
        print(f"❌ Invalid YAML syntax:")
        print(f"   {e}")
        sys.exit(1)
        
    except ValidationError as e:
        print(f"❌ Invalid configuration:")
        for error in e.errors():
            # Display field path: "indexes → standards → vector → chunk_size"
            loc = " → ".join(str(x) for x in error['loc'])
            print(f"   {loc}: {error['msg']}")
            print(f"   Got: {error['input']}")
        sys.exit(1)
        
    # Config is valid, proceed with server startup
    factory = ServerFactory(config)
    server = factory.create_server()
    server.run()
```

**Key Points:**
- Catch specific exceptions (FileNotFoundError, YAMLError, ValidationError)
- Display user-friendly error messages
- Show field paths for validation errors
- Exit with non-zero status code
- Provide hints for common errors

**Anti-Pattern:**
```python
# ❌ DON'T: Generic error handling, no context
try:
    config = load_config()
except Exception as e:
    print("Error loading config")  # What error? Where?
    sys.exit(1)
```

---

### Pattern 3: Type-Safe Config Access

**Purpose:** Use Pydantic models for compile-time safety

**Good Example:**
```python
# ouroboros/server/indexes/standards_index.py

from pathlib import Path
from ...models.config import StandardsIndexConfig

class StandardsIndex(BaseIndex):
    def __init__(self, cache_path: Path, config: StandardsIndexConfig):
        """Initialize with validated config model."""
        self.cache_path = cache_path
        self.config = config  # ← Pydantic model, not dict!
        
        # Type-safe access (IDE autocomplete, no KeyError)
        self.embedding_model = config.vector.model
        self.chunk_size = config.vector.chunk_size
        self.chunk_overlap = config.vector.chunk_overlap
        self.fts_enabled = config.fts.enabled
        
        # Config is already validated, no need to check
        assert self.chunk_size >= 100  # Already validated by Pydantic!
```

**Key Points:**
- Accept Pydantic models, not dicts
- Use dot notation: `config.vector.model`
- No `.get()` calls needed
- No KeyError possible (validated at load)
- IDE provides autocomplete

**Anti-Pattern:**
```python
# ❌ DON'T: Dict access with .get() and defaults
def __init__(self, config: dict):
    self.config = config
    
    # No autocomplete, runtime KeyError risk
    self.embedding_model = config.get("vector", {}).get("model", "default")
    
    # Manual validation (should be in Pydantic schema)
    self.chunk_size = config.get("vector", {}).get("chunk_size", 500)
    if self.chunk_size < 100:
        raise ValueError("chunk_size must be >= 100")
```

---

### Pattern 4: Dependency Injection with Config

**Purpose:** Pass config objects through constructors

**Good Example:**
```python
# ouroboros/server/indexes/index_manager.py

from pathlib import Path
from ...models.config import IndexesConfig
from .standards_index import StandardsIndex
from .code_index import CodeIndex
from .ast_index import ASTIndex

class IndexManager:
    def __init__(self, base_path: Path, config: IndexesConfig):
        """Initialize with validated indexes config.
        
        Args:
            base_path: Root path for index storage
            config: Validated IndexesConfig instance (Pydantic model)
        """
        self.base_path = base_path
        self.config = config
        self.indexes = self._init_indexes()
    
    def _init_indexes(self) -> dict[str, BaseIndex]:
        """Initialize indexes from validated config."""
        indexes = {}
        
        # Standards index (conditional on config.standards.enabled)
        if self.config.standards.enabled:
            indexes["standards"] = StandardsIndex(
                cache_path=self.base_path / "vector_index",
                config=self.config.standards  # ← Pass Pydantic model
            )
        
        # Code index
        if self.config.code.enabled:
            indexes["code"] = CodeIndex(
                cache_path=self.base_path / "code_index",
                config=self.config.code  # ← Pass Pydantic model
            )
        
        # AST index
        if self.config.ast.enabled:
            indexes["ast"] = ASTIndex(
                cache_path=self.base_path / "ast",
                config=self.config.ast  # ← Pass Pydantic model
            )
        
        return indexes
```

**Key Points:**
- Accept Pydantic models in constructors
- Pass subset models to children (config.standards → StandardsIndex)
- Dynamic initialization based on config.enabled flags
- No global config singleton

**Anti-Pattern:**
```python
# ❌ DON'T: Global config singleton
GLOBAL_CONFIG = load_config()  # Tight coupling!

class IndexManager:
    def __init__(self):
        # Hard to test (can't inject mock config)
        self.config = GLOBAL_CONFIG
```

---

### Pattern 5: Config File Structure (YAML)

**Purpose:** Hierarchical, commented YAML config

**Good Example:**
```yaml
# config/mcp.yaml

# ============================================================================
# prAxIs OS MCP Server Configuration
# ============================================================================
# Single source of truth for all MCP server behavior.
# Validated at startup - invalid config = clear error message, won't start.

version: "1.0"

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
      model: "BAAI/bge-small-en-v1.5"  # HuggingFace model ID
      chunk_size: 500        # tokens per chunk (100-2000)
      chunk_overlap: 50      # overlap tokens (0-500, must be < chunk_size)
      batch_size: 32         # embedding batch size (1-128)
      device: "cpu"          # cpu | cuda | mps
```

**Key Points:**
- Use comments generously (explain each section)
- Show valid values in comments (e.g., "cpu | cuda | mps")
- Show constraints in comments (e.g., "100-2000")
- Use hierarchy (indexes → standards → vector → model)
- Use descriptive section headers with separators

**Anti-Pattern:**
```yaml
# ❌ DON'T: No comments, flat structure, unclear values
standards_enabled: true
standards_model: BAAI/bge-small-en-v1.5
standards_chunk_size: 500
standards_chunk_overlap: 50
# No context, hard to understand relationships
```

---

### Pattern 6: Validation Error Testing

**Purpose:** Test that Pydantic validation catches invalid configs

**Good Example:**
```python
# tests/unit/test_config_models.py

import pytest
from pydantic import ValidationError
from ouroboros.models.config import VectorConfig

def test_chunk_size_below_minimum():
    """Test that chunk_size < 100 is rejected."""
    with pytest.raises(ValidationError) as exc_info:
        VectorConfig(chunk_size=50)  # Below minimum (100)
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['loc'] == ('chunk_size',)
    assert 'greater than or equal to 100' in errors[0]['msg']

def test_chunk_overlap_greater_than_size():
    """Test cross-field validation: overlap < chunk_size."""
    with pytest.raises(ValidationError) as exc_info:
        VectorConfig(chunk_size=100, chunk_overlap=150)
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert 'chunk_overlap (150) must be < chunk_size (100)' in str(errors[0])

def test_unknown_field_rejected():
    """Test that extra fields are rejected (extra="forbid")."""
    with pytest.raises(ValidationError) as exc_info:
        VectorConfig(chunk_size=500, admin=True)  # Unknown field
    
    errors = exc_info.value.errors()
    assert 'extra fields not permitted' in str(errors[0])
```

**Key Points:**
- Test constraints (ge, le, pattern)
- Test cross-field validators
- Test extra="forbid" (unknown fields)
- Verify error messages are clear
- Use pytest.raises(ValidationError)

---

### Pattern 7: Migration Script Pattern

**Purpose:** Convert old config to new format

**Good Example:**
```python
# scripts/migrate_config.py

from pathlib import Path
import yaml
from ouroboros.models.config import MCPConfig

def migrate_config(old_path: Path, new_path: Path, dry_run: bool = False):
    """Migrate from old index_config.yaml to new config/mcp.yaml.
    
    Args:
        old_path: Path to old config/index_config.yaml
        new_path: Path to new config/mcp.yaml
        dry_run: If True, validate but don't write file
    """
    # 1. Load old config (raw dict)
    with open(old_path, 'r') as f:
        old_config = yaml.safe_load(f)
    
    # 2. Transform to new structure
    new_config_dict = {
        "version": "1.0",
        "indexes": {
            "standards": {
                "enabled": old_config.get("enabled", True),
                "source_paths": old_config.get("source_paths", ["standards/"]),
                "vector": {
                    "model": old_config.get("embedding", {}).get("model", "BAAI/bge-small-en-v1.5"),
                    "chunk_size": old_config.get("chunk_size", 500),
                    # ... map all fields
                }
            }
        }
    }
    
    # 3. Validate with Pydantic (fail-fast if invalid)
    config = MCPConfig(**new_config_dict)
    
    # 4. Write to new location (if not dry run)
    if not dry_run:
        config.to_yaml(new_path)
        print(f"✅ Migrated config to {new_path}")
    else:
        print(f"✅ Migration would succeed (dry run)")
    
    return config
```

**Key Points:**
- Load old config as dict
- Transform to new structure
- Validate with Pydantic before writing
- Support dry-run mode
- Clear success/error messages

---

## 4. Testing Patterns

### Unit Test Pattern (Pydantic Models)

```python
# tests/unit/test_config_models.py

import pytest
from ouroboros.models.config import MCPConfig

def test_valid_config_loads_successfully():
    """Test that valid config loads without errors."""
    config_data = {
        "version": "1.0",
        "indexes": {
            "standards": {
                "enabled": True,
                "vector": {
                    "model": "BAAI/bge-small-en-v1.5",
                    "chunk_size": 500,
                    "chunk_overlap": 50
                }
            }
        }
    }
    
    config = MCPConfig(**config_data)
    
    # Verify type-safe access works
    assert config.indexes.standards.vector.model == "BAAI/bge-small-en-v1.5"
    assert config.indexes.standards.vector.chunk_size == 500
```

### Integration Test Pattern (Config Loading)

```python
# tests/integration/test_config_integration.py

from pathlib import Path
from ouroboros.models.config import MCPConfig
from ouroboros.server.factory import ServerFactory

def test_server_starts_with_valid_config(tmp_path):
    """Test that server starts successfully with valid config."""
    # 1. Create valid config file
    config_path = tmp_path / "config" / "mcp.yaml"
    config_path.parent.mkdir(parents=True)
    
    MCPConfig().to_yaml(config_path)  # Write default config
    
    # 2. Load config
    config = MCPConfig.from_yaml(config_path)
    
    # 3. Create server
    factory = ServerFactory(config)
    server = factory.create_server()
    
    # 4. Verify server is configured correctly
    assert server is not None
    assert server.index_manager is not None
```

---

## 5. Anti-Patterns to Avoid

### Anti-Pattern 1: Dict Access Instead of Pydantic Models

```python
# ❌ DON'T
config = yaml.safe_load(f)
model = config["indexes"]["standards"]["vector"]["model"]

# ✅ DO
config = MCPConfig.from_yaml(path)
model = config.indexes.standards.vector.model
```

### Anti-Pattern 2: Manual Validation in Application Code

```python
# ❌ DON'T: Validate in multiple places
if chunk_size < 100 or chunk_size > 2000:
    raise ValueError("chunk_size must be 100-2000")

# ✅ DO: Validate once in Pydantic schema
class VectorConfig(BaseConfig):
    chunk_size: int = Field(ge=100, le=2000)
```

### Anti-Pattern 3: Mutable Config

```python
# ❌ DON'T: Allow runtime mutations
config.indexes.standards.vector.model = "new-model"  # Should fail!

# ✅ DO: Use frozen=True in BaseConfig
class BaseConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
```

### Anti-Pattern 4: Silent Defaults for Unknown Fields

```python
# ❌ DON'T: Silently ignore typos
class Config(BaseModel):
    model_config = ConfigDict(extra="allow")  # Typos ignored!

# ✅ DO: Reject unknown fields
class BaseConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")  # Typos raise error
```

---

## 6. Implementation Checklist

**Before starting implementation:**
- [ ] Read specs.md (Architecture, Components, APIs)
- [ ] Read tasks.md (Implementation phases and tasks)
- [ ] Review this file (Code patterns and anti-patterns)
- [ ] Set up development environment (Python 3.10+, pydantic>=2.0)

**During implementation (per task):**
- [ ] Follow phase order from tasks.md
- [ ] Write tests alongside code (TDD)
- [ ] Use type-safe config access (no dict["key"])
- [ ] Add validation in Pydantic schemas (not application code)
- [ ] Update task acceptance criteria checklist
- [ ] Run tests and linters before commit

**Before marking task complete:**
- [ ] All tests pass (unit + integration)
- [ ] Coverage >= target (90% for config code)
- [ ] No linter errors (pylint, ruff)
- [ ] No type errors (mypy --strict)
- [ ] Acceptance criteria met (from tasks.md)
- [ ] Code reviewed

---

## 7. Common Pitfalls

**Pitfall 1:** "Config works in my tests but fails in production"
- **Cause:** Tests use dicts, production uses Pydantic models
- **Fix:** Use Pydantic models in tests too

**Pitfall 2:** "Validation errors are unclear"
- **Cause:** No field descriptions in Pydantic models
- **Fix:** Add `description=` to all Field() definitions

**Pitfall 3:** "Server starts but crashes during search"
- **Cause:** Validation happens too late (runtime)
- **Fix:** Use Pydantic validation at startup (fail-fast)

**Pitfall 4:** "Can't add new config field without breaking old code"
- **Cause:** No default values for new fields
- **Fix:** All new fields must have defaults (backwards compat)

**Pitfall 5:** "IDE autocomplete doesn't work for config"
- **Cause:** Using dict access instead of Pydantic properties
- **Fix:** Use type-hinted Pydantic models everywhere

---

## 8. Testing Strategy

### 8.1 Testing Philosophy

**Core Principles:**
1. **Test-Driven Development** - Write tests alongside implementation
2. **Comprehensive Coverage** - Target >= 90% for config code, >= 80% overall
3. **Fast Feedback** - Unit tests must be fast (<1s for suite)
4. **Realistic Integration Tests** - Test actual file loading, not mocks
5. **Security Testing** - Validate input validation and path security

---

### 8.2 Test Organization

```
tests/
├── unit/                          # Fast, isolated tests
│   ├── test_config_models.py     # Pydantic model validation
│   ├── test_index_manager.py     # IndexManager logic
│   ├── test_standards_index.py   # StandardsIndex logic
│   └── fixtures/
│       └── configs/               # Test config files
│           ├── valid.yaml
│           ├── invalid_chunk_size.yaml
│           └── invalid_yaml.yaml
│
├── integration/                   # Component interaction tests
│   ├── test_config_integration.py # End-to-end config loading
│   ├── test_server_startup.py    # Server initialization
│   └── test_index_integration.py # Index initialization
│
├── performance/                   # Performance regression tests
│   ├── test_config_performance.py # Config load time
│   └── test_property_access.py   # Property access speed
│
└── security/                      # Security validation tests
    ├── test_config_security.py    # Input validation
    └── test_path_security.py      # Path traversal prevention
```

---

### 8.3 Unit Testing Approach

**Coverage Target:** >= 90% for `mcp_server/models/config/`

**Pattern: Arrange-Act-Assert**
```python
# tests/unit/test_config_models.py

import pytest
from pydantic import ValidationError
from ouroboros.models.config import VectorConfig, MCPConfig

def test_vector_config_valid_defaults():
    """Test that VectorConfig initializes with valid defaults."""
    # Arrange (nothing needed for defaults)
    
    # Act
    config = VectorConfig()
    
    # Assert
    assert config.enabled is True
    assert config.model == "BAAI/bge-small-en-v1.5"
    assert config.chunk_size == 500
    assert config.chunk_overlap == 50
    assert config.batch_size == 32


def test_vector_config_chunk_size_below_minimum():
    """Test that chunk_size < 100 raises ValidationError."""
    # Arrange
    invalid_data = {"chunk_size": 50}
    
    # Act & Assert
    with pytest.raises(ValidationError) as exc_info:
        VectorConfig(**invalid_data)
    
    # Verify error details
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]['loc'] == ('chunk_size',)
    assert 'greater than or equal to 100' in errors[0]['msg']


@pytest.mark.parametrize("chunk_size,chunk_overlap,should_pass", [
    (500, 50, True),   # Valid: overlap < chunk_size
    (100, 50, True),   # Valid: overlap < chunk_size
    (100, 99, True),   # Valid: overlap < chunk_size (edge case)
    (100, 100, False), # Invalid: overlap == chunk_size
    (100, 150, False), # Invalid: overlap > chunk_size
])
def test_chunk_overlap_validation(chunk_size, chunk_overlap, should_pass):
    """Test cross-field validation: chunk_overlap < chunk_size."""
    data = {"chunk_size": chunk_size, "chunk_overlap": chunk_overlap}
    
    if should_pass:
        config = VectorConfig(**data)
        assert config.chunk_size == chunk_size
        assert config.chunk_overlap == chunk_overlap
    else:
        with pytest.raises(ValidationError):
            VectorConfig(**data)
```

**Test Coverage Requirements:**
- **Field Constraints:** Test all Field(ge=, le=, pattern=) constraints
- **Cross-Field Validation:** Test all @field_validator methods
- **Unknown Fields:** Test extra="forbid" enforcement
- **Error Messages:** Verify messages are clear and actionable
- **Edge Cases:** Test boundary values (min, max, min-1, max+1)

---

### 8.4 Integration Testing Approach

**Coverage Target:** All critical paths (config load → server start → search)

**Pattern: End-to-End Scenarios**
```python
# tests/integration/test_config_integration.py

from pathlib import Path
import pytest
from ouroboros.models.config import MCPConfig
from ouroboros.server.factory import ServerFactory

@pytest.fixture
def config_dir(tmp_path):
    """Create temporary config directory."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


def test_server_starts_with_valid_config(config_dir):
    """Test complete flow: load config → create server → verify initialized."""
    # Arrange: Create valid config file
    config_path = config_dir / "mcp.yaml"
    default_config = MCPConfig()
    default_config.to_yaml(config_path)
    
    # Act: Load config and create server
    config = MCPConfig.from_yaml(config_path)
    factory = ServerFactory(config)
    server = factory.create_server()
    
    # Assert: Server is properly configured
    assert server is not None
    assert server.index_manager is not None
    assert "standards" in server.index_manager.indexes
    
    # Verify index uses config values
    standards_index = server.index_manager.indexes["standards"]
    assert standards_index.embedding_model == "BAAI/bge-small-en-v1.5"
    assert standards_index.chunk_size == 500


def test_server_startup_fails_with_invalid_config(config_dir):
    """Test that invalid config prevents server startup."""
    # Arrange: Create invalid config file
    config_path = config_dir / "mcp.yaml"
    with open(config_path, 'w') as f:
        f.write("indexes:\n  standards:\n    vector:\n      chunk_size: 50")  # Invalid!
    
    # Act & Assert: Loading config should fail
    with pytest.raises(ValidationError) as exc_info:
        MCPConfig.from_yaml(config_path)
    
    errors = exc_info.value.errors()
    assert any('chunk_size' in str(error['loc']) for error in errors)


def test_config_immutability(config_dir):
    """Test that config is immutable after load (frozen=True)."""
    # Arrange
    config_path = config_dir / "mcp.yaml"
    MCPConfig().to_yaml(config_path)
    config = MCPConfig.from_yaml(config_path)
    
    # Act & Assert: Mutation should fail
    with pytest.raises(ValidationError):
        config.indexes.standards.vector.model = "new-model"
```

**Integration Test Scenarios:**
- **Happy Path:** Valid config → server starts → indexes initialize
- **Invalid Config:** Various validation errors → clear error messages
- **Config Immutability:** Mutations rejected after load
- **Backwards Compatibility:** Old config format still works (with warning)
- **Migration:** Migration script produces valid new config

---

### 8.5 Performance Testing Approach

**Coverage Target:** All NFR-P metrics (<100ms startup, <1μs access)

**Pattern: Timing Assertions**
```python
# tests/performance/test_config_performance.py

import time
import numpy as np
import pytest
from pathlib import Path
from ouroboros.models.config import MCPConfig

@pytest.mark.performance
def test_config_load_time_under_100ms(tmp_path):
    """Test that config loads in < 100ms (p95)."""
    # Arrange: Create config file
    config_path = tmp_path / "config" / "mcp.yaml"
    config_path.parent.mkdir()
    MCPConfig().to_yaml(config_path)
    
    # Act: Time config load (10 iterations for p95)
    times = []
    for _ in range(10):
        start = time.perf_counter()
        config = MCPConfig.from_yaml(config_path)
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to ms
    
    # Assert: p95 < 100ms
    p95_time = np.percentile(times, 95)
    assert p95_time < 100, f"Config load p95: {p95_time:.2f}ms (target: <100ms)"


@pytest.mark.performance
def test_property_access_time_under_1us(tmp_path):
    """Test that property access is < 1μs (mean)."""
    # Arrange
    config_path = tmp_path / "config" / "mcp.yaml"
    config_path.parent.mkdir()
    MCPConfig().to_yaml(config_path)
    config = MCPConfig.from_yaml(config_path)
    
    # Act: Time property access (10,000 iterations for stable mean)
    times = []
    for _ in range(10000):
        start = time.perf_counter()
        _ = config.indexes.standards.vector.model
        end = time.perf_counter()
        times.append((end - start) * 1_000_000)  # Convert to μs
    
    # Assert: mean < 1μs
    mean_time = np.mean(times)
    assert mean_time < 1, f"Property access mean: {mean_time:.3f}μs (target: <1μs)"
```

**Performance Tests Required:**
- **YAML Load Time:** < 20ms
- **Pydantic Validation Time:** < 80ms
- **Total Config Load Time:** < 100ms (p95)
- **Property Access Time:** < 1μs (mean)
- **Memory Footprint:** < 50KB
- **Scalability:** Linear scaling with config size

---

### 8.6 Security Testing Approach

**Coverage Target:** All security controls validated

**Pattern: Attack Simulation**
```python
# tests/security/test_config_security.py

import pytest
from pydantic import ValidationError
from ouroboros.models.config import MCPConfig, StandardsIndexConfig

@pytest.mark.security
def test_type_confusion_prevention():
    """Test that type confusion attacks are prevented."""
    # Attempt: String instead of int
    with pytest.raises(ValidationError):
        StandardsIndexConfig(
            vector={"chunk_size": "999999999"}  # String, not int
        )
    
    # Attempt: Boolean instead of string
    with pytest.raises(ValidationError):
        StandardsIndexConfig(
            vector={"model": True}  # Boolean, not string
        )


@pytest.mark.security
def test_resource_exhaustion_prevention():
    """Test that resource exhaustion attacks are prevented."""
    # Attempt: Huge chunk_size
    with pytest.raises(ValidationError) as exc_info:
        StandardsIndexConfig(
            vector={"chunk_size": 999999999}  # Way above max (2000)
        )
    
    assert "must be <= 2000" in str(exc_info.value)


@pytest.mark.security
def test_unknown_field_injection():
    """Test that unknown fields are rejected (prevents typo-based attacks)."""
    # Attempt: Inject unknown field
    with pytest.raises(ValidationError) as exc_info:
        MCPConfig(
            admin=True,  # Unknown field (typo or malicious)
            indexes={}
        )
    
    assert "extra fields not permitted" in str(exc_info.value)


@pytest.mark.security
def test_path_traversal_detection():
    """Test that path traversal is detected (implementation-level test)."""
    from ouroboros.server.indexes.index_manager import IndexManager
    from pathlib import Path
    
    config = MCPConfig()
    manager = IndexManager(base_path=Path("/tmp/test"), config=config.indexes)
    
    # Attempt: Path traversal
    with pytest.raises(SecurityError):
        manager._validate_source_path("../../etc/")
    
    # Attempt: Absolute path
    with pytest.raises(SecurityError):
        manager._validate_source_path("/etc/passwd")
```

**Security Tests Required:**
- **Type Confusion:** String/int/bool mismatches rejected
- **Resource Exhaustion:** Huge values rejected (chunk_size, batch_size)
- **Path Traversal:** ../ and absolute paths rejected
- **Unknown Fields:** Typos and injections rejected
- **Format Validation:** Regex patterns enforced (version, model)

---

### 8.7 Mocking Strategy

**When to Mock:**
1. **External APIs** - Always mock (HuggingFace model downloads)
2. **File System** - Mock in unit tests, real in integration tests
3. **Time/Dates** - Mock for deterministic tests
4. **Database** - Mock in unit tests, use in-memory DB for integration

**When NOT to Mock:**
- Pydantic validation (always test real validation)
- Config file loading (use temp files)
- Property access (no external dependencies)

**Mock Example:**
```python
# tests/unit/test_standards_index.py

from unittest.mock import Mock, patch
from ouroboros.server.indexes.standards_index import StandardsIndex
from ouroboros.models.config import StandardsIndexConfig

@patch('ouroboros.server.indexes.standards_index.SentenceTransformer')
def test_standards_index_initializes_with_config(mock_transformer):
    """Test StandardsIndex initialization without loading actual model."""
    # Arrange: Mock the expensive model load
    mock_model = Mock()
    mock_transformer.return_value = mock_model
    
    config = StandardsIndexConfig()
    
    # Act
    index = StandardsIndex(cache_path=Path("/tmp/test"), config=config)
    
    # Assert: Model was "loaded" with correct parameters
    mock_transformer.assert_called_once_with("BAAI/bge-small-en-v1.5")
    assert index.embedding_model == "BAAI/bge-small-en-v1.5"
```

---

### 8.8 Test Data Fixtures

**Fixture Pattern:**
```python
# tests/conftest.py

import pytest
from pathlib import Path
from ouroboros.models.config import MCPConfig

@pytest.fixture
def valid_config_dict():
    """Return valid config dictionary."""
    return {
        "version": "1.0",
        "indexes": {
            "standards": {
                "enabled": True,
                "source_paths": ["standards/"],
                "vector": {
                    "model": "BAAI/bge-small-en-v1.5",
                    "chunk_size": 500,
                    "chunk_overlap": 50
                }
            }
        }
    }


@pytest.fixture
def config_file(tmp_path, valid_config_dict):
    """Create temporary config file with valid config."""
    config_path = tmp_path / "config" / "mcp.yaml"
    config_path.parent.mkdir(parents=True)
    
    config = MCPConfig(**valid_config_dict)
    config.to_yaml(config_path)
    
    return config_path


@pytest.fixture
def invalid_config_files(tmp_path):
    """Create various invalid config files for testing error handling."""
    configs = {}
    
    # Invalid YAML syntax
    configs["invalid_yaml"] = tmp_path / "invalid_yaml.yaml"
    with open(configs["invalid_yaml"], 'w') as f:
        f.write("indexes:\n  standards: invalid yaml syntax: [")
    
    # Invalid chunk_size
    configs["invalid_chunk_size"] = tmp_path / "invalid_chunk_size.yaml"
    with open(configs["invalid_chunk_size"], 'w') as f:
        f.write("indexes:\n  standards:\n    vector:\n      chunk_size: 50")
    
    return configs
```

---

### 8.9 Coverage Targets

**Overall Target:** >= 80%  
**Config Module Target:** >= 90% (critical path)

| Module | Target | Rationale |
|--------|--------|-----------|
| `mcp_server/models/config/` | >= 90% | Critical: All validation logic |
| `mcp_server/server/factory.py` | >= 85% | Critical: Server initialization |
| `mcp_server/server/indexes/index_manager.py` | >= 85% | Critical: Index orchestration |
| `mcp_server/server/indexes/*_index.py` | >= 80% | Important: Search functionality |
| Overall | >= 80% | Standard threshold |

**Coverage Commands:**
```bash
# Run tests with coverage
pytest tests/ -v --cov=ouroboros --cov-report=html --cov-report=term

# View coverage report
open htmlcov/index.html

# Fail if coverage < 80%
pytest tests/ --cov=ouroboros --cov-fail-under=80
```

---

### 8.10 Testing Checklist

**Before marking task complete:**
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All performance tests pass (< 100ms load, < 1μs access)
- [ ] All security tests pass (validation enforced)
- [ ] Coverage >= 90% for config code
- [ ] Coverage >= 80% overall
- [ ] No failing tests in CI
- [ ] No linter errors (pylint, ruff)
- [ ] No type errors (mypy --strict)

**Test Quality Checklist:**
- [ ] Tests follow Arrange-Act-Assert pattern
- [ ] Each test has clear, descriptive name
- [ ] Tests are independent (no shared state)
- [ ] Tests are fast (unit tests < 1s total)
- [ ] Edge cases tested (min, max, boundary values)
- [ ] Error cases tested (validation errors)
- [ ] Test fixtures used for common setup
- [ ] Mocks used appropriately (external dependencies only)

---

## 9. Deployment Guidance

### 9.1 Prerequisites
- Python 3.10+ installed
- Git repository access
- Write access to .praxis-os/ directory

### 9.2 Installation Steps
```bash
# 1. Install dependencies
pip install -r mcp_server/requirements.txt

# 2. Create default config (if new install)
python -c "from ouroboros.models.config import MCPConfig; MCPConfig().to_yaml('.praxis-os/config/mcp.yaml')"

# 3. Validate config
python -m mcp_server.models.config validate .praxis-os/config/mcp.yaml

# 4. Run server
python -m mcp_server
```

### 9.3 Migration from Old Config
```bash
# Run migration script
python scripts/migrate_config.py --dry-run  # Check first
python scripts/migrate_config.py  # Actual migration
```

### 9.4 Configuration Updates
1. Edit `.praxis-os/config/mcp.yaml`
2. Validate: Server won't start if invalid
3. Restart server for changes to take effect

---

## 10. Troubleshooting

### Common Issues

**Issue:** Server won't start - "Config file not found"
- **Solution:** Create config with default template or run migration

**Issue:** ValidationError on startup
- **Solution:** Check error message for field path, fix constraint violation

**Issue:** "chunk_overlap must be < chunk_size"
- **Solution:** Ensure chunk_overlap < chunk_size in config

**Issue:** Unknown field rejected
- **Solution:** Check for typos, remove unknown fields

---

**Status:** Implementation Guide COMPLETE  
**Last Updated:** 2025-11-03  
**Phases Completed:** 0 (Supporting Docs) → 1 (Requirements) → 2 (Technical Design) → 3 (Task Breakdown) → 4 (Implementation Guidance)

