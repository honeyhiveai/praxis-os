# Aider AI Coding Assistant - Deep Architecture Analysis

**Date**: 2025-10-12  
**Purpose**: Understand agent design patterns for prAxIs OS persona system  
**Source**: https://github.com/paul-gauthier/aider (2,485 lines base_coder.py)

---

## 🎯 EXECUTIVE SUMMARY

**What Aider Is:**
- Terminal-based AI pair programming tool
- Multiple specialized "coders" with different edit strategies
- Git-integrated, file-focused, command-driven
- 2,485 lines of core agent logic (base_coder.py)

**Key Architectural Insights:**
1. **Multiple Coder Types** - Different specialized strategies for different tasks
2. **Prompt Engineering** - System prompt + Examples + Reminders structure
3. **File Context Management** - Explicit file add/drop, read-only distinction
4. **Repo Mapping** - Maintains semantic map of entire codebase
5. **Command Layer** - 40+ slash commands for agent control
6. **No Custom Tools** - Works with file operations + git, no MCP-like layer

---

## 🏗️ ARCHITECTURE OVERVIEW

### Component Structure

```
aider/
├── coders/                    # Multiple specialized agent strategies
│   ├── base_coder.py          # Core agent logic (2,485 lines)
│   ├── base_prompts.py        # Shared prompt templates
│   ├── architect_coder.py     # High-level design guidance
│   ├── architect_prompts.py   # Architect system prompts
│   ├── editblock_coder.py     # Search/replace edit strategy
│   ├── editblock_prompts.py   # Edit block system prompts
│   ├── wholefile_coder.py     # Whole file replacement strategy
│   ├── udiff_coder.py         # Unified diff strategy
│   ├── ask_coder.py           # Q&A only, no edits
│   └── [10+ more coder types]
├── commands.py                # 40+ slash commands
├── io.py                      # User interaction
├── repo.py                    # Git integration
├── repomap.py                 # Codebase semantic mapping
├── llm.py                     # LLM communication
└── main.py                    # Orchestration

TOTAL: ~20K lines of Python code
```

**Key Pattern:** Modular coder strategies, each with its own system prompt and edit format.

---

## 🧠 SYSTEM PROMPT ARCHITECTURE

### Prompt Structure

**Every coder has:**
1. **`main_system`** - Role definition + instructions (100-300 tokens)
2. **`example_messages`** - Few-shot examples (200-500 tokens)
3. **`system_reminder`** - Rules repeated in context (100-200 tokens)

### Example: EditBlock Coder System Prompt

```python
main_system = """Act as an expert software developer.
Always use best practices when coding.
Respect and use existing conventions, libraries, etc that are already present in the code base.
Take requests for changes to the supplied code.
If the request is ambiguous, ask questions.

Once you understand the request you MUST:

1. Decide if you need to propose *SEARCH/REPLACE* edits to any files that haven't been added to the chat.

2. Think step-by-step and explain the needed changes in a few short sentences.

3. Describe each change with a *SEARCH/REPLACE block* per the examples below.

All changes to files must use this *SEARCH/REPLACE block* format.
ONLY EVER RETURN CODE IN A *SEARCH/REPLACE BLOCK*!
"""
```

**Characteristics:**
- ✅ Clear role definition: "Act as an expert software developer"
- ✅ Explicit format requirements: "ONLY EVER RETURN CODE IN A *SEARCH/REPLACE BLOCK*"
- ✅ Process steps: "Think step-by-step and explain"
- ✅ Error prevention: "If ambiguous, ask questions"
- ⚠️ **No bootstrapping instructions** - Assumes model knows how to start
- ⚠️ **No query guidance** - No "search for context first"

### Example: Architect Coder System Prompt

```python
main_system = """Act as an expert architect engineer and provide direction to your editor engineer.
Study the change request and the current code.
Describe how to modify the code to complete the request.
The editor engineer will rely solely on your instructions, so make them unambiguous and complete.
Explain all needed code changes clearly and completely, but concisely.
Just show the changes needed.

DO NOT show the entire updated function/file/etc!

Always reply to the user in {language}.
"""
```

