# How to Configure Project-Specific Orientation Queries

**Standard for configuring project-specific orientation queries that extend base prAxIs OS orientation with custom context.**

**Keywords for search**: project orientation queries, custom orientation configuration, project-specific AI context, orientation metadata inline, mcp.yaml orientation config, project discovery patterns, priority-based query execution, how to add project orientation, extending base orientation, project-specific knowledge loading, orientation query configuration, inline metadata discovery, orientation merge rules, project context loading

**Last Updated:** 2025-11-23

---

## 🚨 Quick Reference (TL;DR)

**Core Principle:** Project orientation extends the 10 mandatory base queries with project-specific knowledge discovery.

**Two Configuration Methods:**
1. **Inline Metadata** - Add `**Metadata**: orientation=true, priority=1, query="..."` to markdown files
2. **mcp.yaml Config** - Define `project.orientation.queries` section

**Three Priority Levels:**
- **Priority 1:** Critical foundational knowledge (architecture, domain model)
- **Priority 2:** Important guiding context (testing patterns, API standards)
- **Priority 3:** Supplemental nice-to-have (deployment, tooling)

**Execution Flow:**
```
1. Base Orientation (10 queries) → Always executes first
2. Project Discovery → Finds inline metadata + mcp.yaml config
3. Merge & Deduplicate → Config overrides inline for same query
4. Sort by Priority → 1 → 2 → 3, definition order preserved within priority
5. Execute Queries → Load project-specific context into AI
```

**Required Metadata Fields:**
- `orientation=true` (enables discovery)
- `priority=1|2|3` (execution order)
- `query="your query string"` (what to search for)

**Optional Fields:**
- `description="..."` (human-readable purpose)
- `category="..."` (logical grouping)
- `depends_on=[...]` (query dependencies)

**Quick Test:**
```python
# Verify your query loads expected content
pos_search_project(content_type="standards", query="your project query")
```

---

## ❓ Questions This Answers

1. "How do I add project-specific orientation to AI agents?"
2. "What are project orientation queries and how do they work?"
3. "How to configure custom AI context for my project?"
4. "What's the difference between inline metadata and mcp.yaml config?"
5. "How do I set orientation query priority levels?"
6. "What happens when same query is in both inline and config?"
7. "How does project orientation discovery work?"
8. "Where should I put orientation metadata in markdown files?"
9. "What priority should I use for architecture queries vs deployment?"
10. "How to load domain-specific knowledge into AI context?"
11. "Can I make AI learn my project patterns automatically?"
12. "What fields are required in orientation metadata?"
13. "How to troubleshoot orientation queries not executing?"
14. "How does mcp.yaml orientation config override inline metadata?"
15. "What's the execution order for priority 1 vs priority 2 queries?"
16. "How to test if my orientation queries work?"
17. "Can I disable project orientation without deleting queries?"
18. "How to handle circular dependencies in orientation queries?"
19. "What's the best practice for number of orientation queries?"
20. "How does project orientation extend the base 10 queries?"

---

## What is Project Orientation?

**Project orientation** extends the 10 mandatory base prAxIs OS orientation queries with **project-specific knowledge discovery**.

**Base orientation** (always executes first):
- Query 1-10: Core prAxIs OS patterns, tools, workflows, operating model

**Project orientation** (executes after base):
- Your project's architecture and design patterns
- Domain-specific concepts and business logic
- Team conventions and coding standards
- Project-specific workflows and processes

### Why Project Orientation?

**Problem:** Base orientation teaches generic prAxIs OS usage, but every project has unique patterns.

**Solution:** Define queries that load YOUR project's specific knowledge into AI context.

**Example:**
```markdown
Base Query: "How does spec_execution_v1 workflow work?"
→ Learns generic workflow patterns

Project Query: "microservices architecture service boundaries communication patterns"
→ Learns YOUR architecture before implementing features
```

**Result:** AI starts with prAxIs OS foundation + your project's specific context.

---

## How Query Discovery Works

### The Interception Hook

When an AI agent executes:

```python
pos_search_project(query="orientation query list")
```

The system **intercepts** this magic query string and returns a merged list of:

1. **Base queries** - From `orientation.base.queries` in config (praxis-os defaults)
2. **Project queries** - From `orientation.project.queries` in config (project-specific)

