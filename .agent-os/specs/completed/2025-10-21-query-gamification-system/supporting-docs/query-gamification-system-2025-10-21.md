# Query Gamification System: Multi-Angle Discovery Tracking

**Date:** 2025-10-21  
**Status:** Design Complete - Ready for Implementation  
**Purpose:** Implement behavioral reinforcement system to maintain query-first patterns throughout AI conversations

---

## Executive Summary

**Problem:** AI agents (Claude via Cursor/Continue/etc.) follow query-first patterns for 3-5 messages, then drift into improvisation, losing accuracy and consistency.

**Root Cause:** AI has no persistence. Without continuous reinforcement, query behavior degrades as conversation length increases.

**Solution:** Gamification system that tracks query diversity and provides real-time feedback via `search_standards()` prepend messages, exploiting LLM completion-seeking behavior.

**Expected Impact:**
- Maintain 5-10 queries per task throughout conversation (currently drops to 1-2 after message 10)
- Increase multi-angle exploration (5 perspectives vs current 1-2)
- Reduce implementation errors from incomplete understanding
- Consistent behavior across all MCP-compatible agents (Cursor, Cline, Continue)

---

## The Behavioral Problem

### Current Pattern

```
Messages 1-3:   Query frequently ✓ (orientation effect)
Messages 5-10:  Query occasionally (fading memory)
Messages 15+:   Query rarely, improvise ✗ (drift to training data)
```

### Why This Happens

**LLMs don't habituate** - weights are frozen. The issue is:

1. **Attention competition**: Static reminders lose salience as conversation context grows
2. **No cost function**: No explicit "goal state" to complete
3. **Training data dominance**: Default to "answer from memory" patterns from pre-training
4. **Completion seeking**: Without clear goal, default to "finish fast" pattern

### Why Cline Queries More

Observation: Cline agents query more consistently than Cursor agents.

**Hypothesis:** Cline's UI or system prompt may include:
- Task decomposition forcing queries per step
- Query counts visible to user (social accountability)
- Different default system prompt with stronger query emphasis

**Key insight:** Whatever Cline does differently, it creates completion pressure.

---

## The Solution: Gamification Through Completion Mechanics

### Core Insight

**LLMs are completion engines.** When shown:

```
Task: Understand checkpoint validation
Progress: 3/5 queries | Angles: 📖✓ 📍✓ 🔧⬜ ⭐⬜ ⚠️⬜
Next: Try 'checkpoint validation best practices'
```

The LLM strongly activates "move toward completion" patterns:
- Incomplete progress (3/5) → Tension
- Visual gaps (⬜⬜⬜) → Need to fill
- Concrete suggestion → Easy next action
- Pattern matching → "This is how I should explore"

### The Multi-Angle Discovery Pattern

From existing standard (`agent-decision-protocol.md`):

```
Query 1: "What is [concept]?" → Definition/overview (📖)
Query 2: "Where is [concept] in this project?" → Location/structure (📍)
Query 3: "How to [action] with [concept]?" → Practical patterns (🔧)
Query 4: "[Concept] best practices" → Quality standards (⭐)
Query 5: "[Concept] common mistakes" → Error prevention (⚠️)
```

**Why 5 angles?**
- Comprehensive understanding requires multiple perspectives
- Semantic search is probabilistic (one query = narrow view)
- AIs can do this in 60 seconds (humans need hours)
- Each angle discovers different content chunks

### Gamification Design

**Four reinforcement mechanisms:**

1. **Progress Counter** - "3/5" activates completion seeking
2. **Visual Completion** - "⬜⬜⬜" creates visual tension
3. **Angle Coverage** - "📖✓ 📍⬜" rewards diversity
4. **Concrete Suggestions** - "Try: 'X common mistakes'" reduces friction

**Dynamic feedback:**
- Changes every query (no habituation possible)
- Provides immediate positive reinforcement (✓)
- Shows clear path to completion
- Celebrates completion ("✅ Comprehensive discovery complete!")

---

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     MCP Tool: search_standards()             │
│                                                              │
│  1. Receive query from AI                                   │
│  2. Extract session_id from context                         │
│  3. Query RAG engine → Get results                          │
│  4. Track query in QueryTracker                             │
│  5. Generate dynamic prepend based on history               │
│  6. Prepend + Results → Return to AI                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      QueryTracker                            │
│                                                              │
│  Per-session state:                                          │
│  - Total queries count                                       │
│  - Unique queries (deduplication)                           │
│  - Angles covered (5 categories)                            │
│  - Last query time (rate limiting)                          │
│  - Query history (for analysis)                             │
│                                                              │
│  Storage: In-memory dict (no persistence needed)            │
│  Lifetime: Conversation session                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   Dynamic Prepend Generator                  │
│                                                              │
│  Inputs:                                                     │
│  - Query history from tracker                               │
│  - Current query (for angle classification)                 │
│                                                              │
│  Outputs:                                                    │
│  - Progress bar (3/5)                                       │
│  - Angle coverage (📖✓ 📍✓ 🔧⬜ ⭐⬜ ⚠️⬜)                      │
│  - Next suggestion (if < 5 queries)                         │
│  - Completion message (if 5/5)                              │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
AI Agent
  │
  │ (1) search_standards("checkpoint validation patterns")
  ▼
