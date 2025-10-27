# Session History Analysis - Development Standard

**Last Updated:** 2025-10-14  
**Status:** Active  
**Category:** Development / Meta-Analysis

---

## 🎯 TL;DR - Session History Analysis Quick Reference

**Keywords for search**: session history analysis, AI collaboration analysis, conversation history, partnership metrics, Cursor session analysis, Cline task analysis, SQLite database, composer data, collaboration patterns, how to analyze AI sessions

**Core Principle:** Analyzing session history provides empirical evidence of AI-human collaboration patterns, enabling meta-learning and validation of operating models.

**When to Analyze Session History:**
- ✅ Understanding how collaboration evolved over time
- ✅ Validating partnership operating models
- ✅ Identifying patterns in AI-human work distribution
- ✅ Measuring effectiveness of workflows and standards
- ✅ Creating evidence-based collaboration documentation
- ❌ NOT for debugging individual sessions (use logs)
- ❌ NOT for real-time monitoring (use metrics)

**Quick Analysis Process:**
1. Locate session storage (Cursor: state.vscdb, Cline: tasks/)
2. Extract metadata (timestamps, lines changed, topics)
3. Aggregate statistics (sessions, phases, patterns)
4. Analyze collaboration dynamics
5. Document insights

**Key Storage Locations:**
- **Cursor Composer:** `~/Library/Application Support/Cursor/User/workspaceStorage/{workspace-id}/state.vscdb`
- **Cline Tasks:** `~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/tasks/`

**When to Query This Standard:**
- `search_standards("how to analyze session history")`
- `search_standards("AI collaboration metrics")`
- `search_standards("Cursor conversation analysis")`

---

## 🎯 Purpose

Define systematic methodology for analyzing AI agent session history to understand collaboration patterns, validate operating models, and create evidence-based documentation of AI-human partnerships.

This standard enables meta-analysis of the development process itself, turning session data into actionable insights about what works in AI-human collaboration.

---

## ❓ Questions This Answers

1. "How do I analyze Cursor AI session history?"
2. "Where is Cursor conversation data stored?"
3. "How do I analyze Cline task history?"
4. "What metrics should I track for AI collaboration?"
5. "How do I measure partnership effectiveness?"
6. "Where are Cursor sessions stored on macOS?"
7. "How do I extract collaboration statistics?"
8. "What patterns should I look for in session data?"
9. "How do I validate an AI operating model?"
10. "How do I create evidence-based collaboration docs?"

---

## 📋 The Problem

**Without systematic session history analysis:**

- ❌ Collaboration patterns remain anecdotal
- ❌ Operating model effectiveness is unproven
- ❌ Team learnings stay tacit, not codified
- ❌ Partnership dynamics are invisible
- ❌ Quality improvements lack data foundation
- ❌ Meta-learning opportunities are missed

**Example failure:**
> Team: "Our AI partnership is working great!"  
> Reality: No data to prove it, can't replicate success, patterns unclear

**With systematic analysis:**

- ✅ Empirical evidence of what works
- ✅ Quantifiable collaboration metrics
- ✅ Documented patterns for replication
- ✅ Data-driven process improvements
- ✅ Validated operating models

---

## 📊 The Standard

### Step 1: Locate Session Storage

**Cursor Composer Storage:**

```bash
# Find workspace ID
cd ~/Library/Application\ Support/Cursor/User/workspaceStorage/
ls -la | grep $(basename $(pwd))

# Common location pattern
~/Library/Application\ Support/Cursor/User/workspaceStorage/{workspace-hash}/state.vscdb
```

**Cline Task Storage:**

```bash
~/Library/Application\ Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/tasks/
```

**Verification:**
- [ ] Located workspace-specific storage directory
- [ ] Verified state.vscdb exists (Cursor)
- [ ] Found task directories (Cline)
- [ ] Confirmed workspace matches project

### Step 2: Extract Metadata

**For Cursor (SQLite):**

```bash
# Extract composer metadata
sqlite3 "path/to/state.vscdb" "SELECT value FROM ItemTable WHERE key = 'composer.composerData';" | python3 -m json.tool

# Key fields to extract:
# - composerId: Unique session identifier
# - name: Session description
# - createdAt: Start timestamp (ms)
# - lastUpdatedAt: End timestamp (ms)
# - totalLinesAdded: Code additions
# - totalLinesRemoved: Code deletions
# - subtitle: Files modified
# - contextUsagePercent: Context utilization
```

**For Cline (JSON files):**

```bash
# Extract task metadata
cat ~/Library/Application\ Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/tasks/*/task_metadata.json

# Key fields:
# - files_in_context: Files read/edited
# - model_usage: AI model used
# - cline_read_date: When files accessed
# - cline_edit_date: When files modified
```