**This is a special hook** - unlike normal queries that search the standards index, this query reads the configuration and returns a list of queries to execute.

### Configuration Sources

**Base Queries** (`dist/config/mcp.yaml` - distribution template):

```yaml
orientation:
  base:
    queries:
      - query: "stateless AI architecture cease to exist"
        priority: 1
        category: "foundational"
        description: "Core architectural truth"
        filters: {}
```

**Project Queries** (`.praxis-os/config/mcp.yaml` - your project):

```yaml
orientation:
  project:
    queries:
      - query: "dogfooding model self-hosting development"
        priority: 1
        category: "development"
        description: "Learn how this project works"
        filters:
          orientation: true
```

### Execution Flow

```
1. AI executes trigger query: "orientation query list"
   ↓
2. Hook intercepts in pos_search_project._handle_search_standards()
   ↓
3. Hook reads config via index_manager.config
   ↓
4. Returns merged list (base queries + project queries)
   ↓
5. AI receives formatted query list (looks like search results)
   ↓
6. AI executes each query in order:
   - Base queries (priority 1 → 2 → 3)
   - Project queries (priority 1 → 2 → 3)
   ↓
7. Each query returns actual content chunks from standards
   ↓
8. Context loaded: base praxis-os patterns + project-specific knowledge
```

### Response Format

The hook returns results formatted like search results for consistent AI handling:

```python
{
    "status": "success",
    "action": "search_standards",
    "results": [
        {
            "content": "stateless AI architecture cease to exist",  # Query string
            "metadata": {
                "query_number": 1,
                "source": "base",  # or "project"
                "priority": 1,
                "category": "foundational",
                "description": "...",
                "filters": {},
                "type": "orientation_query"
            },
            "file_path": "config:orientation.base",
            "relevance_score": 1.0
        },
        # ... more queries
    ],
    "count": 21,  # Base + project query count
    "metadata": {
        "query": "orientation query list",
        "base_queries": 10,
        "project_queries": 11,
        "total_queries": 21,
        "method": "config_interception"
    }
}
```

### Why This Design?

**Separation of Concerns:**
- Base queries: Defined in distribution template (versioned with praxis-os)
- Project queries: Defined in project config (versioned with your project)

**Transparency:**
- All queries visible in config files
- No hardcoded magic lists
- Easy to add/remove/modify queries

**Flexibility:**
- Projects can add any number of queries
- Base queries can evolve with praxis-os
- Config-driven (no code changes needed)

**Type Safety:**
- Pydantic validates entire structure
- Invalid queries caught at startup
- Fail-fast with actionable errors

---

## How to Add Project Orientation: Two Methods

### Method 1: Inline Metadata in Markdown Files

**Best for:** Co-locating orientation with content, quick additions

**Pattern:**
```markdown
**Metadata**: orientation=true, priority=1, query="your query here"
```

**Example - Architecture Document:**

**File:** `.praxis-os/standards/architecture/system-overview.md`

```markdown
# System Architecture Overview

**Metadata**: orientation=true, priority=1, query="microservices architecture service boundaries event-driven patterns", description="Core system architecture"

Our system uses microservices architecture with event-driven communication...

## Service Boundaries

- **API Gateway**: Routes requests to services
- **Auth Service**: Handles authentication/authorization
- **Data Service**: Database access layer
```

**What happens:**
1. Standards index discovers this file during indexing
2. Extracts orientation metadata: `priority=1`, `query="microservices..."`
3. AI agent executes query during orientation: `pos_search_project(content_type="standards", query="microservices architecture service boundaries event-driven patterns")`
4. Results loaded into AI context before work begins

**Example - Domain Knowledge:**

**File:** `.praxis-os/standards/domain/financial-concepts.md`

```markdown
# Financial Domain Concepts

**Metadata**: orientation=true, priority=2, query="financial domain payment processing compliance regulations", description="Core financial concepts", category="domain"

This project implements payment processing with strict compliance requirements...

## Key Concepts

- All amounts stored as integers (cents) to avoid floating-point errors
- Transactions are idempotent (safe to retry)
- PCI DSS compliance required for card data
```

### Method 2: mcp.yaml Configuration

**Best for:** Centralized management, explicit control, team visibility