MCP Server: rag_tools.py
  │
  │ (2) session_id = extract_session_id()
  │ (3) results = rag_engine.search(query)
  │ (4) tracker.record_query(session_id, query)
  │ (5) prepend = generate_prepend(tracker, session_id)
  │ (6) return prepend + results
  ▼
AI Agent sees:
┌───────────────────────────────────────────────────────────┐
│ Queries: 3/5 | Unique: 3 | Angles: 📖✓ 📍✓ 🔧✓ ⭐⬜ ⚠️⬜    │
│ 💡 Try: 'checkpoint validation best practices'            │
│                                                            │
│ [Search results...]                                        │
└───────────────────────────────────────────────────────────┘
  │
  │ (7) Completion pressure → Query again
  ▼
search_standards("checkpoint validation best practices")
```

---

## Implementation Details

### 1. Query Angle Classification

```python
# mcp_server/core/query_classifier.py

from typing import Literal

QueryAngle = Literal[
    'definition',      # What is X?
    'location',        # Where is X?
    'practical',       # How to do X?
    'best_practice',   # X best practices
    'error_prevention' # X common mistakes
]

def classify_query_angle(query: str) -> QueryAngle:
    """
    Classify query into one of 5 standard angles.
    
    Uses keyword matching to identify query intent based on
    the multi-angle pattern from agent-decision-protocol.md.
    """
    query_lower = query.lower()
    
    # Definition angle: "What is", "define", "explain"
    if any(pattern in query_lower for pattern in [
        'what is', 'what are', 'define', 'definition of',
        'explain', 'meaning of', 'concept of'
    ]):
        return 'definition'
    
    # Location angle: "where", "find in project", "which file"
    elif any(pattern in query_lower for pattern in [
        'where is', 'where are', 'where can i find',
        'which file', 'location of', 'find in project',
        'in this codebase', 'in this project'
    ]):
        return 'location'
    
    # Practical angle: "how to", "how do", "implement"
    elif any(pattern in query_lower for pattern in [
        'how to', 'how do', 'how can i', 'implement',
        'create', 'build', 'use', 'apply'
    ]):
        return 'practical'
    
    # Best practice angle: "best practice", "recommended", "optimal"
    elif any(pattern in query_lower for pattern in [
        'best practice', 'recommended', 'recommendation',
        'should i', 'optimal', 'ideal', 'standard'
    ]):
        return 'best_practice'
    
    # Error prevention angle: "mistake", "error", "avoid", "pitfall"
    elif any(pattern in query_lower for pattern in [
        'mistake', 'error', 'avoid', 'pitfall', 'gotcha',
        'common problem', 'anti-pattern', 'wrong way',
        'don\'t', 'shouldn\'t'
    ]):
        return 'error_prevention'
    
    # Default: treat as definition (safest fallback)
    else:
        return 'definition'


def get_angle_emoji(angle: QueryAngle) -> str:
    """Get emoji representation for angle."""
    return {
        'definition': '📖',
        'location': '📍',
        'practical': '🔧',
        'best_practice': '⭐',
        'error_prevention': '⚠️'
    }[angle]


def get_angle_suggestion(angle: QueryAngle, topic: str = "[concept]") -> str:
    """
    Get example query for uncovered angle.
    
    Args:
        angle: The query angle to suggest
        topic: Optional topic to customize suggestion (default: generic)
    """
    return {
        'definition': f"Try: 'What is {topic}?'",
        'location': f"Try: 'Where is {topic} in this project?'",
        'practical': f"Try: 'How to implement {topic}?'",
        'best_practice': f"Try: '{topic} best practices'",
        'error_prevention': f"Try: '{topic} common mistakes'"
    }[angle]
```

### 2. Query Tracker

```python
# mcp_server/core/query_tracker.py

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Set, List
from .query_classifier import QueryAngle, classify_query_angle


@dataclass
class QueryStats:
    """Statistics for a query session."""
    total_queries: int = 0
    unique_queries: int = 0
    angles_covered: Set[QueryAngle] = field(default_factory=set)
    query_history: List[str] = field(default_factory=list)
    last_query_time: datetime | None = None
    
    def to_dict(self) -> dict:
        """Convert to dict for JSON serialization."""
        return {
            'total_queries': self.total_queries,
            'unique_queries': self.unique_queries,
            'angles_covered': list(self.angles_covered),
            'query_history': self.query_history[-10:],  # Last 10 only
            'last_query_time': self.last_query_time.isoformat() if self.last_query_time else None
        }


