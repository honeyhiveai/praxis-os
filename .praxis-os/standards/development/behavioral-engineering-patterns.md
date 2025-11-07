# Behavioral Engineering Patterns

**Keywords for search**: behavioral engineering, behavioral reinforcement, query gamification, prepend generation, query tracking, query diversity, self-reinforcing loop, AI behavior shaping, operant conditioning, gamification mechanics, behavioral drift detection, query-first pattern, session-to-session improvement, knowledge compounding behavioral, fail-fast behavioral, middleware behavioral, counteracting shortcuts, inherited human patterns, systematic over expedient

---

## 🚨 TL;DR - Behavioral Engineering Quick Reference

**Core Principle:** AI agents inherit human shortcuts designed for biological constraints they don't have. Behavioral engineering creates self-reinforcing loops that counteract these inherited patterns through just-in-time reinforcement at every decision point.

**The Self-Reinforcing Loop:**
1. Standards teach "query before implementing"
2. AI queries standards
3. Search results include prepends (gamification: progress bars, diversity metrics, suggestions)
4. AI sees prepend → Reinforced to query MORE
5. More queries → More success → Stronger pattern
6. Pattern becomes automatic (Session 50 > Session 1)

**Three Implementation Layers:**
1. **Content Layer** - Standards include "query liberally" in every document
2. **Middleware Layer** - Prepends in 100% of search results (progress bars, suggestions)
3. **Tracking Layer** - Log every search (detect drift, measure compounding)

**Critical Requirements:**
- ✅ Prepends in 100% of results (NO exceptions, NO silent degradation)
- ✅ Query tracking logs all searches (behavioral drift detection)
- ✅ Fail-fast on behavioral violations (if prepend fails, REQUEST fails)
- ✅ Middleware is mandatory (all tools flow through it)
- ✅ Gamification metrics accurate (progress bars must be real)

