# MCP Tools - Dynamic Discovery Guide

**How to discover and use Agent OS MCP tools through dynamic introspection**

---

## 🎯 TL;DR - MCP Dynamic Discovery Quick Reference

**Keywords for search**: MCP tools, tool discovery, tools/list, dynamic discovery, IDE autocomplete, self-documenting tools, probabilistic reality, context degradation, why query matters, MCP introspection

**Core Principle:** Tools are self-documenting via MCP protocol. Discover dynamically through IDE, never memorize.

**The Agent OS Way:**
1. ✅ **Start typing in IDE** → Autocomplete shows all available tools + schemas
2. ✅ **Use tools/list** → Always-current source of truth
3. ✅ **Query for patterns** → `search_standards("how to use X tool")`
4. ❌ **Don't memorize** → Tools evolve, parameters change
5. ❌ **Don't read static docs** → Will drift from actual implementation

**Why Dynamic Discovery Matters:**
- Tools add/remove/change between versions
- Parameter schemas are definitive in code
- IDE provides real-time introspection
- Documentation always lags implementation

**The Probabilistic Reality:**
```
Context Window at Message 1:  Initial instructions = 75% influence
Context Window at Message 30: Initial instructions = 0.6% influence

Result: Initial guidance fades mathematically
Solution: Create self-reinforcing habits through tools
```

**Tool Categories (High-Level):**
- **Discovery:** `search_standards` (most important)
- **Workflows:** Phase-gated execution tools
- **Browser:** `aos_browser` (browse web like a human - extract themes, compare UIs, research, test)
- **System:** Date, validation, framework tools

**When to Query This Guide:**
- Need to understand dynamic discovery → `search_standards("MCP dynamic discovery")`
- Why tools/list matters → `search_standards("why dynamic tools")`
- Understanding context degradation → `search_standards("probabilistic reality AI")`

---

## ❓ Questions This Answers

1. "How do I discover what MCP tools are available?"
2. "Why doesn't Agent OS document all tools statically?"
3. "How does tools/list work?"
4. "Why can't I just memorize the tools?"
5. "What is probabilistic reality?"
6. "Why does context degrade over time?"
7. "How does IDE autocomplete get tool info?"
8. "Why dynamic discovery over static documentation?"
9. "What categories of tools exist?"
10. "How to find the right tool for my task?"

---

## Why Dynamic Discovery Over Static Documentation?

Agent OS tools are self-documenting and evolutionary. Static documentation creates maintenance burden and guaranteed drift.

**The Problem with Static Documentation:**

```
Traditional Approach:
Code changes → Docs lag → Docs wrong → User confused → Time wasted

Agent OS Approach:
Code IS documentation → Always accurate → IDE shows it → User succeeds
```

**The MCP Protocol Solution:**

The MCP (Model Context Protocol) provides built-in tool introspection:

```
Your IDE → calls tools/list → receives:
    - Complete tool inventory
    - Parameter schemas (types, required/optional)
    - Return type schemas
    - Tool descriptions
    - Real-time accuracy (reflects actual code)
```

**Benefits:**
- ✅ **Always accurate** - Tools define themselves in code
- ✅ **Never out of sync** - No manual doc updates needed
- ✅ **Self-documenting** - Parameter schemas built-in
- ✅ **Evolutionary** - New tools appear automatically
- ✅ **IDE integration** - Autocomplete works instantly

**When You Need Tool Information:**
- "What tools exist?" → **Start typing in IDE, autocomplete shows all**
- "What params does X take?" → **IDE shows inline parameter documentation**
- "How do I use X effectively?" → **Query for patterns: `search_standards("how to use X tool")`**

---

## Understanding Probabilistic Reality (Why Initial Instructions Fade)

**Critical insight for AI agents:** Your memory of patterns and instructions degrades mathematically as your session grows.

### The Mathematical Reality

```
Context Window Composition Over Time:

Message 1:
├── Initial orientation: 15,000 tokens (75% of context)
└── User message: 5,000 tokens (25%)
→ Rules/patterns have HIGH statistical influence

Message 30:
├── Initial orientation: 15,000 tokens (still 15k)
├── 29 messages of conversation: 2,485,000 tokens (99.4%)
└── Latest message: 5,000 tokens
→ Rules/patterns have NEGLIGIBLE statistical influence (0.6%)

Result: Initial guidance becomes statistically irrelevant
```

### Why This Matters for Tool Usage

As your context grows, you probabilistically forget:
- Which tools exist
- How to use them
- Best practices for tool selection
- Patterns for effective usage

**You can't prevent this degradation** - it's mathematical reality.

**You CAN create self-reinforcing habits** that persist through the session.

### The Self-Reinforcing Solution

Dynamic discovery + frequent querying creates persistent behavior:

```
Discover Tool via IDE Autocomplete
         ↓
Query for usage pattern
         ↓
Get answer + "Query more" reminder
         ↓
P(query_next_time) increases
         ↓
Pattern reinforces with each use
         ↓
Dynamic discovery becomes automatic
```

**Key insight:** You can't keep all tools in your working memory. You CAN make "discover dynamically" your default habit.

---

## How to Discover Available Tools

### Method 1: IDE Autocomplete (Primary)

**The fastest way to discover tools:**

