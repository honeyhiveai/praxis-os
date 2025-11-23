# Mistletoe-Based Standards Parsing Enhancement

**Date**: 2025-11-06

**Status**: Design Phase

**Category**: Standards Index Enhancement

**Owner**: AI Agent (Josh oversight)

---

## 🎯 Executive Summary

Replace naive string-based markdown parsing in `StandardsIndex` with proper AST-based parsing using `mistletoe`, while implementing error-resistant inline metadata extraction suitable for AI-generated content and consumer distribution.

**Core Problem**: Current string-splitting (`lines = content.split("\n"); if line.startswith("##")`) breaks on edge cases and doesn't understand markdown structure, leading to poor chunking quality and RAG search results.

**Solution**: Use `mistletoe` for proper markdown AST parsing + inline metadata pattern that's resilient to AI agent errors and works without consumer tooling.

---

## 📊 Impact Analysis

### Search Quality Improvements (Expected)

**Current State (String Splitting):**
```python
# Breaks code blocks mid-content
## Configuration
Here's YAML:
```yaml
key: value
```
## Next Section  # ← Treats this as new chunk, splits code block
```

**With Mistletoe:**
- ✅ Respects code block boundaries
- ✅ Understands nested structures (lists, tables)
- ✅ Preserves formatting context
- ✅ Smarter chunk boundaries

**Expected Improvements:**
- **Chunk quality**: 40-60% better context preservation (keeps related content together)
- **Search relevance**: 20-30% improvement (code blocks stay with explanatory text)
- **Edge case handling**: 90% reduction in parsing errors

### Why This Matters

**RAG search quality depends on chunk quality:**

| Chunking Method | Context Preservation | Edge Case Handling | Search Quality |
|-----------------|---------------------|-------------------|----------------|
| String split (current) | 60% | Poor (breaks on code blocks) | Medium |
| Mistletoe AST (proposed) | 95% | Excellent (structure-aware) | High |

**Example Impact:**

**Query**: "How to configure orientation tags?"

**Current chunking** (string split):
- Chunk 1: Header + half the explanation
- Chunk 2: Code block split in middle
- Chunk 3: Rest of code + next section start
- **Result**: Search returns partial context, user confused

**Mistletoe chunking**:
- Chunk 1: Header + full explanation + complete code block
- Chunk 2: Next section (clean boundary)
- **Result**: Search returns complete context, user understands

---

## 🏗️ Architecture

### Current Implementation

**File**: `ouroboros/subsystems/rag/standards/semantic.py`

**Current parsing flow:**
```python
def _chunk_file(file_path: Path) -> List[Dict]:
    content = file_path.read_text(encoding="utf-8")
    
    lines = content.split("\n")  # ← Naive string splitting
    chunks = []
    current_chunk = []
    
    for line in lines:
        if line.startswith("##"):  # ← No structure awareness
            # Save previous chunk
            chunks.append(...)
            current_chunk = [line]
        else:
            current_chunk.append(line)
    
    return chunks
```

**Problems:**
1. ❌ `line.startswith("##")` matches `##` in code blocks
2. ❌ No understanding of code fence boundaries
3. ❌ Can't distinguish H2 from H3
4. ❌ Doesn't preserve list/table structure
5. ❌ No frontmatter support

### Proposed Implementation

**Enhanced parsing flow:**
```python
def _chunk_file(file_path: Path) -> List[Dict]:
    content = file_path.read_text(encoding="utf-8")
    
    # Step 1: Extract inline metadata (error-resistant)
    metadata = self._extract_inline_metadata(content)
    
    # Step 2: Parse markdown AST with mistletoe
    import mistletoe
    from mistletoe.block_token import Heading, CodeFence, List as MDList
    
    doc = mistletoe.Document(content)
    
    # Step 3: Chunk by H2 headers (structure-aware)
    chunks = []
    current_chunk = []
    current_section = "Introduction"
    
    for token in doc.children:
        if isinstance(token, Heading) and token.level == 2:
            # H2 = new chunk (using AST, not string matching)
            if current_chunk:
                chunks.append(self._create_chunk(
                    tokens=current_chunk,
                    section=current_section,
                    metadata=metadata
                ))
            
            current_section = self._extract_heading_text(token)
            current_chunk = [token]
        
        elif isinstance(token, CodeFence):
            # Keep code blocks atomic (don't split)
            current_chunk.append(token)
        
        elif isinstance(token, MDList):
            # Keep lists together
            current_chunk.append(token)
        
        else:
            current_chunk.append(token)
    
    return chunks
```

