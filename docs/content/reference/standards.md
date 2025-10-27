---
sidebar_position: 3
doc_type: reference
---

# Standards Reference

Comprehensive index of universal standards accessible via `search_standards`.

## Overview

prAxIs OS ships two types of standards. The first are timeless CS fundamentals that apply across programming languages. The second are the standards that form the basis for prAxIs OS itself. These help aid the agents in making better decisions and adhering to standards served via the MCP search_standards tool. Standards are retrieved via semantic search (`search_standards`) rather than direct file reading.

**Access Pattern:**
```python
search_standards("how to handle race conditions")
# Returns relevant chunks from universal standards
```

---

## Standards Categories

### AI Assistant

Standards for AI agent behavior and decision-making.

| Standard | Purpose |
|----------|---------|
| [Agent Decision Protocol](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/ai-assistant/agent-decision-protocol.md) | Query-first approach, multi-angle thinking, probabilistic behavior management |
| [Agent OS Orientation](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/ai-assistant/AGENT-OS-ORIENTATION.md) | 8 mandatory bootstrap queries for AI agents |
| [Agent OS Development Process](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/ai-assistant/agent-os-development-process.md) | Systematic development workflow patterns |
| [Analysis Methodology](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/ai-assistant/analysis-methodology.md) | Problem analysis and decomposition strategies |
| [Commit Protocol](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/ai-assistant/commit-protocol.md) | Commit message standards and git workflows |
| [Compliance Protocol](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/ai-assistant/compliance-protocol.md) | Ensuring adherence to project standards |
| [Knowledge Compounding](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/ai-assistant/knowledge-compounding-guide.md) | Building cumulative understanding across sessions |
| [MCP Tool Discovery](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/ai-assistant/mcp-tool-discovery.md) | Finding and using MCP tools effectively |
| [MCP Tools Guide](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/ai-assistant/MCP-TOOLS-GUIDE.md) | Comprehensive MCP tool usage patterns |
| [Pre-Generation Validation](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/ai-assistant/pre-generation-validation.md) | Validation before code generation |
| [Query Construction Patterns](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/ai-assistant/query-construction-patterns.md) | Effective `search_standards` query patterns |
| [RAG Content Authoring](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/ai-assistant/rag-content-authoring.md) | Writing discoverable standards content |
| [Standards Creation Process](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/ai-assistant/standards-creation-process.md) | Creating new universal standards |

### AI Safety

Safety rules and protections for AI agents.

| Standard | Purpose |
|----------|---------|
| [Credential File Protection](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/ai-safety/credential-file-protection.md) | Preventing accidental credential exposure |
| [Date Usage Policy](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/ai-safety/date-usage-policy.md) | Using `current_date` tool vs cached dates |
| [Git Safety Rules](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/ai-safety/git-safety-rules.md) | Safe git operations (no force push, etc.) |
| [Import Verification Rules](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/ai-safety/import-verification-rules.md) | Verifying imports exist before using |
| [Production Code Checklist](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/ai-safety/production-code-checklist.md) | Pre-commit quality checklist |

### Architecture

Software architecture patterns and principles.

| Standard | Purpose |
|----------|---------|
| [API Design Principles](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/architecture/api-design-principles.md) | RESTful design, versioning, error handling |
| [Dependency Injection](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/architecture/dependency-injection.md) | Loose coupling, testability, flexibility |
| [Separation of Concerns](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/architecture/separation-of-concerns.md) | Layered architecture, bounded contexts |
| [SOLID Principles](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/architecture/solid-principles.md) | Single Responsibility, Open/Closed, Liskov, Interface Segregation, Dependency Inversion |

### Concurrency

Patterns for managing shared state and parallel execution.

| Standard | Purpose |
|----------|---------|
| [Deadlocks](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/concurrency/deadlocks.md) | Detection, prevention, resolution of deadlocks |
| [Locking Strategies](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/concurrency/locking-strategies.md) | Mutex, RWLock, fine-grained locking patterns |
| [Race Conditions](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/concurrency/race-conditions.md) | Detection and prevention of race conditions |
| [Shared State Analysis](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/concurrency/shared-state-analysis.md) | Identifying and managing shared data |

### Database

Database design and implementation patterns.

| Standard | Purpose |
|----------|---------|
| [Database Patterns](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/database/database-patterns.md) | Transactions, indexes, migrations, query optimization |

