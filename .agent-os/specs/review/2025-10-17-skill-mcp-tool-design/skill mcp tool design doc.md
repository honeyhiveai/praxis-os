# Skill MCP Tool Design

**Date**: 2025-10-17  
**Status**: Design Phase  
**Objective**: Add model-agnostic Skills support to Agent OS Enhanced

---

## Executive Summary

Add a consolidated `skill` MCP tool to Agent OS Enhanced, bringing Anthropic's Skills pattern to any model. Skills complement workflows by providing ad-hoc, deterministic operations while workflows handle complex multi-phase processes. Skills can be discovered, loaded, and executed both independently and from within workflows.

**Key Benefits:**
- Model-agnostic Skills support (not just Claude)
- Complementary to workflows (deterministic ops vs. complex processes)
- Consistent with aos_browser/workflow consolidation pattern
- Context-efficient (progressive disclosure)
- Usable from within workflow phases

---

## Problem Statement

### Current State

**Anthropic Skills:** Claude-specific capability for ad-hoc operations
- Discoverable capabilities (metadata in system prompt)
- Progressive context loading (SKILL.md → additional files)
- Deterministic code execution (bundled scripts)
- **Limitation:** Only works with Claude

**Agent OS Workflows:** Model-agnostic multi-phase processes
- Phase-gated execution with evidence
- Complex project decomposition
- Architectural enforcement
- **Gap:** No lightweight ad-hoc operations

### The Gap

**Missing capability:** Quick, deterministic operations without workflow overhead
- PDF form filling
- Data extraction/transformation
- File format conversions
- API integrations
- Image processing

**Use cases:**
- Standalone: "Extract fields from this PDF"
- Within workflows: Phase 2 → "Use pdf-extraction skill to get form data"

---

## Solution Overview

Add `skill` MCP tool following the consolidated pattern (like aos_browser, workflow).

**Design principles:**
1. **One tool, multiple actions** - Follow aos_browser/workflow pattern
2. **Progressive disclosure** - Load context only as needed
3. **Complementary to workflows** - Different purposes, work together
4. **Model-agnostic** - MCP-based, any LLM can use
5. **Context-efficient** - Deterministic code keeps context lean

---

## Architecture

### Skill Directory Structure

```
.agent-os/skills/
├── pdf-processing/
│   ├── SKILL.md           # Core skill definition
│   ├── forms.md           # Additional context (optional)
│   ├── extract_fields.py  # Deterministic script
│   └── fill_form.py       # Another script
├── web-scraping/
│   ├── SKILL.md
│   └── scrape.py
└── data-transform/
    ├── SKILL.md
    ├── json_to_csv.py
    └── csv_to_json.py
```

### SKILL.md Format (Compatible with Anthropic)

```markdown
---
name: pdf-processing
description: Fill and manipulate PDF forms
version: 1.0.0
author: Agent OS Enhanced
requires: ["pypdf2", "reportlab"]
keywords: ["pdf", "forms", "document"]
---

# PDF Processing Skill

Extract form fields and fill PDF forms programmatically.

## Capabilities

- Extract all form fields from PDF
- Fill form fields with data
- Flatten filled forms
- Merge multiple PDFs

## Scripts

### extract_fields.py
Extracts all form fields from a PDF.

**Usage:**
```bash
python extract_fields.py <input_pdf>
```

**Returns:** JSON with field names and types

### fill_form.py
Fills PDF form with provided data.

**Usage:**
```bash
python fill_form.py <input_pdf> <output_pdf> <data_json>
```

## Additional Resources

For form-specific guidance, see [forms.md](forms.md).

## Examples

### Extract Fields
```bash
python extract_fields.py tax_form.pdf
# Returns: {"fields": [{"name": "full_name", "type": "text"}, ...]}
```

### Fill Form
```bash
python fill_form.py tax_form.pdf filled.pdf '{"full_name": "John Doe"}'
```
```

### Additional Files (Progressive Loading)

```markdown
# forms.md (forms-specific guidance)

## Form Filling Best Practices

1. Always extract fields first
2. Validate data types match
3. Handle missing fields gracefully
4. Flatten forms after filling

## Common Issues

### Issue: Field names don't match
**Solution:** Use fuzzy matching or field mapping

### Issue: Invalid data type
**Solution:** Convert data before filling
```

---

## Consolidated Tool Design

### Single Tool: `skill`