**Pattern:**

**File:** `.praxis-os/config/mcp.yaml`

```yaml
version: "1.0"

# ... other config sections ...

project:
  orientation:
    enabled: true
    queries:
      # Priority 1: Critical foundation (execute first)
      - query: "microservices architecture service boundaries communication patterns"
        priority: 1
        description: "Core architecture that everything depends on"
        category: "architecture"
      
      - query: "domain model entities aggregates value objects DDD patterns"
        priority: 1
        description: "Domain-driven design concepts used throughout"
        category: "domain"
      
      # Priority 2: Important context (execute second)
      - query: "REST API design conventions endpoint patterns error handling"
        priority: 2
        description: "API standards for consistency"
        category: "api"
      
      - query: "testing strategy unit integration e2e patterns"
        priority: 2
        description: "How we approach testing"
        category: "testing"
      
      # Priority 3: Supplemental (execute last)
      - query: "deployment process CI/CD pipeline kubernetes"
        priority: 3
        description: "Operational knowledge"
        category: "deployment"
```

**Disabling project orientation:**
```yaml
project:
  orientation:
    enabled: false  # Skips all project queries
```

Or simply omit the `project` section (backward compatible).

---

## How to Choose Priority Levels

**Three priority levels control execution order:**

| Priority | Name | Use When | Executes | Examples |
|----------|------|----------|----------|----------|
| **1** | Critical | Foundation AI MUST know before any work | First | Architecture, domain model, core patterns |
| **2** | High | Important context that guides implementation | Second | Testing standards, API conventions, code organization |
| **3** | Medium | Supplemental nice-to-have context | Third | Deployment process, tooling, historical context |

### Priority 1 - Critical Foundation

**Use for knowledge that's prerequisite for everything else:**

```yaml
queries:
  # Without this, AI might violate service boundaries
  - query: "microservices bounded contexts service ownership"
    priority: 1
  
  # Without this, AI might use wrong domain concepts
  - query: "domain model ubiquitous language aggregate rules"
    priority: 1
```

**Test:** "If AI doesn't know this, they'll make fundamental mistakes."

### Priority 2 - Important Guidance

**Use for patterns that ensure consistency and quality:**

```yaml
queries:
  # Guides but doesn't block implementation
  - query: "API design REST conventions error responses"
    priority: 2
  
  # Important but learnable from code review
  - query: "testing patterns mocking integration tests"
    priority: 2
```

**Test:** "If AI doesn't know this, code will work but need revision."

### Priority 3 - Supplemental Context

**Use for nice-to-have knowledge:**

```yaml
queries:
  # Helpful but rarely needed during implementation
  - query: "deployment pipeline CI/CD kubernetes helm"
    priority: 3
  
  # Operational knowledge not needed for feature work
  - query: "monitoring observability metrics tracing"
    priority: 3
```

**Test:** "If AI doesn't know this, they can ask or look it up later."

### Execution Order

**Queries execute in priority order with definition order preserved within priority:**

```
1. All priority=1 queries (in definition order)
2. All priority=2 queries (in definition order)  
3. All priority=3 queries (in definition order)
```

**Example:**
```yaml
queries:
  - query: "C"
    priority: 2
  - query: "A"
    priority: 1
  - query: "B"
    priority: 1
  - query: "D"
    priority: 2

# Executes as: A → B → C → D
```

---

## How Discovery and Merging Works

### Discovery Process

**Step 1: Base Orientation**
- 10 mandatory queries execute first
- Query 10: "project orientation discovery" teaches AI to look for project queries

**Step 2: Project Discovery**
```
Inline Metadata Discovery:
├── Search standards index for files with orientation=true
├── Extract query, priority, description, category
└── Build list of inline queries

mcp.yaml Config Discovery:
├── Load .praxis-os/config/mcp.yaml
├── Read project.orientation.queries section
└── Build list of config queries
```

**Step 3: Merge & Deduplicate**
```
For each query string:
├── If exists in BOTH inline AND config
│   └── Config takes precedence (explicit > embedded)
├── If exists in ONLY inline
│   └── Add to final list
└── If exists in ONLY config
    └── Add to final list
```