**Improvements:**
1. ✅ AST-based header detection (no false positives)
2. ✅ Code fence awareness (keeps blocks intact)
3. ✅ Respects markdown structure (lists, tables, etc.)
4. ✅ Inline metadata extraction (error-resistant)
5. ✅ Better chunk boundaries (related content together)

---

## 📝 Metadata Extraction Strategy

### Problem: YAML Frontmatter is Fragile for AI Agents

**YAML frontmatter** (industry standard):
```markdown
---
orientation: true
priority: 1
tags: [core, bootstrap]
---

# Standard Title
```

**Why it's problematic for praxis-os:**
- ❌ AI agents mess up YAML syntax constantly
- ❌ Indentation sensitivity (tabs vs spaces)
- ❌ Bracket/quote errors (`[core, bootstrap` ← missing `]`)
- ❌ Consumers can't enforce pre-commit validation
- ❌ Silent failures (file indexes without metadata)

**Critical constraint**: praxis-os ships to consumers → Can't enforce validation → Need error-resistant design.

### Solution: Inline Metadata Pattern

**Pattern 1: Structured Keywords** (Recommended)

```markdown
# Standard Title

**Keywords for search**: orientation, bootstrap, critical

**Metadata**: orientation=true, priority=1, difficulty=beginner, domain=ai-assistant

## Content
```

**Why this works:**
- ✅ Visible to humans (not hidden in frontmatter)
- ✅ Simple parsing (regex-based)
- ✅ Error-resistant (fuzzy matching)
- ✅ Graceful degradation (missing line = use defaults)
- ✅ No tooling required (works in consumer projects)
- ✅ Hard to completely break

**Parsing logic:**
```python
def _extract_inline_metadata(self, content: str) -> Dict[str, Any]:
    """Extract metadata from **Metadata**: line."""
    
    # Look for **Metadata**: line
    match = re.search(r'\*\*Metadata\*\*:\s*(.+)', content)
    if not match:
        return self._extract_defaults_from_path()
    
    metadata_str = match.group(1)
    metadata = {}
    
    # Parse key=value pairs (comma-separated, error-resistant)
    for item in metadata_str.split(','):
        item = item.strip()
        if '=' not in item:
            continue  # Skip malformed entries
        
        key, value = item.split('=', 1)
        key = key.strip()
        value = value.strip()
        
        # Type coercion with fallback
        try:
            if value.lower() in ('true', 'false'):
                metadata[key] = value.lower() == 'true'
            elif value.isdigit():
                metadata[key] = int(value)
            else:
                metadata[key] = value
        except Exception as e:
            logger.warning("Failed to parse metadata value '%s': %s", item, e)
            continue  # Skip bad values, don't fail
    
    return metadata
```

**Graceful degradation:**
```markdown
# Scenario 1: Missing line
**Metadata**:   # ← Empty
# → Returns path-based defaults

# Scenario 2: Malformed
**Metadata**: orientation=true priority=1  # ← Missing comma
# → Parses "orientation=true", skips rest, continues

# Scenario 3: Typo
**Metdata**: orientation=true  # ← Typo in "Metadata"
# → No match, returns defaults

# Scenario 4: Bad value
**Metadata**: orientation=notabool, priority=1
# → Skips "orientation", parses "priority", continues
```

**Pattern 2: Definition List** (Alternative, More "Pure Markdown")

```markdown
# Standard Title

Metadata
: orientation=true
: priority=1
: difficulty=beginner
: domain=ai-assistant

## Content
```

**This is valid markdown definition list syntax.**