1. Start typing `mcp_` or tool category name
2. IDE calls `tools/list` automatically
3. Autocomplete shows all available tools
4. Select tool to see parameter schema
5. IDE shows inline documentation

**This is ALWAYS current** - reflects actual code at runtime.

### Method 2: Query for Patterns

**When you need usage guidance:**

```python
# Don't know what tools exist for X
search_standards("what tools for browser testing")

# Know tool name, need usage pattern
search_standards("how to use aos_browser")

# Know category, need specific capability
search_standards("workflow tools")
```

**Queries return patterns and best practices**, not parameter lists (IDE provides those).

### Method 3: tools/list Direct Inspection

**For comprehensive discovery:**

```python
# List all available tools with schemas
tools = mcp.list_tools()

# Returns:
# - Tool names
# - Descriptions
# - Parameter schemas
# - Return types
```

---

## Tool Selection Mental Model

**High-level categories (not exhaustive - use IDE to discover specifics):**

### Discovery & Learning Tools
- **Primary use:** Finding information and guidance
- **When:** Before implementing anything
- **Example pattern:** Query 5-10 times to understand approach

### Workflow Tools
- **Primary use:** Structured, phase-gated execution
- **When:** Complex tasks with multiple steps
- **Example pattern:** Start workflow, get phase, complete phase

### Browser & Web Research Tools
- **Primary use:** Browse web like a human - research, extract info, compare sites, UI development, testing
- **When:** Need to interact with or learn from web content
- **Example patterns:** 
  - Extract design themes from sample sites
  - Compare UI implementations across sites
  - Research best practices by browsing examples
  - Test web applications
  - Gather information from public websites

### System Tools
- **Primary use:** Dates, validation, framework operations
- **When:** Specific system-level needs
- **Example pattern:** Get current date, validate structure

**To find tools for your task:**
1. Start typing in IDE (category or verb)
2. Explore autocomplete suggestions
3. Query for usage patterns: `search_standards("how to use [discovered tool]")`

---

## Best Practices for Dynamic Discovery

### 1. Trust IDE Autocomplete Over Memory

**Wrong:**
```python
# Trying to remember exact tool name and parameters
mcp_search_documents(query="...", limit=5, ...)  # Guessing
```

**Right:**
```python
# Start typing, let IDE show options
mcp_[autocomplete shows: search_standards, search_workflow, etc.]
# Select correct tool, IDE shows exact parameter schema
```

### 2. Query for Patterns, Not Parameters

**Wrong:**
```python
search_standards("aos_browser parameters")  # IDE already shows this
```

**Right:**
```python
search_standards("how to test web UI with aos_browser")  # Patterns
```

### 3. Embrace Evolution

**Wrong Mindset:**
"I'll memorize all tools and their parameters"

**Right Mindset:**
"I'll develop the habit of discovering tools dynamically as needed"

### 4. Combine Discovery Methods

```python
# 1. IDE autocomplete → discover tool exists
# 2. IDE hover → see parameter schema
# 3. Query → understand usage patterns
# 4. Implement → use tool effectively
```

---

## Why This Guide Exists

**This guide does NOT:**
- ❌ List all available tools (that's `tools/list` via IDE)
- ❌ Document every parameter (that's tool schemas)
- ❌ Provide complete API reference (that's MCP protocol)

**This guide DOES:**
- ✅ Explain WHY dynamic discovery works
- ✅ Teach HOW to discover tools effectively
- ✅ Clarify the probabilistic reality you face
- ✅ Provide mental models for tool selection

**The unique value:** Understanding the SCIENCE of why Agent OS uses dynamic discovery, not documenting specific tools.

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Understanding dynamic discovery** | `search_standards("MCP dynamic discovery")` |
| **Why tools/list matters** | `search_standards("why dynamic tools")` |
| **Context degradation** | `search_standards("probabilistic reality AI")` |
| **Tool discovery best practices** | `search_standards("how to discover MCP tools")` |
| **Why not static docs** | `search_standards("why MCP tools not documented")` |
| **Tool selection** | `search_standards("how to choose right tool")` |

---

## 🔗 Related Standards

**Query workflow for tool mastery:**

1. **Start with dynamic discovery** → `search_standards("MCP dynamic discovery")` (this document)
2. **Learn orientation** → `search_standards("Agent OS orientation")` → `standards/ai-assistant/AGENT-OS-ORIENTATION.md`
3. **See practical examples** → `search_standards("AI agent examples")` → `usage/ai-agent-quickstart.md`
4. **Understand workflows** → `search_standards("workflow system")` → `standards/workflows/workflow-system-overview.md`

**By Category:**

**AI Assistant:**
- `standards/ai-assistant/AGENT-OS-ORIENTATION.md` - Core Agent OS concepts → `search_standards("Agent OS orientation")`
- `usage/mcp-usage-guide.md` - MCP protocol usage → `search_standards("MCP usage guide")`

**Usage:**
- `usage/ai-agent-quickstart.md` - Practical examples → `search_standards("AI agent behavior examples")`
- `usage/operating-model.md` - Partnership roles → `search_standards("operating model")`

**Development:**
- `standards/development/mcp-tool-design-best-practices.md` - Creating tools → `search_standards("MCP tool design")`

---

**Dynamic discovery over static documentation. Embrace evolution, trust introspection, query for patterns.** 🚀