**Step 4: Dependency Resolution**
```
For queries with depends_on field:
├── Ensure dependencies exist
├── Resolve execution order (topological sort)
└── Detect circular dependencies (error if found)
```

**Step 5: Sort by Priority**
```
Sort queries:
├── Primary sort: priority (1 < 2 < 3)
└── Secondary sort: definition order (preserved)
```

**Step 6: Execute**
```
For each query in sorted list:
├── Execute: pos_search_project(content_type="standards", query="...")
├── Load results into AI context
├── Track timing and metrics
└── Continue to next query
```

### Merge Rules Examples

**Example 1: Config Overrides Inline**

**Inline metadata:**
```markdown
**Metadata**: orientation=true, priority=2, query="architecture patterns"
```

**mcp.yaml config:**
```yaml
queries:
  - query: "architecture patterns"
    priority: 1  # Higher priority!
    description: "Critical architecture knowledge"
```

**Result:** Config version wins (priority=1, config description used)

**Why:** Explicit configuration should override embedded metadata.

**Example 2: No Conflict**

**Inline metadata:**
```markdown
**Metadata**: orientation=true, priority=1, query="domain model DDD"
```

**mcp.yaml config:**
```yaml
queries:
  - query: "API design REST conventions"
    priority: 2
```

**Result:** Both queries execute (different query strings, no conflict)

**Example 3: Inline Only**

**Inline metadata:**
```markdown
**Metadata**: orientation=true, priority=1, query="testing patterns"
```

**mcp.yaml:** (No project.orientation section)

**Result:** Inline query executes (backward compatible)

---

## Metadata Field Reference

### Required Fields

| Field | Type | Values | Description | Example |
|-------|------|--------|-------------|---------|
| `orientation` | boolean | `true` | Must be true to enable discovery | `orientation=true` |
| `priority` | integer | 1, 2, or 3 | Execution priority (1=highest) | `priority=1` |
| `query` | string | Any query | Search query to execute | `query="architecture patterns"` |

### Optional Fields

| Field | Type | Values | Description | Example |
|-------|------|--------|-------------|---------|
| `description` | string | Any text | Human-readable purpose | `description="Loads architecture"` |
| `category` | string | Any text | Logical grouping | `category="architecture"` |
| `depends_on` | list | Query strings | Execution dependencies | `depends_on=["other query"]` |

### Metadata Syntax Rules

**1. Single-line format (recommended):**
```markdown
**Metadata**: orientation=true, priority=1, query="architecture patterns"
```

**2. Multi-word values need quotes:**
```markdown
**Metadata**: orientation=true, priority=1, query="multi word query", description="a description"
```

**3. Commas separate fields:**
```markdown
**Metadata**: field1=value1, field2=value2, field3=value3
```

**4. Lists use bracket notation:**
```markdown
**Metadata**: orientation=true, priority=1, query="test", depends_on=["query A", "query B"]
```

**5. Case-sensitive keys:**
```markdown
orientation=true  ✅
Orientation=true  ❌ (wrong case)
ORIENTATION=true  ❌ (wrong case)
```

---

## Example Configurations by Project Type

### Microservices Architecture Project

```yaml
project:
  orientation:
    enabled: true
    queries:
      # Critical: Service boundaries and communication
      - query: "microservices architecture service boundaries communication patterns"
        priority: 1
        category: "architecture"
      
      - query: "event-driven architecture event sourcing CQRS patterns"
        priority: 1
        category: "architecture"
      
      # Important: API and observability
      - query: "API gateway routing authentication authorization service mesh"
        priority: 2
        category: "api"
      
      - query: "distributed tracing logging observability monitoring"
        priority: 2
        category: "monitoring"
      
      # Supplemental: Deployment
      - query: "kubernetes helm deployment CI/CD pipeline"
        priority: 3
        category: "deployment"
```

**Use case:** Large microservices system where service boundaries are critical.

### Domain-Driven Design Project

```yaml
project:
  orientation:
    enabled: true
    queries:
      # Critical: Domain model foundation
      - query: "domain model bounded contexts aggregates entities value objects"
        priority: 1
        category: "domain"
      
      - query: "ubiquitous language domain events domain services repositories"
        priority: 1
        category: "domain"
      
      # Important: Application layer patterns
      - query: "application services use cases commands queries CQRS"
        priority: 2
        category: "application"
      
      - query: "repository pattern unit of work persistence strategies"
        priority: 2
        category: "persistence"
```