```python
@mcp.tool()
async def skill(
    action: str,
    
    # Discovery params
    category: Optional[str] = None,
    search_query: Optional[str] = None,
    limit: Optional[int] = 10,
    
    # Loading params
    skill_name: Optional[str] = None,
    file_name: Optional[str] = None,  # For loading additional files
    
    # Execution params
    script_name: Optional[str] = None,
    script_args: Optional[List[str]] = None,
    working_dir: Optional[str] = None,
    
    # Management params
    install_path: Optional[str] = None,
    skill_source: Optional[str] = None,  # URL or local path
) -> Dict[str, Any]:
    """
    Consolidated skill management tool.
    
    Handles skill discovery, loading, execution, and management.
    Follows same pattern as workflow and aos_browser for consistency.
    
    Actions:
        Discovery:
            - list: List available skills with metadata
            - get_metadata: Get detailed skill metadata
            - search: Semantic search over skills
        
        Loading:
            - load: Load skill instructions (SKILL.md)
            - load_file: Load additional skill file (progressive)
        
        Execution:
            - execute: Run skill script with args
            - list_scripts: List available scripts in skill
        
        Management:
            - install: Install skill from source
            - uninstall: Remove installed skill
            - validate: Validate skill structure
            - list_requirements: Get skill dependencies
    
    Args:
        action: Operation to perform
        category: Skill category filter (for list, search)
        search_query: Search query (for search)
        limit: Result limit (for search, list)
        skill_name: Skill identifier (for most operations)
        file_name: Additional file to load (for load_file)
        script_name: Script to execute (for execute)
        script_args: Arguments for script (for execute)
        working_dir: Working directory for execution (for execute)
        install_path: Where to install skill (for install)
        skill_source: Source URL/path (for install)
    
    Returns:
        Dictionary with operation-specific results
    
    Examples:
        # Discovery
        skills = skill(action="list", category="pdf")
        metadata = skill(action="get_metadata", skill_name="pdf-processing")
        results = skill(action="search", search_query="extract PDF data")
        
        # Loading (progressive disclosure)
        core = skill(action="load", skill_name="pdf-processing")
        detail = skill(action="load_file", skill_name="pdf-processing", file_name="forms.md")
        
        # Execution
        scripts = skill(action="list_scripts", skill_name="pdf-processing")
        result = skill(
            action="execute",
            skill_name="pdf-processing",
            script_name="extract_fields.py",
            script_args=["tax_form.pdf"]
        )
        
        # Management
        skill(action="install", skill_source="https://github.com/user/skill", install_path="my-skill")
        deps = skill(action="list_requirements", skill_name="pdf-processing")
        skill(action="validate", skill_name="pdf-processing")
        skill(action="uninstall", skill_name="old-skill")
    """
```

---

## Action Specifications

### Discovery Actions

#### list
Lists available skills with metadata.

**Parameters:**
- `category` (optional): Filter by category
- `search_query` (optional): Filter by keyword
- `limit` (optional): Max results

**Returns:**
```json
{
  "skills": [
    {
      "name": "pdf-processing",
      "description": "Fill and manipulate PDF forms",
      "version": "1.0.0",
      "category": "document",
      "keywords": ["pdf", "forms"]
    }
  ],
  "total": 10,
  "categories": ["document", "web", "data"]
}
```

#### get_metadata
Get detailed metadata for specific skill.

**Parameters:**
- `skill_name` (required): Skill identifier

**Returns:**
```json
{
  "name": "pdf-processing",
  "description": "Fill and manipulate PDF forms",
  "version": "1.0.0",
  "author": "Agent OS Enhanced",
  "requires": ["pypdf2", "reportlab"],
  "keywords": ["pdf", "forms", "document"],
  "scripts": [
    {
      "name": "extract_fields.py",
      "description": "Extract form fields",
      "usage": "python extract_fields.py <input_pdf>"
    },
    {
      "name": "fill_form.py",
      "description": "Fill form with data",
      "usage": "python fill_form.py <input_pdf> <output_pdf> <data_json>"
    }
  ],
  "additional_files": ["forms.md"],
  "path": ".agent-os/skills/pdf-processing"
}
```

#### search
Semantic search over skill descriptions and keywords.

**Parameters:**
- `search_query` (required): Search query
- `limit` (optional): Max results

**Returns:**
```json
{
  "results": [
    {
      "name": "pdf-processing",
      "description": "Fill and manipulate PDF forms",
      "relevance_score": 0.89,
      "matched_keywords": ["pdf", "forms"]
    }
  ],
  "total": 3
}
```