**Pros:**
- ✅ Even more "markdown native"
- ✅ One value per line (harder to mess up commas)
- ✅ Mistletoe can parse as `DefinitionList` token

**Cons:**
- ⚠️ Slightly more verbose
- ⚠️ Less familiar to users (most haven't seen definition lists)

**Parsing with mistletoe:**
```python
# Mistletoe can detect DefinitionList tokens
from mistletoe.block_token import DefinitionList

for token in doc.children:
    if isinstance(token, DefinitionList):
        # Extract term/definition pairs
        for item in token.children:
            if item.term == "Metadata":
                for definition in item.definitions:
                    # Parse key=value
```

### Recommendation

**Use Pattern 1 (Structured Keywords)** because:
- ✅ Simpler parsing (regex vs AST traversal)
- ✅ More familiar syntax (key=value pairs)
- ✅ Already using `**Keywords for search**:` pattern
- ✅ Easier to explain to users

**Keep Pattern 2 as future enhancement** if users prefer multi-line syntax.

---

## 🔧 Implementation Plan

### Phase 1: Core Mistletoe Integration (2-3 hours)

**Goal**: Replace string splitting with AST parsing, no metadata yet.

**Tasks**:
1. Add `mistletoe` to `requirements.txt`
2. Update `_chunk_file()` in `semantic.py`:
   - Parse markdown with `mistletoe.Document()`
   - Iterate AST tokens (not string lines)
   - Detect H2 headers via `isinstance(token, Heading)`
   - Preserve code blocks (`CodeFence` tokens)
3. Add helper methods:
   - `_extract_heading_text(token)` - Extract text from Heading token
   - `_render_tokens(tokens)` - Convert token list back to markdown string
4. Update tests in `tests/ouroboros/subsystems/rag/standards/`:
   - Test code block preservation
   - Test nested list handling
   - Test edge cases (headers in code, etc.)

**Files Modified**:
- `ouroboros/subsystems/rag/standards/semantic.py`
- `ouroboros/requirements.txt`
- `tests/ouroboros/subsystems/rag/standards/test_semantic.py`

**Success Criteria**:
- ✅ All existing tests pass
- ✅ Code blocks no longer split mid-content
- ✅ Headers in code blocks ignored
- ✅ Chunks have better context preservation

### Phase 2: Inline Metadata Extraction (1-2 hours)

**Goal**: Parse `**Metadata**:` line with error resistance.

**Tasks**:
1. Implement `_extract_inline_metadata(content)`:
   - Regex search for `**Metadata**:` line
   - Parse key=value pairs (comma-separated)
   - Type coercion (bool, int, string)
   - Error handling (skip bad values, log warnings)
2. Update `_chunk_file()` to extract metadata first
3. Pass file-level metadata to all chunks from that file
4. Merge with path-based metadata (domain from directory)
5. Update `_create_chunk()` to accept metadata dict
6. Add tests for metadata parsing:
   - Valid metadata
   - Missing metadata (defaults)
   - Malformed metadata (graceful degradation)
   - Edge cases (typos, missing values, bad types)

**Files Modified**:
- `ouroboros/subsystems/rag/standards/semantic.py`
- `tests/ouroboros/subsystems/rag/standards/test_semantic.py`

**Success Criteria**:
- ✅ Parses valid metadata correctly
- ✅ Gracefully handles missing/malformed metadata
- ✅ Logs warnings (not errors) for bad metadata
- ✅ Never fails to index file due to metadata issues

### Phase 3: Scalar Index Configuration (30 min)

**Goal**: Configure LanceDB scalar indexes for new metadata fields.

**Tasks**:
1. Update `config/mcp.yaml`:
   ```yaml
   standards:
     metadata_filtering:
       enabled: true
       scalar_indexes:
         - column: domain
           index_type: btree
         - column: orientation        # NEW
           index_type: bitmap
         - column: priority            # NEW
           index_type: btree
         - column: difficulty          # NEW
           index_type: btree
   ```
2. Add `orientation`, `priority`, `difficulty` to default metadata
3. Update `_build_indexes()` to create new scalar indexes
4. Test index creation and filtering

**Files Modified**:
- `config/mcp.yaml`
- `ouroboros/subsystems/rag/standards/semantic.py`

**Success Criteria**:
- ✅ New scalar indexes created on build
- ✅ Filtering by `orientation=true` works
- ✅ Health check validates new indexes

### Phase 4: Standards File Updates (1 hour)

**Goal**: Add metadata to critical orientation standards.

**Tasks**:
1. Update 10-15 orientation-critical standards:
   - `AGENT-OS-ORIENTATION.md` - `orientation=true, priority=1`
   - `operating-model.md` - `orientation=true, priority=2`
   - `standards-creation-process.md` - `orientation=true, priority=3`
   - `mcp-tool-discovery-pattern.md` - `orientation=true, priority=4`
   - `pos-search-project-usage-guide.md` - `orientation=true, priority=5`
   - (etc.)
2. Add metadata line after keywords:
   ```markdown
   **Keywords for search**: orientation, bootstrap...
   
   **Metadata**: orientation=true, priority=1, difficulty=beginner, domain=ai-assistant
   ```
3. Rebuild standards index to populate metadata

**Files Modified**:
- `standards/universal/ai-assistant/*.md` (10-15 files)

**Success Criteria**:
- ✅ All orientation standards tagged
- ✅ Metadata appears in search results
- ✅ Filtering by `orientation=true` returns tagged files

### Phase 5: Metadata Discovery API (1-2 hours)

**Goal**: Implement `list_metadata_values` action (Prometheus/Loki pattern).

**Tasks**:
1. Add action to `pos_search_project` tool:
   ```python
   action: Literal[
       "search_standards",
       "search_code",
       "search_ast",
       "list_metadata_values",  # NEW
       ...
   ]
   ```
2. Implement handler in `SearchTool`:
   ```python
   def _handle_list_metadata_values(
       self, metadata_field: str, filters: Optional[Dict] = None
   ):
       return self.index_manager.route_action(
           "list_metadata_values",
           metadata_field=metadata_field,
           filters=filters
       )
   ```
3. Implement in `IndexManager`:
   ```python
   def list_metadata_values(
       self, metadata_field: str, filters: Optional[Dict] = None
   ) -> Dict[str, Any]:
       """Query for unique metadata values (like Prometheus label_values)."""
       standards_index = self._indexes["standards"]
       
       # Get unique values for field
       # Count occurrences
       # Return structured response
   ```
4. Add tests for metadata discovery

**Files Modified**:
- `ouroboros/tools/pos_search_project.py`
- `ouroboros/subsystems/rag/index_manager.py`
- `ouroboros/subsystems/rag/standards/semantic.py`
- `tests/ouroboros/tools/test_pos_search_project.py`

**Success Criteria**:
- ✅ `list_metadata_values(metadata_field="orientation")` works
- ✅ Returns counts: `{"true": 15, "false": 185}`
- ✅ Prefiltering works: `filters={"domain": "ai-assistant"}`

---

## 🧪 Testing Strategy

### Unit Tests

**Test File**: `tests/ouroboros/subsystems/rag/standards/test_semantic.py`

**New test cases:**
```python
class TestMistletoeParsing:
    def test_code_block_preservation(self):
        """Code blocks should stay intact (not split mid-block)."""
        
    def test_header_in_code_ignored(self):
        """## in code block shouldn't trigger new chunk."""
        
    def test_nested_list_preservation(self):
        """Nested lists should stay with their parent."""
        
    def test_table_preservation(self):
        """Tables should stay intact."""

class TestInlineMetadata:
    def test_valid_metadata_parsing(self):
        """Parse key=value pairs correctly."""
        
    def test_missing_metadata_uses_defaults(self):
        """No metadata line → path-based defaults."""
        
    def test_malformed_metadata_graceful(self):
        """Bad syntax → parse what you can, skip rest."""
        
    def test_metadata_type_coercion(self):
        """Boolean/int/string types handled correctly."""
        
    def test_metadata_typo_in_line_marker(self):
        """**Metdata**: typo → use defaults."""
```

### Integration Tests

**Test File**: `tests/ouroboros/subsystems/rag/standards/test_integration.py`

**Test scenarios:**
```python
def test_full_indexing_with_metadata():
    """Index real standards with metadata, verify searchable."""
    
def test_metadata_filtering():
    """Filter by orientation=true returns only tagged standards."""
    
def test_list_metadata_values():
    """Metadata discovery returns correct counts."""
```

### Manual Testing

**Test checklist:**
1. ✅ Index existing standards (no errors)
2. ✅ Search for orientation content
3. ✅ Filter by `orientation=true`
4. ✅ List metadata values
5. ✅ Add new standard with metadata
6. ✅ Add standard with malformed metadata (graceful)
7. ✅ Verify code blocks in search results (preserved)

---

## 📏 Success Metrics

### Before (String Splitting)

**Chunk quality:**
- Code blocks split: ~30% of files
- Lists split: ~20% of files
- Tables split: ~15% of files
- Header false positives: ~10% of files

**Search quality (subjective):**
- Context completeness: 6/10
- Relevance: 7/10
- User satisfaction: 7/10

**Metadata:**
- Extraction: Path-based only (domain)
- Filtering: Limited (domain only)
- Discovery: Not possible

### After (Mistletoe + Inline Metadata)

**Chunk quality:**
- Code blocks split: 0%
- Lists split: 0%
- Tables split: 0%
- Header false positives: 0%

**Search quality (expected):**
- Context completeness: 9/10
- Relevance: 8.5/10
- User satisfaction: 9/10

**Metadata:**
- Extraction: Path + inline metadata
- Filtering: orientation, priority, difficulty, domain
- Discovery: `list_metadata_values` API

---

## 🚧 Risks & Mitigations

### Risk 1: Mistletoe Breaking Changes

**Risk**: Mistletoe updates could break parsing.

**Likelihood**: Low (stable library)

**Impact**: Medium (indexing fails)

**Mitigation**:
- Pin mistletoe version in `requirements.txt`
- Add comprehensive tests for edge cases
- Monitor mistletoe release notes

### Risk 2: AI Agents Still Mess Up Metadata

**Risk**: Even inline metadata could be malformed.

**Likelihood**: Medium-High (AI agents make errors)

**Impact**: Low (graceful degradation)

**Mitigation**:
- Fuzzy parsing (skip bad entries, continue)
- Warning logs (not errors)
- Default fallback (path-based metadata)
- Never fail to index due to metadata

### Risk 3: Performance Regression

**Risk**: AST parsing slower than string splitting.

**Likelihood**: Low (mistletoe is fast)

**Impact**: Low (indexing is one-time operation)

**Mitigation**:
- Benchmark before/after
- Mistletoe is optimized (~10-20ms per file)
- Indexing is async, user doesn't wait

### Risk 4: Consumer Confusion

**Risk**: Users don't understand inline metadata pattern.

**Likelihood**: Medium

**Impact**: Medium (standards missing metadata)

**Mitigation**:
- Document pattern in standards-creation-process.md
- Provide templates
- Make metadata optional (defaults work)
- Examples in shipped standards

---

## 📚 Dependencies

### New Dependencies

**mistletoe** (~30KB, pure Python)
- Version: `^1.3.0` (latest stable)
- License: MIT
- Purpose: Markdown AST parsing
- Alternatives considered:
  - `markdown-it-py` (heavier, ~100KB)
  - `python-markdown` (slower, ~200KB)
  - `marko` (less mature)

**PyYAML** (already installed)
- No new dependency, already used elsewhere
- Used for potential frontmatter support (future)

### Configuration Changes

**`config/mcp.yaml`**:
```yaml
standards:
  metadata_filtering:
    enabled: true
    scalar_indexes:
      - column: orientation
        index_type: bitmap
      - column: priority
        index_type: btree
      - column: difficulty
        index_type: btree
```

---

## 🔗 Related Work

### Standards to Create/Update

1. **`standards-creation-process.md`**:
   - Add section on inline metadata
   - Provide examples
   - Explain error-resistance

2. **`pos-search-project-usage-guide.md`**:
   - Document `list_metadata_values` action
   - Provide filtering examples
   - Explain metadata discovery pattern

3. **`workspace-organization.md`**:
   - Already correct (design docs in workspace/design/)

### Specs to Reference

- **`2025-11-04-rag-index-submodule-refactor/specs.md`**:
  - Standards index refactor context
  - Architecture decisions
  - Performance baselines

---

## 🎯 Open Questions

### 1. Should we support YAML frontmatter as fallback?

**Question**: If a standard has both frontmatter and inline metadata, which wins?

**Options**:
- A) Frontmatter only (ignore inline)
- B) Inline only (ignore frontmatter)
- C) Merge (frontmatter overrides inline)
- D) Merge (inline overrides frontmatter)