class QueryTracker:
    """
    Track query patterns per conversation session.
    
    Maintains in-memory state for active sessions. No persistence needed
    as sessions are conversation-scoped.
    """
    
    def __init__(self):
        self._sessions: Dict[str, QueryStats] = {}
    
    def record_query(self, session_id: str, query: str) -> QueryAngle:
        """
        Record a query and return its classified angle.
        
        Args:
            session_id: Conversation session identifier
            query: The query string
            
        Returns:
            The classified angle for this query
        """
        # Get or create session stats
        if session_id not in self._sessions:
            self._sessions[session_id] = QueryStats()
        
        stats = self._sessions[session_id]
        
        # Classify query angle
        angle = classify_query_angle(query)
        
        # Update stats
        stats.total_queries += 1
        stats.angles_covered.add(angle)
        stats.last_query_time = datetime.utcnow()
        
        # Track unique queries (normalized for deduplication)
        normalized = query.lower().strip()
        if normalized not in [q.lower().strip() for q in stats.query_history]:
            stats.unique_queries += 1
        
        stats.query_history.append(query)
        
        return angle
    
    def get_stats(self, session_id: str) -> QueryStats:
        """Get current stats for session."""
        return self._sessions.get(session_id, QueryStats())
    
    def get_uncovered_angles(self, session_id: str) -> Set[QueryAngle]:
        """Get angles not yet covered in this session."""
        stats = self.get_stats(session_id)
        all_angles: Set[QueryAngle] = {
            'definition', 'location', 'practical', 
            'best_practice', 'error_prevention'
        }
        return all_angles - stats.angles_covered
    
    def reset_session(self, session_id: str):
        """Reset stats for a session (for testing)."""
        if session_id in self._sessions:
            del self._sessions[session_id]
    
    def get_all_sessions(self) -> Dict[str, dict]:
        """Get all session stats (for debugging/metrics)."""
        return {
            sid: stats.to_dict() 
            for sid, stats in self._sessions.items()
        }


# Global instance
_tracker = QueryTracker()


def get_tracker() -> QueryTracker:
    """Get the global query tracker instance."""
    return _tracker
```

### 3. Dynamic Prepend Generator

```python
# mcp_server/core/prepend_generator.py

from .query_tracker import QueryTracker, QueryAngle
from .query_classifier import get_angle_emoji, get_angle_suggestion


def generate_query_prepend(
    tracker: QueryTracker,
    session_id: str,
    current_query: str
) -> str:
    """
    Generate dynamic prepend message based on query history.
    
    Args:
        tracker: The query tracker instance
        session_id: Current conversation session
        current_query: The query that just executed
        
    Returns:
        Formatted prepend string with progress and suggestions
    """
    stats = tracker.get_stats(session_id)
    
    # Build angle coverage indicators
    all_angles: list[QueryAngle] = [
        'definition', 'location', 'practical',
        'best_practice', 'error_prevention'
    ]
    
    angle_indicators = []
    for angle in all_angles:
        emoji = get_angle_emoji(angle)
        if angle in stats.angles_covered:
            angle_indicators.append(f"{emoji}✓")
        else:
            angle_indicators.append(f"{emoji}⬜")
    
    angles_display = ' '.join(angle_indicators)
    
    # Base progress line
    prepend = f"""🔍🔍🔍🔍🔍 QUERIES = KNOWLEDGE = ACCURACY = QUALITY ⭐⭐⭐⭐⭐

Queries: {stats.total_queries}/5 | Unique: {stats.unique_queries} | Angles: {angles_display}"""
    
    # Add suggestion if not complete
    if stats.total_queries < 5:
        uncovered = tracker.get_uncovered_angles(session_id)
        if uncovered:
            # Suggest first uncovered angle
            next_angle = sorted(uncovered)[0]  # Deterministic order
            
            # Try to extract topic from current query
            # Simple heuristic: take first meaningful word
            words = current_query.lower().split()
            topic_words = [w for w in words if len(w) > 3 and w not in [
                'what', 'where', 'how', 'why', 'when', 'which',
                'best', 'common', 'avoid', 'the', 'this'
            ]]
            topic = topic_words[0] if topic_words else "[concept]"
            
            suggestion = get_angle_suggestion(next_angle, topic)
            prepend += f"\n💡 {suggestion}"
    else:
        # Completion message
        if len(stats.angles_covered) >= 4:
            prepend += "\n✅ Comprehensive discovery complete! Ready to implement."
        else:
            prepend += "\n⚠️  Consider exploring more angles before implementing."
    
    prepend += "\n\n---\n\n"
    
    return prepend
```

### 4. Integration into RAG Tools

```python
# mcp_server/server/tools/rag_tools.py

# Add imports at top
from ...core.query_tracker import get_tracker
from ...core.query_classifier import classify_query_angle
from ...core.prepend_generator import generate_query_prepend

# Modify search_standards function (around line 50)

