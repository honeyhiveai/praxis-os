# Hybrid Installation Script Design

**Date**: 2025-10-23  
**Status**: Draft - Awaiting Decision  
**Decision Maker**: Josh (Founder)  
**Context**: Enterprise adoption requires bulletproof installation experience

---

## 🎯 Problem Statement

### Current Pain Points

**Installation Today (Pure LLM Approach):**
1. **Unreliable**: LLM must manually copy ~337 files one-by-one or in batches
2. **Slow**: 8-10 minutes for file operations that could take 30 seconds
3. **Unvalidated**: No guaranteed file counts, easy to skip files/directories
4. **Unclear Progress**: User doesn't know what's happening ("Is it still working?")
5. **Token Intensive**: Hundreds of file operations consume thousands of tokens
6. **Hard to Debug**: If something breaks, unclear what was copied vs. skipped

**Why This Matters Now:**
- **Enterprise Adoption**: Companies want fast, reliable, auditable installations
- **Customer Interest**: HoneyHive customers and FAANG contacts evaluating Agent OS Enhanced
- **Trust Building**: Installation is the FIRST interaction - must build trust immediately
- **Scale**: As we go from 10 → 100 → 1000 users, installation reliability becomes critical

### Impact If Not Solved

**Without Improvement:**
- ❌ Slow installations frustrate enterprise users
- ❌ Installation failures damage credibility
- ❌ Support burden increases (helping users debug failed installs)
- ❌ Lost customers (if installation fails, they don't try again)
- ❌ No competitive advantage (Cursor/Cline install instantly)

**With Improvement:**
- ✅ Fast installations (30 sec mechanical + 3-5 min intelligent tasks)
- ✅ Reliable installations (guaranteed file operations)
- ✅ Trust building (transparent progress, validation)
- ✅ Competitive advantage (fastest agentic framework to install)
- ✅ Enterprise ready (auditable, reproducible)

### Scope Boundaries

**In Scope:**
- Script for mechanical file operations (clone, copy, validate)
- LLM instructions for intelligent tasks (language detection, standards generation, venv setup)
- Progress reporting standards
- Validation and error handling

**Out of Scope:**
- Complete replacement of installation guides (keep as fallback/manual option)
- GUI installer or web-based installation
- Automatic language detection in script (LLM handles this)
- Package manager integration (pip install agent-os-enhanced comes later)

### Success Looks Like

**User Experience:**
```
User: "Install Agent OS Enhanced"

LLM: "I'll use the fast installer script..."
[30 seconds: Script clones, copies 337 files, validates]
✓ Mechanical installation complete (337 files)

[3-5 minutes: LLM handles intelligent tasks]
✓ Detected Python project (FastAPI + pytest)
✓ Generated 5 language-specific standards
✓ Created venv + installed 4 dependencies
✓ Configured Cursor (dual transport)
✓ Built RAG index (450 chunks)

✅ Installation complete! (Total: ~5 minutes)
```

**Metrics:**
- Installation time: 8-10 min → 5-6 min (30-40% faster)
- Reliability: ~85% success → 99% success
- User confidence: "Did it work?" → "I watched it work"

---

## 🎯 Goals & Non-Goals

### Goals (In Scope)

1. **Reduce installation time by 30-40%**
   - Mechanical operations: 8-10 min → 30 sec
   - Total: 8-10 min → 5-6 min

2. **Increase installation reliability to 99%**
   - Guaranteed file operations (no partial copies)
   - Automatic validation (file counts, checksums)
   - Automatic cleanup (temp directories)

3. **Build trust through transparency**
   - Clear progress reporting (Step X/Y: Task)
   - Validation checkpoints (✓ 337 files copied)
   - Explicit handoff (Script → LLM tasks)

4. **Maintain flexibility**
   - Keep manual installation path (airgapped, debugging)
   - Allow customization (skip steps, resume)
   - Support all platforms (macOS, Linux, Windows)

5. **Enable enterprise adoption**
   - Auditable (script code reviewable)
   - Reproducible (same script = same result)
   - Documented (design doc, installation guide)

### Non-Goals (Out of Scope)

1. **Complete automation** - LLM still handles intelligent tasks (language detection, standards generation)
2. **GUI installer** - Command-line script is sufficient
3. **Package manager** - `pip install agent-os-enhanced` is future work
4. **Deprecate manual install** - Keep guides as fallback
5. **Auto-update** - Upgrade workflow handles updates, not installation script
6. **Custom IDE support** - Focus on Cursor, expand later

---

## 📊 Current State Analysis

### What Exists Today

**Installation Guides (installation/*.md):**
```
00-START.md           Clone to /tmp
01-directories.md     Create 8 directories
02-copy-files.md      Copy ~337 files
03-cursorrules.md     Merge .cursorrules
04-gitignore.md       Configure .gitignore
05-venv-mcp.md        Create venv, install deps, build RAG
06-validate.md        Validate + cleanup
```

**Design Philosophy:**
- **Horizontally scaled** - Each file ~200-250 lines (vanilla LLM attention span)
- **Sequential** - Chain navigation (explicit "Next Step")
- **Validated** - Checkpoints after each step
- **Bootstrapping-friendly** - Works before MCP server exists

### What Works Well (Keep This)

✅ **Clear sequencing** - Step-by-step chain prevents skipping
✅ **Validation checkpoints** - Each step has validation
✅ **Critical mistakes upfront** - Common errors listed early
✅ **Works for vanilla LLMs** - No advanced capabilities required
✅ **Complete manual fallback** - If automation fails, guides still work

### What's Broken (Fix This)

❌ **Speed** - LLM copying files takes 8-10 minutes
❌ **Reliability** - LLM might skip files, forget validation
❌ **Progress visibility** - User doesn't see what's happening
❌ **Token cost** - Hundreds of file operations = high token usage
❌ **Debugging** - Hard to tell what was copied vs. skipped

### What's Missing (Add This)

🆕 **Fast path** - Script for mechanical operations
🆕 **Progress reporting** - Real-time feedback to user
🆕 **Guaranteed validation** - Automatic file counts, checksums
🆕 **Error recovery** - Rollback on failure, resume capability
🆕 **Trust building** - Transparent, auditable, reproducible

### Metrics/Data Supporting Need

**Current Installation Performance:**
- Time: 8-10 minutes average
- Success rate: ~85% (based on Discord reports, dogfooding)
- Token usage: 3,000-5,000 tokens (file operations)
- User questions: "Did it finish?", "How many files?", "Is it working?"

**Potential With Script:**
- Time: 5-6 minutes (30 sec script + 5 min LLM tasks)
- Success rate: 99% (file operations guaranteed)
- Token usage: 1,000-1,500 tokens (LLM only does intelligent tasks)
- User confidence: High (sees progress, validation)

---

## 🏗️ Proposed Design

### Architecture: Hybrid Approach

```
┌─────────────────────────────────────────────────────────────┐
│ USER: "Install Agent OS Enhanced"                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │ LLM Decision:          │
        │ Fast or Guided?        │
        └───────────┬─────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌───────────────┐      ┌────────────────┐
│  FAST PATH    │      │  GUIDED PATH   │
│  (Script)     │      │  (Manual)      │
└───────┬───────┘      └────────┬───────┘
        │                       │
        ▼                       ▼
┌───────────────────────────────────────┐
│ SCRIPT PHASE (Fast Path Only)        │
│ • Clone to /tmp                       │
│ • Create 8 directories                │
│ • Copy 337 files                      │
│ • Validate (file counts, structure)   │
│ • Cleanup temp directory              │
│ Time: 30 seconds                      │
└───────────────┬───────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│ LLM PHASE (Both Paths)                │
│ • Detect project language             │
│ • Generate language standards         │
│ • Merge .cursorrules (if exists)      │
│ • Create venv + install dependencies  │
│ • Configure .cursor/mcp.json          │
│ • Build RAG index                     │
│ • Validate installation               │
│ Time: 3-5 minutes                     │
└───────────────┬───────────────────────┘
                │
                ▼
        ┌───────────────┐
        │ ✅ COMPLETE   │
        └───────────────┘
```

### Key Components

#### 1. Installation Script (`scripts/install-agent-os.py`)

**Requirements:**
- ✅ **Stdlib only** - No external dependencies
- ✅ **Cross-platform** - macOS, Linux, Windows
- ✅ **Fast** - <30 seconds for all file operations
- ✅ **Validated** - Built-in checks (file counts, structure)
- ✅ **Progress reporting** - Print each step with ✓/✗
- ✅ **Error handling** - Clear messages, automatic cleanup
- ✅ **Auditable** - Readable code, comments

**Core Functions:**
```python
def check_prerequisites()      # git, Python 3.9+
def clone_repo(temp_dir)       # Clone to /tmp
def create_directories(target) # Create .praxis-os/* structure
def copy_files(source, target) # Copy standards/workflows/mcp_server
def validate_installation()     # Check file counts, structure
def cleanup_temp(temp_dir)     # Remove cloned repo
def print_next_steps()         # What LLM should do next
```

**Output Example:**
```
Agent OS Enhanced Installer v1.0.0

Step 1/4: Checking prerequisites
✓ Git detected
✓ Python 3.11.5 detected
✓ 8.4GB disk space available

Step 2/4: Cloning repository
✓ Cloned to /tmp/agent-os-install-abc123

Step 3/4: Copying files
✓ Standards: 231 files
✓ Workflows: 47 files
✓ Usage: 12 files
✓ MCP Server: 47 files
✓ Total: 337 files copied

Step 4/4: Validating installation
✓ All directories exist
✓ Workflows: 47 files (expected 40+)
✓ MCP Server: 47 Python files
✓ Temp directory cleaned up

✅ Mechanical installation complete!

Next steps (for LLM):
1. Detect project language
2. Generate language-specific standards
3. Merge .cursorrules (if exists)
4. Create venv + install dependencies
5. Configure .cursor/mcp.json
6. Build RAG index
7. Validate installation

Estimated time: 3-5 minutes
```

#### 2. LLM Post-Script Guide (`installation/POST-SCRIPT-TASKS.md`)

**Purpose:** Explicit instructions for what LLM does after script completes

**Structure:**
```markdown
# Post-Script Installation Tasks

The mechanical installation (script) is complete. You now handle:

## Task 1: Detect Project Language
[Instructions...]

## Task 2: Generate Language-Specific Standards
[Instructions...]

## Task 3: Merge .cursorrules
[Instructions...]

[... etc ...]
```

#### 3. Updated Installation Docs

**Update `installation/00-START.md`:**
```markdown
## Installation Paths

### Path 1: Fast Installation (Recommended)
Download and run the installation script:
- Time: ~5 minutes total
- Requires: Internet connection, git, Python 3.9+

### Path 2: Guided Installation (Manual)
Follow the step-by-step guides:
- Time: ~8-10 minutes total
- Use for: Airgapped environments, debugging, learning
```

### Data Flow

**Fast Path:**
```
User → LLM → Download script → Run script →
Script output (337 files) → LLM continues →
Complete installation
```

**Guided Path:**
```
User → LLM → Read 00-START.md → Follow guides →
Manual file operations → LLM continues →
Complete installation
```

### Integration Points

**With Existing System:**
- ✅ **Installation guides** - Keep as fallback (Path 2)
- ✅ **Upgrade workflow** - Separate workflow, not affected
- ✅ **MCP server** - Script just copies code, LLM installs deps
- ✅ **RAG index** - LLM builds after script completes

**With Future Features:**
- 🔮 **Package manager** - Script becomes fallback for edge cases
- 🔮 **GUI installer** - Script becomes backend for GUI
- 🔮 **CI/CD** - Script enables automated testing

---

## 🔄 Options Considered

### Option 1: Pure Script (Fully Automated) ❌

**Approach:** Script handles EVERYTHING (clone, copy, detect language, generate standards, create venv, build RAG, configure Cursor)

**Pros:**
- ✅ Fastest possible (3-4 minutes total)
- ✅ Most reliable (no LLM involvement)
- ✅ Lowest token cost (script does all work)

**Cons:**
- ❌ Can't adapt to project context (language detection brittle)
- ❌ Can't merge .cursorrules intelligently (needs LLM context)
- ❌ Misses the point - Agent OS is about AI-enhanced development
- ❌ Complex script maintenance (language templates, etc.)
- ❌ No trust building - user doesn't see AI working

**Why Rejected:**
This defeats the purpose of Agent OS Enhanced. We WANT the LLM to be involved in intelligent tasks (language detection, standards generation). The script should only handle mechanical operations.

### Option 2: Hybrid Script + LLM (Proposed) ✅

**Approach:** Script handles mechanical operations (clone, copy, validate), LLM handles intelligent tasks (language detection, standards generation, venv, RAG, configuration)

**Pros:**
- ✅ Fast (30 sec script + 3-5 min LLM)
- ✅ Reliable file operations (guaranteed by script)
- ✅ Intelligent customization (LLM detects language, generates standards)
- ✅ Trust building (user sees both automation and intelligence)
- ✅ Simple script (just file operations)
- ✅ Maintains flexibility (LLM can adapt to project context)

**Cons:**
- ⚠️ Two systems to maintain (script + guides)
- ⚠️ More complex handoff (script → LLM)

**Why Recommended:**
Perfect balance. Script does what it's good at (fast, reliable file ops). LLM does what it's good at (context-aware, adaptive intelligence). User sees both working together.

### Option 3: Enhanced Guides Only ❌

**Approach:** Keep current approach, just improve guides with better progress reporting and validation

**Pros:**
- ✅ Simple (single system)
- ✅ Works today (proven approach)
- ✅ No new code to maintain

**Cons:**
- ❌ Still slow (8-10 minutes)
- ❌ Still unreliable (LLM might skip steps)
- ❌ Still high token cost
- ❌ Doesn't solve enterprise adoption concerns

**Why Rejected:**
Incremental improvement, but doesn't solve core problems (speed, reliability). Not competitive with enterprise expectations.

### Recommendation: Option 2 (Hybrid Script + LLM)

**Rationale:**
- Solves speed problem (30 sec for mechanical ops)
- Solves reliability problem (script guarantees file ops)
- Maintains intelligent customization (LLM does adaptive tasks)
- Builds trust (transparent, auditable)
- Simple to maintain (script is ~300 lines of stdlib Python)
- Keeps fallback (guided path still works)

---

## ⚠️ Risks & Mitigations

### Risk 1: Script Maintenance Burden
**Probability:** Medium  
**Impact:** Medium  
**Description:** Script becomes complex over time, hard to maintain

**Mitigation:**
- Keep script simple (stdlib only, ~300 lines)
- Clear function boundaries (one function = one task)
- Comprehensive comments
- Unit tests for critical functions

**Contingency:**
If script becomes unmaintainable, deprecate and fall back to guided path

### Risk 2: Platform Compatibility
**Probability:** Medium  
**Impact:** High  
**Description:** Script breaks on Windows, specific Linux distros, etc.

**Mitigation:**
- Use Python stdlib (Path, shutil, subprocess work everywhere)
- Test on macOS, Ubuntu, Windows
- Clear error messages with platform-specific remediation
- Fallback to guided path if script fails

**Contingency:**
Document known platform issues, maintain guided path as universal fallback

### Risk 3: User Distrust of Script
**Probability:** Low  
**Impact:** Medium  
**Description:** Users don't trust downloading/running script from internet

**Mitigation:**
- Script is auditable (readable Python, no obfuscation)
- Hosted on GitHub (public, reviewable)
- Clear documentation (what it does, why)
- Optional (guided path always available)

**Contingency:**
Emphasize guided path for security-conscious users

### Risk 4: Script + Guide Divergence
**Probability:** High  
**Impact:** Medium  
**Description:** Script and guides fall out of sync, confusing users

**Mitigation:**
- Single source of truth (repo structure)
- Script validates against structure (not hardcoded expectations)
- Update both when structure changes
- CI tests for both paths

**Contingency:**
If divergence detected, priority fix before next release

### Risk 5: LLM Doesn't Use Script
**Probability:** Low  
**Impact:** High  
**Description:** LLM doesn't know about script, always uses guided path

**Mitigation:**
- Clear documentation in installation guides
- .cursorrules mention script option
- Standard for "fast install" triggers script path

**Contingency:**
If LLMs ignore script, make it more explicit in docs/cursorrules

---

## ❓ Open Questions

### Question 1: Should script be fast path or default path?
**Context:** Users say "Install Agent OS Enhanced" - which path should LLM choose?

**Options:**
- **A:** Script is default, guided is fallback ("unless you want manual control")
- **B:** Guided is default, script is opt-in ("install using fast installer")
- **C:** LLM decides based on context (airgapped = guided, normal = script)

**Recommendation:** **Option A** - Script is default for best first impression

**Decision Needed By:** Before implementation  
**Decision Maker:** Josh

---

### Question 2: Should script live in repo or be downloadable?
**Context:** Where should install-agent-os.py live?

**Options:**
- **A:** In repo (`scripts/install-agent-os.py`) - LLM downloads repo, runs script
- **B:** Separate URL (`curl https://.../install.py | python`) - Like Homebrew
- **C:** Both - Repo for development, URL for production

**Recommendation:** **Option A** - Simpler, more transparent (script is versioned with repo)

**Decision Needed By:** Before implementation  
**Decision Maker:** Josh

---

### Question 3: Should we support resume/partial install?
**Context:** If script fails at Step 3, should user be able to resume from Step 3?

**Options:**
- **A:** No resume - script is atomic (all or nothing, rollback on failure)
- **B:** Resume supported - script checks what's already installed, skips steps
- **C:** Manual resume - LLM can re-run script with flags (`--skip-clone`, etc.)

**Recommendation:** **Option A** initially - Keep simple, add resume later if needed

**Decision Needed By:** Before implementation  
**Decision Maker:** Josh

---

## ✅ Success Criteria

### Quantitative Metrics

1. **Installation Time**
   - Current: 8-10 minutes average
   - Target: ≤5-6 minutes (30 sec script + 5 min LLM)
   - Measurement: Dogfooding, user reports

2. **Reliability**
   - Current: ~85% success rate
   - Target: ≥99% success rate
   - Measurement: Error reports, telemetry (if added)

3. **Token Usage**
   - Current: 3,000-5,000 tokens (file operations)
   - Target: 1,000-1,500 tokens (LLM only does intelligent tasks)
   - Measurement: Token counting during dogfooding

4. **User Satisfaction**
   - Current: Mixed (slow, unclear progress)
   - Target: >90% positive feedback
   - Measurement: Discord feedback, GitHub issues

### Qualitative Outcomes

1. **Trust Building**
   - User sees transparent progress
   - User understands what was installed
   - User confident installation succeeded

2. **Enterprise Readiness**
   - Auditable (script code reviewable)
   - Reproducible (same result every time)
   - Documented (design doc, guides)

3. **Competitive Advantage**
   - Faster than manual git clone + copy
   - More reliable than pure LLM approach
   - Better UX than competitors

### Acceptance Criteria

- [ ] Script completes in <30 seconds
- [ ] Script copies all 337 files correctly
- [ ] Script validates installation automatically
- [ ] Script cleans up temp directory
- [ ] LLM completes post-script tasks in 3-5 minutes
- [ ] Total installation time ≤6 minutes
- [ ] Success rate ≥99% in dogfooding
- [ ] Works on macOS, Ubuntu, Windows
- [ ] Guided path still works as fallback
- [ ] Documentation updated for both paths

---

## 📝 File Change Summary

### Files to Create

1. **`scripts/install-agent-os.py`** - Main installation script (~300 lines)
2. **`installation/POST-SCRIPT-TASKS.md`** - LLM guide for post-script tasks
3. **`tests/test_install_script.py`** - Unit tests for script functions

### Files to Modify

1. **`installation/README.md`** - Add fast path documentation
2. **`installation/00-START.md`** - Add fast vs guided path choice
3. **`.cursorrules`** - Mention fast installer option (optional)

### Files to Keep (No Changes)

1. **`installation/01-06-*.md`** - Keep as guided path fallback
2. **`universal/workflows/agent_os_upgrade_v1/`** - Upgrade is separate

---

## 🧪 Testing Approach

### Unit Tests

**Test Script Functions:**
- `test_check_prerequisites()` - Mock git/python checks
- `test_create_directories()` - Verify directory structure
- `test_copy_files()` - Verify file counts, checksums
- `test_validate_installation()` - Verify validation logic
- `test_cleanup_temp()` - Verify temp directory removed

### Integration Tests

**Test End-to-End Flow:**
1. Create fresh test directory
2. Run script
3. Verify:
   - All directories created
   - All files copied
   - File counts match
   - Temp directory cleaned up

**Test Error Conditions:**
1. No git installed → Clear error message
2. Python 3.8 → Version error
3. No internet → Clone fails gracefully
4. Insufficient disk space → Clear error
5. Target directory not empty → Conflict detection

### Dogfooding

**Test in Real Projects:**
1. Agent OS Enhanced (Python, this repo)
2. hive-kube (JavaScript/TypeScript, monorepo)
3. python-sdk (Python, smaller repo)
4. Fresh empty directory
5. Directory with existing .cursorrules

**Platforms:**
- macOS (primary development platform)
- Ubuntu 22.04 (common server environment)
- Windows 11 (if accessible)

---

## 🔮 Future Enhancements (Out of Scope)

### Phase 2: Package Manager Integration
- `pip install agent-os-enhanced` (Python projects)
- `npx agent-os-enhanced` (JavaScript projects)
- Script becomes backend for package installers

### Phase 3: Update Mechanism
- Script can update itself (`install-agent-os.py --update`)
- Check for new versions on GitHub
- Automatic migration of old installations

### Phase 4: Telemetry
- Optional anonymous metrics (with user consent)
- Track installation success/failure rates
- Identify common issues
- Improve reliability over time

### Phase 5: GUI Installer
- Electron/web-based installer
- Visual progress bar
- Configuration options (skip RAG, choose language, etc.)
- Script becomes backend

---

## 📋 Implementation Checklist

### Pre-Implementation
- [ ] **Decision:** Josh approves hybrid approach
- [ ] **Decision:** Fast path is default (vs opt-in)
- [ ] **Decision:** Script lives in repo (vs separate URL)

### Implementation
- [ ] Write `scripts/install-agent-os.py`
- [ ] Test on macOS (primary platform)
- [ ] Test on Ubuntu (secondary platform)
- [ ] Test on Windows (if accessible)
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Dogfood in 3+ projects

### Documentation
- [ ] Update `installation/README.md`
- [ ] Update `installation/00-START.md`
- [ ] Create `installation/POST-SCRIPT-TASKS.md`
- [ ] Update main README (mention fast installer)

### Validation
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Script completes in <30 seconds
- [ ] Total installation ≤6 minutes
- [ ] Works on macOS, Ubuntu, Windows
- [ ] Guided path still works

### Rollout
- [ ] Merge to main branch
- [ ] Tag release (v1.1.0 or similar)
- [ ] Announce in docs
- [ ] Monitor GitHub issues for feedback

---

## 🎯 Key Takeaways

1. **Hybrid approach is best** - Script for mechanical ops, LLM for intelligent tasks
2. **Speed matters** - 30 sec script vs 8-10 min manual is huge win
3. **Reliability matters** - Guaranteed file ops build trust
4. **Keep fallback** - Guided path for airgapped, debugging, learning
5. **Trust building** - Transparent, auditable, reproducible
6. **Enterprise ready** - Fast, reliable, documented

---

**Next Step:** Josh decides on open questions, then implement via spec workflow.

**Estimated Effort:** 
- Script development: 2-3 hours
- Testing: 1-2 hours
- Documentation: 1 hour
- Total: 4-6 hours

**ROI:**
- Saves 3-4 minutes per installation
- At 100 installations: 5-6 hours saved (break even)
- At 1000 installations: 50-60 hours saved
- Plus: reliability, trust, enterprise readiness

---

**Version**: 1.0  
**Created**: 2025-10-23  
**Author**: AI Assistant (Claude Sonnet 4.5) + Josh  
**Status**: Awaiting approval