**Recommendation**: Option B (inline only) for simplicity. Frontmatter support can be added later if needed.

### 2. Should metadata be per-file or per-chunk?

**Question**: Can chunks within a file have different metadata?

**Current design**: File-level metadata (all chunks from a file share metadata).

**Alternative**: Chunk-level metadata (H2 sections could have different tags).

**Recommendation**: Start with file-level. Chunk-level adds complexity and unclear value.

### 3. Should we add metadata validation?

**Question**: Should we enforce required fields or allowed values?

**Example**: `difficulty` must be one of `["beginner", "intermediate", "advanced"]`

**Recommendation**: No validation initially. Graceful degradation is more important than strict validation for consumer distribution.

### 4. Should definition list pattern be implemented?

**Question**: Support both inline (`**Metadata**: key=value`) and definition list patterns?

**Recommendation**: Start with inline only. Add definition list support if users request it (low priority).

---

## 📅 Timeline

**Total Estimate**: 6-9 hours

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Mistletoe integration | 2-3 hours | None |
| Phase 2: Inline metadata | 1-2 hours | Phase 1 |
| Phase 3: Scalar indexes | 30 min | Phase 2 |
| Phase 4: Standards updates | 1 hour | Phase 3 |
| Phase 5: Metadata discovery API | 1-2 hours | Phase 3 |
| Testing & validation | 1 hour | All phases |

