# Session Tracking Addendum

**Date:** 2025-10-23  
**Context:** Query Gamification System session identification strategy

---

## Session Tracking Investigation Summary

### What's Available in MCP

**FastMCP provides `Context` object with:**
- `ctx.client_id` - Unique identifier per client connection (from MCP `initialize` handshake)
- `ctx.request_id` - Unique identifier per individual request

### The Session Challenge

**User workflow:**
```
User: "Implement authentication"
  → AI queries 5x → Session should track as "Query 1/5, 2/5, 3/5, 4/5, 5/5"
  → AI responds

User: "Now implement authorization" (NEW USER PROMPT)
  → AI queries 3x → Session should RESET to "Query 1/5, 2/5, 3/5"
```

**Problem:** MCP has no concept of "user prompt boundaries." The `client_id` persists for the entire conversation (stdio) or connection (HTTP).

**We cannot distinguish:**
- "3rd query in current task"
- "1st query of next task"

### Constraint: Zero Control Over Main Agents

- Main agents (Cursor, Cline, etc.) cannot be modified
- No way to inject "new prompt" signals
- Must implement session logic purely server-side with available information

### Recommended Solution for V1

**Use `client_id` + time-based bucketing:**

```python
# Combine client_id with 90-second time buckets
session_key = f"{ctx.client_id}_{int(time.time() / 90)}"

# Same client in same 90-second window → Same session
# Same client in different 90-second window → New session
```

**Rationale:**
- **Simple:** One-line implementation
- **Agent-agnostic:** Works for all MCP clients (stdio and HTTP)
- **Transport-aware:** `client_id` naturally distinguishes Cursor vs sub-agents
- **Good enough:** 90 seconds captures most "single task" query bursts
- **Imperfect but acceptable:** Matches "ship and learn" philosophy

**Accuracy estimate:**
- ✅ Captures typical query patterns (AI queries 5-10x within 30-60 seconds per task)
- ⚠️ False reset: If AI thinks >90s, counter resets mid-task (minor)
- ⚠️ False continuation: If user sends new prompt <90s after last query (minor)
- **Overall: ~85% accurate** - sufficient for behavioral nudge in v1

### Why 90 Seconds?

- Too short (30s): False resets during normal query patterns
- Too long (180s): Tasks bleed together, no reset between prompts
- **90s sweet spot:** Captures query bursts, resets between most user prompts

### Future Enhancements (Post-V1)

**When sub-agents are implemented:**
- Sub-agents can pass explicit `session_id` parameter
- Server accepts optional `session_id` override
- Main agents continue using `client_id` + time bucketing
- Sub-agents get perfect session tracking

**Possible v2 improvements:**
- Topic similarity detection (semantic analysis to detect topic changes)
- Adaptive timeout (learn query patterns per client)
- Optional explicit session lifecycle tools (`start_session`, `end_session`)

### Implementation Note

**Tool signature change:**
```python
from fastmcp import Context

@mcp.tool()
async def search_standards(
    query: str,
    n_results: int = 5,
    filter_phase: Optional[int] = None,
    filter_tags: Optional[List[str]] = None,
    ctx: Context = None,  # Add Context injection
) -> Dict[str, Any]:
    
    # Extract session key
    if ctx and ctx.client_id:
        session_key = f"{ctx.client_id}_{int(time.time() / 90)}"
    else:
        session_key = "default"  # Fallback
    
    # Use session_key for query tracking...
```

---

## Recommendation

**Ship v1 with `client_id` + 90-second bucketing.**

- Implement in ~30 minutes
- Observe actual query patterns in real usage
- Iterate based on observed false positive/negative rates
- Add explicit session support when sub-agents are built

**This aligns with the "ship and learn" philosophy:** Simple heuristic that's good enough for behavioral nudge, with clear path to refinement based on real data.

---

**Next Action:** Prioritize sub-agent implementation. Query gamification can wait for that work to complete, then implement with both heuristic (main agents) and explicit (sub-agents) session tracking.