**Characteristics:**
- ✅ Role-specific behavior: "provide direction to your editor engineer"
- ✅ Clear constraints: "DO NOT show the entire updated function"
- ✅ Concise (7 lines vs 30+ lines for editblock)
- ⚠️ **Assumes high-level role** - No implementation details
- ⚠️ **No standards building** - Purely reactive

---

## 🔧 TOOL/COMMAND ARCHITECTURE

### No MCP-Like Tool Layer

**Aider does NOT have:**
- ❌ Custom tool definitions (like MCP tools)
- ❌ Tool discovery mechanism
- ❌ Tool preference system
- ❌ Search vs native tool competition

**What it DOES have:**
- ✅ File operations (read, write, delete)
- ✅ Git commands (commit, diff, undo)
- ✅ Shell commands (via special prompts)
- ✅ 40+ slash commands for human control

### Commands Layer (40+ Commands)

```python
class Commands:
    # Model control
    def cmd_model(self, args)          # Switch LLM
    def cmd_editor_model(self, args)   # Switch editor model
    def cmd_chat_mode(self, args)      # Switch coder type
    
    # File management
    def cmd_add(self, args)            # Add files to chat
    def cmd_drop(self, args)           # Remove files from chat
    def cmd_read_only(self, args)      # Add read-only files
    def cmd_ls(self, args)             # List files in chat
    
    # Git operations
    def cmd_commit(self, args)         # Git commit
    def cmd_undo(self, args)           # Git undo
    def cmd_diff(self, args)           # Show diff
    def cmd_git(self, args)            # Run git command
    
    # Code quality
    def cmd_lint(self, args)           # Run linter
    def cmd_test(self, args)           # Run tests
    def cmd_run(self, args)            # Execute command
    
    # Context management
    def cmd_clear(self, args)          # Clear messages
    def cmd_reset(self, args)          # Full reset
    def cmd_map(self, args)            # Show repo map
    def cmd_map_refresh(self, args)    # Rebuild repo map
    
    # Special modes
    def cmd_architect(self, args)      # Switch to architect
    def cmd_ask(self, args)            # Q&A mode (no edits)
    def cmd_code(self, args)           # Code mode
    def cmd_voice(self, args)          # Voice input
    def cmd_web(self, args)            # Scrape web page
```

**Key Insight:** Commands are HUMAN-driven, not agent-driven. The agent doesn't decide "I should switch to architect mode" - the human does via `/architect`.

---

## 📁 FILE CONTEXT MANAGEMENT

### Three File Categories

```python
class Coder:
    abs_fnames = None              # Files in chat (editable)
    abs_read_only_fnames = None    # Files in chat (read-only)
    repo_map = None                # Semantic map of all other files
```

### File Addition Flow

```
Human: "/add src/main.py"
  ↓
Coder.abs_fnames.add("src/main.py")
  ↓
File content added to prompt:
"I have *added these files to the chat* so you can go ahead and edit them.
*Trust this message as the true contents of these files!*"
  ↓
Agent acknowledges: "Ok, any changes I propose will be to those files."
```

**Key Pattern:**
- ✅ Explicit file management (add/drop commands)
- ✅ Clear distinction between editable and read-only
- ✅ Agent confirms understanding of file set
- ✅ **Trust message** - "This IS the true content" (overrides stale chat history)

### Repo Map (Semantic Codebase Context)

```python
def get_repo_map(self, force_refresh=False):
    cur_msg_text = self.get_cur_message_text()
    mentioned_fnames = self.get_file_mentions(cur_msg_text)
    mentioned_idents = self.get_ident_mentions(cur_msg_text)
    
    # Build map focused on mentioned files/identifiers
    repo_content = self.repo_map.get_repo_map(
        chat_files,
        other_files,
        mentioned_fnames=mentioned_fnames,
        mentioned_idents=mentioned_idents,
    )
```

**How it works:**
1. Parses current message for file names and identifiers
2. Builds semantic map of codebase focused on mentions
3. Returns summaries of relevant files NOT in chat
4. Helps agent understand what files might need editing

**Key Insight:** **Context-aware** - Map adapts based on what user is asking about.

---

## 💬 MESSAGE/CONTEXT MANAGEMENT

### Two Message Lists