**Use case:** DDD project where domain model is the foundation.

### AI/ML Project

```yaml
project:
  orientation:
    enabled: true
    queries:
      # Critical: ML pipeline and data
      - query: "machine learning pipelines training inference deployment"
        priority: 1
        category: "ml"
      
      - query: "data preprocessing feature engineering validation pipelines"
        priority: 1
        category: "data"
      
      # Important: MLOps and evaluation
      - query: "model versioning experiment tracking MLOps best practices"
        priority: 2
        category: "mlops"
      
      - query: "model evaluation metrics performance monitoring drift detection"
        priority: 2
        category: "evaluation"
```

**Use case:** ML project where understanding pipelines is critical.

---

## How to Troubleshoot Orientation Issues

### Issue: Queries Not Executing

**Symptoms:**
- Project queries don't appear to run
- AI lacks expected project context

**Solutions:**

**1. Check enabled flag:**
```yaml
project:
  orientation:
    enabled: true  # Must be true!
```

**2. Verify inline metadata syntax:**
```markdown
<!-- WRONG: Missing priority -->
**Metadata**: orientation=true, query="test"

<!-- WRONG: Missing quotes for multi-word -->
**Metadata**: orientation=true, priority=1, query=multi word query

<!-- CORRECT: All required fields, proper quotes -->
**Metadata**: orientation=true, priority=1, query="multi word query"
```

**3. Check file is indexed:**
- Inline metadata only discovered in indexed markdown files
- Verify file is in `indexes.standards.source_paths` from mcp.yaml:
```yaml
indexes:
  standards:
    source_paths:
      - ".praxis-os/standards/"  # Your file must be here
```

**4. Validate YAML syntax:**
```bash
python -c "import yaml; yaml.safe_load(open('.praxis-os/config/mcp.yaml'))"
```

### Issue: Circular Dependency Error

**Symptoms:**
```
ValueError: Circular dependency detected: query A → query B → query A
```

**Cause:** `depends_on` creates cycle

**Example of circular dependency:**
```yaml
queries:
  - query: "A"
    priority: 1
    depends_on: ["B"]
  - query: "B"
    priority: 1
    depends_on: ["A"]  # ← Circular!
```

**Solution - Remove cycle:**
```yaml
queries:
  - query: "A"
    priority: 1
  - query: "B"
    priority: 1
    depends_on: ["A"]  # Linear dependency
```

### Issue: Query Takes Too Long

**Symptoms:**
- Orientation timeout warnings
- Query exceeds 10-second limit

**Solutions:**

**1. Make query more specific:**
```yaml
# VAGUE (searches everything, slow):
query: "api"

# SPECIFIC (targets content, fast):
query: "REST API design conventions endpoint naming patterns"
```

**2. Split large query:**
```yaml
# Instead of one huge query:
- query: "architecture patterns testing deployment monitoring security"

# Split into focused queries:
- query: "architecture patterns microservices event-driven"
  priority: 1
- query: "testing strategy unit integration e2e"
  priority: 2
- query: "deployment CI/CD kubernetes"
  priority: 3
```

**3. Review indexed content size:**
- Large markdown files (>5000 lines) slow search
- Consider splitting into focused documents

### Issue: Duplicate Query Warning

**Symptoms:**
```
Removed 2 duplicate queries (config took precedence over standards)
```

**This is normal behavior!** Config intentionally overrides inline for same query string.

**To resolve (if unwanted):**
- Remove duplicate from inline metadata, OR
- Remove duplicate from mcp.yaml, OR  
- Change query strings to make them unique

---

## Best Practices for Project Orientation

### 1. Start Small, Expand Gradually

**Begin with 2-3 critical queries:**
```yaml
project:
  orientation:
    enabled: true
    queries:
      - query: "system architecture overview patterns"
        priority: 1
      - query: "testing strategy conventions"
        priority: 2
```

Observe what AI lacks, add queries for those gaps.

### 2. Use Specific, Multi-Keyword Queries

**Bad (vague):**
```yaml
query: "api"  # Too broad, matches everything
```

**Good (specific):**
```yaml
query: "REST API design conventions endpoint naming error handling versioning"
```

