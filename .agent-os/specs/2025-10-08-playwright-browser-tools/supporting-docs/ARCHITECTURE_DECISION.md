# Architecture Decision: Per-Session Browsers
## Why "Fully Threaded" Wins Over "Singleton"

**Date**: October 8, 2025  
**Decision**: Use per-session browser processes (not shared browser)  
**Status**: APPROVED - Design updated

---

## The Question

> "Why is BrowserManager a singleton? Why not make the full stack threaded?"

## Initial Answer (WRONG)

**Singleton chosen because**:
- Memory efficiency: 3 sessions = 115MB (vs 300MB fully threaded)
- Playwright designed for Browser → Context → Page hierarchy
- One browser launch (2s) vs N launches

**This was WRONG thinking** - optimized for memory, not user experience.

---

## The Reframing

> "You are the ultimate consumer of this tool. Think about debugging frontends you're building. Which provides YOU the best experience?"

## Real-World Scenarios (From AI Agent Perspective)

### Scenario 1: Multi-Page Debugging

**Me with 3 concurrent chats**:
- Chat A: Debug login form
- Chat B: Fix dashboard layout  
- Chat C: Test profile page

**Singleton**: Chat A crashes → **ALL 3 CHATS DIE** 💥  
**Fully Threaded**: Chat A crashes → **ONLY Chat A affected** ✅

**Winner**: Fully threaded. Failure isolation is CRITICAL.

---

### Scenario 2: Testing Auth States

**Me testing**:
- Chat A: Logged out user
- Chat B: Admin user
- Chat C: Regular user

**Singleton**: Separate contexts BUT:
- Shared browser process (memory leaks affect all)
- Restart browser? ALL sessions killed
- Debugging: "Is this MY issue or another session?"

**Fully Threaded**: 
- Complete isolation
- Simple mental model: "My chat = My browser"
- Restart one doesn't affect others

**Winner**: Fully threaded. Simpler mental model.

---

### Scenario 3: Visual Testing

**Me building component library**:
- Chat A: Screenshot button variants
- Chat B: Screenshot dark mode
- Chat C: Screenshot mobile viewport

**Singleton**:
- Lock contention on session dict
- One hang potentially blocks others
- Shared failure point

**Fully Threaded**:
- Truly parallel (no shared state)
- Independent operations
- Clear ownership

**Winner**: Fully threaded. True parallelism.

---

## The Killer Arguments

### 1. Failure Isolation ⭐ MOST IMPORTANT
**Singleton**: One crash affects ALL work  
**Fully Threaded**: Failures isolated per chat ✅

### 2. Mental Model
**Singleton**: "Shared browser, separate contexts, but..."  
**Fully Threaded**: "My chat = My browser. Simple." ✅

### 3. Debugging Clarity
**Singleton**: "Which session caused this?"  
**Fully Threaded**: "My session, my problem." ✅

### 4. Memory Arguments Fall Apart
- 300MB for 3 sessions = **1.8% of 16GB RAM** (trivial)
- Target users: Developers on modern machines
- False economy: Save 200MB but lose all sessions on crash

### 5. Startup Cost is Acceptable
- 2s per session for INTERACTIVE debugging workflow
- Not a server handling thousands of requests
- Human wait time > absolute efficiency

### 6. Code is SIMPLER
**Singleton**:
```python
- Manage shared _browser
- Lock protects both dict AND browser state
- Complex stale session cleanup
- Shared Playwright instance
```

**Fully Threaded**:
```python
- No shared browser!
- Lock only protects session dict
- Simple cleanup (kill process)
- Each session independent
```

---

## Decision: Per-Session Browsers (Fully Threaded)

### Implementation
```python
class BrowserSession:
    playwright: Any       # THIS session's Playwright
    browser: Browser      # THIS session's Chromium process
    page: Page           # THIS session's page
    created_at: float
    last_access: float

class BrowserManager:
    _sessions: Dict[str, BrowserSession]
    _lock: asyncio.Lock  # Only protects dict, not browser
    # NO shared _browser or _playwright!
```

### Benefits
- ✅ Each chat gets independent browser process
- ✅ Crash in one chat doesn't affect others
- ✅ Simpler code (no shared browser management)
- ✅ Clear mental model ("my browser")
- ✅ True parallelism (no lock contention on browser)
- ✅ Easier debugging (ownership is clear)

### Trade-offs
- ⚠️ 300MB for 3 sessions (vs 115MB) → **ACCEPTABLE** on dev machines
- ⚠️ 2s startup per session (vs once) → **ACCEPTABLE** for interactive use

---

## Comparison Table

| Aspect | Singleton (Rejected) | Per-Session (✅ Chosen) |
|--------|---------------------|------------------------|
| **User Experience** | ❌ One crash kills all | ✅ Failures isolated |
| **Mental Model** | ❌ Complex (shared + contexts) | ✅ Simple (my browser) |
| **Debugging** | ❌ "Which session?" | ✅ "My session" |
| **Parallel Work** | ⚠️ Lock contention | ✅ Independent |
| **Fault Tolerance** | ❌ Single failure point | ✅ Isolated |
| **Code Complexity** | ❌ Locks, shared state | ✅ Simpler |
| **Memory (3 sessions)** | ✅ 115MB | ⚠️ 300MB (1.8% of 16GB) |
| **Startup** | ✅ 2s once | ⚠️ 2s per session |
| **Target Environment** | Server (many sessions) | Dev machine (few sessions) |

---

## Key Insight

**Developer Experience > Memory Efficiency**

When building tools for DEVELOPERS (not production servers):
- Reliability matters more than 200MB savings
- Failure isolation matters more than 2s startup savings
- Simplicity matters more than "efficiency"
- Your USER is debugging; don't make it worse with shared state

---

## Implementation Changes

### Original Design (Singleton)
```python
class BrowserManager:
    _playwright: Playwright  # SHARED
    _browser: Browser        # SHARED - single failure point
    _sessions: Dict[session_id, BrowserSession]
    _lock: asyncio.Lock      # Protects dict AND browser

class BrowserSession:
    context: BrowserContext  # From shared browser
    page: Page
```

### New Design (Per-Session)
```python
class BrowserManager:
    _sessions: Dict[session_id, BrowserSession]
    _lock: asyncio.Lock      # Only protects dict

class BrowserSession:
    playwright: Playwright   # Per session
    browser: Browser         # Per session - isolated
    page: Page
```

**Simpler code, better UX** ✅

---

## Future Consideration

Could add config for resource-constrained environments:
```python
BrowserManager(mode="isolated")  # v1: Per-session (default)
BrowserManager(mode="shared")    # Future: Shared browser option
```

But DEFAULT should be per-session for best developer experience.

---

## Lessons Learned

### ❌ Don't Optimize For
- Memory on modern dev machines (16GB+)
- Startup time for interactive workflows
- "Efficiency" at the cost of reliability

### ✅ DO Optimize For
- Failure isolation (crashes don't cascade)
- Simple mental models ("my browser")
- Debugging clarity (ownership is obvious)
- User experience (fewer WTF moments)

---

## Credits

This architectural revision was prompted by the question:

> "You are the ultimate user of this tool. Which approach gives YOU the best experience debugging frontends?"

**The right question changed the design.**

Developer tools should be designed for DEVELOPERS' workflows, not abstract efficiency metrics.

---

**Status**: ✅ APPROVED  
**Specification**: Updated (specs.md, implementation.md, README.md)  
**Impact**: Simpler code, better UX, more reliable  
**Confidence**: HIGH

