# Contributing to Agent OS Enhanced

Thank you for your interest in contributing! This guide will help you add universal standards, language instructions, or MCP server features.

## 🔄 Development Workflow (CRITICAL)

**We dogfood Agent OS - our local installation mirrors consumer experience.**

### The Copy Workflow

**DO NOT use symlinks. Always copy framework source to `.agent-os/`.**

#### Editing Framework Source (universal/)

```bash
# 1. Edit framework source
vim universal/standards/ai-safety/production-code-checklist.md

# 2. Copy to .agent-os/ (like consumers do)
cp -r universal/standards .agent-os/standards/universal

# 3. File watcher auto-rebuilds RAG index
# (triggered by file change in .agent-os/)

# 4. Restart MCP server if you edited server code
# Cursor → Settings → MCP → Restart agent-os-rag

# 5. Test in Cursor
# Query MCP to verify your changes appear

# 6. Commit BOTH source and installed copy
git add universal/standards/ .agent-os/standards/universal/
git commit -m "docs: your change"
```

**Why?** This validates:
- ✅ Copy process works correctly
- ✅ Path resolution is correct
- ✅ Same experience as consumers
- ✅ Installation bugs caught early

#### Editing Project-Specific Files (.agent-os/standards/development/)

```bash
# These are NOT framework source - edit directly
vim .agent-os/standards/development/python-testing.md

# File watcher auto-rebuilds index
# No copy needed
```

### Key Rules

1. **NEVER edit `.agent-os/standards/universal/`** - it's managed by copy
2. **ALWAYS edit `universal/`** - it's the source of truth
3. **ALWAYS copy** after editing framework source
4. **File watcher auto-rebuilds** - don't manually rebuild
5. **Track both** in git - source + installed copy

### What Gets Tracked in Git?

```
✅ Tracked (committed):
- universal/                    # Framework source
- .agent-os/standards/universal/  # Installed copy (example for consumers)
- .agent-os/standards/development/  # Project-specific
- .agent-os/config.json

❌ Not tracked (gitignored):
- .agent-os/venv/               # Python virtualenv
- .agent-os/.cache/             # RAG vector index
```

See `ARCHITECTURE.md` for detailed explanation of dogfooding model.

---

## 🎯 Contribution Areas

### 1. Universal Standards (High Value)
Add timeless CS fundamentals that apply to all languages.

**Examples:**
- Concurrency patterns (race conditions, deadlocks)
- Testing strategies (test pyramid, test doubles)
- Architecture patterns (SOLID, dependency injection)
- Failure handling (graceful degradation, circuit breakers)

### 2. Language Instructions (High Value)
Add instructions for generating language-specific standards.

**Examples:**
- Go concurrency (goroutines, channels, mutexes)
- JavaScript async (promises, async/await, event loop)
- Rust ownership (borrowing, lifetimes, Arc/Mutex)

### 3. MCP Server Features (Medium Value)
Add new sub-agents or enhance RAG capabilities.

**Examples:**
- New sub-agent: API design critic
- Enhanced RAG: Better chunk retrieval
- New workflow: API design validation

---

## 📝 Writing Universal Standards

### Template Structure

```markdown
# [Title] - Universal [Category]

**Timeless pattern applicable to all programming languages and paradigms.**

## What is [Concept]?

[Clear definition]

## Universal Pattern

```
[Pseudo-code or abstract representation]
```

## Why [Concept] Matters

[Explanation with real-world impact]

## [Strategy/Pattern Name] (Universal)

### Strategy 1: [Name]
**Pattern:** [Abstract pattern]

[Universal example]

**Use cases:**
- [Case 1]
- [Case 2]

### Strategy 2: [Name]
...

## Common [Anti-Patterns/Mistakes]

### Anti-Pattern 1: [Name]
❌ [What not to do]
✅ [What to do instead]

## Testing [Concept]

[How to verify this pattern works]

## Language-Specific Implementation

**This document covers universal concepts. For language-specific implementations:**
- See `.agent-os/standards/development/python-[topic].md` (Python)
- See `.agent-os/standards/development/go-[topic].md` (Go)
- Etc.

---

**This is a timeless CS fundamental. The concepts apply universally, implementations vary by language.**
```

### Guidelines

✅ **DO:**
- Use language-agnostic pseudocode
- Focus on concepts, not syntax
- Include real-world examples
- Show universal patterns
- Explain "why" not just "what"
- Reference other universal standards

❌ **DON'T:**
- Use language-specific syntax (Python, Go, etc.)
- Include framework-specific patterns (Django, Flask, etc.)
- Add project-specific examples
- Assume prior knowledge (explain fundamentals)

### Example: Good vs Bad

**❌ BAD (Too Python-specific):**
```markdown
# Race Conditions

Use `threading.Lock()` to prevent race conditions:

```python
import threading
lock = threading.Lock()
with lock:
    x += 1
```
```

**✅ GOOD (Universal):**
```markdown
# Race Conditions - Universal CS Fundamentals

## What is a Race Condition?

A race condition occurs when multiple execution contexts access
shared state concurrently...

## Universal Pattern

```
acquire_lock()
try:
    # Critical section
    modify_shared_state()
finally:
    release_lock()
