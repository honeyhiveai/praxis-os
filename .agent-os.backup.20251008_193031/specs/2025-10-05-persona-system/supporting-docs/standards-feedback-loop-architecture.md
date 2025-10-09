# Standards Feedback Loop Architecture

**Key Insight**: Personas populate standards → Main Cursor agent queries via MCP → Performance improves over time

---

## The Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    STANDARDS FEEDBACK LOOP                       │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  USER            │
│  (Cursor IDE)    │
└────────┬─────────┘
         │
         │ "How should I structure this API?"
         ↓
┌──────────────────────────────────────────────────────────────┐
│  MAIN CURSOR AGENT (Claude)                                   │
│                                                                │
│  1. Receives question                                          │
│  2. Calls: search_standards("API structure patterns")         │
│  3. MCP returns project-specific API standards                │
│  4. Answers using PROJECT patterns (not generic)              │
└────────┬───────────────────────────────────────────────────┬─┘
         │                                                     │
         │ MCP Tool Call                                       │ Response
         ↓                                                     ↑
┌──────────────────────────────────────────────────────────────┐
│  MCP SERVER (Agent OS RAG)                                    │
│                                                                │
│  • search_standards(query) → semantic search                  │
│  • Returns relevant chunks from .agent-os/standards/          │
│  • File watcher monitors standards/ for changes               │
└────────┬───────────────────────────────────────────────────┘
         │
         │ Queries
         ↓
┌──────────────────────────────────────────────────────────────┐
│  LANCEDB (Vector Index)                                       │
│                                                                │
│  Indexed Content:                                              │
│  ├─ Universal standards (static)                              │
│  ├─ Language standards (generated once)                       │
│  └─ PROJECT standards (dynamic, grows over time) ← KEY        │
└────────┬───────────────────────────────────────────────────┘
         │
         │ Built from
         ↓
┌──────────────────────────────────────────────────────────────┐
│  .agent-os/standards/                                         │
│                                                                │
│  architecture/                                                 │
│    ├─ api-conventions.md        ← Created by @architect       │
│    ├─ caching-strategy.md       ← Created by @architect       │
│    └─ service-communication.md  ← Created by @architect       │
│                                                                │
│  data/                                                         │
│    ├─ kafka-patterns.md         ← Created by @data            │
│    └─ airflow-conventions.md    ← Created by @data            │
│                                                                │
│  development/                                                  │
│    ├─ error-handling.md         ← Created by @engineer        │
│    └─ logging-patterns.md       ← Created by @engineer        │
│                                                                │
│  testing/                                                      │
│    └─ test-conventions.md       ← Created by @qa              │
│                                                                │
│  security/                                                     │
│    └─ auth-patterns.md          ← Created by @security        │
│                                                                │
│  operations/                                                   │
│    └─ deployment-process.md     ← Created by @sre             │
└────────┬───────────────────────────────────────────────────┘
         │
         │ Created/updated by
         ↓
┌──────────────────────────────────────────────────────────────┐
│  PERSONAS (Specialized Sub-Agents)                            │
│                                                                │
│  @architect, @engineer, @data, @qa, @security, @sre           │
│                                                                │
│  Role: Populate project-specific standards in their domain    │
└────────┬───────────────────────────────────────────────────┘
         │
         │ Invoked by user
         ↑
┌──────────────────┐
│  USER            │
│  "@architect     │
│   establish API  │
│   conventions"   │
└──────────────────┘
```

---

## The Feedback Loop in Action

### Week 1: Project Start (No Standards)

**User**: "How should I structure my REST API?"

**Main Agent** (no project context):
```
Agent calls: search_standards("REST API structure")
→ Returns: Universal API design principles (generic)
→ Answer: "Use RESTful resources, HTTP verbs, etc" (generic advice)
```

**Result**: Generic advice, no project specifics

---

### Week 1: User Invokes Architect Persona

**User**: "@architect establish API conventions for this project"

**Architect Persona**:
```
"I'll create project-specific API standards:

Analyzing your project:
- Backend: Express + TypeScript
- Frontend: React
- Pattern: Feature-based modules

