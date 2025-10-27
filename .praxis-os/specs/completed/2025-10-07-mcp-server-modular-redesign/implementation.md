# MCP Server Modular Redesign - Implementation Details

**Detailed guidance for implementing this feature.**

---

## 🎯 IMPLEMENTATION OVERVIEW

This document provides detailed guidance for implementing the MCP Server Modular Redesign. Follow phases in order and complete validation gates before proceeding.

**Key Principles:**
1. **No breaking changes** - Existing MCP tools must work identically
2. **Dependency injection** - Components receive dependencies, don't create them
3. **Single responsibility** - Each module <200 lines, clear purpose
4. **Standards compliance** - Follow Agent OS production code checklist

---

## 🔧 SETUP & PREREQUISITES

### Environment Setup
```bash
# Navigate to project
cd /path/to/agent-os-enhanced

# Ensure MCP server venv activated
source .praxis-os/venv/bin/activate

# Install dependencies (if needed)
pip install -r mcp_server/requirements.txt

# Run existing tests to establish baseline
tox -e py38
```

### Dependencies
- **Python**: 3.8+ (existing requirement)
- **FastMCP**: Latest (existing)
- **LanceDB**: Latest (existing)
- **Watchdog**: Latest (existing)
- **No new dependencies required**

### Configuration
Existing `config.json` format still works:
```json
{
  "rag": {
    "standards_path": ".praxis-os/standards",
    "usage_path": ".praxis-os/usage",
    "workflows_path": ".praxis-os/workflows"
  }
}
```

New optional section:
```json
{
  "mcp": {
    "enabled_tool_groups": ["rag", "workflow"],
    "max_tools_warning": 20
  }
}
```

---

## 📂 FILE STRUCTURE

### Before (Current)
```
mcp_server/
├── agent_os_rag.py          # 984 lines - MONOLITHIC
├── models.py                # 411 lines - ALL models
├── rag_engine.py
├── workflow_engine.py
├── state_manager.py
└── ...
```

### After (Target)
```
mcp_server/
├── models/                     # Scalable models
│   ├── __init__.py
│   ├── config.py               # ~50 lines
│   ├── workflow.py             # ~200 lines
│   ├── rag.py                  # ~50 lines
│   └── sub_agents/
│
├── config/                     # Configuration
│   ├── __init__.py
│   ├── loader.py               # ~80 lines
│   └── validator.py            # ~60 lines
│
├── monitoring/                 # File watching
│   ├── __init__.py
│   └── watcher.py              # ~150 lines
│
├── server/                     # Server & tools
│   ├── __init__.py
│   ├── factory.py              # ~200 lines
│   └── tools/
│       ├── __init__.py         # ~80 lines
│       ├── rag_tools.py        # ~50 lines
│       ├── workflow_tools.py   # ~180 lines
│       └── sub_agent_tools/
│
├── core/                       # Existing (minimal changes)
│   ├── rag_engine.py
│   ├── workflow_engine.py
│   ├── state_manager.py
│   └── framework_generator.py
│
└── __main__.py                 # ~50 lines
```

---

## 💻 IMPLEMENTATION PATTERNS

### Pattern 1: Dataclass Configuration

**Use Case:** Defining configuration with clear defaults

**Implementation:**
```python
# models/config.py
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

@dataclass
class RAGConfig:
    """RAG system configuration with validated defaults."""
    
    # Clear defaults at class level
    standards_path: str = ".praxis-os/standards"
    usage_path: str = ".praxis-os/usage"
    workflows_path: str = ".praxis-os/workflows"
    index_path: str = ".praxis-os/.cache/vector_index"
    embedding_provider: str = "local"
    
    def resolve_paths(self, project_root: Path) -> Dict[str, Path]:
        """Resolve relative paths to absolute paths.
        
        :param project_root: Project root directory
        :return: Dictionary of resolved Path objects
        :raises ValueError: If paths are invalid
        """
        return {
            "standards_path": project_root / self.standards_path,
            "usage_path": project_root / self.usage_path,
            "workflows_path": project_root / self.workflows_path,
            "index_path": project_root / self.index_path,
        }

@dataclass
class ServerConfig:
    """Complete MCP server configuration."""
    
    base_path: Path
    rag: RAGConfig
    
    @property
    def project_root(self) -> Path:
        """Project root is parent of .praxis-os/."""
        return self.base_path.parent
    
    @property
    def resolved_paths(self) -> Dict[str, Path]:
        """Get all resolved paths for easy access."""
        return self.rag.resolve_paths(self.project_root)
```