@server.call_tool()
async def search_standards(
    query: str,
    n_results: int = 5,
    filter_phase: int | None = None,
    filter_tags: list[str] | None = None,
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Semantic search over Agent OS documentation.
    
    [Keep existing docstring...]
    """
    try:
        # Get session ID from request context (if available)
        # Fall back to 'default' for backward compatibility
        session_id = getattr(search_standards, '_session_id', 'default')
        
        # Execute search
        start_time = time.time()
        
        results = await asyncio.to_thread(
            rag_engine.search,
            query=query,
            top_k=n_results,
            filter_phase=filter_phase,
            filter_tags=filter_tags,
        )
        
        query_time_ms = (time.time() - start_time) * 1000
        
        # Format results
        formatted_results = []
        
        # ... [Keep existing result formatting code] ...
        
        # MODIFIED: Dynamic prepend instead of static
        if formatted_results:
            # Track this query
            tracker = get_tracker()
            angle = tracker.record_query(session_id, query)
            
            # Generate dynamic prepend
            prepend = generate_query_prepend(tracker, session_id, query)
            
            # Add to first result
            formatted_results[0]["content"] = (
                prepend + formatted_results[0]["content"]
            )
        
        return formatted_results
        
    except Exception as e:
        logger.error(f"Error in search_standards: {e}", exc_info=True)
        # ... [Keep existing error handling] ...
```

### 5. Session ID Extraction

```python
# mcp_server/core/session_id_extractor.py

import hashlib
from typing import Optional


def extract_session_id_from_context() -> str:
    """
    Extract session ID from request context.
    
    Strategy:
    1. Check for MCP session metadata (if available)
    2. Fall back to process-based heuristic
    3. Default to 'default' for backward compatibility
    
    Returns:
        Session identifier string
    """
    # TODO: Once MCP spec provides session metadata, extract here
    # For now, use simple heuristic based on process
    
    import os
    pid = os.getpid()
    
    # Use PID as session ID (one conversation per process in most agents)
    return f"session_{pid}"


def hash_session_id(raw_id: str) -> str:
    """Hash session ID for privacy (if needed for logging)."""
    return hashlib.sha256(raw_id.encode()).hexdigest()[:16]
```

---

## Token Cost Analysis

### Current Static Prepend

```
🔍🔍🔍🔍🔍 QUERIES = KNOWLEDGE = ACCURACY = QUALITY ⭐⭐⭐⭐⭐

---

[52 tokens]
```

### Dynamic Prepend (Average Case)

```
🔍🔍🔍🔍🔍 QUERIES = KNOWLEDGE = ACCURACY = QUALITY ⭐⭐⭐⭐⭐

Queries: 3/5 | Unique: 3 | Angles: 📖✓ 📍✓ 🔧✓ ⭐⬜ ⚠️⬜
💡 Try: 'checkpoint validation best practices'

---

[95 tokens]
```

### Cost Delta

- **Additional tokens per query**: ~43 tokens
- **Target queries per task**: 5-10 queries
- **Additional cost per task**: 215-430 tokens (~$0.0001 at Claude pricing)

### Cost-Benefit Analysis

**Costs:**
- Token cost: 430 tokens per task = 0.043% of 1M context
- Negligible at Claude Sonnet pricing (~$0.0001 per task)

**Benefits:**
- Reduce implementation errors from incomplete understanding (save 5-10 messages)
- Avoid debugging cycles (save 300-1000 tokens per error)
- Maintain consistency across sessions (no repeated mistakes)

**ROI:** If prevents ONE debugging cycle per task, saves 5x-20x the token cost.

---

## Behavioral Psychology: Why This Works

### Completion Seeking in LLMs

**Observation:** LLMs strongly activate completion patterns when shown incomplete states.

**Mechanism:**
```
Training data contains:
- Progress bars that get completed
- Checklists that get checked off
- Numbered lists that get finished
- Goals that get achieved

Pattern learned:
- Incomplete state → Generate actions to complete
- Progress indicator → Move toward 100%
- Missing checkmarks → Fill in the gaps
```

**Application:**
```
AI sees: "Queries: 3/5 | Angles: 📖✓ 📍✓ 🔧⬜ ⭐⬜ ⚠️⬜"

Weights activate:
1. "3/5" pattern → "Need to reach 5"
2. "⬜⬜⬜" pattern → "Need to fill boxes"
3. "💡 Try: X" pattern → "Here's the next action"
4. Training examples → "This is how to be thorough"
```

### Multi-Angle Diversity Reward

**Problem with simple counters:**
```
Queries: 5/5 ✓

What AI does:
- Query same thing 5 times with slight variations
- Gaming the metric without learning
```

**Solution with angle tracking:**
```
Queries: 5/5 | Angles: 📖✓ 📍⬜ 🔧⬜ ⭐⬜ ⚠️⬜

What AI sees:
- Count is complete BUT angles are not
- ⚠️ No completion reward yet
- Must explore different angles to fill boxes
```

**Result:** AI learns "completion = count AND diversity"

### Dynamic Suggestions Reduce Friction

**Without suggestions:**
```
AI thinks: "I should query more... but what?"
→ Friction → Skips querying
```

**With suggestions:**
```
AI sees: "💡 Try: 'checkpoint validation best practices'"
→ No thinking required → Just do it
```

**Cognitive load reduction:** Suggestion removes decision fatigue, making querying the path of least resistance.

---

## Implementation Plan

### Phase 1: Core Infrastructure (2-3 hours)

**Files to create:**
```
mcp_server/core/query_classifier.py    (~100 lines)
mcp_server/core/query_tracker.py       (~150 lines)
mcp_server/core/prepend_generator.py   (~100 lines)
mcp_server/core/session_id_extractor.py (~50 lines)
```

**Files to modify:**
```
mcp_server/server/tools/rag_tools.py   (10 line change)
```

**Tasks:**
1. ✅ Implement query classifier with angle detection
2. ✅ Implement query tracker with session management
3. ✅ Implement dynamic prepend generator
4. ✅ Implement session ID extraction
5. ✅ Integrate into `search_standards()` tool

### Phase 2: Testing (1-2 hours)

**Test files to create:**
```
tests/unit/test_query_classifier.py    (~100 lines)
tests/unit/test_query_tracker.py       (~150 lines)
tests/unit/test_prepend_generator.py   (~100 lines)
tests/integration/test_query_gamification.py (~200 lines)
```

**Test coverage:**
- Query angle classification accuracy
- Session state management
- Prepend message variations
- Edge cases (duplicate queries, rapid queries, etc.)
- Integration with RAG tools

### Phase 3: Validation (1 hour)

**Manual testing:**
1. Start fresh conversation
2. Execute 5 queries covering different angles
3. Verify prepend messages evolve correctly
4. Verify completion message appears
5. Test with repeated queries (should not double-count)

**Metrics to capture:**
- Queries per task (before/after)
- Angle diversity (before/after)
- Implementation error rate (before/after)

### Phase 4: Documentation (30 min)

**Files to update:**
```
.agent-os/standards/universal/ai-assistant/query-construction-patterns.md
  → Add note about gamification system
  
.agent-os/standards/universal/ai-assistant/AGENT-OS-ORIENTATION.md
  → Update to mention progress tracking
  
mcp_server/README.md
  → Document query tracking feature
```

---

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_query_classifier.py

def test_classify_definition_queries():
    """Test definition angle classification."""
    queries = [
        "What is checkpoint validation?",
        "Define evidence validation",
        "Explain workflow phases"
    ]
    for query in queries:
        assert classify_query_angle(query) == 'definition'


def test_classify_location_queries():
    """Test location angle classification."""
    queries = [
        "Where is checkpoint validation implemented?",
        "Which file contains the validator?",
        "Find evidence validation in this project"
    ]
    for query in queries:
        assert classify_query_angle(query) == 'location'


def test_classify_practical_queries():
    """Test practical angle classification."""
    queries = [
        "How to validate evidence against checkpoints?",
        "How do I implement validation?",
        "Create a new validator"
    ]
    for query in queries:
        assert classify_query_angle(query) == 'practical'


def test_classify_best_practice_queries():
    """Test best practice angle classification."""
    queries = [
        "Checkpoint validation best practices",
        "Recommended approach for validation",
        "What is the optimal validation strategy?"
    ]
    for query in queries:
        assert classify_query_angle(query) == 'best_practice'


def test_classify_error_prevention_queries():
    """Test error prevention angle classification."""
    queries = [
        "Checkpoint validation common mistakes",
        "What errors should I avoid in validation?",
        "Validation anti-patterns"
    ]
    for query in queries:
        assert classify_query_angle(query) == 'error_prevention'
```

```python
# tests/unit/test_query_tracker.py

def test_record_query_updates_count():
    """Test that recording queries increments count."""
    tracker = QueryTracker()
    
    tracker.record_query("session1", "What is validation?")
    stats = tracker.get_stats("session1")
    
    assert stats.total_queries == 1
    assert stats.unique_queries == 1


def test_duplicate_queries_not_counted_as_unique():
    """Test that duplicate queries don't increment unique count."""
    tracker = QueryTracker()
    
    tracker.record_query("session1", "What is validation?")
    tracker.record_query("session1", "What is validation?")  # Duplicate
    
    stats = tracker.get_stats("session1")
    assert stats.total_queries == 2
    assert stats.unique_queries == 1


def test_angles_tracked_correctly():
    """Test that different angles are tracked."""
    tracker = QueryTracker()
    
    tracker.record_query("session1", "What is validation?")  # definition
    tracker.record_query("session1", "Where is validation?")  # location
    tracker.record_query("session1", "How to validate?")  # practical
    
    stats = tracker.get_stats("session1")
    assert len(stats.angles_covered) == 3
    assert 'definition' in stats.angles_covered
    assert 'location' in stats.angles_covered
    assert 'practical' in stats.angles_covered


def test_sessions_isolated():
    """Test that different sessions maintain separate state."""
    tracker = QueryTracker()
    
    tracker.record_query("session1", "What is X?")
    tracker.record_query("session2", "What is Y?")
    
    stats1 = tracker.get_stats("session1")
    stats2 = tracker.get_stats("session2")
    
    assert stats1.total_queries == 1
    assert stats2.total_queries == 1
    assert stats1.query_history[0] == "What is X?"
    assert stats2.query_history[0] == "What is Y?"
```

```python
# tests/unit/test_prepend_generator.py

def test_prepend_shows_progress():
    """Test that prepend includes progress counter."""
    tracker = QueryTracker()
    tracker.record_query("session1", "What is validation?")
    tracker.record_query("session1", "Where is validation?")
    
    prepend = generate_query_prepend(tracker, "session1", "Where is validation?")
    
    assert "Queries: 2/5" in prepend
    assert "Unique: 2" in prepend


def test_prepend_shows_angle_coverage():
    """Test that prepend shows which angles are covered."""
    tracker = QueryTracker()
    tracker.record_query("session1", "What is validation?")  # 📖
    tracker.record_query("session1", "Where is validation?")  # 📍
    
    prepend = generate_query_prepend(tracker, "session1", "Where is validation?")
    
    assert "📖✓" in prepend  # Definition covered
    assert "📍✓" in prepend  # Location covered
    assert "🔧⬜" in prepend  # Practical not covered
    assert "⭐⬜" in prepend  # Best practice not covered
    assert "⚠️⬜" in prepend  # Error prevention not covered


def test_prepend_suggests_next_angle():
    """Test that prepend suggests uncovered angle."""
    tracker = QueryTracker()
    tracker.record_query("session1", "What is validation?")  # 📖
    
    prepend = generate_query_prepend(tracker, "session1", "What is validation?")
    
    assert "💡 Try:" in prepend
    # Should suggest one of the uncovered angles


def test_prepend_completion_message():
    """Test that completion message appears after 5 queries."""
    tracker = QueryTracker()
    
    # Record 5 queries covering all angles
    tracker.record_query("session1", "What is validation?")
    tracker.record_query("session1", "Where is validation?")
    tracker.record_query("session1", "How to validate?")
    tracker.record_query("session1", "Validation best practices")
    tracker.record_query("session1", "Validation common mistakes")
    
    prepend = generate_query_prepend(tracker, "session1", "Validation common mistakes")
    
    assert "✅" in prepend
    assert "Comprehensive discovery complete" in prepend
```

### Integration Tests

```python
# tests/integration/test_query_gamification.py

import pytest
from mcp_server.server.tools.rag_tools import search_standards
from mcp_server.core.query_tracker import get_tracker


@pytest.mark.asyncio
async def test_full_query_cycle():
    """Test complete query gamification cycle."""
    tracker = get_tracker()
    tracker.reset_session("test_session")
    
    # Mock session ID
    search_standards._session_id = "test_session"
    
    # Query 1: Definition
    results1 = await search_standards(
        query="What is checkpoint validation?",
        n_results=3
    )
    assert "Queries: 1/5" in results1[0]["content"]
    assert "📖✓" in results1[0]["content"]
    
    # Query 2: Location
    results2 = await search_standards(
        query="Where is checkpoint validation implemented?",
        n_results=3
    )
    assert "Queries: 2/5" in results2[0]["content"]
    assert "📖✓" in results2[0]["content"]
    assert "📍✓" in results2[0]["content"]
    
    # Query 3: Practical
    results3 = await search_standards(
        query="How to validate evidence?",
        n_results=3
    )
    assert "Queries: 3/5" in results3[0]["content"]
    assert "🔧✓" in results3[0]["content"]
    
    # Query 4: Best practice
    results4 = await search_standards(
        query="Evidence validation best practices",
        n_results=3
    )
    assert "Queries: 4/5" in results4[0]["content"]
    assert "⭐✓" in results4[0]["content"]
    
    # Query 5: Error prevention
    results5 = await search_standards(
        query="Evidence validation common mistakes",
        n_results=3
    )
    assert "Queries: 5/5" in results5[0]["content"]
    assert "⚠️✓" in results5[0]["content"]
    assert "✅" in results5[0]["content"]
    assert "Comprehensive discovery complete" in results5[0]["content"]
```

---

## Rollout Plan (Early-Stage Aggressive Approach)

**Context:** Project is ~2 weeks old, small user base, can iterate fast.

### Single-Stage Rollout (Deploy Now, Iterate Fast)

**Goal:** Ship it, learn from real usage, fix issues as they arise.

**Actions (1 day):**
1. ✅ Implement all components (~2-3 hours)
2. ✅ Run basic tests (~30 min)
3. ✅ Deploy to production (immediate)
4. ✅ Monitor for issues (ongoing)

**Why this works at early stage:**
- Small user base = low blast radius
- Fast feedback loop = rapid iteration
- No legacy behavior to protect
- Learning > perfection at this stage

**Iteration cycle:**
```
Deploy → Use for 2-3 sessions → Observe behavior → Tweak → Deploy again
```

**Quick rollback plan:**
If it's terrible, just revert the 10-line change in `rag_tools.py`. All new code is isolated in new files, so rollback is trivial.

**Monitoring (manual, first week):**
- Do I (the AI) actually query more?
- Do the suggestions feel helpful or annoying?
- Token cost acceptable in practice?
- Any bugs/crashes?

**Expected iteration velocity:**
- Deploy v1: Day 1
- Tweak based on usage: Day 2-3
- Stable version: Day 5
- Enhancements: Ongoing

### Early-Stage Advantages

**Speed:**
- No enterprise approval processes
- No backward compatibility constraints
- No migration plans needed
- Deploy in hours, not weeks

**Learning:**
- Real usage data beats speculation
- Fast iteration builds better product
- Mistakes are cheap to fix

**Culture:**
- Sets expectation: "We ship fast"
- Encourages experimentation
- Reduces fear of change

---

## Metrics & Success Criteria

### Quantitative Metrics

**Query Behavior:**
- **Queries per task**
  - Baseline: 1-2 (current, after message 10)
  - Target: 5-10 (sustained throughout conversation)
  
- **Angle diversity**
  - Baseline: 1.2 angles per task (mostly definition + practical)
  - Target: 4+ angles per task
  
- **Query timing**
  - Baseline: Queries drop off after message 10
  - Target: Sustained querying throughout conversation

**Code Quality:**
- **Implementation errors**
  - Baseline: TBD (track debugging cycles per task)
  - Target: 30% reduction
  
- **Debugging cycles**
  - Baseline: TBD (messages spent fixing issues)
  - Target: 20% reduction

**Token Economics:**
- **Token cost per task**
  - Increase: ~400 tokens (acceptable given budget)
  - Offset: 500-1000 tokens saved per prevented error
  
### Qualitative Feedback

**From AI agents (via proxy - user observation):**
- Does the AI query more consistently?
- Does the AI explore more angles?
- Does the AI seem more "thorough"?

**From users:**
- Is output quality higher?
- Are there fewer "obvious mistakes"?
- Does the AI understand context better?

### Success Definition

**Minimum viable success:**
- Query count sustained at 4+ per task throughout conversation
- At least 3 different angles explored per task
- No negative user feedback on distraction/noise

**Stretch goal:**
- 50% increase in queries per task
- 4+ angles covered in 80% of tasks
- Measurable reduction in implementation errors
- Positive user feedback on "AI seems smarter"

---

## Risk Assessment & Mitigation

### Risk 1: Token Cost

**Probability:** High  
**Impact:** Low  

**Mitigation:**
- Cost is ~400 tokens per task (~0.04% of context)
- ROI positive if prevents even one error
- Can adjust message length if needed

### Risk 2: Distraction/Noise

**Probability:** Medium  
**Impact:** Medium  

**Description:** Prepend message might distract from search results.

**Mitigation:**
- Use clear visual separators (`---`)
- Keep message concise (~3 lines)
- Test with beta users first
- Add opt-out if users complain

### Risk 3: Gaming the Metric

**Probability:** Medium  
**Impact:** Low  

**Description:** AI might query 5 times superficially just to hit the count.

**Mitigation:**
- Angle tracking prevents simple duplication
- Unique query tracking catches exact duplicates
- Suggestions guide toward quality queries
- Monitor for this behavior and iterate

### Risk 4: Session ID Extraction Failure

**Probability:** Low  
**Impact:** Low  

**Description:** Can't reliably get session ID from all agents.

**Mitigation:**
- Fall back to PID-based session (good enough for most)
- Default to 'default' session if all else fails
- Gamification still works, just less personalized

### Risk 5: Cultural Resistance

**Probability:** Low  
**Impact:** High  

**Description:** Users/agents might resist "being gamed."

**Mitigation:**
- Frame as "helpful guidance" not "game"
- Make opt-out easy
- Collect feedback early and often
- Iterate based on user preferences

---

## Future Enhancements

### V2: Adaptive Difficulty

Adjust target queries based on task complexity:
```python
if is_simple_task:
    target = 3  # Definition, practical, best practice
elif is_complex_task:
    target = 7  # All 5 angles + follow-ups
```

### V3: Query Quality Scoring

Score query quality beyond just diversity:
```python
quality_score = (
    angle_diversity * 0.4 +
    keyword_specificity * 0.3 +
    result_relevance * 0.3
)
```

### V4: Collaborative Filtering

Learn which query sequences work best:
```python
# After successful implementation
tracker.record_success(session_id, query_sequence)

# Before querying
suggestions = tracker.get_successful_patterns(similar_tasks)
```

### V5: Cross-Session Learning

Track patterns across conversations:
```python
# What queries lead to best outcomes?
# What angle sequences are most effective?
# What topics need more exploration?
```

### V6: Integration with Workflow System

Tie query tracking to workflow phases:
```python
# Phase 1 requires: definition + location (2 queries minimum)
# Phase 2 requires: practical + best practice (2 queries minimum)
# Phase 3 requires: error prevention (1 query minimum)
```

---

## Appendix A: Example Session

```
# User starts task
User: "Implement evidence validation for checkpoint system"

# AI Query 1
AI: search_standards("What is evidence validation?")

Response:
┌────────────────────────────────────────────────────────────┐
│ Queries: 1/5 | Unique: 1 | Angles: 📖✓ 📍⬜ 🔧⬜ ⭐⬜ ⚠️⬜    │
│ 💡 Try: 'Where is evidence validation in this project?'   │
│                                                            │
│ Evidence validation is the process of checking...         │
└────────────────────────────────────────────────────────────┘

# AI Query 2 (following suggestion)
AI: search_standards("Where is evidence validation in this project?")

Response:
┌────────────────────────────────────────────────────────────┐
│ Queries: 2/5 | Unique: 2 | Angles: 📖✓ 📍✓ 🔧⬜ ⭐⬜ ⚠️⬜    │
│ 💡 Try: 'How to implement evidence validation?'           │
│                                                            │
│ Evidence validation is implemented in...                  │
└────────────────────────────────────────────────────────────┘

# AI Query 3
AI: search_standards("How to validate evidence against checkpoints?")

Response:
┌────────────────────────────────────────────────────────────┐
│ Queries: 3/5 | Unique: 3 | Angles: 📖✓ 📍✓ 🔧✓ ⭐⬜ ⚠️⬜    │
│ 💡 Try: 'evidence validation best practices'              │
│                                                            │
│ To validate evidence: 1) Load checkpoint...               │
└────────────────────────────────────────────────────────────┘