### Loading Actions (Progressive Disclosure)

#### load
Load core skill instructions (SKILL.md).

**Parameters:**
- `skill_name` (required): Skill identifier

**Returns:**
```json
{
  "name": "pdf-processing",
  "content": "# PDF Processing Skill\n\nExtract form fields...",
  "has_additional_files": true,
  "additional_files": ["forms.md"],
  "scripts": ["extract_fields.py", "fill_form.py"]
}
```

#### load_file
Load additional skill file (second level of progressive disclosure).

**Parameters:**
- `skill_name` (required): Skill identifier
- `file_name` (required): File to load

**Returns:**
```json
{
  "skill_name": "pdf-processing",
  "file_name": "forms.md",
  "content": "# Form Filling Best Practices\n\n1. Always extract..."
}
```

### Execution Actions

#### execute
Execute skill script with arguments.

**Parameters:**
- `skill_name` (required): Skill identifier
- `script_name` (required): Script to execute
- `script_args` (optional): Script arguments
- `working_dir` (optional): Working directory

**Returns:**
```json
{
  "success": true,
  "stdout": "{\"fields\": [{\"name\": \"full_name\", \"type\": \"text\"}]}",
  "stderr": "",
  "exit_code": 0,
  "execution_time_ms": 145
}
```

#### list_scripts
List available scripts in skill.

**Parameters:**
- `skill_name` (required): Skill identifier

**Returns:**
```json
{
  "skill_name": "pdf-processing",
  "scripts": [
    {
      "name": "extract_fields.py",
      "description": "Extract form fields",
      "usage": "python extract_fields.py <input_pdf>"
    },
    {
      "name": "fill_form.py",
      "description": "Fill form with data",
      "usage": "python fill_form.py <input_pdf> <output_pdf> <data_json>"
    }
  ],
  "total": 2
}
```

### Management Actions

#### install
Install skill from source (URL or local path).

**Parameters:**
- `skill_source` (required): URL or local path
- `install_path` (optional): Installation name

**Returns:**
```json
{
  "success": true,
  "skill_name": "pdf-processing",
  "path": ".agent-os/skills/pdf-processing",
  "dependencies_installed": true
}
```

#### uninstall
Remove installed skill.

**Parameters:**
- `skill_name` (required): Skill identifier

**Returns:**
```json
{
  "success": true,
  "skill_name": "pdf-processing",
  "removed_path": ".agent-os/skills/pdf-processing"
}
```

#### validate
Validate skill structure and requirements.

**Parameters:**
- `skill_name` (required): Skill identifier

**Returns:**
```json
{
  "valid": true,
  "skill_name": "pdf-processing",
  "checks": {
    "has_skill_md": true,
    "has_metadata": true,
    "scripts_exist": true,
    "dependencies_available": true
  },
  "warnings": [],
  "errors": []
}
```

#### list_requirements
Get skill Python dependencies.

**Parameters:**
- `skill_name` (required): Skill identifier

**Returns:**
```json
{
  "skill_name": "pdf-processing",
  "requirements": ["pypdf2>=2.0.0", "reportlab>=3.6.0"],
  "installed": true,
  "missing": []
}
```

---

## Integration with Workflows

### Usage Pattern

Skills can be used from within workflow phases:

```markdown
# Phase 2: Extract Form Data

## Task 1: Get PDF Form Fields

### Instructions

1. Use pdf-processing skill to extract fields
2. Validate field types
3. Create field mapping

### Steps

```bash
# Discover skill
skill(action="get_metadata", skill_name="pdf-processing")

# Execute extraction
result = skill(
    action="execute",
    skill_name="pdf-processing",
    script_name="extract_fields.py",
    script_args=["${TARGET_FILE}"]
)

# Parse results
fields = json.loads(result["stdout"])
```

### Acceptance Criteria

- [ ] All form fields extracted
- [ ] Field types identified
- [ ] Field mapping created
```

### Example Workflow Phase Using Skills