**Best Practices:**
- Use `@dataclass` for automatic `__init__` and `__repr__`
- Define defaults at class level for discoverability
- Add `@property` methods for computed values
- Type hint everything

**Anti-Patterns to Avoid:**
- ❌ Hardcoded paths inside methods
- ❌ Mutable default values (use `field(default_factory=...)`)
- ❌ Missing type hints
- ❌ Complex logic in `__init__` (use separate methods)

---

### Pattern 2: Configuration Loading with Graceful Fallback

**Use Case:** Loading user configuration with safe defaults

**Implementation:**
```python
# config/loader.py
from pathlib import Path
import json
import logging
from ..models.config import RAGConfig, ServerConfig

logger = logging.getLogger(__name__)

class ConfigLoader:
    """Load configuration from config.json with graceful fallback."""
    
    @staticmethod
    def load(base_path: Path) -> ServerConfig:
        """Load server configuration.
        
        :param base_path: Path to .praxis-os/ directory
        :return: Fully configured ServerConfig
        :raises ValueError: If base_path invalid
        """
        if not base_path.exists():
            raise ValueError(f"Base path does not exist: {base_path}")
        
        rag_config = ConfigLoader._load_rag_config(base_path)
        return ServerConfig(base_path=base_path, rag=rag_config)
    
    @staticmethod
    def _load_rag_config(base_path: Path) -> RAGConfig:
        """Load RAG configuration from config.json.
        
        Falls back to defaults if:
        - config.json doesn't exist
        - JSON parse fails
        - rag section missing
        
        :param base_path: Path to .praxis-os/
        :return: RAGConfig with overrides or defaults
        """
        config_path = base_path / "config.json"
        
        if not config_path.exists():
            logger.info(f"No config.json found at {config_path}, using defaults")
            return RAGConfig()
        
        try:
            with open(config_path, encoding="utf-8") as f:
                data = json.load(f)
            
            rag_section = data.get("rag", {})
            
            # Use .get() with class defaults as fallback
            return RAGConfig(
                standards_path=rag_section.get("standards_path", RAGConfig.standards_path),
                usage_path=rag_section.get("usage_path", RAGConfig.usage_path),
                workflows_path=rag_section.get("workflows_path", RAGConfig.workflows_path),
                index_path=rag_section.get("index_path", RAGConfig.index_path),
                embedding_provider=rag_section.get("embedding_provider", RAGConfig.embedding_provider),
            )
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse config.json: {e}. Using defaults.")
            return RAGConfig()
        except Exception as e:
            logger.warning(f"Unexpected error loading config: {e}. Using defaults.")
            return RAGConfig()
```

**Best Practices:**
- Log each fallback scenario
- Use `.get()` with class defaults
- Catch specific exceptions first, then general
- Never crash on missing config

**Anti-Patterns to Avoid:**
- ❌ Bare `except:` without logging
- ❌ Raising exceptions for missing optional config
- ❌ Silently using wrong defaults
- ❌ Not validating loaded config

---

### Pattern 3: Configuration Validation

**Use Case:** Validate configuration before use

**Implementation:**
```python
# config/validator.py
from pathlib import Path
from typing import List
import logging
from ..models.config import ServerConfig

logger = logging.getLogger(__name__)

class ConfigValidator:
    """Validate configuration paths and settings."""
    
    @staticmethod
    def validate(config: ServerConfig) -> List[str]:
        """Validate configuration.
        
        :param config: ServerConfig to validate
        :return: List of error messages (empty if valid)
        """
        errors = []
        paths = config.resolved_paths
        
        # Validate source paths exist
        for name in ["standards_path", "usage_path", "workflows_path"]:
            path = paths[name]
            if not path.exists():
                errors.append(f"❌ {name} does not exist: {path}")
            elif not path.is_dir():
                errors.append(f"❌ {name} is not a directory: {path}")
        
        # Index path created on demand, just check parent
        index_path = paths["index_path"]
        if not index_path.parent.exists():
            errors.append(f"❌ Index parent directory missing: {index_path.parent}")
        
        # Validate embedding provider
        valid_providers = ["local", "openai"]
        if config.rag.embedding_provider not in valid_providers:
            errors.append(
                f"❌ Invalid embedding_provider: {config.rag.embedding_provider}. "
                f"Must be one of: {valid_providers}"
            )
        
        return errors
```