```

## Language-Specific Implementation
- Python: `threading.Lock`, `with lock:`
- Go: `sync.Mutex`, `mu.Lock()/mu.Unlock()`
- Rust: `Mutex<T>`, `lock.lock().unwrap()`
```

---

## 📚 Writing Language Instructions

### Template Structure

```markdown
# [Language] Language-Specific Standards Generation Instructions

**For the Cursor Agent: When installing Agent OS in a [Language] project, use these instructions...**

## Instructions Overview

You will generate [N] [Language]-specific standard files by:
1. Reading universal standards from `universal/standards/`
2. Analyzing the target [Language] project
3. Applying [Language]-specific context
4. Integrating project-specific patterns

## File 1: `[language]-concurrency.md`

### Source Materials
Read these universal standards:
- `universal/standards/concurrency/race-conditions.md`
- `universal/standards/concurrency/locking-strategies.md`

### [Language]-Specific Context to Add

#### [Language Concurrency Model]
Explain:
- [Language-specific concurrency primitive 1]
- [Language-specific concurrency primitive 2]

#### Mapping Universal to [Language]

| Universal Concept | [Language] Implementation | When to Use |
|-------------------|---------------------------|-------------|
| Mutex | [language primitive] | [use case] |
| Semaphore | [language primitive] | [use case] |

#### Code Examples
[Language-specific examples]

### Project Context Integration
- **If [framework] detected**: Add [framework-specific patterns]
- **If [library] detected**: Add [library-specific patterns]

## Installation Steps You Should Follow

1. **Analyze target [Language] project**
2. **Read universal standards**
3. **Generate [Language]-specific standards**
4. **Create files**
5. **Cross-reference universal standards**

---

**Result:** [Language]-specific standards that reference universal CS fundamentals...
```

### Adding a New Language

1. **Copy python.md as template**
   ```bash
   cp language-instructions/python.md language-instructions/go.md
   ```

2. **Update language-specific sections**
   - Concurrency model (goroutines vs threads)
   - Testing framework (go test vs pytest)
   - Package manager (go mod vs pip)
   - Code quality tools (gofmt vs Black)

3. **Add project detection logic**
   ```
   Go: Check for go.mod
   Rust: Check for Cargo.toml
   JavaScript: Check for package.json
   ```

4. **Test with real project**
   - Create sample project in that language
   - Run installation
   - Verify generated standards make sense

---

## 🔧 MCP Server Development

### Adding a New Sub-Agent

1. **Create file in `mcp_server/sub_agents/`**
   ```python
   # Example: api_design_critic.py
   
   @server.call_tool()
   async def critique_api_design(
       api_spec: str,
       standard: str = "REST"
   ) -> CritiqueReport:
       """
       Sub-agent for API design review.
       
       Analyzes API designs against best practices.
       """
       # Implementation
   ```

2. **Register in agent_os_rag.py**
   ```python
   from sub_agents.api_design_critic import critique_api_design
   
   # Register tool
   server.add_tool(critique_api_design)
   ```

3. **Add tests**
   ```python
   # tests/test_api_design_critic.py
   def test_rest_api_critique():
       result = critique_api_design(sample_api_spec)
       assert result.issues_found > 0
   ```

4. **Update CHANGELOG.md**
   ```markdown
   ## [1.1.0] - 2025-10-06
   ### Added
   - New sub-agent: API Design Critic
   ```

---

## 🧪 Testing Your Contributions

### Universal Standards
1. Read it aloud - does it make sense without language context?
2. Can it apply to Python, Go, Rust, JavaScript?
3. Are examples language-agnostic?

### Language Instructions
1. Test with a real project in that language
2. Does generated content make sense?
3. Are framework detections accurate?

### MCP Server Features
1. Write unit tests
2. Test in sample project
3. Verify no performance regression

---

## 📦 Submitting Your Contribution

1. **Fork the repository**
   ```bash
   git clone github.com/your-org/agent-os-enhanced
   cd agent-os-enhanced
   git checkout -b feature/api-design-patterns
   ```

2. **Make your changes**
   - Follow templates above
   - Add tests if applicable

3. **Test locally**
   - Test universal standards (language-agnostic check)
   - Test language instructions (install in sample project)
   - Test MCP server (run tests)

4. **Submit PR**
   - Clear title: "Add API design universal standard"
   - Description: What, why, how
   - Link to test project if applicable

---

## 💡 Contribution Ideas

### High-Impact, Low-Effort
- [ ] Add universal standard: Circuit Breakers
- [ ] Add universal standard: Retry Strategies
- [ ] Add language instructions: Go
- [ ] Add language instructions: JavaScript

### High-Impact, Medium-Effort
- [ ] Create sub-agent: API Design Critic
- [ ] Create sub-agent: Security Analyzer
- [ ] Add universal standards for: Security patterns

### High-Impact, High-Effort
- [ ] Multi-language project support (Python + Go in same repo)
- [ ] Hot reload optimization (faster index rebuilds)
- [ ] Advanced RAG (better chunk retrieval algorithms)

---

## 📞 Questions?

- **Universal standards questions**: Read existing standards for pattern
- **Language instructions questions**: See python.md as reference
- **MCP server questions**: Check mcp_server/README.md

---

**Thank you for contributing to Agent OS Enhanced!**

Your contributions help developers worldwide build better software with AI assistance.