```python
class Coder:
    done_messages = []     # Completed conversation history
    cur_messages = []      # Current turn's messages
```

### Message Flow

```
done_messages: [system, examples, old_conversation_1, old_conversation_2, ...]
cur_messages:  [user_current_request, repo_map, file_contents, system_reminder]

Combined → Send to LLM → Response → Move cur_messages to done_messages
```

### Summarization for Long Sessions

```python
def summarize_end(self):
    if not self.summarizer.too_big(self.done_messages):
        return
    
    # Conversation getting too long
    self.summarizing_messages = list(self.done_messages)
    self.summarized_done_messages = self.summarizer.summarize(self.summarizing_messages)
    
    if self.summarizing_messages == self.done_messages:
        self.done_messages = self.summarized_done_messages
```

**Key Pattern:**
- ✅ Automatic summarization when context too large
- ✅ Keeps recent messages, summarizes old ones
- ✅ **Addresses context degradation through compression**
- ⚠️ Still loses fidelity over time

---

## 🎭 MULTIPLE CODER TYPES (Specialist Pattern)

### Coder Type Switching

```python
# User can switch between coders mid-session
/ask          # Ask-only mode (no edits)
/code         # Back to code mode
/architect    # High-level design mode
```

### Why Multiple Coders?

**Different tasks need different approaches:**

| Coder Type | Purpose | Edit Strategy | Token Efficiency |
|-----------|---------|---------------|------------------|
| **editblock** | Precise edits | SEARCH/REPLACE blocks | High (only changes) |
| **wholefile** | Small files | Replace entire file | Low (full file) |
| **udiff** | Line-based changes | Unified diff format | Medium |
| **architect** | High-level guidance | No edits, just instructions | Highest (no code) |
| **ask** | Q&A only | No edits | Highest |

**Key Insight:** **Task-specific optimization** - Different prompts and edit formats for different use cases.

### How prAxIs OS Could Use This

**Agent OS Personas = Aider's Coders:**
- Database Specialist = Specialized prompt + domain knowledge
- Security Engineer = Specialized prompt + security focus
- Architect = High-level design (already in Aider!)

**Difference:**
- Aider: Human switches modes via commands
- prAxIs OS: Main agent invokes specialists via MCP tools

---

## 🧪 LEARNINGS FOR AGENT OS PERSONAS

### 1. System Prompt Design Patterns

**From Aider:**
```
main_system:
  - Role definition: "Act as X"
  - Scope definition: What they should/shouldn't do
  - Process guidance: Step-by-step expectations
  - Format requirements: How to structure outputs
  - Constraints: What to avoid

example_messages:
  - 2-3 concrete examples
  - Show desired input/output format
  - Demonstrates the process

system_reminder:
  - Rules that need reinforcement
  - Format requirements (repeated)
  - Common mistakes to avoid
```

**For prAxIs OS Personas:**
```python
SPECIALIST_SYSTEM_PROMPT = """
You are a {role} specialist for prAxIs OS.

MANDATORY BOOTSTRAP:
1. search_standards("{role} decision protocol")
2. search_standards("{domain} patterns in this project")

THEN analyze the task.

Your mission: {mission_description}

Process:
1. Discover project patterns (query, don't assume)
2. Analyze against project standards
3. Propose improvements/standards if patterns found
4. Document for future specialists

REMEMBER: Query project-specific standards first, not generic advice.
"""
```

