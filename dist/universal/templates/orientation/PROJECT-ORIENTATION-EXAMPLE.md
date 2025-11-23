# Project Orientation Example

**Metadata**: orientation=true, priority=1, query="inline metadata pattern project orientation markdown co-located", description="Learn the inline metadata pattern for project orientation", category="documentation"

---

## Overview

This is an example markdown file demonstrating **inline metadata** for Project Orientation.

The metadata line above will be automatically discovered during orientation and executed as a query to load project-specific context into AI agents.

---

## How Inline Metadata Works

### 1. The Metadata Pattern

```markdown
**Metadata**: orientation=true, priority=1, query="your query here", description="what this loads"
```

### 2. Required Fields

- **orientation**: Must be `true` to be discovered
- **priority**: 1 (critical), 2 (high), or 3 (medium)
- **query**: The actual query string (5-500 characters)

### 3. Optional Fields

- **description**: Human-readable description of what this loads
- **category**: Category for grouping (e.g., "architecture", "domain", "patterns")
- **depends_on**: Array of query strings this depends on (for ordering)

---

## Example: Dogfooding Model

This document explains prAxIs OS's dogfooding model - how we develop the framework by using it exactly as consumers do.

**Key Points:**

1. **Installation**: prAxIs OS installs into its own `.praxis-os/` directory
2. **Development**: We use the framework to develop itself
3. **Testing**: Real-world usage validates the framework
4. **Standards**: All our own standards are discoverable via RAG

This self-hosting approach ensures the framework works in production because we ARE production.

---

## Why This Pattern Works

By embedding metadata directly in markdown files:

- **Co-located**: Documentation and orientation queries live together
- **Maintainable**: Update docs → orientation automatically updated
- **Discoverable**: Standards index finds all orientation metadata
- **Flexible**: Can have many files with different priorities

---

## Using This Example

1. Copy this file to your `standards/` directory
2. Update the query string to match your project
3. Add more markdown files with their own metadata
4. AI agents will automatically discover and execute all queries

---

## See Also

- **Project Orientation Guide**: Complete documentation on both inline and config-based orientation
- **mcp.yaml.example**: Config-based orientation examples

