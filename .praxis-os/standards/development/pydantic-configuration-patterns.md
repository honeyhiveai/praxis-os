# Pydantic Configuration Patterns

**Keywords for search**: Pydantic patterns, Pydantic v2, configuration validation, BaseModel patterns, Field validators, nested models, config loading, fail-fast validation, type-safe config, Pydantic testing, custom validators, config composition, settings management, validation errors, config hierarchies, Pydantic best practices

---

## 🚨 TL;DR - Pydantic Configuration Quick Reference

**Core Principle:** Config should fail-fast at startup with clear, actionable errors. Use Pydantic v2 for type-safe, validated configuration that prevents runtime errors.

**The Pattern:**
```python
class MCPConfig(BaseModel):
    model_config = ConfigDict(
        validate_assignment=True,  # Validate on attribute changes
        extra="forbid",  # Reject unknown fields
        frozen=False  # Allow runtime changes if needed
    )
    
    field: Type = Field(..., description="...", ge=0)  # Constrained field
    
    @field_validator("field")
    @classmethod
    def validate_field(cls, v):
        # Custom validation
        return v
```

**Critical Requirements:**
- ✅ All configs inherit from BaseModel
- ✅ Use Field() for constraints and descriptions
- ✅ Custom validators for complex rules
- ✅ Load and validate at startup (fail-fast)
- ✅ Clear error messages with field paths
- ✅ Test validation with invalid inputs

**Common Anti-Patterns:**
- ❌ Dict access (`config["key"]` instead of `config.key`)
- ❌ Runtime validation (should fail at startup)
- ❌ Vague field descriptions
- ❌ No constraints on numeric fields
- ❌ Accepting extra fields (typos go undetected)

---

## ❓ Questions This Answers

1. "How do I structure Pydantic configuration models?"
2. "What is BaseModel and when should I use it?"
3. "How do I add field constraints?"
4. "How do I write custom validators?"
5. "How do I compose nested configuration models?"
6. "How do I load and validate config from YAML?"
7. "How do I handle validation errors?"
8. "How do I make config fail-fast at startup?"
9. "How do I test Pydantic models?"
10. "What are Field constraints and validators?"
11. "How do I document config fields?"
12. "How do I handle optional vs required fields?"
13. "How do I validate cross-field dependencies?"
14. "How do I provide default values?"
15. "How do I format validation error messages?"

---

## 🎯 Purpose

Define patterns for structuring type-safe, validated configuration using Pydantic v2, ensuring config errors are caught at startup with clear, actionable error messages.

**Key Distinction:** Pydantic vs Plain Dicts
- **Pydantic:** Type-safe, validated, IDE autocomplete, clear errors (this standard)
- **Plain Dicts:** Runtime errors, no validation, dict["key"] access, typos go undetected

**Why This Matters:** Config errors discovered at runtime (during actual use) cause mysterious failures. Pydantic catches errors at startup with clear field paths, making issues immediately obvious and fixable.

---

## ❌ The Problem

**Without Pydantic:**

1. **Runtime Config Errors**
   ```python
   # Typo in config key - no error until used
   db_host = config["datbase_host"]  # Typo!
   # Error: KeyError: 'datbase_host' (during request)
   ```

2. **No Type Safety**
   ```python
   # Config says "5" (string) but code expects 5 (int)
   port = config["port"]
   bind(port)  # Error: bind() expects int, got str
   ```

3. **No Validation**
   ```python
   # Invalid values not caught
   config = {"chunk_size": -100}  # Negative size!
   # Error happens deep in code when chunk_size used
   ```

4. **Vague Errors**
   ```python
   # What field failed? Where in config?
   # ValidationError: Value must be positive
   # (No indication which of 50 fields is the problem)
   ```

---

## ✅ The Standard

### Pattern 1: BaseModel Structure (Foundation)