```markdown
# workflow_v1/phases/3/task-2-pdf-processing.md

## Task: Fill Tax Forms

Use the pdf-processing skill to automate form filling.

### Steps

1. **Discover skill capabilities**
   ```python
   metadata = skill(action="get_metadata", skill_name="pdf-processing")
   print(f"Available scripts: {metadata['scripts']}")
   ```

2. **Extract existing fields**
   ```python
   fields = skill(
       action="execute",
       skill_name="pdf-processing",
       script_name="extract_fields.py",
       script_args=["input_tax_form.pdf"]
   )
   ```

3. **Prepare data**
   ```python
   data = {
       "full_name": "John Doe",
       "ssn": "123-45-6789",
       "income": "50000"
   }
   ```

4. **Fill form**
   ```python
   result = skill(
       action="execute",
       skill_name="pdf-processing",
       script_name="fill_form.py",
       script_args=[
           "input_tax_form.pdf",
           "filled_tax_form.pdf",
           json.dumps(data)
       ]
   )
   ```

### Acceptance Criteria

- [ ] Form fields extracted successfully
- [ ] Data validated against field types
- [ ] Form filled without errors
- [ ] Output PDF generated
```

---

## Skills vs. Workflows Comparison

| Aspect | Skills | Workflows |
|--------|--------|-----------|
| **Purpose** | Deterministic operations | Complex processes |
| **Scope** | Single task (ad-hoc) | Multi-phase project |
| **Enforcement** | None (execute anytime) | Phase gating + evidence |
| **Context** | Minimal (progressive) | Comprehensive (phases) |
| **Code** | Primary (deterministic) | Optional (supporting) |
| **Discovery** | By capability | By process type |
| **Usage** | Standalone or in workflows | Always structured |
| **Complexity** | Low (single operation) | High (decomposed tasks) |

### When to Use What

**Use Skills When:**
- Single, deterministic operation
- Immediate result needed
- No multi-step validation
- Context efficiency critical
- Example: "Extract PDF fields", "Convert JSON to CSV"

**Use Workflows When:**
- Multi-phase process
- Phase dependencies exist
- Evidence/validation needed
- Complex project decomposition
- Example: "Create API spec", "Generate test suite"

**Use Skills FROM Workflows When:**
- Workflow phase needs deterministic operation
- Context efficiency important in phase
- Code execution more reliable than LLM generation
- Example: Workflow phase 2 uses pdf-extraction skill

---

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)

**Deliverables:**
- Skill directory structure (`.agent-os/skills/`)
- SKILL.md parser with YAML frontmatter
- Basic skill registry/discovery
- skill tool with core actions:
  - list
  - get_metadata
  - load
  - execute

**Test with:** Create pdf-processing skill, verify discovery and execution

### Phase 2: Progressive Disclosure (Week 2)

**Deliverables:**
- load_file action for additional files
- Caching strategy for loaded content
- list_scripts action
- Semantic search integration

**Test with:** Multi-file skill, verify progressive loading

### Phase 3: Management (Week 3)

**Deliverables:**
- install action (from URL or local)
- uninstall action
- validate action
- list_requirements action
- Dependency management integration

**Test with:** Install skill from GitHub, validate, uninstall

### Phase 4: Workflow Integration (Week 4)

**Deliverables:**
- Example workflows using skills
- Documentation for skill usage in phases
- Best practices guide
- Migration guide for Anthropic Skills

**Test with:** Create workflow that uses multiple skills

---

## File Organization

```
.agent-os/
├── skills/                          # Installed skills
│   ├── pdf-processing/
│   │   ├── SKILL.md
│   │   ├── forms.md
│   │   ├── extract_fields.py
│   │   └── fill_form.py
│   ├── web-scraping/
│   │   ├── SKILL.md
│   │   └── scrape.py
│   └── data-transform/
│       ├── SKILL.md
│       ├── json_to_csv.py
│       └── csv_to_json.py
├── mcp_server/
│   ├── server/
│   │   └── tools/
│   │       ├── skill_tool.py      # NEW: Skill tool implementation
│   │       └── skill_manager.py   # NEW: Skill management logic
│   └── models/
│       └── skill.py                # NEW: Skill data models
└── workflows/                       # Can use skills
    └── spec_creation_v1/
        └── phases/
            └── 2/
                └── task-1.md        # Can call skill tool
```

---

## Tool Count Impact

### Before (Current)
- workflow (1 tool, 18 actions)
- search_standards (1 tool)
- get_server_info (1 tool)
- aos_browser (1 tool, 20+ actions)
- current_date (1 tool)
= **5 tools**

### After (With Skills)
- workflow (1 tool, 18 actions)
- skill (1 tool, 10 actions) ← NEW
- search_standards (1 tool)
- get_server_info (1 tool)
- aos_browser (1 tool, 20+ actions)
- current_date (1 tool)
= **6 tools** (Still optimal!)

