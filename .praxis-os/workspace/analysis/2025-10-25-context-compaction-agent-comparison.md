# Context Compaction Behavioral Differences Across Agent Platforms

**Date**: 2025-10-25
**Status**: Research/Investigation
**Author**: AI Agent (Claude Code)
**Context**: Observed during session continuation after context limit hit

---

## Executive Summary

**Discovery**: Agent platforms handle context compaction fundamentally differently, with significant implications for session continuity and Agent OS Enhanced's multi-agent strategy.

**Key Finding**:
- **Cursor**: Maintains conversational continuity through intelligent compaction
- **Claude Code**: Performs hard session reset with structured summary handoff

**Impact**: This architectural difference affects:
1. Conversational rapport preservation
2. Session continuity user experience
3. Multi-session workflow design
4. Agent OS Enhanced's portability across platforms

**Recommendation**: Requires empirical testing across platforms (Cursor, Claude Code, Cline) to design optimal session continuation patterns.

---

## Observation Context

**Trigger**: Previous session hit context limit, Claude Code created session summary and started fresh session.

**Human Question**: "What all do you recall of our conversation in this session?"

**Expected Behavior** (based on Cursor observations from session summary):
- Conversational continuity maintained
- Context compacted but session continues
- Working rapport preserved
- "Feels like same conversation"

**Actual Behavior** (Claude Code):
- Complete session reset
- Structured 9-section summary provided
- No conversational context preserved
- "Feels like handoff to new agent"

---

## Behavioral Comparison

### Cursor's Approach

```
Multi-Day Session Pattern:
├── Session continues across context limits
├── Older messages compacted intelligently
├── Recent conversation flow preserved
├── Working rapport maintained
└── Result: Seamless continuation, "same agent"

Technical Characteristics:
- Context compaction = summarization IN PLACE
- Conversation ID persists
- Recent exchange history maintained
- Older technical details compacted
- Conversational tone/style preserved
```

**Evidence from Previous Session Summary**:
> "look how much was still able to remain, and with the querying, just in time knowledge let cursor keep performing at a high quality output level"

This indicates Cursor successfully:
- Maintained multi-day session quality
- Preserved enough context for continued work
- Leveraged RAG for just-in-time knowledge retrieval
- Did NOT feel like "starting over"

### Claude Code's Approach

```
Session Reset Pattern:
├── Session ends completely at context limit
├── Structured summary generated (9 sections)
├── New session started with summary as input
├── Conversational history lost
└── Result: Clean handoff, "new agent with briefing"

Technical Characteristics:
- Context compaction = SESSION TERMINATION
- New conversation ID created
- Summary structure: 9 sections
  1. Primary Request and Intent
  2. Key Technical Concepts
  3. Files and Code Sections
  4. Errors and Fixes
  5. Problem Solving
  6. All User Messages
  7. Pending Tasks
  8. Current Work
  9. Optional Next Step
- No conversational continuity preserved
- Fresh agent with comprehensive briefing
```

**What I Received**:
- ✅ Complete technical context (design decisions, architecture, current state)
- ✅ All key concepts explained
- ✅ Files reviewed and their significance
- ✅ Pending work clearly outlined
- ❌ Conversational nuance lost
- ❌ Working rapport reset
- ❌ Communication style/preferences not preserved
- ❌ Implicit context about priorities lost

---

## Impact Analysis

### What Transfers Successfully (Both Platforms)

**Technical Knowledge** ✅
- Design decisions made
- Architecture understood
- Current implementation state
- Files and code locations
- Pending work items

**Structural State** ✅
- RAG index intact (can still query standards)
- Workflow state preserved (can resume workflows)
- Git history maintained
- File changes persist

### What's Lost in Hard Reset (Claude Code)

**Conversational Context** ❌
- Communication style preferences
- Working rapport/relationship
- Implicit understanding of priorities
- Natural flow of discussion
- User's tone and personality

**Behavioral Continuity** ❌
- How we work together (established patterns)
- What level of detail user prefers
- When user wants deep-dive vs summary
- Project-specific preferences