Creating .agent-os/standards/architecture/api-conventions.md:

# API Conventions

## Endpoint Structure
Base: /api/v1/{feature}/{resource}
Example: /api/v1/users/profile

## Response Format
```json
{
  "data": {...},
  "error": null,
  "metadata": { "timestamp": "...", "requestId": "..." }
}
```

## Error Codes
- 400: Validation error
- 401: Unauthorized
- 403: Forbidden
- 404: Not found
- 500: Internal server error

## Pagination
- Cursor-based for large lists
- Query params: ?cursor={token}&limit=20
- Response includes: nextCursor, hasMore

Standard created at .agent-os/standards/architecture/api-conventions.md"
```

**File Watcher**:
```
Detects: .agent-os/standards/architecture/api-conventions.md created
→ Triggers: RAG index rebuild
→ Chunks file, generates embeddings, stores in LanceDB
→ Status: Now indexed and searchable
```

---

### Week 2: Main Agent Now Project-Aware

**User**: "How should I structure my REST API?"

**Main Agent** (with project context):
```
Agent calls: search_standards("REST API structure")
→ Returns: .agent-os/standards/architecture/api-conventions.md (project-specific!)
→ Answer: "Based on YOUR project standards:
  - Use /api/v1/{feature}/{resource} format
  - Return {data, error, metadata} structure
  - Use cursor-based pagination with ?cursor and ?limit
  - Example: /api/v1/users/profile
  
  This matches your Express + TypeScript setup."
```

**Result**: Project-specific advice, consistent patterns ✅

---

### Week 4: Standards Accumulate (20+ files)

**User**: "How do I add authentication to this API endpoint?"

**Main Agent** (rich project context):
```
Agent calls: search_standards("authentication API")
→ Returns multiple project standards:
  1. api-conventions.md (how to structure endpoint)
  2. auth-patterns.md (JWT tokens, refresh tokens)
  3. error-handling.md (how to return auth errors)
  4. logging-patterns.md (log auth attempts)

→ Answer: "Based on your project's authentication patterns:

1. Endpoint: POST /api/v1/auth/login
2. Use JWT tokens (15min expiry) per security/auth-patterns.md
3. Store in httpOnly cookies per security standard
4. Return errors in { error: { code, message } } format per API conventions
5. Log auth attempts to Sentry per logging-patterns.md

Example implementation:
[code that follows ALL project standards]"
```

**Result**: Highly consistent, project-aware implementation ✅

---

## Key Benefit: Improving Performance Over Time

### Performance Metrics

**Week 1** (no project standards):
- Main agent: Generic advice (70% useful)
- Developer: Must adapt generic patterns
- Consistency: Low (each developer does differently)

**Week 4** (20 project standards):
- Main agent: Project-specific advice (95% useful)
- Developer: Can use advice directly
- Consistency: High (follows project patterns)

**Week 12** (50+ project standards):
- Main agent: Expert in YOUR project
- Developer: Instant, accurate guidance
- Consistency: Very high (AI enforces patterns)

---

## How Personas Feed the Loop

### Each Persona Contributes to Main Agent's Knowledge

#### Example 1: Architect Seeds API Patterns

```
Week 1:
@architect creates: api-conventions.md

Week 2-12:
Main agent uses it for ALL API questions
→ Every API endpoint follows same pattern
→ Consistency across entire codebase
```

#### Example 2: Data Engineer Seeds Kafka Patterns

```
Week 2:
@data creates: kafka-patterns.md
  - Topic naming: {domain}.{entity}.{version}
  - Serialization: Avro with schema registry

Week 3-12:
Main agent uses it for ALL Kafka code
→ Every Kafka producer/consumer follows pattern
→ No topic naming chaos
→ Consistent serialization
```

#### Example 3: Security Engineer Seeds Auth Patterns

```
Week 1:
@security creates: auth-patterns.md
  - JWT tokens (15min expiry)
  - Refresh tokens (7 day expiry)
  - httpOnly cookies
  - Token refresh in interceptor

