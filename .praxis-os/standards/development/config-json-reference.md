# config.json Configuration Guide

**Guide for configuring prAxIs OS MCP/RAG paths in consuming projects**

---

## 🎯 Purpose

The `config.json` file allows consuming projects to customize directory paths for standards, usage docs, and workflow metadata. This is essential for projects with non-standard directory structures.

---

## 📍 File Location

```
project-root/
└── .praxis-os/
    └── config.json    # Place config here
```

---

## 📋 Schema

### Complete Example

```json
{
  "rag": {
    "standards_path": ".praxis-os-source/standards",
    "usage_path": ".praxis-os-source/usage",
    "workflows_path": ".praxis-os-source/workflows"
  }
}
```

### Field Descriptions

| Field | Type | Required | Description | Default |
|-------|------|----------|-------------|---------|
| `rag.standards_path` | string | No | Path to technical standards | `"universal/standards"` |
| `rag.usage_path` | string | No | Path to usage guides | `"universal/usage"` |
| `rag.workflows_path` | string | No | Path to workflow metadata | `"universal/workflows"` |

**Important:** Paths are resolved **relative to project root** (parent of `.praxis-os/`)

---

## 📂 Common Directory Structures

### Default Structure (No config.json needed)

```
project/
├── .praxis-os/
│   ├── mcp_server/
│   └── .cache/
└── universal/
    ├── standards/
    ├── usage/
    └── workflows/
```

**config.json:** Not needed (uses defaults)

---

### Custom Source Directory

```
project/
├── .praxis-os/
│   ├── mcp_server/
│   ├── .cache/
│   └── config.json          # Configure paths
└── .praxis-os-source/
    ├── standards/
    ├── usage/
    └── workflows/
```

**config.json:**
```json
{
  "rag": {
    "standards_path": ".praxis-os-source/standards",
    "usage_path": ".praxis-os-source/usage",
    "workflows_path": ".praxis-os-source/workflows"
  }
}
```

---

### Split Directories

```
project/
├── .praxis-os/
│   └── config.json
├── docs/
│   └── standards/           # Standards here
├── guides/
│   └── usage/               # Usage here
└── workflows/               # Workflows at root
```

**config.json:**
```json
{
  "rag": {
    "standards_path": "docs/standards",
    "usage_path": "guides/usage",
    "workflows_path": "workflows"
  }
}
```

---

### Partial Configuration

You can specify only the paths you want to customize:

```json
{
  "rag": {
    "workflows_path": ".praxis-os-source/workflows"
  }
}
```

Result:
- `workflows_path`: Uses custom path `.praxis-os-source/workflows`
- `standards_path`: Uses default `universal/standards`
- `usage_path`: Uses default `universal/usage`

---

## 🔧 How It Works

### Path Resolution

1. **MCP server starts** and looks for `.praxis-os/config.json`
2. **If config exists:**
   - Read `rag` section
   - Resolve paths relative to **project root** (parent of `.praxis-os/`)
   - Use defaults for missing fields
3. **If config missing:**
   - Use all default paths

### Example Resolution

Given:
- Project root: `/Users/josh/myproject/`
- Config path: `/Users/josh/myproject/.praxis-os/config.json`

Config:
```json
{
  "rag": {
    "workflows_path": "custom/workflows"
  }
}
```

Resolution:
```python
project_root = Path("/Users/josh/myproject")  # .praxis-os parent

workflows_path = project_root / "custom" / "workflows"
# = /Users/josh/myproject/custom/workflows

standards_path = project_root / "universal" / "standards"  # default
# = /Users/josh/myproject/universal/standards
```

---

## ✅ Verification

### Check Configuration Loading

When MCP server starts, check logs:

```bash
tail -f .praxis-os/.cache/mcp_server.log
```

**With config.json:**
```
INFO - Loaded paths from config.json:
INFO -   Standards: /path/to/project/.praxis-os-source/standards
INFO -   Usage: /path/to/project/.praxis-os-source/usage
INFO -   Workflows: /path/to/project/.praxis-os-source/workflows
```

**Without config.json:**
```
INFO - No config.json found, using default paths
```

### Test Workflow Metadata Loading

```python
# Start workflow and check for rich metadata
session = await start_workflow("test_generation_v3", "file.py")

phase3 = session["workflow_overview"]["phases"][3]

# If loaded correctly from metadata.json:
assert phase3["phase_name"] == "Integration Test Generation"
assert len(phase3["key_deliverables"]) > 0

# If using fallback (wrong path):
assert phase3["phase_name"] == "Phase 3"  # ❌ Generic fallback
```