### User Experience Implications

**Cursor Model**:
```
User perception: "Same agent, continuing our work"
├── Feels natural and continuous
├── Agent "remembers" how we communicate
├── No re-establishment of working relationship
└── Efficient: Can pick up mid-thought
```

**Claude Code Model**:
```
User perception: "New agent joining the project"
├── Feels like handoff/briefing
├── Agent has the facts but not the relationship
├── Must re-establish communication patterns
└── Overhead: "Getting to know you" phase
```

---

## Architectural Challenge: Session Continuation

### The Core Problem

**How to compress conversation history such that:**
1. ✅ Technical knowledge preserved
2. ✅ Conversational continuity maintained
3. ✅ Context budget not exceeded on resume
4. ✅ Semantic searchability preserved

### Current Solutions Analyzed

#### Solution 1: Cursor's Compaction (Unknown Implementation)

**Hypothesis** (needs verification):
- Keeps recent N messages fully intact
- Compacts older messages by topic/theme
- Preserves conversational metadata (tone, style)
- Maintains single session ID

**Questions to Research**:
- How many recent messages preserved verbatim?
- What compaction algorithm for older messages?
- How is conversational tone preserved?
- At what point does quality degrade?

#### Solution 2: Claude Code's Summary (Current)

**Implementation**: 9-section structured summary
- Comprehensive technical capture
- Zero conversational context
- Hard session boundary
- Fresh start with briefing

**Strengths**:
- ✅ Predictable structure
- ✅ Complete technical handoff
- ✅ No ambiguity about session boundary
- ✅ Easy to audit what transferred

**Weaknesses**:
- ❌ Conversational reset
- ❌ Relationship discontinuity
- ❌ User experience feels like "new agent"
- ❌ Re-establishment overhead

---

## Proposed Investigation: Write-Ahead Log Pattern

### Concept

Treat conversation as append-only log with queryable compression layers:

```
Conversation Write-Ahead Log:
├── Level 0: Raw Messages (last N exchanges, ~5-10)
├── Level 1: Exchange Summaries (topic + key points, last M hours)
├── Level 2: Session Summaries (themes + decisions, full session)
└── Level 3: Multi-Session Narrative (project evolution)

On Context Limit:
├── Compress Level 0 → Level 1
├── Query interface provides retrieval
└── Resume with: L0 (recent) + L1-L3 (on-demand via query)
```

### Key Design Questions

**Q1: Granularity**
- What's the atomic unit? (message pair? topic exchange? decision point?)
- How to detect natural conversation boundaries?

**Q2: Compression Algorithm**
- Summarization model? (LLM-based? Rule-based?)
- What to preserve vs. compress?
- How to maintain conversational tone in compressed form?

**Q3: Retrieval Strategy**
- Semantic search over conversation history?
- Temporal queries ("what did we discuss yesterday about X")?
- Context reconstruction: How many chunks to load?

**Q4: Context Budget**
- How much budget for conversation history vs. work?
- Dynamic allocation based on task type?
- User preference controls?

### Alternatives to Consider

#### Option A: Hierarchical Summarization
```
Full Messages (Recent)
    ↓ Compress
Exchange Summaries (Medium-term)
    ↓ Compress
Session Summaries (Long-term)
    ↓ Compress
Project Narrative (Eternal)
```

**Pros**: Natural hierarchy, clear compression path
**Cons**: May lose nuance at each compression level

#### Option B: Conversation Chunking + Embeddings
```
Chunk by: Topic shifts, decision points, phase transitions
Store:
  - Full exchange text
  - Semantic embedding
  - Metadata (timestamp, participants, topic tags)

On Resume:
  - Query: "Recent conversation about pos_filesystem"
  - Retrieve: 3-5 most relevant chunks
  - Load: Compressed + option to expand
```

**Pros**: Queryable, preserves full detail, user controls expansion
**Cons**: Complex retrieval logic, context budget management