**Checklist:**
- [ ] Extracted all session timestamps
- [ ] Gathered lines added/removed per session
- [ ] Collected file modification data
- [ ] Retrieved session names/descriptions
- [ ] Noted context usage patterns

### Step 3: Aggregate Statistics

**Calculate Core Metrics:**

```python
# Session volume
total_sessions = len(all_sessions)
date_range = (earliest_session, latest_session)
sessions_per_day = total_sessions / days_active

# Code contribution
total_lines_added = sum(s['totalLinesAdded'] for s in sessions)
total_lines_removed = sum(s['totalLinesRemoved'] for s in sessions)
net_lines = total_lines_added - total_lines_removed

# Work distribution
sessions_by_topic = Counter(extract_topic(s['name']) for s in sessions)
sessions_by_phase = group_by_timeframe(sessions)
```

**Required Metrics:**
- Total sessions (count)
- Date range (first to last)
- Lines added (sum)
- Lines removed (sum)
- Net contribution (added - removed)
- Sessions per day (avg)
- Biggest sessions (top 10)
- Topic distribution (categories)

### Step 4: Analyze Collaboration Patterns

**Identify Phases:**

Look for natural groupings in session activity:

```python
# Example phase detection
def detect_phases(sessions, threshold_days=2):
    phases = []
    current_phase = []
    
    for i, session in enumerate(sorted(sessions, key=lambda s: s['createdAt'])):
        if i == 0:
            current_phase.append(session)
            continue
            
        time_gap = (session['createdAt'] - current_phase[-1]['createdAt']) / 86400000
        
        if time_gap > threshold_days:
            phases.append(current_phase)
            current_phase = [session]
        else:
            current_phase.append(session)
    
    if current_phase:
        phases.append(current_phase)
    
    return phases
```

**Patterns to Extract:**

1. **Work Distribution:**
   - Implementation vs design vs documentation
   - Bug fixes vs new features
   - Planning vs execution

2. **Collaboration Dynamics:**
   - Session length patterns
   - Context switching frequency
   - Iterative refinement cycles

3. **Quality Indicators:**
   - Bug fix session ratio
   - Lines changed per session
   - Test coverage sessions

4. **Effectiveness Measures:**
   - Time from concept to implementation
   - Rework indicators
   - Standards compliance patterns

### Step 5: Document Insights

**Create Analysis Document:**

```markdown
# [Project] Session History Analysis
## AI-Human Collaboration Patterns

**Period:** [start date] - [end date]
**Total Sessions:** [count]
**Net Contribution:** [lines] lines

### Key Phases

[Phase breakdown with narrative]

### Collaboration Patterns

[What worked, what didn't]

### Metrics

[Tables and statistics]

### Insights

[Learnings and recommendations]
```

**Required Sections:**
- [ ] Executive summary with key metrics
- [ ] Phase-by-phase breakdown
- [ ] Collaboration pattern analysis
- [ ] Statistical evidence
- [ ] Actionable insights
- [ ] Lessons learned

---

## ✅ Checklist

Before completing session history analysis:

- [ ] Located all relevant session storage
- [ ] Extracted complete metadata (no missing sessions)
- [ ] Calculated core metrics (sessions, lines, dates)
- [ ] Identified collaboration phases
- [ ] Analyzed work distribution patterns
- [ ] Documented quality indicators
- [ ] Created analysis document
- [ ] Validated findings with examples
- [ ] Generated actionable insights
- [ ] Saved analysis for future reference

---

## 💡 Examples

### Example 1: Cursor Composer Analysis

**Scenario:** Analyzing 67 Cursor sessions over 10 days

**Analysis Process:**

```python
# 1. Extract data
with open('composer_data.json') as f:
    data = json.load(f)
    composers = data['allComposers']

# 2. Calculate metrics
total_lines = sum(c['totalLinesAdded'] for c in composers)
# Result: 353,106 lines added

# 3. Identify phases
phase1 = [c for c in composers if c['createdAt'] < threshold1]
# Result: Foundation phase, 48 sessions, 260K lines

# 4. Extract patterns
documentation_sessions = [c for c in composers if 'doc' in c['name'].lower()]
# Result: 40% of sessions involved documentation

# 5. Generate insights
# Design > Implementation (unusual but effective)
# Query-first reduced bug rate
# Self-dogfooding accelerated development
```

**Output:** [Link to full analysis document]

### Example 2: Cline Task History

**Scenario:** Analyzing 18 Cline tasks for meta-framework work