**Best Practices:**
- Return list of errors (don't raise on first error)
- Use descriptive error messages with paths
- Validate early (before creating components)
- Check existence, type, permissions

**Anti-Patterns to Avoid:**
- ❌ Raising exception on first error (validate all)
- ❌ Vague error messages ("Invalid config")
- ❌ Not checking parent directories
- ❌ Validating during normal operation (validate once at startup)

---

### Pattern 4: Dependency Injection with Factory

**Use Case:** Create and wire components without tight coupling

**Implementation:**
```python
# server/factory.py
from pathlib import Path
from typing import Optional
import logging
from fastmcp import FastMCP

from ..models.config import ServerConfig
from ..core.rag_engine import RAGEngine
from ..core.workflow_engine import WorkflowEngine
from ..core.state_manager import StateManager
from ..core.framework_generator import FrameworkGenerator

logger = logging.getLogger(__name__)

class ServerFactory:
    """Factory for creating MCP server with dependency injection."""
    
    def __init__(self, config: ServerConfig):
        """Initialize factory with validated configuration.
        
        :param config: Validated ServerConfig
        """
        self.config = config
        self.paths = config.resolved_paths
    
    def create_server(self) -> FastMCP:
        """Create fully configured MCP server.
        
        :return: FastMCP server ready to run
        :raises ValueError: If component creation fails
        """
        logger.info("🏗️  Creating MCP server with modular architecture")
        
        # Ensure directories exist
        self._ensure_directories()
        
        # Ensure RAG index exists
        self._ensure_index()
        
        # Create core components (dependency injection!)
        rag_engine = self._create_rag_engine()
        state_manager = self._create_state_manager()
        workflow_engine = self._create_workflow_engine(rag_engine, state_manager)
        framework_generator = self._create_framework_generator(rag_engine)
        
        # Start file watchers
        self._start_file_watchers(rag_engine)
        
        # Create and register MCP tools
        mcp = self._create_mcp_server(
            rag_engine=rag_engine,
            workflow_engine=workflow_engine,
            framework_generator=framework_generator
        )
        
        logger.info("✅ MCP server created successfully")
        return mcp
    
    def _create_rag_engine(self) -> RAGEngine:
        """Create RAG engine with configured paths."""
        return RAGEngine(
            index_path=self.paths["index_path"],
            standards_path=self.paths["standards_path"].parent.parent
        )
    
    def _create_state_manager(self) -> StateManager:
        """Create state manager with configured path."""
        return StateManager(base_path=self.config.base_path)
    
    def _create_workflow_engine(
        self,
        rag_engine: RAGEngine,
        state_manager: StateManager
    ) -> WorkflowEngine:
        """Create workflow engine with dependencies."""
        return WorkflowEngine(
            state_manager=state_manager,
            rag_engine=rag_engine,
            workflows_base_path=self.paths["workflows_path"]
        )
    
    # ... other _create_X methods ...
```

**Best Practices:**
- Factory receives configuration, not individual paths
- Each component created in separate method
- Dependencies explicitly passed (no globals)
- Clear creation order (dependencies first)

**Anti-Patterns to Avoid:**
- ❌ Components creating their own dependencies
- ❌ Global state or singletons
- ❌ Circular dependencies
- ❌ Complex logic in __init__ (use create_server)

---

### Pattern 5: Tool Registration with Monitoring

**Use Case:** Register MCP tools with performance monitoring

**Implementation:**
```python
# server/tools/__init__.py
from typing import List, Optional
import logging
from fastmcp import FastMCP

from .rag_tools import register_rag_tools
from .workflow_tools import register_workflow_tools

logger = logging.getLogger(__name__)

def register_all_tools(
    mcp: FastMCP,
    rag_engine: "RAGEngine",
    workflow_engine: "WorkflowEngine",
    framework_generator: "FrameworkGenerator",
    enabled_groups: Optional[List[str]] = None
) -> int:
    """Register MCP tools with selective loading.
    
    Research shows LLM performance degrades by up to 85% with >20 tools.
    This function monitors tool count and enables selective loading.
    
    :param mcp: FastMCP server instance
    :param rag_engine: RAG engine for search tools
    :param workflow_engine: Workflow engine for workflow tools
    :param framework_generator: Generator for create_workflow tool
    :param enabled_groups: Tool groups to enable (None = default groups)
    :return: Total number of registered tools
    """
    if enabled_groups is None:
        enabled_groups = ["rag", "workflow"]  # Default: core tools only
    
    tool_count = 0
    
    if "rag" in enabled_groups:
        count = register_rag_tools(mcp, rag_engine)
        tool_count += count
        logger.info(f"✅ Registered {count} RAG tools")
    
    if "workflow" in enabled_groups:
        count = register_workflow_tools(mcp, workflow_engine, framework_generator)
        tool_count += count
        logger.info(f"✅ Registered {count} workflow tools")
    
    # Future: sub-agent tools
    # if "design_validator" in enabled_groups:
    #     count = register_design_validator_tools(mcp, ...)
    #     tool_count += count
    
    logger.info(f"📊 Total MCP tools registered: {tool_count}")
    
    if tool_count > 20:
        logger.warning(
            f"⚠️  Tool count ({tool_count}) exceeds recommended limit (20). "
            "LLM performance may degrade by up to 85%. "
            "Consider selective loading via enabled_tool_groups config."
        )
    
    return tool_count
```

**Best Practices:**
- Return tool count for monitoring
- Log each group registration
- Warn at research-based threshold (20)
- Provide guidance in warning message

**Anti-Patterns to Avoid:**
- ❌ Hardcoded tool list
- ❌ No monitoring of tool count
- ❌ Silent performance degradation
- ❌ All-or-nothing loading

---

## 🧪 TESTING IMPLEMENTATION

### Unit Test Template

```python
# tests/unit/test_config_loader.py
import pytest
import json
from pathlib import Path
from mcp_server.models.config import RAGConfig, ServerConfig
from mcp_server.config.loader import ConfigLoader

class TestConfigLoader:
    """Unit tests for ConfigLoader."""
    
    def test_load_with_missing_config_uses_defaults(self, tmp_path):
        """Test that missing config.json uses defaults gracefully."""
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        
        # Act
        config = ConfigLoader.load(base_path)
        
        # Assert
        assert config.base_path == base_path
        assert config.rag.standards_path == ".praxis-os/standards"
        assert config.rag.usage_path == ".praxis-os/usage"
    
    def test_load_with_valid_config_overrides_defaults(self, tmp_path):
        """Test that valid config.json overrides defaults."""
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        
        config_data = {
            "rag": {
                "standards_path": "custom/standards",
                "usage_path": "custom/usage"
            }
        }
        
        config_path = base_path / "config.json"
        with open(config_path, "w") as f:
            json.dump(config_data, f)
        
        # Act
        config = ConfigLoader.load(base_path)
        
        # Assert
        assert config.rag.standards_path == "custom/standards"
        assert config.rag.usage_path == "custom/usage"
        # Defaults for missing keys
        assert config.rag.workflows_path == ".praxis-os/workflows"
    
    def test_load_with_invalid_json_uses_defaults(self, tmp_path):
        """Test that invalid JSON falls back to defaults."""
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        
        config_path = base_path / "config.json"
        with open(config_path, "w") as f:
            f.write("{invalid json")
        
        # Act
        config = ConfigLoader.load(base_path)
        
        # Assert
        assert config.rag.standards_path == ".praxis-os/standards"
```

### Integration Test Template

```python
# tests/integration/test_server_creation.py
import pytest
from pathlib import Path
from mcp_server.config.loader import ConfigLoader
from mcp_server.config.validator import ConfigValidator
from mcp_server.server.factory import ServerFactory

@pytest.mark.integration
class TestServerCreation:
    """Integration tests for full server creation."""
    
    def test_create_server_with_default_config(self, tmp_path):
        """Test end-to-end server creation with defaults."""
        # Arrange
        base_path = tmp_path / ".praxis-os"
        base_path.mkdir()
        
        # Create required directories
        (base_path.parent / "universal" / "standards").mkdir(parents=True)
        (base_path.parent / "universal" / "usage").mkdir(parents=True)
        (base_path.parent / "universal" / "workflows").mkdir(parents=True)
        
        config = ConfigLoader.load(base_path)
        errors = ConfigValidator.validate(config)
        
        assert errors == [], f"Config validation failed: {errors}"
        
        # Act
        factory = ServerFactory(config)
        server = factory.create_server()
        
        # Assert
        assert server is not None
        assert server.name == "agent-os-rag"
```

---

## 🔍 CODE REVIEW CHECKLIST

**Before submitting for review, verify:**

### Standards Compliance
- [ ] Queried MCP for production code checklist
- [ ] All files have complete type annotations
- [ ] No bare `except:` clauses
- [ ] Concurrency safety documented
- [ ] Configuration validated at startup
- [ ] Resource lifecycle managed (observers stopped)

### Code Quality
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Code follows project style guide
- [ ] All public APIs have docstrings
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate
- [ ] No duplicated code

### Architecture
- [ ] Dependency injection throughout
- [ ] No hardcoded paths
- [ ] Single responsibility per module
- [ ] Clear module boundaries
- [ ] All files <200 lines

### Testing
- [ ] Test coverage ≥ 90% for new code
- [ ] Unit tests for each module
- [ ] Integration tests for workflows
- [ ] Backward compatibility tested

---

## 📊 VALIDATION CRITERIA

### Functional Validation
- [ ] All 7 existing MCP tools work identically
- [ ] Configuration loading works with missing/invalid/valid config
- [ ] File watcher triggers index rebuild
- [ ] Tool count monitoring logs warnings appropriately

### Non-Functional Validation
- [ ] Server startup time <2 seconds
- [ ] No performance regression
- [ ] Memory usage comparable to current

### Quality Validation
- [ ] Test coverage ≥ 90%
- [ ] No linter errors
- [ ] No type errors (mypy clean)
- [ ] Documentation complete

---

## 🚀 DEPLOYMENT GUIDANCE

### Pre-Deployment Checklist
- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Documentation updated (README, ARCHITECTURE, CONTRIBUTING)
- [ ] CHANGELOG.md updated with version and changes
- [ ] Backward compatibility verified

### Deployment Steps
1. Merge to main branch
2. Tag release (e.g., `v1.4.0-modular-redesign`)
3. Update `.praxis-os/` installation in consuming projects
4. Users restart MCP server (Cursor auto-restarts)

### Post-Deployment Verification
- [ ] MCP server starts successfully
- [ ] All tools discoverable
- [ ] File watcher working
- [ ] No error logs

### Rollback Procedure
1. `git revert <commit-hash>`
2. Push to main
3. Users restart MCP server
4. Verify old functionality restored

---

## 🔧 TROUBLESHOOTING

### Issue 1: ImportError with new modules
**Symptoms:** `ModuleNotFoundError: No module named 'mcp_server.models'`  
**Cause:** Missing `__init__.py` files  
**Solution:** Ensure all new directories have `__init__.py`

### Issue 2: Configuration not loading
**Symptoms:** Still using hardcoded paths  
**Cause:** Old code path still active  
**Solution:** Verify `__main__.py` uses new ConfigLoader

### Issue 3: Tests failing with "Path does not exist"
**Symptoms:** ConfigValidator errors in tests  
**Cause:** Test fixture not creating required directories  
**Solution:** Use `tmp_path` fixture and create directory structure

### Issue 4: Tool count warning not appearing
**Symptoms:** Warning not logged with >20 tools  
**Cause:** Logging level too high  
**Solution:** Check logger configuration, should be INFO or lower

---

## 📚 ADDITIONAL RESOURCES

- [MCP Server Architecture Redesign Document](../../../MCP_SERVER_ARCHITECTURE_REDESIGN.md)
- [MCP Tool Scalability Research](../../../MCP_TOOL_SCALABILITY_SUMMARY.md)
- [Agent OS Production Code Checklist](.praxis-os/standards/development/production-code-checklist.md)
- [Dependency Injection Pattern](.praxis-os/standards/architecture/dependency-injection.md)

---

**Follow this implementation guide to ensure high-quality, maintainable code that follows Agent OS standards.**