---

## ⚠️ Common Issues

### Issue 1: Metadata Not Loading

**Symptom:**
```json
{
  "phases": [
    {
      "phase_name": "Phase 3",              // Generic name
      "key_deliverables": [],               // Empty
      "validation_criteria": []             // Empty
    }
  ]
}
```

**Cause:** `workflows_path` pointing to wrong location

**Solution:**
1. Check `config.json` has correct `workflows_path`
2. Verify path relative to project root
3. Check `.praxis-os/.cache/mcp_server.log` for loaded paths
4. Ensure `metadata.json` exists at configured path

### Issue 2: Index Not Building

**Symptom:** Search doesn't return workflow information

**Cause:** Paths not configured before index build

**Solution:**
1. Create `config.json` first
2. Force rebuild: `python .praxis-os/scripts/build_rag_index.py --force`
3. Check logs for "Including workflow metadata from: ..."

### Issue 3: Relative Path Confusion

**Symptom:** Paths don't resolve correctly

**Remember:** Paths are relative to **project root** (parent of `.praxis-os/`), NOT relative to `.praxis-os/`

```json
// ❌ WRONG - relative to .praxis-os/
{
  "rag": {
    "workflows_path": "../workflows"
  }
}

// ✅ CORRECT - relative to project root
{
  "rag": {
    "workflows_path": "workflows"
  }
}
```

---

## 🧪 Testing Your Configuration

### Manual Test

1. **Create config.json:**
   ```bash
   cat > .praxis-os/config.json << 'EOF'
   {
     "rag": {
       "workflows_path": "your-custom-path/workflows"
     }
   }
   EOF
   ```

2. **Create test metadata:**
   ```bash
   mkdir -p your-custom-path/workflows/test_workflow
   cat > your-custom-path/workflows/test_workflow/metadata.json << 'EOF'
   {
     "workflow_type": "test_workflow",
     "version": "1.0.0",
     "description": "Test",
     "total_phases": 1,
     "estimated_duration": "5 minutes",
     "primary_outputs": ["test"],
     "phases": [{
       "phase_number": 0,
       "phase_name": "Test Phase",
       "purpose": "Test",
       "estimated_effort": "5 min",
       "key_deliverables": ["test"],
       "validation_criteria": ["done"]
     }]
   }
   EOF
   ```

3. **Restart MCP server** (Cursor restart or kill process)

4. **Check logs:**
   ```bash
   grep "Loaded paths from config" .praxis-os/.cache/mcp_server.log
   ```

5. **Test loading:**
   ```python
   result = await start_workflow("test_workflow", "file.py")
   assert result["workflow_overview"]["phases"][0]["phase_name"] == "Test Phase"
   ```

---

## 📚 Related Documentation

- [Workflow Metadata Guide](mcp_server/WORKFLOW_METADATA_GUIDE.md) - Creating metadata
- [MCP RAG Configuration](universal/standards/workflows/mcp-rag-configuration.md) - RAG setup
- [Installation Guide](installation-guide.md) - Initial setup

---

## 🔍 Migration Guide

### From Hardcoded Paths to Config

If you have an existing installation with symlinks:

**Before:**
```bash
# Using symlink workaround
cd .praxis-os
mkdir -p universal
ln -s ../.praxis-os-source/workflows universal/workflows
```

**After:**

1. **Remove symlink:**
   ```bash
   rm .praxis-os/universal/workflows
   ```

2. **Create config.json:**
   ```bash
   cat > .praxis-os/config.json << 'EOF'
   {
     "rag": {
       "workflows_path": ".praxis-os-source/workflows"
     }
   }
   EOF
   ```

3. **Force rebuild index:**
   ```bash
   cd .praxis-os
   python scripts/build_rag_index.py --force
   ```

4. **Verify:**
   ```bash
   grep "workflows_path" .praxis-os/.cache/mcp_server.log
   ```

---

## 📊 Version Support

| Feature | Version | Notes |
|---------|---------|-------|
| `config.json` support | 1.2.2+ | Custom path configuration |
| Hardcoded paths only | 1.2.1 and earlier | Required symlinks |
| Backward compatible | All versions | Falls back to defaults |

---

**Remember:** `config.json` is optional. Without it, prAxIs OS uses default paths (`universal/standards`, `universal/usage`, `universal/workflows`).