```python
# Extract from task directories
for task_dir in task_directories:
    with open(f'{task_dir}/api_conversation_history.json') as f:
        conversations = json.load(f)
        
    # Analyze conversation patterns
    topics = extract_topics(conversations)
    tool_usage = count_tool_calls(conversations)
    
    # Track: MCP (496 mentions), RAG (397 mentions), Testing (263 mentions)
```

**Insights:**
- Heavy MCP/RAG focus validated architectural decisions
- Testing mentions (263) showed quality-first approach
- Tool usage patterns revealed workflow effectiveness

### Example 3: Combined Analysis

**Scenario:** Comparing Cursor vs Cline collaboration

```python
cursor_stats = {
    'sessions': 67,
    'lines_added': 353106,
    'avg_per_session': 5270
}

cline_stats = {
    'sessions': 18,
    'total_messages': 1130,
    'user_messages': 567,
    'assistant_messages': 563
}

# Finding: Perfect 50/50 message balance in Cline
# Indicates true collaboration vs assistance
```

---

## ❌ Anti-Patterns

### Anti-Pattern 1: Analysis Without Purpose

**Wrong:**
```python
# Just extracting data without clear goal
sessions = get_all_sessions()
print(f"Total: {len(sessions)}")
# What now?
```

**Why it fails:**
- No insights generated
- Data without narrative
- Wasted analysis effort

**Right:**
```python
# Analysis with specific question
sessions = get_all_sessions()

# Question: Did query-first approach reduce bugs?
bug_fix_sessions = [s for s in sessions if 'fix' in s['name'].lower()]
bug_rate = len(bug_fix_sessions) / len(sessions)
# Result: 7% bug rate (low) validates approach
```

### Anti-Pattern 2: Missing Collaboration Context

**Wrong:**
```
Total Sessions: 67
Lines Added: 353,106
```

**Why it fails:**
- Numbers without story
- No partnership dynamics
- Misses the "how" of collaboration

**Right:**
```markdown
## Collaboration Dynamics

67 sessions over 10 days showed clear trust progression:
- Week 1: Josh tested capabilities with moderate tasks
- Week 2: 40K+ line refactoring given with confidence  
- Week 3: Meta-analysis of our own partnership

Evidence: Session size grew 5x as trust compounded.
```

### Anti-Pattern 3: Ignoring Phase Patterns

**Wrong:**
```python
# Treating all sessions as homogeneous
avg_lines = total_lines / total_sessions
# Ignores that phases had different characteristics
```

**Why it fails:**
- Masks important transitions
- Loses phase-specific insights
- Can't replicate success patterns

**Right:**
```python
# Identify distinct phases
phase1 = foundation_sessions()  # High volume, exploration
phase2 = acceleration_sessions()  # Focused, quality
phase3 = polish_sessions()  # Refinement, meta

# Each phase has different metrics and learnings
```

### Anti-Pattern 4: No Actionable Insights

**Wrong:**
```
Analysis shows we worked hard and created lots of code.
```

**Why it fails:**
- Obvious, not insightful
- Can't improve from this
- Doesn't help future work

**Right:**
```
Key Insight: Query overhead (141 queries in one session) 
prevented bugs - 7% bug rate vs industry 20-30%.

Actionable: Reinforce "query liberally" pattern in onboarding.
Teach new team members to query 5-10 times per task.
```

---

## 🔗 Related Standards

**Query for complete context:**

- `search_standards("RAG content authoring")` - How to document findings
- `search_standards("compliance checking")` - How to validate patterns
- `search_standards("standards creation")` - How to turn insights into standards
- `search_standards("agent decision protocol")` - Understanding AI behavior patterns

**Related documentation:**
- `usage/operating-model.md` - Partnership roles and dynamics
- `standards/ai-assistant/knowledge-compounding-guide.md` - How learnings compound
- `standards/development/agent-os-architecture.md` - System context

---

## 📞 Questions?

**How do I find my Cursor workspace ID?**
→ Look in `.cursor/mcp.json` for workspaceFolder path, then search Application Support

**What if I can't access SQLite database?**
→ Use `sqlite3` command-line tool or Python's sqlite3 library

**How far back does session history go?**
→ Varies by agent. Cursor keeps indefinitely (until manual cleanup), Cline may prune old conversations

**Should I analyze every session?**
→ No. Focus on meaningful periods (sprints, phases, milestones)

**How do I validate my analysis?**
→ Cross-reference with actual deliverables, git history, and qualitative experience

**What if patterns aren't clear?**
→ Try different groupings (time periods, topics, contributors) until natural patterns emerge

---

**This standard emerged from dogfooding: We analyzed our own 85 sessions (67 Cursor + 18 Cline) to understand how prAxIs OS was built. The insights validated our operating model and became this standard.**