Specific queries load targeted content faster and more accurately.

### 3. Prioritize Ruthlessly

**Not everything needs priority=1!**

Reserve priority=1 for truly foundational knowledge. Most queries should be priority=2 or 3.

**Ask:** "Can AI implement features correctly without this knowledge?"
- **No:** Priority 1
- **Maybe, but inconsistently:** Priority 2
- **Yes, they'll learn as needed:** Priority 3

### 4. Document in Both Places When Appropriate

**Inline metadata:** Quick, co-located with content
**mcp.yaml config:** Explicit, centralized, team-visible

Use both! Config can override inline when needed for priority tuning.

### 5. Test Your Queries Manually

**Before adding to orientation, test queries work:**
```python
pos_search_project(content_type="standards", query="your proposed query")
```

**Verify:**
- ✅ Returns expected documents
- ✅ Results are relevant
- ✅ Completes in < 5 seconds
- ✅ Loads useful context

Refine query string based on results.

### 6. Maintain Query Hygiene

**Periodically review orientation queries:**
- Remove obsolete queries (patterns no longer used)
- Update query strings (as content evolves)
- Adjust priorities (based on actual importance)
- Consolidate duplicate/overlapping queries

**Schedule quarterly review:** "Are these queries still loading the right context?"

### 7. Avoid Query Overload

**Recommended query counts:**
- **Small project (<10K LOC):** 3-5 queries
- **Medium project (10K-50K LOC):** 5-10 queries
- **Large project (>50K LOC):** 10-15 queries

**More queries ≠ better orientation.** Focus on high-value, frequently-needed knowledge.

### 8. Use Categories for Organization

**Organize queries by category:**
```yaml
queries:
  # Architecture category
  - query: "microservices architecture"
    category: "architecture"
    priority: 1
  
  # Domain category  
  - query: "domain model DDD"
    category: "domain"
    priority: 1
  
  # Testing category
  - query: "testing patterns"
    category: "testing"
    priority: 2
```

Makes configuration easier to scan and maintain.

---

## 🔗 Related Standards

**Query workflow for project orientation mastery:**

1. **This guide** → `pos_search_project(content_type="standards", query="project orientation guide")`
2. **Base orientation** → `pos_search_project(content_type="standards", query="prAxIs OS orientation 10 bootstrap queries")`
3. **Query construction** → `pos_search_project(content_type="standards", query="query construction patterns semantic search")`
4. **RAG optimization** → `pos_search_project(content_type="standards", query="RAG content authoring optimization")`

**By Category:**

**AI Assistant Orientation:**
- `standards/ai-assistant/PRAXIS-OS-ORIENTATION.md` - Base 10 queries → `pos_search_project(content_type="standards", query="prAxIs OS orientation")`
- `standards/ai-assistant/training-data-versus-project-knowledge.md` - Why orientation matters → `pos_search_project(content_type="standards", query="training data versus project knowledge")`

**Configuration:**
- `standards/operations/mcp-rag-configuration.md` - MCP RAG config → `pos_search_project(content_type="standards", query="MCP RAG configuration")`

**Content Authoring:**
- `standards/ai-assistant/rag-content-authoring.md` - How to write discoverable content → `pos_search_project(content_type="standards", query="RAG content authoring")`

---

## 📊 Validation

**This standard is discoverable from multiple query angles:**

**Tested queries that return this standard:**
- "how to configure project orientation"
- "project-specific AI context loading"
- "add custom orientation queries"
- "inline metadata orientation discovery"
- "mcp.yaml orientation configuration"
- "priority levels project queries"
- "extend base orientation with project knowledge"
- "project discovery patterns AI agents"

**RAG optimization checklist:**
- ✅ Keyword line with specific multi-keyword terms
- ✅ "Questions This Answers" section (20 questions)
- ✅ Query-oriented headers ("How to X" not generic "Configuration")
- ✅ TL;DR with high keyword density
- ✅ Multiple query angles tested
- ✅ Links to related standards
- ✅ Cross-references with query patterns
- ✅ Chunks are semantically complete

---

**Remember: Base orientation provides the foundation. Project orientation adds YOUR project's unique context. Together they give AI agents complete knowledge to implement features correctly the first time.** 🎯