**Basic Pattern:**
```python
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings
from typing import Literal

class ServiceConfig(BaseModel):
    """Configuration for a service.
    
    Use BaseModel for nested configs that are part of larger config.
    Use BaseSettings for root configs that load from environment/files.
    """
    
    # Configure Pydantic behavior
    model_config = ConfigDict(
        validate_assignment=True,  # Validate when setting attributes
        extra="forbid",  # Reject unknown fields (catch typos)
        frozen=False  # Allow mutation if needed
    )
    
    # Required field with constraints
    host: str = Field(
        ...,  # Required (no default)
        description="Service hostname or IP",
        min_length=1,
        max_length=255
    )
    
    # Optional field with default
    port: int = Field(
        default=8080,
        description="Service port number",
        ge=1,  # >= 1
        le=65535  # <= 65535
    )
    
    # Enum-like field
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging level"
    )
```

**Why This Works:**
- IDE autocomplete (knows all fields)
- Type checking (mypy/pyright catches errors)
- Validation at assignment
- Clear error messages
- Self-documenting (descriptions)

---

### Pattern 2: Field Constraints (Validation)

**Numeric Constraints:**
```python
class IndexConfig(BaseModel):
    chunk_size: int = Field(
        default=200,
        ge=100,  # greater than or equal
        le=1000,  # less than or equal
        description="Chunk size in tokens"
    )
    
    timeout_seconds: float = Field(
        default=30.0,
        gt=0,  # greater than (exclusive)
        description="Request timeout"
    )
    
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts"
    )
```

**String Constraints:**
```python
class AuthConfig(BaseModel):
    api_key: str = Field(
        ...,  # Required
        min_length=32,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]+$",  # Regex
        description="API authentication key"
    )
    
    base_url: AnyHttpUrl = Field(  # Built-in URL validator
        ...,
        description="API base URL"
    )
```

**Collection Constraints:**
```python
class LanguagesConfig(BaseModel):
    enabled: List[str] = Field(
        default=["python", "typescript"],
        min_length=1,  # At least one language
        description="Enabled programming languages"
    )
    
    file_extensions: Dict[str, List[str]] = Field(
        default={"python": [".py"], "typescript": [".ts", ".tsx"]},
        description="File extensions per language"
    )
```

---

### Pattern 3: Custom Validators (Complex Rules)

**Field Validator:**
```python
class PathConfig(BaseModel):
    base_path: Path = Field(..., description="Base directory path")
    
    @field_validator("base_path")
    @classmethod
    def validate_path_exists(cls, v: Path) -> Path:
        """Ensure path exists and is a directory."""
        if not v.exists():
            raise ValueError(f"Path does not exist: {v}")
        if not v.is_dir():
            raise ValueError(f"Path is not a directory: {v}")
        return v
```

**Model Validator (Cross-Field):**
```python
class RangeConfig(BaseModel):
    min_value: int = Field(..., description="Minimum value")
    max_value: int = Field(..., description="Maximum value")
    
    @model_validator(mode="after")
    def validate_range(self) -> "RangeConfig":
        """Ensure min < max."""
        if self.min_value >= self.max_value:
            raise ValueError(
                f"min_value ({self.min_value}) must be < max_value ({self.max_value})"
            )
        return self
```

**Transform Validator:**
```python
class NormalizedConfig(BaseModel):
    name: str = Field(..., description="Service name")
    
    @field_validator("name")
    @classmethod
    def normalize_name(cls, v: str) -> str:
        """Normalize to lowercase, replace spaces."""
        return v.lower().replace(" ", "_")
```

---

### Pattern 4: Nested Models (Composition)

**Hierarchical Config:**
```python
class VectorConfig(BaseModel):
    """Vector index configuration."""
    model: str = Field(default="all-MiniLM-L6-v2")
    dimension: int = Field(default=384, ge=1)
    metric: Literal["cosine", "euclidean"] = "cosine"

class FTSConfig(BaseModel):
    """Full-text search configuration."""
    enabled: bool = Field(default=True)
    language: str = Field(default="english")

class StandardsIndexConfig(BaseModel):
    """Standards index configuration."""
    vector: VectorConfig = Field(default_factory=VectorConfig)
    fts: FTSConfig = Field(default_factory=FTSConfig)
    chunk_size: int = Field(default=200, ge=100, le=1000)

class IndexesConfig(BaseModel):
    """All indexes configuration."""
    standards: StandardsIndexConfig = Field(default_factory=StandardsIndexConfig)
    code: StandardsIndexConfig = Field(default_factory=StandardsIndexConfig)

class MCPConfig(BaseModel):
    """Root configuration."""
    version: str = Field(pattern=r"^\d+\.\d+$")
    indexes: IndexesConfig = Field(default_factory=IndexesConfig)
```