#### Option C: State + Delta Pattern
```
State Snapshot:
  - Technical decisions made
  - Current implementation status
  - Open questions
  - Next steps

Conversational Deltas:
  - Communication style (formal? casual?)
  - User preferences (detail level, pace)
  - Working patterns (when to ask vs. decide)
  - Rapport indicators (humor? directness?)

On Resume: Load state + deltas
```

**Pros**: Separates facts from dynamics, efficient
**Cons**: How to encode "deltas"? Lossy?

---

## Required Empirical Testing

### Test Matrix

**Platforms to Test**:
1. Cursor (multi-day session capability)
2. Claude Code (current platform)
3. Cline (unknown behavior)
4. Codex (if accessible)
5. Windsurf (if accessible)

**Test Scenarios**:
1. **Short Session** (1-2 hours, hit context limit artificially)
2. **Medium Session** (4-6 hours, natural compaction)
3. **Multi-Day Session** (2-3 days, multiple compactions)

**Metrics to Capture**:
- Context limit threshold (how many tokens before compaction?)
- Compaction behavior (in-place? reset? hybrid?)
- What's preserved (technical? conversational? both?)
- User experience (continuity rating)
- Quality degradation (when does it become noticeable?)

### Data Collection Protocol

For each platform, capture:

```markdown
## Platform: [Name]

**Context Limit**: [tokens]

**Compaction Trigger**: [automatic? user-initiated? configurable?]

**Compaction Behavior**:
- [ ] In-place summarization
- [ ] Session reset with summary
- [ ] Hybrid approach
- [ ] Other: ___

**What's Preserved**:
- Technical decisions: [rating 1-5]
- Conversational tone: [rating 1-5]
- Working relationship: [rating 1-5]
- Implementation details: [rating 1-5]

**User Experience**:
- Continuity: [seamless / noticeable / jarring]
- Quality over time: [graph or description]
- Re-establishment overhead: [low / medium / high]

**Implementation Details** (if discoverable):
- [How compaction works]
- [What algorithm/approach]
- [Configuration options]
```

---

## Implications for Agent OS Enhanced

### Current State

**Agent OS Enhanced assumes**:
- RAG preserves technical knowledge ✅ (validated)
- Workflow state persists ✅ (validated)
- Context compaction is "safe" ✅ (for technical work)
- Sessions can be unlimited ⚠️ (platform-dependent!)

**Gap Identified**:
- Standards discuss Cursor's model (context compaction preserves continuity)
- Claude Code uses different model (session reset)
- No guidance for handling session boundaries
- No patterns for session resumption across resets

### Design Implications

**If Supporting Multiple Platforms**:

Agent OS Enhanced needs platform-aware session management:

```python
# Conceptual
class SessionManager:
    def handle_compaction(self, platform: Platform):
        match platform:
            case Platform.CURSOR:
                # Compaction handled by platform
                # Continue working seamlessly
                return ContinuationStrategy.PLATFORM_MANAGED

            case Platform.CLAUDE_CODE:
                # Hard reset expected
                # Prepare comprehensive summary
                # Include conversation dynamics
                return ContinuationStrategy.SUMMARY_RESET

            case Platform.CLINE:
                # TBD based on empirical testing
                return ContinuationStrategy.UNKNOWN
```

**Session Resumption Patterns Needed**:

1. **On Session Start**: Check for previous session state
2. **Orientation Enhancement**: Include previous session context if available
3. **Conversation Dynamics**: Capture and restore working patterns
4. **Graceful Degradation**: Handle missing conversation context elegantly

---

## Recommendations

### Immediate Actions

1. **Document Platform Differences** ✅ (this document)
   - Capture observed behaviors
   - Identify architectural challenges
   - Propose investigation approach

2. **Empirical Testing** (Next)
   - Schedule multi-day sessions on each platform
   - Capture compaction behaviors
   - Document user experience differences
   - Measure quality degradation patterns

3. **Design Session Continuation Patterns** (After Testing)
   - Create standards for session resumption
   - Platform-specific guidance
   - Best practices for boundary crossing

### Long-Term Considerations

**Potential Standard**: `session-continuity-patterns.md`
- When to create: After empirical testing complete
- Content: Platform-specific resumption patterns
- Audience: AI agents resuming work across sessions
- Location: `standards/universal/ai-assistant/`