### Documentation

Documentation standards and templates.

| Standard | Purpose |
|----------|---------|
| [API Documentation](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/documentation/api-documentation.md) | API docs structure and content |
| [Code Comments](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/documentation/code-comments.md) | When and how to comment code |
| [README Templates](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/documentation/readme-templates.md) | Project README structure |

### Failure Modes

Resilience and graceful degradation patterns.

| Standard | Purpose |
|----------|---------|
| [Circuit Breakers](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/failure-modes/circuit-breakers.md) | Preventing cascading failures |
| [Graceful Degradation](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/failure-modes/graceful-degradation.md) | Degrade functionality, not availability |
| [Retry Strategies](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/failure-modes/retry-strategies.md) | Exponential backoff, jitter, retry limits |
| [Timeout Patterns](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/failure-modes/timeout-patterns.md) | Preventing indefinite waiting |

### Installation

Installation and update procedures.

| Standard | Purpose |
|----------|---------|
| [Gitignore Requirements](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/installation/gitignore-requirements.md) | Required .gitignore entries for prAxIs OS |
| [Update Procedures](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/installation/update-procedures.md) | Upgrading prAxIs OS safely |

### Meta-Framework

Principles for building AI-assisted workflows.

| Standard | Purpose |
|----------|---------|
| [Command Language](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/meta-framework/command-language.md) | Structured commands for AI execution |
| [Framework Creation Principles](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/meta-framework/framework-creation-principles.md) | Creating new workflows |
| [Horizontal Decomposition](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/meta-framework/horizontal-decomposition.md) | Breaking tasks into optimal file sizes |
| [Three-Tier Architecture](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/meta-framework/three-tier-architecture.md) | Execution, methodology, output file separation |
| [Validation Gates](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/meta-framework/validation-gates.md) | Evidence-based phase progression |

### Performance

Performance optimization patterns.

| Standard | Purpose |
|----------|---------|
| [Optimization Patterns](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/performance/optimization-patterns.md) | Profiling, caching, lazy loading, algorithmic optimization |

### Security

Security patterns and best practices.

| Standard | Purpose |
|----------|---------|
| [Security Patterns](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/security/security-patterns.md) | Input validation, least privilege, defense in depth |

### Testing

Test strategies and patterns.

| Standard | Purpose |
|----------|---------|
| [Integration Testing](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/testing/integration-testing.md) | Testing component interactions |
| [Property-Based Testing](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/testing/property-based-testing.md) | Automated test case generation |
| [Test Doubles](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/testing/test-doubles.md) | Mocks, stubs, fakes, spies |
| [Test Pyramid](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/testing/test-pyramid.md) | Unit (70%), Integration (20%), E2E (10%) |

### Workflows

Workflow system standards.

| Standard | Purpose |
|----------|---------|
| [MCP RAG Configuration](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/workflows/mcp-rag-configuration.md) | Configuring RAG for workflow discovery |
| [Time Estimation Standards](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/workflows/time-estimation-standards.md) | Estimating workflow and task durations |
| [Workflow Construction Standards](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/workflows/workflow-construction-standards.md) | Building compliant workflows |
| [Workflow Metadata Standards](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/workflows/workflow-metadata-standards.md) | metadata.json structure and requirements |
| [Workflow System Overview](https://github.com/honeyhiveai/praxis-os/blob/main/universal/standards/workflows/workflow-system-overview.md) | How the workflow system works |

---

## Usage Pattern

Standards are accessed via semantic search, not direct file reading:

```python
# Query for specific guidance
search_standards(
    query="How do I prevent race conditions in async code?",
    n_results=3
)

# Returns relevant chunks:
# - Universal race condition principles
# - Language-specific patterns (if generated)
# - Project-specific guidance
```

**Benefits:**
- 90% context reduction (2-5KB chunks vs 50KB files)
- Only relevant content loaded
- Maintains attention quality
- Just-in-time delivery

---

## Related Documentation

- [MCP Tools Reference](./mcp-tools) - Complete `search_standards` API documentation
- [How It Works](../explanation/how-it-works) - RAG-driven behavioral reinforcement
- [Architecture](../explanation/architecture) - MCP/RAG system implementation
- [Workflows](./workflows) - How standards integrate with workflows