**Why Nested:**
- Clear hierarchy (indexes → standards → vector)
- Reusable components (StandardsIndexConfig used twice)
- Type-safe access (config.indexes.standards.vector.model)
- Validation at each level

---

### Pattern 5: Loading from YAML (Fail-Fast)

**Load Pattern:**
```python
import yaml
from pathlib import Path

class ConfigLoader:
    @staticmethod
    def load_yaml(path: Path) -> MCPConfig:
        """Load and validate config from YAML.
        
        Raises:
            FileNotFoundError: Config file not found
            yaml.YAMLError: Invalid YAML syntax
            ValidationError: Config validation failed
        """
        # Read YAML
        if not path.exists():
            raise FileNotFoundError(f"Config not found: {path}")
        
        with open(path) as f:
            data = yaml.safe_load(f)
        
        # Validate with Pydantic (fail-fast)
        try:
            return MCPConfig(**data)
        except ValidationError as e:
            # Re-raise with file context
            raise ConfigError(
                f"Config validation failed: {path}",
                errors=e.errors()
            ) from e

# Usage
try:
    config = ConfigLoader.load_yaml(Path("config/mcp.yaml"))
except ConfigError as e:
    print(f"❌ {e}")
    print("\n".join(e.format_errors()))
    sys.exit(1)

# If we get here, config is valid and type-safe
print(f"✅ Config loaded: {config.version}")
```

---

### Pattern 6: Error Message Formatting

**Format Validation Errors:**
```python
class ConfigError(Exception):
    def __init__(self, message: str, errors: List[Dict]):
        self.message = message
        self.errors = errors
        super().__init__(message)
    
    def format_errors(self) -> List[str]:
        """Format Pydantic errors for display."""
        formatted = []
        
        for error in self.errors:
            # Build field path
            loc = " → ".join(str(l) for l in error["loc"])
            
            # Format error
            msg = error["msg"]
            
            # Add input value if available
            if "input" in error["ctx"]:
                input_val = error["ctx"]["input"]
                msg += f" (got: {input_val!r})"
            
            formatted.append(f"{loc}: {msg}")
        
        return formatted

# Example output:
"""
❌ Config validation failed: config/mcp.yaml

indexes → standards → vector → chunk_size: must be >= 100 (got: 50)
indexes → code → fts → language: value must be one of ['english', 'spanish', 'french'] (got: 'german')
"""
```

---

### Pattern 7: Testing Pydantic Models

**Test Valid Configs:**
```python
def test_valid_config():
    """Test config with valid values."""
    config = IndexConfig(
        chunk_size=200,
        timeout_seconds=30.0,
        max_retries=3
    )
    
    assert config.chunk_size == 200
    assert config.timeout_seconds == 30.0
    assert config.max_retries == 3


def test_config_defaults():
    """Test config uses defaults."""
    config = IndexConfig()
    
    assert config.chunk_size == 200  # default
    assert config.timeout_seconds == 30.0  # default
```

**Test Invalid Configs:**
```python
def test_chunk_size_too_small():
    """Test chunk_size below minimum."""
    with pytest.raises(ValidationError) as exc_info:
        IndexConfig(chunk_size=50)
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("chunk_size",)
    assert "greater than or equal to 100" in errors[0]["msg"]


def test_negative_timeout():
    """Test negative timeout rejected."""
    with pytest.raises(ValidationError):
        IndexConfig(timeout_seconds=-5.0)


def test_extra_fields_rejected():
    """Test unknown fields rejected."""
    with pytest.raises(ValidationError) as exc_info:
        IndexConfig(chunk_size=200, unknown_field="value")
    
    errors = exc_info.value.errors()
    assert any("extra" in str(e) for e in errors)
```