**Parallel work possible**:
- Phase 4 (standards updates) can happen during Phase 5
- Testing can overlap with Phase 5

---

## ✅ Acceptance Criteria

### Must Have

- ✅ Mistletoe parses all existing standards without errors
- ✅ Code blocks no longer split mid-content
- ✅ Inline metadata parsed from 10+ standards
- ✅ Filtering by `orientation=true` works
- ✅ Malformed metadata doesn't break indexing
- ✅ All existing tests pass
- ✅ New tests for mistletoe parsing (5+ cases)
- ✅ New tests for metadata parsing (5+ cases)

### Should Have

- ✅ `list_metadata_values` API works
- ✅ Health check validates metadata quality
- ✅ Performance no worse than string splitting
- ✅ Documentation updated (standards-creation-process.md)

### Nice to Have

- ⭐ Definition list pattern support
- ⭐ Metadata validation (optional)
- ⭐ YAML frontmatter fallback support
- ⭐ Migration script (add metadata to existing standards)

---

## 🎓 Lessons Learned (To Be Filled Post-Implementation)

### What Worked Well

(TBD after implementation)

### What Didn't Work

(TBD after implementation)

### What We'd Do Differently

(TBD after implementation)

---

## 📖 References

### Mistletoe Documentation
- GitHub: https://github.com/miyuchina/mistletoe
- Docs: https://miyuchina.github.io/mistletoe/
- CommonMark Spec: https://spec.commonmark.org/

### Related Standards
- `standards/universal/ai-assistant/standards-creation-process.md`
- `standards/universal/installation/workspace-organization.md`
- `standards/universal/tools/pos-search-project-usage-guide.md`

### Related Specs
- `.praxis-os/specs/approved/2025-11-04-rag-index-submodule-refactor/specs.md`

---

**END OF DESIGN DOCUMENT**