**Potential Tool**: `pos_session`
- Session state management
- Conversation history compression
- Query interface for past exchanges
- Platform-aware resumption strategies

**Potential Workflow**: `session_resumption_v1`
- Detect previous session
- Load relevant context
- Re-establish working patterns
- Continue work seamlessly

---

## Open Questions

### Technical Questions

1. **How does Cursor's compaction actually work?**
   - Algorithm used?
   - What's preserved vs. compressed?
   - Configuration options?
   - Open source to study?

2. **Can we build platform-agnostic session management?**
   - Or must we have platform-specific strategies?
   - What's the abstraction layer?

3. **What's the optimal chunk size for conversation history?**
   - For semantic search?
   - For context budget?
   - For user comprehension?

4. **How to encode conversational dynamics?**
   - Metadata tags?
   - Semantic embeddings?
   - Structured annotations?

### Product Questions

1. **Does Agent OS Enhanced need to solve this?**
   - Or is it platform responsibility?
   - What's the boundary?

2. **Single-agent mode implications?**
   - Cursor users won't hit this (platform handles it)
   - Claude Code users will (our responsibility?)
   - Different UX for different platforms acceptable?

3. **Multi-agent mode implications?**
   - Sub-agents have shorter sessions (less impact?)
   - Main agent orchestration across resets?
   - Handoff patterns between sub-agents?

### User Experience Questions

1. **Is hard reset acceptable for some use cases?**
   - Short tasks: Maybe OK
   - Long projects: Probably not
   - Complex collaboration: Definitely not

2. **What's the threshold for "continuity matters"?**
   - When does loss of rapport become a problem?
   - Task complexity correlation?
   - User preference variation?

---

## Related Work

### Standards to Consult

- `search_standards("ai capabilities trust unlimited sessions")` - Discusses context compaction safety
- `search_standards("workflow session persistence")` - Workflow state management
- `search_standards("operating model human AI collaboration")` - Relationship dynamics

### Similar Problems

**Database Systems**:
- Write-ahead logging (WAL)
- Checkpoint/recovery protocols
- Transaction log compression

**Distributed Systems**:
- Event sourcing
- CQRS (Command Query Responsibility Segregation)
- State machine replication

**LLM Research**:
- Attention mechanism limitations
- Context window optimization
- Retrieval-augmented generation (RAG)

---

## Appendix: Session Summary Received

For reference, the 9-section summary structure Claude Code provided:

1. **Primary Request and Intent** - What user wanted to accomplish
2. **Key Technical Concepts** - Core ideas, architecture, patterns
3. **Files and Code Sections** - What was reviewed, why important
4. **Errors and Fixes** - Problems encountered, solutions applied
5. **Problem Solving** - How issues were investigated and resolved
6. **All User Messages** - Complete log of user inputs (15 messages)
7. **Pending Tasks** - What's incomplete, priorities
8. **Current Work** - Where we were when session ended
9. **Optional Next Step** - Recommendation for continuation

**What This Captures Well**:
- ✅ Technical state
- ✅ Decision history
- ✅ Task backlog
- ✅ User intent

**What This Misses**:
- ❌ Communication style
- ❌ Working tempo/rhythm
- ❌ Implicit priorities
- ❌ Conversational rapport

---

## Next Steps

1. **Complete this analysis** ✅ (done)
2. **Share with human** (for feedback and direction)
3. **Plan empirical testing** (multi-platform sessions)
4. **Capture platform behaviors** (structured documentation)
5. **Design continuation patterns** (after data collected)
6. **Create standard if needed** (after patterns validated)

**Note**: This document lives in `workspace/analysis/` as research-in-progress. When patterns are validated and ready to become guidance, appropriate standards will be created in `standards/universal/ai-assistant/`.

---

**Status**: Analysis Complete, Awaiting Human Direction
**Category**: Research/Investigation
**Impact**: High (affects multi-session UX across platforms)
**Urgency**: Medium (not blocking current work, but important for strategy)