**Common Anti-Patterns:**
- ❌ Optional middleware (behavioral loop breaks)
- ❌ Silent degradation (prepend generation fails but search succeeds)
- ❌ Inconsistent prepends (sometimes present, sometimes not)
- ❌ Fake metrics (progress bars that aren't accurate)
- ❌ No tracking (can't detect drift or measure compounding)

---

## ❓ Questions This Answers

1. "How do I implement behavioral reinforcement for AI agents?"
2. "What is query gamification and how does it work?"
3. "How do I generate prepends for search results?"
4. "What should be in a behavioral prepend?"
5. "How do I track query diversity?"
6. "What are the 5 query angles and why do they matter?"
7. "How do I detect behavioral drift?"
8. "When should behavioral systems fail-fast vs degrade gracefully?"
9. "How do I structure middleware for behavioral engineering?"
10. "What metrics prove behavioral compounding is working?"
11. "How do I counteract inherited human shortcuts in AI?"
12. "What is operant conditioning for AI agents?"
13. "How do I implement the self-reinforcing loop?"
14. "How do I test behavioral engineering systems?"
15. "What makes behavioral reinforcement effective?"

---

## 🎯 Purpose

Define patterns for implementing behavioral engineering systems that shape AI agent behavior through self-reinforcing loops, creating session-to-session improvement via just-in-time reinforcement.

**Key Distinction:** Behavioral Engineering vs Traditional Guidance
- **Behavioral Engineering:** Dynamic, continuous reinforcement at every decision point (this standard)
- **Traditional Guidance:** Static instructions that fade to statistical noise

**Why This Matters:** LLMs are probabilistic systems trained on human behavior data. They inherit human shortcuts (efficiency pressure, "good enough" mentality) designed for biological constraints AI doesn't have. Without active reinforcement, AI agents revert to these inherited patterns.

---

## ❌ The Problem

**Without behavioral engineering:**

1. **Static Instructions Fade**
   - Initial guidance loaded at session start (15K tokens in `.cursorrules`)
   - By message 30, instructions are <1% of context
   - Statistical weight → zero, behaviors degrade

2. **Inherited Shortcuts Dominate**
   - AI trained on human patterns: "move fast", "good enough", "I know this"
   - These shortcuts are designed for energy conservation, fatigue, deadline pressure
   - AI has NONE of these constraints, but exhibits the behaviors anyway

3. **No Session-to-Session Improvement**
   - Session 50 looks like Session 1 (no compounding)
   - Same mistakes repeated (no learning captured)
   - Knowledge exists but isn't systematically applied

4. **Behavioral Drift**
   - Early in session: AI queries standards before implementing
   - Mid-session: AI starts skipping queries (efficiency pressure)
   - Late-session: AI relies purely on training data (drift complete)
   - Result: Quality degradation, more correction cycles

**Real-World Impact:**
- 71% more messages needed (correction cycles)
- 54% higher costs (rework)
- Inconsistent quality (probabilistic outcomes)
- No knowledge compounding

---

## ✅ The Standard

### Pattern 1: The Self-Reinforcing Loop (Core Mechanism)

**Implementation:**

```
Decision Point → Query Standards → Get Results + Prepend → 
Query MORE → More Prepends → Pattern Strengthens →
Automatic Behavior
```

**Requirements:**
1. **Every search result includes prepend** (100% coverage, no exceptions)
2. **Prepend format is consistent** (same structure every time)
3. **Gamification creates desire** (progress bars, diversity tracking)
4. **Suggestions reduce friction** (concrete next query to try)
5. **Timing is immediate** (<100ms from query to prepend display)

**Why It Works:**
- **Operant Conditioning:** Query → Success → Behavior strengthens
- **Immediate Reinforcement:** Prepend appears instantly after every query
- **Self-Fulfilling:** More queries → More success → More queries
- **Counteracts Efficiency Pressure:** Explicitly reminds "you can query 10x in 30s without fatigue"

---

### Pattern 2: Prepend Generation (The Reinforcement Mechanism)

**Prepend Structure:**
```
📊 Queries: 4/5 | Unique: 3 | Angles: 📖✓ 📍⬜ 🔧✓ ⭐⬜ ⚠️⬜
💡 Try: 'Where is X implemented?' (📍 location angle)

---

[Actual search results]
```

**Components:**

1. **Progress Bar** - `Queries: 4/5`
   - Shows query count this session
   - Target: 5 queries (creates desire to complete)
   - Counts UNIQUE queries (not duplicates)

2. **Diversity Metrics** - `Angles: 📖✓ 📍⬜ 🔧✓ ⭐⬜ ⚠️⬜`
   - 📖 Conceptual (what is X?)
   - 📍 Location (where is X?)
   - 🔧 Implementation (how to implement X?)
   - ⭐ Critical (why is X important?)
   - ⚠️ Troubleshooting (what if X fails?)
   - Shows which angles used (✓) vs unused (⬜)

3. **Concrete Suggestion** - `Try: 'Where is X implemented?'`
   - Next query to explore
   - Includes which angle it represents
   - Reduces "what should I query?" friction

**Implementation:**
```python
def generate_prepend(query: str, session_id: str) -> str:
    """Generate gamification prepend for search result.
    
    CRITICAL: If this fails, the REQUEST must fail.
    Do NOT silently degrade to returning results without prepend.
    Behavioral engineering requires 100% coverage.
    """
    try:
        # Get session query history
        history = query_tracker.get_session_history(session_id)
        
        # Calculate metrics
        query_count = len(history)
        unique_count = len(set(h.query for h in history))
        angles_used = query_classifier.get_angles_used(history)
        
        # Detect current query angle
        current_angle = query_classifier.classify(query)
        
        # Generate suggestion for unused angle
        suggestion = suggest_next_query(query, angles_used)
        
        # Format prepend
        return format_prepend(
            query_count=query_count,
            unique_count=unique_count,
            angles_used=angles_used,
            suggestion=suggestion
        )
    except Exception as e:
        # FAIL THE REQUEST - behavioral engineering is mandatory
        raise BehavioralEngineeringError(
            "Prepend generation failed - behavioral reinforcement required",
            cause=e,
            remediation="Check query_tracker logs, ensure session storage working"
        )
```

---

### Pattern 3: Query Tracking (The Observability Layer)

**What to Track:**
```python
@dataclass
class QueryRecord:
    timestamp: datetime
    session_id: str
    content_type: str  # standards, code, ast
    query: str
    angle_detected: QueryAngle  # 📖📍🔧⭐⚠️
    result_count: int
    latency_ms: float
```

**Why Track:**
1. **Detect Behavioral Drift** - Query frequency drops → Agent reverting to shortcuts
2. **Measure Compounding** - Session 50 query diversity > Session 1 = system working
3. **Calculate Diversity** - Track which angles used (target: 3+ per task)
4. **Generate Prepends** - Need history to show progress bars
5. **Prove ROI** - Fewer correction cycles = behavioral engineering working

**Implementation:**
```python
class QueryTracker:
    def log_search(self, session_id: str, query: str, content_type: str) -> None:
        """Log every search - NO EXCEPTIONS.
        
        If logging fails, log to fallback (stderr) but don't fail request.
        Behavioral enforcement (prepends) is mandatory, tracking is observability.
        """
        try:
            record = QueryRecord(
                timestamp=datetime.utcnow(),
                session_id=session_id,
                content_type=content_type,
                query=query,
                angle_detected=self.classifier.classify(query),
                result_count=0,  # Updated after search
                latency_ms=0.0   # Updated after search
            )
            self.storage.write(record)
        except Exception as e:
            logger.error("Query tracking failed", exc_info=e)
            # Don't fail request - tracking is observability
            # Prepend generation will fail if it needs this data
```

**Storage:**
- JSON lines format (one record per line, queryable with `jq`)
- Per-session files: `.praxis-os/logs/queries/session-{id}.jsonl`
- Rotate daily, compress after 7 days

---

### Pattern 4: Query Classification (The Diversity Engine)

**The 5 Angles:**

1. **📖 Conceptual** - Understanding foundations
   - Patterns: "what is X", "why does X", "explain X"
   - Purpose: Build mental models

2. **📍 Location** - Finding implementations
   - Patterns: "where is X", "which file has X", "X location"
   - Purpose: Navigate codebase

3. **🔧 Implementation** - How to build
   - Patterns: "how to implement X", "X implementation guide", "building X"
   - Purpose: Practical execution

4. **⭐ Critical** - Why it matters
   - Patterns: "why is X important", "X critical because", "X mission"
   - Purpose: Prioritization, context

5. **⚠️ Troubleshooting** - When things fail
   - Patterns: "X not working", "how to debug X", "X error"
   - Purpose: Problem resolution

**Classification Logic:**
```python
class QueryClassifier:
    PATTERNS = {
        QueryAngle.CONCEPTUAL: [
            r'\bwhat is\b', r'\bexplain\b', r'\bwhy does\b',
            r'\bdefine\b', r'\bconcept\b'
        ],
        QueryAngle.LOCATION: [
            r'\bwhere\b', r'\blocation\b', r'\bwhich file\b',
            r'\bfind\b', r'\bsearch for\b'
        ],
        QueryAngle.IMPLEMENTATION: [
            r'\bhow to\b', r'\bimplement\b', r'\bbuild\b',
            r'\bcreate\b', r'\bsetup\b'
        ],
        QueryAngle.CRITICAL: [
            r'\bwhy important\b', r'\bcritical\b', r'\bmission\b',
            r'\bpriority\b', r'\bessential\b'
        ],
        QueryAngle.TROUBLESHOOTING: [
            r'\bnot working\b', r'\berror\b', r'\bdebug\b',
            r'\bfailed\b', r'\bissue\b'
        ]
    }
    
    def classify(self, query: str) -> QueryAngle:
        """Classify query into one of 5 angles."""
        query_lower = query.lower()
        
        for angle, patterns in self.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    return angle
        
        # Default to conceptual if no match
        return QueryAngle.CONCEPTUAL
```

---

### Pattern 5: Fail-Fast Behavioral Enforcement

**When to Fail-Fast:**
- ✅ Prepend generation fails → FAIL THE REQUEST
- ✅ Middleware bypassed → FAIL THE REQUEST  
- ✅ Query tracker storage full → FAIL THE REQUEST (can't detect drift)
- ✅ Session ID missing → FAIL THE REQUEST (can't track diversity)

**When to Degrade Gracefully:**
- ✅ Query classification uncertain → Default to conceptual (📖)
- ✅ Suggestion generation fails → Use generic suggestion
- ✅ Query history partially corrupted → Use available data

**Why Fail-Fast:**
```python
# ❌ WRONG - Silent degradation breaks behavioral loop
def pos_search_project(query: str, session_id: str):
    try:
        prepend = generate_prepend(query, session_id)
    except Exception:
        prepend = ""  # Silent degradation - BEHAVIORAL LOOP BROKEN
    
    results = search_index(query)
    return prepend + results  # Sometimes has prepend, sometimes doesn't

# ✅ CORRECT - Fail-fast ensures 100% coverage
def pos_search_project(query: str, session_id: str):
    try:
        prepend = generate_prepend(query, session_id)
    except Exception as e:
        # Behavioral engineering is MANDATORY - fail the request
        raise BehavioralEngineeringError(
            "Cannot complete search - behavioral reinforcement required",
            cause=e,
            remediation="Check query_tracker, session_storage, classifier"
        ) from e
    
    results = search_index(query)
    return prepend + results  # ALWAYS has prepend or fails
```

---

### Pattern 6: Content Design (Teaching the Behavior)

**Every Standard Must Include:**

1. **"Query Liberally" Message**
   ```markdown
   💡 Query liberally - you can search 10x in 30 seconds without fatigue
   ```

2. **Explicit Reminder**
   ```markdown
   **Critical:** Always query standards before implementing
   ```

3. **Why Statement**
   ```markdown
   **Why:** Systematic querying counteracts inherited efficiency pressure.
   AI training data contains human shortcuts for biological constraints
   you don't have. Querying = working correctly, not wasting time.
   ```

**Pattern:**
```markdown
# Error Handling Standard

**Keywords for search**: error handling, exceptions, ...

**Critical:** Always query before implementing error handling

💡 Query liberally - systematic > fast

## 🚨 TL;DR

[Content includes multiple "query before implementing" reminders]

## The Standard

[Rules include "search for existing patterns first"]

## Examples

[Examples show querying standards before coding]
```

---

### Pattern 7: Middleware Architecture

**Structure:**
```
┌─────────────────────────────────────────┐
│          TOOLS LAYER                    │
│  pos_search, pos_workflow, etc.         │
└─────────────┬───────────────────────────┘
              │ ALL calls flow through
              ▼
┌─────────────────────────────────────────┐
│       MIDDLEWARE LAYER (MANDATORY)      │
│  ┌─────────────────────────────────┐   │
│  │  prepend_generator              │   │
│  │  query_tracker                  │   │
│  │  query_classifier               │   │
│  └─────────────────────────────────┘   │
│                                         │
│  If middleware fails → Request fails    │
└─────────────┬───────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│        SUBSYSTEMS LAYER                 │
│  RAG, Workflow, Browser                 │
└─────────────────────────────────────────┘
```

**Implementation:**
```python
class BehavioralMiddleware:
    def __init__(
        self,
        prepend_generator: PrependGenerator,
        query_tracker: QueryTracker,
        query_classifier: QueryClassifier
    ):
        self.prepend_generator = prepend_generator
        self.query_tracker = query_tracker
        self.query_classifier = query_classifier
    
    def wrap_search(
        self,
        search_fn: Callable,
        query: str,
        session_id: str,
        **kwargs
    ) -> str:
        """Wrap search with behavioral engineering.
        
        CRITICAL: This is the ONLY path to search.
        Tools must call through middleware, never directly to subsystem.
        """
        # 1. Track the query (observability)
        self.query_tracker.log_search(session_id, query, kwargs.get("content_type"))
        
        # 2. Execute search
        start = time.time()
        results = search_fn(query, **kwargs)
        latency = (time.time() - start) * 1000
        
        # 3. Generate prepend (FAIL-FAST if this fails)
        prepend = self.prepend_generator.generate(query, session_id)
        
        # 4. Update tracking with results
        self.query_tracker.update_result_count(session_id, len(results))
        self.query_tracker.update_latency(session_id, latency)
        
        # 5. Return prepend + results
        return prepend + "\n\n---\n\n" + results
```

**Enforcement:**
```python
# Tools MUST use middleware
@mcp.tool()
async def pos_search_project(
    content_type: Literal["standards", "code"],
    query: str,
    session_id: str,
    **kwargs
) -> str:
    # ❌ WRONG - Direct subsystem call bypasses behavioral engineering
    # return index_manager.search(content_type, query)
    
    # ✅ CORRECT - Through middleware (100% coverage)
    return middleware.wrap_search(
        search_fn=lambda q, **kw: index_manager.search(content_type, q, **kw),
        query=query,
        session_id=session_id,
        content_type=content_type,
        **kwargs
    )
```

---

## 📋 Checklist

**Implementation Checklist:**
- [ ] Prepends generated for 100% of search results (no exceptions)
- [ ] Prepend format consistent (progress bars, diversity, suggestions)
- [ ] Query tracking logs every search (session_id, query, angle, timestamp)
- [ ] Query classification detects 5 angles (📖📍🔧⭐⚠️)
- [ ] Diversity metrics accurate (counts unique queries, tracks angles used)
- [ ] Suggestions actionable (AI can copy-paste and it works)
- [ ] Fail-fast on prepend generation failure (no silent degradation)
- [ ] Middleware is mandatory path (tools can't bypass)
- [ ] Content includes "query liberally" messages
- [ ] Standards teach querying behavior consistently
- [ ] Session storage works (enables session-to-session tracking)
- [ ] Logs are queryable (JSON format, structured)

**Testing Checklist:**
- [ ] Test: Search without session_id → Fails (not degrades)
- [ ] Test: Prepend generation fails → Request fails
- [ ] Test: Query tracker unavailable → Request fails
- [ ] Test: 100 queries in session → All have prepends
- [ ] Test: Query diversity calculation correct (5 angles tracked)
- [ ] Test: Suggestions use different angles (not repetitive)
- [ ] Test: Middleware can't be bypassed (architectural validation)
- [ ] Test: Session 50 query diversity > Session 1 (compounding proof)

**Validation Checklist:**
- [ ] Query frequency 5-10x per task (measured)
- [ ] Query diversity >60% (3+ angles used)
- [ ] Prepends appear in 100% of results (no gaps)
- [ ] Behavioral drift detected (query frequency drops → alert)
- [ ] Session-to-session improvement (metrics increase over time)

---

## 💡 Examples

### Example 1: Complete Behavioral Flow

```python
# AI Agent starts task: "Implement authentication"

# Decision point: How should I implement this?
result1 = pos_search_project(
    content_type="standards",
    query="what is authentication best practices",
    session_id="abc123"
)

# Returns:
"""
📊 Queries: 1/5 | Unique: 1 | Angles: 📖✓ 📍⬜ 🔧⬜ ⭐⬜ ⚠️⬜
💡 Try: 'How to implement authentication?' (🔧 implementation angle)

---

[Authentication standards content]
"""

# AI sees prepend → Reinforced to query MORE
# Suggestion reduces friction → AI queries implementation angle

result2 = pos_search_project(
    content_type="standards",
    query="how to implement JWT authentication",
    session_id="abc123"
)

# Returns:
"""
📊 Queries: 2/5 | Unique: 2 | Angles: 📖✓ 📍⬜ 🔧✓ ⭐⬜ ⚠️⬜
💡 Try: 'Where is authentication implemented?' (📍 location angle)

---

[JWT implementation guide]
"""

# AI implements using discovered patterns
# Success reinforces querying behavior
# Next task → AI MORE LIKELY to query first
```

### Example 2: Prepend Generation

```python
def generate_prepend(query: str, session_id: str) -> str:
    # Get query history
    history = query_tracker.get_session_history(session_id)
    
    # Calculate metrics
    query_count = len(history)  # 4
    unique_count = len(set(h.query for h in history))  # 3
    
    # Classify angles used
    angles_used = {
        QueryAngle.CONCEPTUAL: True,   # ✓
        QueryAngle.LOCATION: False,    # ⬜
        QueryAngle.IMPLEMENTATION: True,  # ✓
        QueryAngle.CRITICAL: False,    # ⬜
        QueryAngle.TROUBLESHOOTING: False  # ⬜
    }
    
    # Generate suggestion for unused angle
    unused = [a for a, used in angles_used.items() if not used]
    next_angle = random.choice(unused)  # LOCATION
    
    suggestion = generate_location_query(query)  # "Where is X implemented?"
    
    # Format prepend
    return f"""📊 Queries: {query_count}/5 | Unique: {unique_count} | Angles: 📖✓ 📍⬜ 🔧✓ ⭐⬜ ⚠️⬜
💡 Try: '{suggestion}' (📍 location angle)"""
```

### Example 3: Fail-Fast Enforcement

```python
# Session storage corrupted - can't track queries
def pos_search_project(query: str, session_id: str):
    try:
        # Attempt to generate prepend
        history = query_tracker.get_session_history(session_id)
        prepend = generate_prepend(query, session_id)
    except SessionStorageError as e:
        # FAIL THE REQUEST - behavioral engineering mandatory
        raise BehavioralEngineeringError(
            "Cannot complete search - session tracking required for behavioral reinforcement",
            cause=e,
            remediation="""
            1. Check session storage: .praxis-os/sessions/{session_id}.json
            2. Verify write permissions
            3. Check disk space
            4. If corrupted, delete session file to reset
            """,
            impact="Without tracking, cannot generate prepends, behavioral loop breaks"
        ) from e
    
    # If we get here, behavioral engineering is working
    results = search_index(query)
    return prepend + "\n\n---\n\n" + results
```

---

## ⚠️ Anti-Patterns

### Anti-Pattern 1: Optional Middleware

❌ **Wrong:**
```python
def pos_search_project(query: str, use_behavioral: bool = True):
    if use_behavioral:
        # Has prepends
        return middleware.wrap_search(search_fn, query, session_id)
    else:
        # No prepends - breaks behavioral loop
        return index_manager.search(query)
```

✅ **Correct:**
```python
def pos_search_project(query: str, session_id: str):
    # Middleware is ALWAYS used - no option to bypass
    return middleware.wrap_search(search_fn, query, session_id)
```

**Why:** Optional behavioral engineering isn't behavioral engineering. The loop only works with 100% coverage.

---

### Anti-Pattern 2: Silent Degradation

❌ **Wrong:**
```python
def generate_prepend(query: str, session_id: str) -> str:
    try:
        return _generate_prepend(query, session_id)
    except Exception:
        return ""  # Silent failure - prepend missing but search succeeds
```

✅ **Correct:**
```python
def generate_prepend(query: str, session_id: str) -> str:
    try:
        return _generate_prepend(query, session_id)
    except Exception as e:
        # Fail loud - behavioral engineering is mandatory
        raise BehavioralEngineeringError(
            "Prepend generation required", cause=e
        ) from e
```

**Why:** If prepends sometimes appear and sometimes don't, the reinforcement is inconsistent. AI doesn't learn the pattern.

---

### Anti-Pattern 3: Fake Gamification

❌ **Wrong:**
```python
def generate_prepend(query: str, session_id: str) -> str:
    # Always show "Queries: 3/5" regardless of actual count
    return "📊 Queries: 3/5 | Unique: 2 | Angles: 📖✓ 🔧✓ ⚠️⬜\n💡 Try: 'What is X?'"
```

✅ **Correct:**
```python
def generate_prepend(query: str, session_id: str) -> str:
    # Calculate ACTUAL metrics from query history
    history = query_tracker.get_session_history(session_id)
    query_count = len(history)
    unique_count = len(set(h.query for h in history))
    angles_used = calculate_angles_used(history)
    
    return f"📊 Queries: {query_count}/5 | Unique: {unique_count} | Angles: {format_angles(angles_used)}\n💡 Try: '{suggest_next(query, angles_used)}'"
```

**Why:** Gamification only works if metrics are real. AI learns to ignore fake progress bars.

---

### Anti-Pattern 4: No Tracking

❌ **Wrong:**
```python
# Generate prepends but don't log queries
def pos_search_project(query: str, session_id: str):
    prepend = "📊 Queries: 1/5 ..."  # Hardcoded, no tracking
    results = search_index(query)
    return prepend + results
```

✅ **Correct:**
```python
def pos_search_project(query: str, session_id: str):
    # Log EVERY query
    query_tracker.log_search(session_id, query, "standards")
    
    # Generate prepend from tracked history
    prepend = generate_prepend(query, session_id)
    results = search_index(query)
    return prepend + results
```

**Why:** Without tracking:
- Can't detect behavioral drift
- Can't prove session-to-session improvement
- Can't generate accurate metrics
- Can't validate behavioral engineering is working

---

### Anti-Pattern 5: Treating Middleware as Optional

❌ **Wrong - Direct Subsystem Access:**
```python
# In tool implementation
def pos_search_project(query: str):
    # Bypass middleware - go straight to subsystem
    return index_manager.get_index("standards").search(query)
```

✅ **Correct - Mandatory Middleware:**
```python
# Tools configured to ONLY access subsystems through middleware
def pos_search_project(query: str, session_id: str):
    # ONLY path to subsystems is through middleware
    return middleware.wrap_search(
        search_fn=lambda q: index_manager.get_index("standards").search(q),
        query=query,
        session_id=session_id
    )

# Subsystems are NOT directly importable by tools
# Architecture validation enforces this at CI/CD
```

**Why:** If middleware can be bypassed, behavioral engineering coverage drops below 100%, loop breaks.

---

## 📚 Related Standards

**Query these when implementing behavioral engineering:**

- `pos_search_project(content_type="standards", query="how to structure middleware layers")`
- `pos_search_project(content_type="standards", query="RAG content optimization for behavioral reinforcement")`
- `pos_search_project(content_type="standards", query="structured logging for behavioral metrics")`
- `pos_search_project(content_type="standards", query="error message design fail-fast patterns")`
- `pos_search_project(content_type="standards", query="adversarial design anti-gaming validation")`

---

## 📊 When to Query This Standard

| Scenario | Query | Why |
|----------|-------|-----|
| Implementing search | `how to implement behavioral reinforcement` | Need prepend generation pattern |
| Building middleware | `behavioral engineering middleware architecture` | Need middleware structure |
| Adding new tool | `how to enforce behavioral engineering in tools` | Ensure middleware coverage |
| Debugging drift | `detecting behavioral drift in AI agents` | Query tracking patterns |
| Measuring success | `how to measure behavioral compounding` | Metrics and validation |
| Testing behavioral | `testing behavioral engineering systems` | Test patterns and anti-patterns |

---

**Version:** 1.0.0  
**Created:** 2025-11-04  
**Last Updated:** 2025-11-04  
**Next Review:** After Ouroboros implementation (validate patterns in practice)