**Impact:** 5 → 6 tools (still well within optimal range)

---

## Example Skills to Include

### 1. pdf-processing
- Extract form fields
- Fill forms
- Merge PDFs
- Split PDFs
- Convert PDF to text

### 2. web-scraping
- Extract structured data
- Handle pagination
- Respect robots.txt
- Rate limiting

### 3. data-transform
- JSON ↔ CSV
- JSON ↔ YAML
- XML ↔ JSON
- Data validation

### 4. image-processing
- Resize images
- Format conversion
- EXIF data extraction
- Thumbnail generation

### 5. api-client
- REST API calls
- Authentication handling
- Response parsing
- Error handling

---

## Security Considerations

### Script Execution Safety

**Sandboxing:**
- Execute in isolated environment
- Resource limits (CPU, memory, time)
- Network access controls
- Filesystem restrictions

**Code Review:**
- All included skills code-reviewed
- Community skills require approval
- Script signatures/checksums

**Dependency Management:**
- Pin dependency versions
- Security scanning
- License compliance

### Skill Installation

**Trusted Sources:**
- Official Agent OS Enhanced skills (pre-approved)
- Community skills (requires review)
- Private skills (user responsibility)

**Validation:**
- Structure validation
- Code scanning
- Dependency audit

---

## Migration from Anthropic Skills

### Compatibility

Agent OS Enhanced skills use **compatible format** with Anthropic Skills:
- Same SKILL.md structure
- Same YAML frontmatter
- Same progressive disclosure pattern
- Compatible script execution

### Migration Path

1. **Copy skill directory** to `.agent-os/skills/`
2. **Validate structure**: `skill(action="validate", skill_name="...")`
3. **Install dependencies**: `skill(action="list_requirements", skill_name="...")`
4. **Test execution**: `skill(action="execute", skill_name="...", ...)`

**Anthropic Skill:**
```bash
claude-skills/pdf-processing/
├── SKILL.md
└── extract_fields.py
```

**Agent OS Enhanced Skill:** (Same!)
```bash
.agent-os/skills/pdf-processing/
├── SKILL.md
└── extract_fields.py
```

---

## Documentation Requirements

### User Documentation

1. **Getting Started with Skills**
   - What are skills
   - Skills vs. workflows
   - Installing your first skill

2. **Using Skills**
   - Discovery
   - Loading
   - Execution
   - Error handling

3. **Creating Skills**
   - SKILL.md format
   - Script requirements
   - Testing skills
   - Publishing skills

4. **Skills in Workflows**
   - When to use skills in workflows
   - Best practices
   - Examples

### Developer Documentation

1. **Skill Tool Implementation**
   - Architecture
   - Action handlers
   - Testing

2. **Skill Registry**
   - Discovery mechanism
   - Caching strategy
   - Performance

3. **Script Execution**
   - Sandboxing
   - Resource limits
   - Error handling

---

## Success Metrics

### Adoption
- Number of skills created
- Number of skill executions
- Skills used in workflows

### Performance
- Skill discovery latency (<50ms)
- Script execution overhead (<100ms)
- Context savings (vs. non-skill approach)

### Quality
- Skill validation pass rate
- Script execution success rate
- User satisfaction

---

## Future Enhancements

### Phase 5+: Advanced Features

1. **Skill Marketplace**
   - Browse public skills
   - Rate and review
   - One-click installation

2. **Skill Composition**
   - Chain multiple skills
   - Skill pipelines
   - Conditional execution

3. **Remote Skills**
   - Skills as API services
   - Distributed execution
   - Cloud skill hosting

4. **AI-Generated Skills**
   - Create skills from natural language
   - Automatic script generation
   - Validation and testing

---

## Conclusion

Adding the `skill` MCP tool brings Anthropic's Skills pattern to Agent OS Enhanced in a model-agnostic way. Skills complement workflows perfectly:
- **Skills:** Quick, deterministic operations (context-efficient)
- **Workflows:** Complex, multi-phase processes (enforced quality)

Together, they provide comprehensive coverage:
- Ad-hoc tasks → Skills
- Complex projects → Workflows
- Deterministic ops in phases → Skills in Workflows

The consolidated design (1 tool, 10 actions) maintains optimal tool count while adding powerful new capabilities.

**Next Steps:**
1. Review this design doc
2. Create detailed technical specifications
3. Begin Phase 1 implementation
4. Create example skills for testing