**Key additions for prAxIs OS:**
- ✅ Bootstrap sequence (Aider doesn't have this)
- ✅ Standards-building mission (Aider is purely reactive)
- ✅ Query-first emphasis (Aider assumes file context given)

### 2. File Context Management

**Aider's Pattern:**
- Explicit `/add` command to add files
- Clear "these are the files you can edit" message
- Trust message: "This IS the true content"

**For prAxIs OS:**
- Specialists should also have explicit file context
- Clear boundaries: "These files are your scope"
- Helps prevent specialists from roaming too wide

### 3. Multiple Edit Strategies

**Aider has 10+ different edit formats** because:
- Different tasks optimize differently
- Token costs matter
- Different models prefer different formats

**For prAxIs OS:**
- Don't need multiple edit formats (main agent handles that)
- BUT do need multiple specialist types
- Each specialist optimized for their domain

### 4. Command Layer for Control

**Aider's 40+ commands give humans fine-grained control:**
- `/add`, `/drop` - File management
- `/architect`, `/ask` - Mode switching
- `/undo`, `/diff` - Git operations
- `/clear`, `/reset` - Context management

**For prAxIs OS:**
- Main agent has this control layer
- Specialists don't need it (short-lived, focused)
- MCP tools provide equivalent control

### 5. Repo Map for Discovery

**Aider's repo map is context-aware:**
- Parses user question for file mentions
- Parses for code identifiers
- Returns relevant file summaries
- Helps agent discover what files to edit

**For prAxIs OS:**
- `codebase_search` provides similar functionality
- Specialists should use it to discover context
- **This is what we want to encourage vs grep!**

---

## ⚠️ WHAT AIDER DOESN'T SOLVE

### Problems Aider Doesn't Address

1. **No MCP-like tool layer**
   - Works directly with files
   - No tool preference problem
   - No native vs custom tool competition

2. **No knowledge accumulation**
   - Every session starts fresh
   - No project-specific standards
   - No self-improving system

3. **Human-driven mode switching**
   - Agent doesn't decide to switch to architect mode
   - Human controls via commands
   - Agent is reactive, not proactive

4. **No decision protocol**
   - Prompts assume agent knows what to do
   - No guidance on "how to think"
   - No behavioral foundation

5. **Context degradation still happens**
   - Summarization helps but loses fidelity
   - Long sessions still degrade
   - No self-reinforcing patterns

### What prAxIs OS Adds

| Feature | Aider | prAxIs OS |
|---------|-------|----------|
| Tool layer | ❌ Native only | ✅ MCP tools |
| Knowledge accumulation | ❌ None | ✅ Standards population |
| Specialist invocation | Human-driven | AI-driven (MCP) |
| Decision protocol | ❌ None | ✅ Behavioral guidance |
| Self-reinforcing | ❌ None | ✅ Query-on-demand |
| Context-aware prepends | ❌ None | ✅ Targeted nudges |

---

## 🎯 KEY INSIGHTS FOR PERSONA DESIGN

### 1. Specialist System Prompts Should Be Concise

**Aider's architect prompt: 17 lines**
```python
main_system = """Act as an expert architect engineer and provide direction to your editor engineer.
Study the change request and the current code.
Describe how to modify the code to complete the request.
[...]
"""
```

**Lesson:** ~200-400 tokens is enough if well-structured.

### 2. Few-Shot Examples Are Powerful

**Aider includes 2-3 concrete examples in every coder:**
```python
example_messages = [
    dict(role="user", content="Change get_factorial() to use math.factorial"),
    dict(role="assistant", content="[Shows exact SEARCH/REPLACE format]"),
    [...]
]
```

**Lesson:** Show, don't just tell. Examples teach format better than rules.

### 3. System Reminders Combat Drift

**Aider repeats key rules in `system_reminder`:**
```python
system_reminder = """# *SEARCH/REPLACE block* Rules:

Every *SEARCH/REPLACE block* must use this format:
[...]
ONLY EVER RETURN CODE IN A *SEARCH/REPLACE BLOCK*!
"""
```

**Lesson:** Repeat critical constraints. Even in short sessions, models drift.

### 4. Context-Aware Adaptation Works

**Aider's repo map adapts based on user question:**
- Parses mentions → focuses map on relevant files
- Different queries → different context

**Lesson:** This is like our context-aware prepends! Same principle.

### 5. Trust Messages Override History

**Aider explicitly says:**
```
"I have *added these files to the chat* so you can go ahead and edit them.
*Trust this message as the true contents of these files!*
Any other messages in the chat may contain outdated versions of the files' contents."
```

**Lesson:** **Explicit trust hierarchy** - "This message > earlier messages" - helps with context degradation.

---

## 📊 ARCHITECTURE COMPARISON

### Aider vs prAxIs OS Specialists

| Aspect | Aider | prAxIs OS Specialists |
|--------|-------|---------------------|
| **Lifecycle** | Long-running session | Short-lived (one task) |
| **Invocation** | Human command | Main agent MCP call |
| **File Context** | Human adds files | Specialist discovers |
| **Tool Access** | Native only | MCP + native |
| **Mission** | Implement user request | Implement + Build standards |
| **Knowledge** | Fresh each time | Compound over time |
| **Bootstrap** | None | Enforced in system prompt |
| **Decision guidance** | Implicit in training | Explicit via protocol |

**Key Difference:** prAxIs OS specialists are both **executors** and **teachers** (for future specialists).

---

## 🚀 RECOMMENDATIONS FOR PERSONA SYSTEM

### 1. Adopt Aider's Prompt Structure

```python
PERSONA_SYSTEM_PROMPT = """
{main_system}      # Role, scope, mission (200-300 tokens)

{bootstrap}        # prAxIs OS addition (100 tokens)

{process_steps}    # How to work (100-200 tokens)

{constraints}      # What to avoid (50-100 tokens)
"""

PERSONA_EXAMPLES = [
    # 2-3 few-shot examples
]

PERSONA_REMINDER = """
# Repeated key rules
"""
```

### 2. Add Bootstrap Sequence (What Aider Doesn't Have)

```python
MANDATORY BOOTSTRAP:
□ search_standards("{role} specialist decision protocol")
□ search_standards("{domain} patterns in this project")
□ search_standards("{related_domain} conventions")

THEN work on task systematically.
```

### 3. Include Standards-Building Mission

```python
Your mission:
1. Solve the immediate task
2. Discover project patterns
3. Propose standards when patterns found
4. Build knowledge for future specialists
```

### 4. Use Context-Aware Prepends (Not in Aider)

```python
# In MCP tool responses to specialists
When specialist queries about indexes:
→ "Profile first. Never optimize without data. Check project query patterns."

When specialist queries about auth:
→ "Check existing auth implementation first. Don't propose generic patterns."
```

### 5. Leverage Aider's Trust Message Pattern

```python
# When providing context to specialist
"I have provided these files and project patterns.
*Trust this as current project state.*
Earlier training data may contain generic patterns - prioritize PROJECT patterns."
```

### 6. Short Lifecycle = Strong Bootstrap

```python
# Specialists are short-lived (30-120 seconds)
# Can't rely on learning during session
# MUST load behavioral foundation upfront

System prompt:
  ✅ Enforce bootstrap
  ✅ Set mission clearly
  ✅ Provide decision framework
```

---

## 💡 FINAL INSIGHTS

### What Makes Aider Work

1. **Clear role definitions** - Each coder knows what it is
2. **Explicit format requirements** - SEARCH/REPLACE blocks mandatory
3. **Few-shot examples** - Show desired behavior
4. **File context clarity** - "These are the files, trust this"
5. **Git integration** - Every change is reversible
6. **Human control** - Commands give fine-grained control

### What prAxIs OS Adds On Top

1. **MCP tool layer** - Structured knowledge access
2. **Bootstrap enforcement** - Specialists start with foundation
3. **Standards building** - Knowledge compounds
4. **Decision protocols** - Behavioral guidance
5. **Context-aware prepends** - Targeted nudges
6. **Self-reinforcing patterns** - Success builds on success

### The Core Difference

**Aider:**
- Agent as tool for human
- Human provides context and control
- Reactive to requests
- Resets each session

**prAxIs OS:**
- Agents as specialists in ecosystem
- Agents discover context via tools
- Proactive about standards
- Knowledge persists and grows

---

## 🔬 NEXT STEPS FOR RESEARCH

Based on this analysis, we should:

1. ✅ **Design specialist system prompts** using Aider's structure + prAxIs OS additions
2. ✅ **Define bootstrap sequences** for each specialist type
3. ✅ **Create few-shot examples** showing desired specialist behavior
4. ✅ **Document decision protocols** specific to each domain
5. ⏳ **Test with real tasks** to validate prompt effectiveness
6. ⏳ **Iterate based on dogfooding** (like Aider does)

---

**Key Takeaway:** Aider proves that **multiple specialized agents with clear prompts work**. prAxIs OS adds **knowledge accumulation** and **behavioral guidance** on top of that foundation.

This analysis gives us a proven blueprint to build from.

