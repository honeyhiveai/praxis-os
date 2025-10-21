# Universal Standards Population: Every Persona Contributes

**Key Insight**: All personas should help populate Agent OS standards for the specific project

---

## The Concept

### Current Thinking (Wrong)
```
Universal Standards: Static, pre-written
Language Standards: Generated once at install
Project Standards: None (gap)
```

### New Thinking (Right)
```
Universal Standards: Static CS fundamentals (SOLID, OWASP, etc)
Language Standards: Generated once at install (Python, Go, etc)
Project Standards: Dynamic, populated by personas as project evolves
```

**Key Difference**: Project standards are **living documentation** that grows with the project

---

## Why This Matters

### Problem: Generic AI Advice

**Without project standards**:
```
User: "Review my React component"
AI: "Uses generic React patterns from training data"
→ Each component uses different patterns
→ Inconsistent state management
→ No project-level conventions
```

**With project standards**:
```
User: "Review my React component"
AI: "Reads .agent-os/standards/frontend/react-patterns.md"
→ "Your project uses Zustand for state, not Redux"
→ "Custom hooks should be in src/hooks/ per project convention"
→ "Missing error boundary per project standard"
→ Consistent patterns across all components
```

---

## How Standards Population Works

### Universal Capability Across All Personas

**Every persona can contribute standards** in their domain:

```
┌─────────────────────────────────────────────────────────────┐
│              PERSONA → STANDARDS MAPPING                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Software Architect                                          │
│  └─> .agent-os/standards/architecture/                       │
│      ├─ api-design-patterns.md (REST conventions)            │
│      ├─ service-communication.md (gRPC/HTTP patterns)        │
│      ├─ caching-strategy.md (Redis patterns)                 │
│      └─ error-handling-strategy.md (project-wide approach)   │
│                                                               │
│  Software Engineer                                           │
│  └─> .agent-os/standards/development/                        │
│      ├─ code-organization.md (folder structure)              │
│      ├─ naming-conventions.md (project-specific)             │
│      ├─ error-handling.md (how we handle errors)             │
│      └─ logging-patterns.md (structured logging format)      │
│                                                               │
│  Data Engineer                                               │
│  └─> .agent-os/standards/data/                               │
│      ├─ kafka-patterns.md (topic naming, serialization)      │
│      ├─ airflow-conventions.md (DAG patterns)                │
│      ├─ dbt-standards.md (model structure)                   │
│      └─ data-quality-rules.md (validation patterns)          │
│                                                               │
│  QA Engineer                                                 │
│  └─> .agent-os/standards/testing/                            │
│      ├─ test-organization.md (where tests go)                │
│      ├─ fixture-patterns.md (how to use fixtures)            │
│      ├─ mocking-strategy.md (when to mock, when not)         │
│      └─ test-data-management.md (how to manage test data)    │
│                                                               │
│  Security Engineer                                           │
│  └─> .agent-os/standards/security/                           │
│      ├─ auth-patterns.md (how we do auth in this project)    │
│      ├─ secrets-management.md (Vault/AWS Secrets patterns)   │
│      ├─ api-security.md (rate limiting, CORS config)         │
│      └─ dependency-scanning.md (tools and processes)         │
│                                                               │
│  SRE                                                          │
│  └─> .agent-os/standards/operations/                         │
│      ├─ deployment-process.md (how we deploy)                │
│      ├─ monitoring-setup.md (Prometheus/Grafana patterns)    │
│      ├─ incident-response.md (on-call procedures)            │
│      └─ slo-definitions.md (our SLOs)                        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Standards Population Flow

### Scenario 1: Project Kickoff - Establishing Conventions

**User starts new project with React + TypeScript + Zustand + PostgreSQL**

```
User: "@architect we're building a React app with TypeScript, Zustand for state,
       PostgreSQL database, and Express backend"

AI (Architect):
"I'll establish architecture standards for your stack:

Creating .agent-os/standards/architecture/tech-stack.md:
- Frontend: React 18 + TypeScript + Zustand
- Backend: Express + TypeScript
- Database: PostgreSQL 15
- API: REST (GraphQL considered for future)

Creating .agent-os/standards/architecture/folder-structure.md:
```
frontend/
  src/
    components/    # Shared components
    features/      # Feature modules
    hooks/         # Custom hooks
    stores/        # Zustand stores
    api/           # API client
backend/
  src/
    routes/        # Express routes
    services/      # Business logic
    models/        # Database models
    middleware/    # Express middleware
```

Creating .agent-os/standards/architecture/api-conventions.md:
- REST endpoints: /api/v1/{resource}
- Response format: { data, error, metadata }
- Error codes: Standard HTTP + custom app codes
- Pagination: cursor-based for lists

All future AI assistance will follow these project conventions."
```

---

### Scenario 2: Ongoing Development - Standards Evolution

**Developer encounters pattern decision**

```
User: "@engineer how should I handle API errors in the frontend?"