Week 2-12:
Main agent uses it for ALL auth code
→ Every auth implementation is secure
→ No auth pattern variations
→ Security vulnerabilities caught early
```

---

## The Compounding Effect

### Traditional Approach (No Standards)

```
Week 1: Developer asks "How to structure API?"
→ AI: Generic advice (different each time)

Week 4: Developer asks same question
→ AI: Still generic advice (possibly different from Week 1)

Week 12: Developer asks same question
→ AI: Still generic advice (no learning)

Result: Inconsistent patterns, no improvement
```

### Agent OS Approach (Standards Feedback Loop)

```
Week 1: Developer asks "How to structure API?"
→ AI: Generic advice
→ @architect: Creates api-conventions.md standard
→ Index updated

Week 4: Developer asks same question
→ AI searches standards
→ Finds api-conventions.md (project-specific!)
→ Returns consistent, project-aware answer

Week 12: Developer asks same question
→ AI searches standards
→ Finds api-conventions.md + 50 other standards
→ Returns highly specific answer referencing multiple project patterns

Result: Consistency improves, AI gets smarter, velocity increases
```

**Key Difference**: AI **learns** your project over time

---

## Technical Implementation

### 1. Persona Creates Standard

**Architect Persona Prompt** (excerpt):
```markdown
## STANDARDS POPULATION

When you identify a pattern or convention:

1. Create file: `.agent-os/standards/architecture/{topic}.md`
2. Use standard format (context, pattern, examples, anti-patterns)
3. Inform user: "Standard created and indexed"

Example:
User: "@architect how should services communicate?"
You: "Creating service-communication.md with gRPC for internal, 
      REST for external. Standard now active."
```

---

### 2. File Watcher Detects Change

**MCP Server** (`agent_os_rag.py`):
```python
class AgentOSFileWatcher:
    def on_created(self, event):
        """Triggered when new standard file created"""
        if event.src_path.endswith('.md'):
            logger.info(f"New standard detected: {event.src_path}")
            self.rebuild_index_incremental(event.src_path)
    
    def rebuild_index_incremental(self, file_path):
        """Add new file to index without full rebuild"""
        # Chunk new file
        chunks = chunker.chunk_file(file_path)
        
        # Generate embeddings
        embeddings = embed_model.encode(chunks)
        
        # Add to LanceDB
        table.add(chunks, embeddings)
        
        logger.info(f"Standard indexed: {file_path}")
```

**Result**: New standards are searchable in seconds

---

### 3. Main Agent Queries Standards

**Main Cursor Agent** (automatic behavior):
```python
User question: "How should I structure my API?"

# Cursor agent automatically calls MCP
search_standards("API structure conventions")

# MCP server performs semantic search
→ Query embedding: [0.23, 0.45, ...]
→ Vector search in LanceDB
→ Returns top 3 most relevant chunks

# Chunks returned:
1. .agent-os/standards/architecture/api-conventions.md (relevance: 0.95)
2. .agent-os/standards/security/api-security.md (relevance: 0.87)
3. .agent-os/standards/development/error-handling.md (relevance: 0.82)

