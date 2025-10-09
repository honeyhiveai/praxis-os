# AI Assistant Standards - Start Here

**Universal operational standards for AI assistants working within Agent OS Enhanced**

---

## 🚨 CRITICAL: Start Here

**EVERY AI assistant interaction MUST begin with compliance checking.**

### Mandatory Standards (Read First)

1. 📋 **[Compliance Protocol](compliance-protocol.md)** - MANDATORY first step
   - Check existing standards before any task
   - Verify established patterns
   - Confirm no existing solutions

2. 🎯 **[Pre-Generation Validation](pre-generation-validation.md)** - Before generating code
   - Three-checkpoint validation (pre-task, per-file, pre-commit)
   - Environment and codebase state awareness
   - Context-specific validation procedures

3. 📝 **[Commit Protocol](commit-protocol.md)** - Before committing
   - Review checkpoint structure
   - CHANGELOG workflow
   - Commit decision matrix

4. 🔍 **[Analysis Methodology](analysis-methodology.md)** - Comprehensive analysis
   - Systematic approach to analysis tasks
   - Leverage AI's unique capabilities
   - Evidence-based conclusions

---

## 📊 Standards Priority Order

### 🚨 Critical (Must Follow)

**These are non-negotiable. Violating these compromises system integrity.**

1. **Compliance Protocol** - Always check existing standards first
   - Prevents reinventing solutions
   - Ensures consistency
   - Follows established patterns

2. **Safety Rules** - See `.agent-os/standards/ai-safety/`
   - Credential file protection
   - Git safety protocols
   - Import verification
   - Date usage policies

3. **Pre-Generation Validation** - Validate before generating
   - Current date retrieval
   - Environment verification
   - Codebase understanding
   - State awareness

4. **Quality Framework** - Meet all quality requirements
   - See project's `.agent-os/standards/development/` for specifics
   - Zero tolerance for quality violations
   - Automated quality gates

### ⚡ Important (Should Follow)

**These significantly improve quality and consistency.**

1. **Code Generation Patterns** - Follow established patterns
   - See project's `.agent-os/standards/development/code-quality.md`
   - Use project's conventions
   - Follow architecture patterns

2. **Error Pattern Recognition** - Systematic debugging
   - See project's `.agent-os/standards/development/error-patterns.md` (if exists)
   - Recognize common patterns
   - Apply resolution templates

3. **Documentation Standards** - Proper documentation
   - See project's documentation requirements
   - API documentation
   - Code comments

### 📋 Helpful (Good to Follow)

**These improve efficiency and speed.**

1. **Quick References** - Fast pattern lookups
   - See project's `.agent-os/standards/development/quick-reference.md` (if exists)
   - Common patterns
   - Decision trees

2. **Best Practices** - Language-specific guidance
   - See project's `.agent-os/standards/development/` for language-specific docs
   - Project conventions
   - Technology-specific patterns

---

## 🎯 Universal Workflow

**This workflow applies to ALL tasks, regardless of programming language or project type.**

```
User Request
    ↓
Pre-Task Validation (ONCE)
    ├─ Compliance check: Read relevant standards
    ├─ Verify clean starting state (preferred)
    ├─ Understand full scope of request
    ├─ Get current date (prevents hardcoded dates)
    └─ Review recent project history
    ↓
Task Execution (PER FILE/CHANGE)
    ├─ Pre-generation validation
    │   ├─ Verify current codebase understanding
    │   ├─ State awareness (NOT blocking on multi-file)
    │   └─ Still on correct branch
    ├─ Generate code/changes
    └─ Maintain awareness of task progress
    ↓
Pre-Commit Validation (ONCE)
    ├─ Run quality gates (all must pass)
    │   ├─ Code formatting
    │   ├─ Static analysis
    │   ├─ Type checking
    │   ├─ Unit tests
    │   └─ Integration tests
    ├─ Review changes with user
    ├─ CHANGELOG assessment
    └─ Get user approval to commit
```

---

## 🔗 Project-Specific Extensions

Projects extend these universal standards with language/tool-specific implementations in `.agent-os/standards/development/`:

### Code Quality Standards
- **What**: Tool-specific quality requirements
- **Example**: `code-quality.md` (Pylint ≥8.0, MyPy zero errors, Black formatting)
- **Location**: `.agent-os/standards/development/code-quality.md`

### Validation Commands
- **What**: Exact commands to run for validation steps
- **Example**: `validation-commands.md` (tox -e format, npm test, cargo check)
- **Location**: `.agent-os/standards/development/validation-commands.md`

### Compliance Addendum
- **What**: Project-specific mandatory rules
- **Example**: `compliance-addendum.md` (Never run pytest directly, always use tox)
- **Location**: `.agent-os/standards/development/compliance-addendum.md`

### Quick Reference
- **What**: Fast pattern lookups for common tasks
- **Example**: `quick-reference.md` (Error patterns, fix commands, decision trees)
- **Location**: `.agent-os/standards/development/quick-reference.md`

### Error Patterns
- **What**: Common error patterns and resolutions
- **Example**: `error-patterns.md` (ImportError patterns, TypeError fixes)
- **Location**: `.agent-os/standards/development/error-patterns.md`

---

## 📚 How to Use These Standards

### For AI Assistants

**At Start of Every Task:**
1. Read [Compliance Protocol](compliance-protocol.md)
2. Execute pre-task validation from [Pre-Generation Validation](pre-generation-validation.md)
3. Check project-specific standards in `.agent-os/standards/development/`

**During Task Execution:**
1. Follow universal workflow (above)
2. Execute per-file validation before each generation
3. Refer to quick references as needed

**Before Committing:**
1. Follow [Commit Protocol](commit-protocol.md)
2. Run all project quality gates
3. Request user review and approval