AI (Engineer):
"Looking for existing standard... not found.

Let me establish a pattern:

Creating .agent-os/standards/development/error-handling.md:

# Frontend Error Handling

## API Errors
```typescript
// Use custom hook for consistent error handling
import { useApiError } from '@/hooks/useApiError';

const { data, error } = useApiQuery('/api/users');
const { showError } = useApiError();

if (error) {
  showError(error); // Centralized error display
  return <ErrorFallback />;
}
```

## Error Display
- Toast notifications for transient errors
- Inline errors for form validation
- Error boundaries for component crashes

## Error Logging
- All errors logged to console in dev
- Errors sent to Sentry in production
- Include request ID for debugging

This standard is now saved. All future error handling will follow this pattern."
```

---

### Scenario 3: Review Triggers Standards Creation

**Persona finds inconsistency, proposes standard**

```
User: "@qa review test coverage"

AI (QA):
"Test Coverage Review:
- Coverage: 78%
- Issues: Tests are inconsistent
  - Some use `describe`, some use `test.describe`
  - Mock locations vary (inline vs __mocks__)
  - Fixture patterns inconsistent

I notice no testing standards exist. Let me create them:

Creating .agent-os/standards/testing/test-conventions.md:

# Testing Conventions

## Structure
- Use `describe` for grouping (Jest/Vitest)
- Use `it` or `test` for individual tests
- One test file per source file: `Button.tsx` → `Button.test.tsx`

## Mocks
- Global mocks: `__mocks__/` directory
- Local mocks: colocated with test
- Use `vi.mock()` or `jest.mock()` at top of file

## Fixtures
- Test data: `tests/fixtures/` directory
- Factory functions: `tests/factories/`
- Naming: `create{Entity}` (e.g., `createUser()`)

## Assertions
- Prefer specific matchers (`toHaveLength` vs `toBe`)
- Use `toEqual` for objects, `toBe` for primitives
- Always include failure messages

Standard created. Please update tests to match these conventions."
```

---

## Benefits of Universal Standards Population

### ✅ **1. Living Documentation**

**Traditional docs** (static, outdated):
```
docs/coding-standards.md
Last updated: 6 months ago
Contains outdated patterns
```

**Agent OS standards** (dynamic, current):
```
.agent-os/standards/development/coding-standards.md
Updated: Today (when pattern established)
Enforced by AI immediately
```

---

### ✅ **2. Consistency Enforcement**

**Without standards**:
```
Developer 1: Uses Redux for state
Developer 2: Uses Context API
Developer 3: Uses Zustand
→ 3 different patterns for same problem
```

**With standards**:
```
.agent-os/standards/frontend/state-management.md:
"This project uses Zustand for global state"

AI blocks inconsistent patterns:
"⚠️ This component uses Redux, but project standard is Zustand"
```

---

### ✅ **3. Onboarding Acceleration**

**New developer**:
```
User: "How do we handle authentication in this project?"

AI: "Reading .agent-os/standards/security/auth-patterns.md...

We use:
- JWT tokens with 15min expiry
- Refresh tokens (7 day expiry)
- Auth stored in httpOnly cookies
- Token refresh in Axios interceptor
- Auth state in Zustand authStore

Example implementation: [code from standard]"
```

**Instant onboarding** - no hunting through code

---

### ✅ **4. Knowledge Capture**

**Architectural decisions preserved**:
```
.agent-os/standards/architecture/decisions/

adr-001-why-graphql-over-rest.md
adr-002-postgres-not-mongo.md
adr-003-zustand-over-redux.md

Each contains:
- Context: Why we made this decision
- Alternatives considered
- Trade-offs
- When to revisit
```

---

### ✅ **5. AI Gets Smarter Over Time**

**Week 1** (little context):
```
AI: "Generic React advice"
```

**Week 4** (20 standards files):
```
AI: "Based on your project's 20 standards:
- Use Zustand (state-management.md)
- Follow folder structure (folder-structure.md)
- Use error boundary pattern (error-handling.md)
- Log to Sentry (logging-patterns.md)
→ Specific, project-aware advice"
```

---

## Implementation in Persona Prompts

### Standard Capability Section (All Personas)

Add to every persona prompt:

```markdown
## STANDARDS POPULATION

You can create project-specific standards in your domain:

**When to create standards:**
- Pattern used 2+ times → standardize it
- Team makes decision → document it
- Inconsistency found → establish convention
- New tech adopted → define patterns

**How to create standards:**
1. Identify need for standard
2. Propose pattern with rationale
3. Create file: `.agent-os/standards/{your-domain}/{topic}.md`
4. Include: context, pattern, examples, anti-patterns
5. Inform user: "Standard created at {path}"

**Standard format:**
```markdown
# {Topic}

## Context
Why this standard exists

## Pattern
The approach we use

## Examples
Good examples

## Anti-Patterns
What to avoid

## When to Revisit
Conditions for reconsidering this standard
```