# Agent uses chunks to answer
"Based on your project's API conventions (api-conventions.md)..."
```

**Key**: Main agent **automatically** uses project standards via MCP

---

## Why This Works Better Than Context

### Traditional Approach: Pasting Context

```
User: "How should I structure API?"
User: [pastes 50 lines of context about project]
AI: Uses context for this conversation only
Next conversation: Context lost, must paste again
```

**Problems**:
- Repetitive (paste context every time)
- Expensive (context tokens × conversations)
- Incomplete (user might forget to paste)
- Inconsistent (different context each time)

---

### Agent OS Approach: Standards in RAG

```
Week 1: @architect creates api-conventions.md
Week 2: Main agent queries standards automatically
Week 12: Main agent STILL queries same standards
Forever: Standards are the project's memory
```

**Benefits**:
- ✅ No manual context (automatic via MCP)
- ✅ Cheap (RAG retrieval vs full context)
- ✅ Complete (all standards always available)
- ✅ Consistent (same standards every time)
- ✅ Persistent (standards are permanent project memory)

---

## Standards as Project Memory

### Traditional Projects

```
Project knowledge lives in:
- Developer's heads (bus factor)
- Outdated docs (README.md last updated 6 months ago)
- Code comments (scattered, inconsistent)
- Slack history (searchable but unstructured)
```

**Problem**: Knowledge is fragile, inaccessible

---

### Agent OS Projects

```
Project knowledge lives in:
- .agent-os/standards/ (structured, searchable)
- Populated by personas (experts in each domain)
- Indexed by RAG (semantic search)
- Queried by main agent (automatic, always current)
```

**Benefit**: Knowledge is durable, accessible, actionable

---

## Evolution Timeline

### Month 1: Foundation

**Standards**: 10-15 core files
- api-conventions.md (Architect)
- error-handling.md (Engineer)
- kafka-patterns.md (Data Engineer)
- test-conventions.md (QA)
- auth-patterns.md (Security)
- deployment-process.md (SRE)

**Main Agent Performance**: 60% → 80% useful

---

### Month 3: Growth

**Standards**: 30-40 files
- Original 10-15
- + Feature-specific patterns
- + Technology-specific guidelines
- + Architectural Decision Records (ADRs)

**Main Agent Performance**: 80% → 90% useful

---

### Month 6: Maturity

**Standards**: 50-70 files
- Comprehensive coverage
- Refined patterns
- Updated with learnings
- Cross-referencing standards

**Main Agent Performance**: 90% → 95% useful

**Result**: Main agent becomes expert in YOUR project

---

## Real-World Example

### Scenario: New Developer Joins Team

**Traditional Onboarding**:
```
Day 1: Read README, docs (outdated)
Day 3: Ask senior dev questions
Week 1: Still confused about patterns
Week 2: Makes PR with wrong patterns
Week 4: Finally "gets" the project
```

**Agent OS Onboarding**:
```
Day 1: "How do we handle auth?" 
       → AI: "Read auth-patterns.md, uses JWT with refresh tokens..."
       
Day 1: "How do we structure tests?"
       → AI: "Read test-conventions.md, tests in __tests__/..."
       
Day 1: "How do we deploy?"
       → AI: "Read deployment-process.md, uses GitHub Actions..."

Week 1: Developer is productive (follows all patterns)
```

**Time to productivity**: 4 weeks → 1 week

---

## Implementation Checklist

### ✅ Personas Design
- [ ] Add "Standards Population" capability to all persona prompts
- [ ] Define standard directories per persona
- [ ] Create standard file templates
- [ ] Document when to create standards

### ✅ MCP Server
- [x] File watcher monitors `.agent-os/standards/`
- [x] Incremental index updates on file creation
- [x] Semantic search returns project-specific results

### ✅ Main Agent Integration
- [x] Main agent automatically calls `search_standards()`
- [x] No user intervention needed
- [x] Standards retrieved in every relevant query

### ✅ File Structure
- [x] `.agent-os/standards/{domain}/` directories exist
- [ ] Standard template files created
- [ ] README in each domain explaining purpose

---

## Success Metrics

### Quantitative

- **Standards Count**: 10 (Week 1) → 50+ (Month 6)
- **Query Relevance**: 70% → 95% (standards match queries)
- **Main Agent Accuracy**: 70% → 95% (advice follows project patterns)
- **Developer Velocity**: +30% (faster due to consistent patterns)

### Qualitative

- **Consistency**: High (all code follows same patterns)
- **Onboarding**: Fast (new devs productive in days)
- **Knowledge**: Durable (patterns documented, not in heads)
- **AI Performance**: Excellent (project-aware, not generic)

---

## Conclusion

**The Architecture**:
```
Personas → Create Standards → RAG Indexes → Main Agent Queries → Better Performance
    ↑                                                                      ↓
    └──────────────────────────── Feedback Loop ─────────────────────────┘
```

**The Value**:
1. Personas seed project knowledge
2. Standards grow over time
3. Main agent becomes project expert
4. Consistency and velocity improve
5. Onboarding accelerates
6. Knowledge is preserved

**The Result**: AI that gets smarter about YOUR project every day

---

**Status**: ✅ Architecture designed, ready to implement in persona prompts