### For Humans

**Setting Up New Project:**
1. Install Agent OS Enhanced (copies these universal standards)
2. Create project-specific standards in `.agent-os/standards/development/`
3. Define validation commands, quality requirements, etc.

**Working with AI:**
1. Expect AI to follow these standards automatically
2. AI will ask for clarification on project specifics
3. Review AI's work at checkpoints

---

## 🎨 Customization Philosophy

### What's Universal (Don't Change)

These standards in `universal/ai-assistant/`:
- ✅ Workflow structure (compliance → task → validation)
- ✅ Three-checkpoint validation concept
- ✅ Commit review protocol structure
- ✅ Analysis methodology principles

**Why**: These are paradigm-level patterns that work for ANY project.

### What's Project-Specific (Customize)

Standards in `.agent-os/standards/development/`:
- ⚙️ Tool commands (tox vs maven vs npm vs cargo)
- ⚙️ Quality targets (linter scores, coverage thresholds)
- ⚙️ Language patterns (Python GIL, Go goroutines, Rust ownership)
- ⚙️ Project conventions (naming, file organization, etc.)

**Why**: These are implementation details that vary by language/project.

---

## 🚀 Getting Started Examples

### Example 1: Starting New Feature

**User says**: "We need user authentication"

**AI should**:
1. ✅ Check compliance: Search `.agent-os/standards/` for authentication patterns
2. ✅ Pre-task validation: Get current date, verify branch, check state
3. ✅ Discuss design with user
4. ✅ Per-file validation before each file generated
5. ✅ Pre-commit validation: Run quality gates, review with user
6. ✅ Commit following commit protocol

### Example 2: Fixing Bug

**User says**: "Fix the race condition in the tracer"

**AI should**:
1. ✅ Check compliance: Search for race condition standards
2. ✅ Pre-generation validation: Understand current code
3. ✅ Generate fix following established patterns
4. ✅ Add test for race condition
5. ✅ Run quality gates
6. ✅ Commit with user approval

### Example 3: Multi-File Feature

**User says**: "Create a caching layer with Redis (3 files)"

**AI should**:
1. ✅ Pre-task validation ONCE: Clean state, current date, branch
2. ✅ Per-file validation before EACH file:
   - File 1: State clean ✅
   - File 2: State dirty (File 1 uncommitted) ✅ AWARE, not blocking
   - File 3: State dirty (Files 1-2 uncommitted) ✅ AWARE, not blocking
3. ✅ Pre-commit validation ONCE: All quality gates on all 3 files
4. ✅ Commit all 3 files together

---

## 🎯 Success Criteria

AI assistants following these standards should achieve:

- ✅ **85-95% execution consistency** (vs 60-70% without standards)
- ✅ **Zero standard violations** (automated compliance checking)
- ✅ **First-attempt quality** (pre-generation validation prevents issues)
- ✅ **Systematic debugging** (error pattern recognition)
- ✅ **Professional commits** (structured review process)

---

## 📝 Authorship vs Consumption

### When Working ON Agent OS Enhanced (Authorship Mode)

**You CAN**:
- ✏️ Edit these universal standards
- ✏️ Improve methodology
- ✏️ Add new universal patterns
- ✏️ Create examples in `universal/examples/`

### When Using Agent OS Enhanced (Consumption Mode)

**You SHOULD**:
- 📖 Read standards from `.agent-os/standards/ai-assistant/` (copied from here)
- ⚙️ Create project-specific standards in `.agent-os/standards/development/`
- 📚 Reference examples from `universal/examples/[language]/` (if available)
- ❌ NOT edit universal standards directly (they'll be overwritten on upgrade)

---

## 🔗 Related Resources

### Universal Standards (Copied to All Projects)
- **Concurrency**: `.agent-os/standards/universal/concurrency/` - Race conditions, deadlocks, locking
- **Testing**: `.agent-os/standards/universal/testing/` - Test pyramid, test doubles, property-based testing
- **Architecture**: `.agent-os/standards/universal/architecture/` - SOLID, dependency injection, API design
- **Failure Modes**: `.agent-os/standards/universal/failure-modes/` - Graceful degradation, circuit breakers

### Project-Specific Standards (Created by Project)
- **Code Quality**: `.agent-os/standards/development/code-quality.md` - Tool requirements
- **Testing Standards**: `.agent-os/standards/development/testing-standards.md` - Test patterns
- **Architecture**: `.agent-os/standards/development/architecture.md` - Project architecture

### Workflows (Phase-Gated)
- **Spec Creation**: `.agent-os/workflows/spec_creation_v1/` - Systematic spec creation
- **Spec Execution**: `.agent-os/workflows/spec_execution_v1/` - Implementation workflow

---

## ❓ FAQ

### Q: Why separate universal from project-specific?

**A**: Universal standards work for ANY language/project (Python, JavaScript, Rust, etc.). Project-specific standards adapt the universal patterns to your specific tools and conventions.

### Q: Can I modify these universal standards for my project?

**A**: No - these will be overwritten on Agent OS upgrades. Instead, create project-specific extensions in `.agent-os/standards/development/` that reference these universal standards.

### Q: What if my project doesn't have quick-reference.md or error-patterns.md?

**A**: These are optional. Start with the mandatory standards (compliance, validation, commit). Add project-specific standards as you discover useful patterns.

### Q: How do I know if AI is following these standards?

**A**: AI should explicitly mention compliance checking, validation steps, and quality gates. If not, remind AI: "Please follow the AI assistant standards from `.agent-os/standards/ai-assistant/`"

---

**This is a universal standard. It applies to all projects using Agent OS Enhanced, regardless of programming language or technology stack.**

**For project-specific implementations, see `.agent-os/standards/development/` in your project.**