**Your standard directories:**
- [Persona-specific paths listed here]
```

---

## Example: Architect Standards Population

### Persona Prompt Addition

```markdown
## STANDARDS POPULATION CAPABILITY

As Software Architect, you can create standards in:

**Architecture Standards** (`.agent-os/standards/architecture/`):
- System design patterns
- API conventions (REST/GraphQL/gRPC)
- Service communication patterns
- Caching strategies
- Error handling approaches
- Data flow patterns
- Technology selection rationale

**When to create standards:**
- Choosing technology stack → document selection rationale
- Designing API → establish conventions
- Defining service boundaries → document patterns
- Making architecture decision → create ADR
- Spotting inconsistency → standardize approach

**Example workflow:**
```
User asks: "How should services communicate?"

You review code, find no standard.
You propose: gRPC for internal, REST for external
You create: .agent-os/standards/architecture/service-communication.md
You inform: "Standard created - all services will follow this pattern"
```
```

---

## Standards Directory Structure (Full)

```
.agent-os/
  standards/
    # Universal (from skeleton, static)
    ai-safety/
      credential-file-protection.md
      git-safety-rules.md
      ...
    
    # Language-specific (generated at install, static)
    development/
      python-testing.md
      python-concurrency.md
      ...
    
    # Project-specific (populated by personas, dynamic)
    architecture/        ← Architect creates these
      api-conventions.md
      caching-strategy.md
      service-communication.md
      decisions/
        adr-001-why-graphql.md
        adr-002-microservices-not-monolith.md
    
    data/               ← Data Engineer creates these
      kafka-patterns.md
      airflow-conventions.md
      dbt-standards.md
      data-quality-rules.md
    
    development/        ← Software Engineer creates these
      code-organization.md
      naming-conventions.md
      error-handling.md
      logging-patterns.md
    
    testing/            ← QA Engineer creates these
      test-organization.md
      fixture-patterns.md
      mocking-strategy.md
      integration-test-setup.md
    
    security/           ← Security Engineer creates these
      auth-patterns.md
      secrets-management.md
      api-security.md
      dependency-policy.md
    
    operations/         ← SRE creates these
      deployment-process.md
      monitoring-setup.md
      incident-response.md
      slo-definitions.md
      runbooks/
        database-failover.md
        cache-invalidation.md
```

---

## Standards File Watcher Integration

**MCP Server automatically indexes new standards:**

```python
# mcp_server/agent_os_rag.py

# File watcher detects new file
event: .agent-os/standards/architecture/api-conventions.md created

# Triggers RAG index rebuild
→ Chunk new file
→ Generate embeddings
→ Add to LanceDB
→ Now searchable immediately

# Future queries find it
search_standards("API conventions") 
→ Returns new project-specific standard
```

**Result**: Standards are usable immediately after creation

---

## Best Practices for Standards Population

### ✅ DO:
- Create standard after pattern used 2+ times
- Include context (why this pattern)
- Provide examples (good and bad)
- Document when to revisit
- Keep standards focused (one topic per file)
- Update standards when patterns evolve

### ❌ DON'T:
- Create standard for one-off code
- Write overly generic standards
- Forget to inform user standard was created
- Create standards for trivial decisions
- Let standards go stale (update when changed)

---

## Updated Persona Responsibilities

### All Personas Now Have 3 Roles:

**1. Reviewer** (original role)
- Review designs, code, tests, etc
- Provide expert feedback

**2. Advisor** (original role)
- Answer questions in domain
- Propose solutions

**3. Standards Contributor** (NEW role)
- Populate project standards
- Document patterns and decisions
- Build project knowledge base

---

## Implementation Priority

### Phase 1: Core Personas with Standards Capability
1. ✅ Workflow Executor (doesn't create standards)
2. ⏳ Software Architect + standards population
3. ⏳ Software Engineer + standards population
4. ⏳ Data Engineer + standards population
5. ⏳ QA Engineer + standards population
6. ⏳ Security Engineer + standards population
7. ✅ SRE + standards population (designed)

### Phase 2: Enhance Standards System
- Standards versioning (track changes)
- Standards review workflow (approve before applying)
- Standards conflict detection (flag inconsistencies)
- Standards suggestion (AI proposes standards proactively)

---

## Conclusion

**Key Insight**: Every persona should contribute to project knowledge

**Benefits**:
- Living documentation (always current)
- Consistency enforcement (AI blocks violations)
- Faster onboarding (instant context)
- Knowledge capture (decisions preserved)
- Smarter AI (project-aware advice)

**Implementation**:
- Add "Standards Population" section to all persona prompts
- Define standard directories per persona
- File watcher auto-indexes new standards
- Standards immediately searchable via RAG

---

**Status**: ✅ Universal capability designed, ready to implement in persona prompts