**Test Custom Validators:**
```python
def test_path_must_exist():
    """Test path validator rejects non-existent paths."""
    with pytest.raises(ValidationError) as exc_info:
        PathConfig(base_path=Path("/fake/path"))
    
    assert "does not exist" in str(exc_info.value)


def test_min_max_validation():
    """Test cross-field validation."""
    # Valid: min < max
    config = RangeConfig(min_value=1, max_value=10)
    assert config.min_value == 1
    
    # Invalid: min >= max
    with pytest.raises(ValidationError) as exc_info:
        RangeConfig(min_value=10, max_value=5)
    
    assert "must be <" in str(exc_info.value)
```

---

## 📋 Checklist

**Design Checklist:**
- [ ] All configs inherit from BaseModel
- [ ] Use Field() for all fields (even without constraints)
- [ ] Descriptions provided for all fields
- [ ] Numeric fields have constraints (ge, le, gt, lt)
- [ ] String fields have constraints (min_length, max_length, pattern)
- [ ] Collections have size constraints (min_length)
- [ ] Use Literal for enum-like fields
- [ ] Custom validators for complex rules
- [ ] Cross-field validation with model_validator
- [ ] Nested models for hierarchy

**Implementation Checklist:**
- [ ] Config loaded at startup (fail-fast)
- [ ] Validation errors formatted with field paths
- [ ] Type-safe access (config.field, not config["field"])
- [ ] IDE autocomplete works (BaseModel)
- [ ] Extra fields rejected (extra="forbid")
- [ ] Defaults provided where appropriate

**Testing Checklist:**
- [ ] Test valid configs
- [ ] Test invalid configs (each constraint)
- [ ] Test defaults applied
- [ ] Test custom validators
- [ ] Test cross-field validation
- [ ] Test error messages helpful

---

## 💡 Examples

See Pattern sections above for comprehensive examples.

---

## ⚠️ Anti-Patterns

### Anti-Pattern 1: Dict Access

❌ **Wrong:**
```python
host = config["host"]  # No type safety, no autocomplete
```

✅ **Correct:**
```python
host = config.host  # Type-safe, autocomplete works
```

---

### Anti-Pattern 2: No Constraints

❌ **Wrong:**
```python
class Config(BaseModel):
    chunk_size: int  # Any int accepted, including negative!
```

✅ **Correct:**
```python
class Config(BaseModel):
    chunk_size: int = Field(ge=100, le=1000, description="Chunk size in tokens")
```

---

### Anti-Pattern 3: Runtime Validation

❌ **Wrong:**
```python
# Load config but don't validate until used
config_data = yaml.safe_load(f)
# ... much later ...
chunk_size = config_data["chunk_size"]  # Error here if invalid
```

✅ **Correct:**
```python
# Validate at startup (fail-fast)
config = MCPConfig(**yaml.safe_load(f))  # Fails immediately if invalid
# ... much later ...
chunk_size = config.chunk_size  # Guaranteed valid
```

---

## 📚 Related Standards

- `pos_search_project(content_type="standards", query="error message design field paths")`
- `pos_search_project(content_type="standards", query="fail-fast validation startup")`
- `pos_search_project(content_type="standards", query="configuration testing patterns")`

---

## 📊 When to Query This Standard

| Scenario | Query | Why |
|----------|-------|-----|
| Creating config | `Pydantic configuration patterns` | Need BaseModel structure |
| Field validation | `Pydantic field constraints` | Need constraint patterns |
| Custom rules | `Pydantic custom validators` | Need validation logic |
| Testing | `testing Pydantic models` | Need test patterns |
| Error handling | `Pydantic error message formatting` | Need error display |

---

**Version:** 1.0.0  
**Created:** 2025-11-04  
**Last Updated:** 2025-11-04  
**Next Review:** After Ouroboros unified config implementation