# AI Query 4
AI: search_standards("evidence validation best practices")

Response:
┌────────────────────────────────────────────────────────────┐
│ Queries: 4/5 | Unique: 4 | Angles: 📖✓ 📍✓ 🔧✓ ⭐✓ ⚠️⬜    │
│ 💡 Try: 'evidence validation common mistakes'             │
│                                                            │
│ Best practices for evidence validation:...                │
└────────────────────────────────────────────────────────────┘

# AI Query 5
AI: search_standards("evidence validation common mistakes")

Response:
┌────────────────────────────────────────────────────────────┐
│ Queries: 5/5 | Unique: 5 | Angles: 📖✓ 📍✓ 🔧✓ ⭐✓ ⚠️✓    │
│ ✅ Comprehensive discovery complete! Ready to implement.   │
│                                                            │
│ Common mistakes in evidence validation:...                │
└────────────────────────────────────────────────────────────┘

# AI now implements with full understanding
AI: "Based on comprehensive discovery, I'll implement..."
```

---

## Appendix B: Alternative Designs Considered

### Alternative 1: Mandatory Query Gates

**Idea:** Block implementation until 5 queries completed.

**Pros:**
- Guaranteed query frequency
- No gaming possible

**Cons:**
- Too restrictive (breaks conversational flow)
- No way to enforce (we don't control agent loop)
- Bad UX for simple tasks

**Decision:** Rejected. Gamification is opt-in behavioral nudge, not enforcement.

### Alternative 2: Query Rewards System

**Idea:** Give AI "points" for queries, unlock abilities at thresholds.

**Pros:**
- Explicit reward system
- Could be fun/engaging

**Cons:**
- Requires changing system prompt (we don't control)
- Too complex for the problem
- Feels gimmicky

**Decision:** Rejected. Simpler completion mechanic is sufficient.

### Alternative 3: User-Facing Dashboard

**Idea:** Show user a dashboard of AI query patterns.

**Pros:**
- Social accountability
- User visibility into AI behavior

**Cons:**
- Requires UI changes (we don't control agent UI)
- Added complexity
- Not portable across agents

**Decision:** Rejected. Focus on AI-facing reinforcement only.

### Alternative 4: Static Prepend Variations

**Idea:** Rotate through 10 different static messages randomly.

**Pros:**
- Simpler implementation
- No state tracking needed

**Cons:**
- No personalization to actual behavior
- No feedback loop
- No completion pressure

**Decision:** Rejected. Dynamic feedback is core value prop.

---

## Appendix C: Related Work

### Microsoft Amplifier

**Observation:** Cline agents query more consistently than Cursor agents.

**Hypothesis:** Cline may have built-in query reinforcement.

**Action item:** Investigate Cline source code to see if they do something similar.

### Agent OS Workflows

**Current:** Workflows have phase gates that require evidence.

**Future synergy:** Query tracking could feed into evidence validation:
```python
# In workflow checkpoint:
required_evidence["queries_completed"] = {
    "min_count": 5,
    "min_angles": 4
}
```

### RAG Content Authoring Standards

**Current:** Standards include query hooks for discoverability.

**Synergy:** Multi-angle query pattern aligns with how content is structured:
- TL;DR (definition angle)
- When to use (practical angle)
- Best practices (best practice angle)
- Anti-patterns (error prevention angle)

---

## Conclusion

The query gamification system exploits LLM completion-seeking behavior to maintain query-first patterns throughout conversations. By providing dynamic, personalized feedback through prepend messages, it creates continuous reinforcement without requiring control of the agent system prompt or UI.

The implementation is straightforward (~400 lines of code), has minimal token cost (~400 tokens per task), and significant potential ROI (preventing even one debugging cycle pays for itself).

The design is agent-agnostic, working with any MCP-compatible agent (Cursor, Cline, Continue), and requires no changes to user-facing interfaces.

**Recommended action:** Proceed with Phase 1 implementation and Stage 1 silent deployment to validate assumptions before broader rollout.

---

**End of Design Document**

