# Middleware Architecture Patterns

**Keywords for search**: middleware architecture, cross-cutting concerns, middleware patterns, middleware layer, behavioral middleware, request wrapping, middleware composition, 100% coverage enforcement, fail-fast middleware, middleware testing, tool wrapping, subsystem isolation, middleware validation, architectural boundaries, one-way dependencies, middleware mandatory

---

## 🚨 TL;DR - Middleware Architecture Quick Reference

**Core Principle:** Middleware is a mandatory layer between tools and subsystems that enforces cross-cutting concerns (behavioral engineering, logging, metrics) with 100% coverage. If middleware can be bypassed, the architectural guarantees break.

**The Pattern:**
```
Tools → MIDDLEWARE (mandatory) → Subsystems
```

**Critical Requirements:**
- ✅ ALL tool calls flow through middleware (100% coverage, no exceptions)
- ✅ Middleware failures fail the request (no silent degradation)
- ✅ Tools CANNOT directly access subsystems (architectural enforcement)
- ✅ Middleware is composable (prepend generation + tracking + logging)
- ✅ Middleware is testable in isolation

**The Three Types:**
1. **Request Middleware** - Wraps subsystem calls (behavioral engineering, auth, validation)
2. **Response Middleware** - Transforms results (prepend generation, formatting)
3. **Observability Middleware** - Logs, tracks, measures (query tracking, metrics)

**Anti-Patterns:**
- ❌ Optional middleware (makes coverage <100%)
- ❌ Tools bypass middleware (direct subsystem access)
- ❌ Middleware fails silently (degrades instead of failing)
- ❌ Multiple middleware paths (inconsistent coverage)
- ❌ Middleware contains business logic (wrong layer)

---

## ❓ Questions This Answers

1. "How do I structure middleware layers?"
2. "What belongs in middleware vs tools vs subsystems?"
3. "How do I enforce 100% middleware coverage?"
4. "When should middleware fail-fast vs degrade gracefully?"
5. "How do I compose multiple middleware concerns?"
6. "How do I test middleware in isolation?"
7. "How do I prevent tools from bypassing middleware?"
8. "What is the middleware execution order?"
9. "How do I handle middleware failures?"
10. "How do I validate middleware coverage?"
11. "What are cross-cutting concerns?"
12. "How do I make middleware mandatory?"
13. "How do I structure middleware for behavioral engineering?"
14. "What metrics should middleware collect?"
15. "How do I document middleware requirements?"

---

## 🎯 Purpose

Define patterns for structuring middleware layers that enforce cross-cutting concerns with 100% coverage, ensuring behavioral engineering, observability, and quality gates are reliably applied to all tool invocations.

**Key Distinction:** Middleware vs Business Logic
- **Middleware:** Cross-cutting concerns applied to ALL requests (logging, auth, behavioral engineering)
- **Business Logic:** Domain-specific functionality in subsystems (search algorithms, workflow state)

**Why This Matters:** Behavioral engineering requires 100% coverage. If even one tool call bypasses middleware, the self-reinforcing loop breaks. Middleware architecture makes 100% coverage structurally guaranteed.

---

## ❌ The Problem

**Without middleware architecture:**

1. **Scattered Cross-Cutting Concerns**
   - Logging duplicated in every tool
   - Behavioral engineering copy-pasted
   - Inconsistent error handling
   - No single source of truth

2. **Incomplete Coverage**
   - Some tools have prepends, some don't
   - Behavioral reinforcement inconsistent
   - Can't guarantee observability
   - Quality gates skippable

3. **Direct Subsystem Access**
   - Tools call subsystems directly
   - No way to enforce middleware
   - Behavioral engineering bypassed
   - Can't measure coverage

4. **Architectural Violations Hard to Detect**
   - No structural enforcement
   - Violations discovered at runtime
   - Refactoring accidentally bypasses middleware
   - Tests don't catch architectural drift

**Real-World Impact:**
- Behavioral engineering fails (prepends missing from some results)
- Observability gaps (some queries not tracked)
- Inconsistent quality (some validations skipped)
- Technical debt (cross-cutting logic scattered everywhere)

---

## ✅ The Standard

### Pattern 1: Three-Layer Architecture (The Foundation)

**Layer Structure:**
```
┌─────────────────────────────────────────────────────┐
│                  TOOLS LAYER                        │
│  pos_search, pos_workflow, pos_browser, etc.        │
│                                                     │
│  Responsibility: Parameter validation, MCP protocol │
└────────────────┬────────────────────────────────────┘
                 │ ALL calls through middleware
                 │ (NO direct subsystem access)
                 ▼
┌─────────────────────────────────────────────────────┐
│              MIDDLEWARE LAYER                       │
│  prepend_generator, query_tracker, auth, etc.       │
│                                                     │
│  Responsibility: Cross-cutting concerns (100%)      │
└────────────────┬────────────────────────────────────┘
                 │ Delegates to subsystems
                 ▼
┌─────────────────────────────────────────────────────┐
│              SUBSYSTEMS LAYER                       │
│  RAG (IndexManager), Workflows, Browser             │
│                                                     │
│  Responsibility: Domain logic, business rules       │
└─────────────────────────────────────────────────────┘
```

**One-Way Dependencies (Enforced):**
- ✅ Tools → Middleware → Subsystems (allowed)
- ❌ Tools → Subsystems (blocked by architecture)
- ❌ Middleware → Tools (blocked)
- ❌ Subsystems → Middleware (blocked)
- ❌ Subsystems → Tools (blocked)

**Why This Works:**
- Structural guarantee of coverage (tools can't bypass)
- Clear separation of concerns (middleware = cross-cutting only)
- Testable in isolation (each layer independently testable)
- Refactor-safe (architecture validation catches violations)

---

### Pattern 2: Middleware Composition (Building Blocks)

**Middleware Types:**

1. **Pre-Request Middleware** (Before subsystem call)
   - Authentication/authorization
   - Request validation
   - Rate limiting
   - Query classification

2. **Post-Response Middleware** (After subsystem call)
   - Prepend generation
   - Response formatting
   - Result filtering
   - Error transformation

3. **Observability Middleware** (Wraps entire call)
   - Logging (entry/exit/duration)
   - Metrics collection
   - Query tracking
   - Performance monitoring

**Composition Pattern:**
```python
class MiddlewareStack:
    def __init__(self, middlewares: List[Middleware]):
        """Compose multiple middleware in order.
        
        Execution: middleware[0] → middleware[1] → ... → subsystem
        """
        self.middlewares = middlewares
    
    def execute(self, request: Request) -> Response:
        """Execute middleware stack."""
        # Build chain from inside-out
        handler = self.subsystem_handler
        
        # Wrap with each middleware (reverse order)
        for middleware in reversed(self.middlewares):
            handler = middleware.wrap(handler)
        
        # Execute composed chain
        return handler(request)
```

**Example Composition:**
```python
# Compose behavioral engineering middleware
behavioral_stack = MiddlewareStack([
    AuthMiddleware(),           # 1. Check auth
    QueryClassifier(),          # 2. Classify query angle
    QueryTracker(),             # 3. Log the query
    SubsystemCaller(),          # 4. Call subsystem
    PrependGenerator(),         # 5. Generate prepend
    ResponseFormatter(),        # 6. Format final response
])
```

---

### Pattern 3: Mandatory Middleware (Structural Enforcement)

**Implementation:**
```python
# subsystems/__init__.py
# DO NOT export subsystems directly
# This prevents tools from importing them

# Only export middleware
from .middleware import get_middleware

__all__ = ["get_middleware"]

# Tools can ONLY access subsystems through middleware
```

**Tool Pattern:**
```python
# tools/pos_search.py
from subsystems import get_middleware  # CAN import
# from subsystems.rag import IndexManager  # CANNOT import (not exported)

@mcp.tool()
async def pos_search_project(
    content_type: Literal["standards", "code"],
    query: str,
    session_id: str,
    **kwargs
) -> str:
    """Search tool - MUST use middleware."""
    # Get middleware (only access point)
    middleware = get_middleware()
    
    # Call through middleware (only path)
    return middleware.search(
        content_type=content_type,
        query=query,
        session_id=session_id,
        **kwargs
    )
```

**Architectural Validation:**
```python
# tests/architecture/test_middleware_enforcement.py
import ast
import os

def test_tools_cannot_import_subsystems_directly():
    """Ensure tools only import middleware, never subsystems."""
    tools_dir = "tools/"
    violations = []
    
    for root, dirs, files in os.walk(tools_dir):
        for file in files:
            if not file.endswith(".py"):
                continue
            
            path = os.path.join(root, file)
            with open(path) as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and node.module.startswith("subsystems."):
                        # Direct subsystem import detected
                        if not node.module == "subsystems.middleware":
                            violations.append(f"{path}: imports {node.module}")
    
    assert len(violations) == 0, f"Tools bypass middleware:\n" + "\n".join(violations)
```

---

### Pattern 4: Fail-Fast Middleware (Error Handling)

**Decision Tree:**
```
Middleware Failure Occurs
    │
    ├─ Is it a BEHAVIORAL concern?
    │  (prepend generation, query tracking, auth)
    │  └─> YES → FAIL THE REQUEST
    │      (Behavioral engineering requires 100% coverage)
    │
    └─ Is it OBSERVABILITY only?
       (logging, metrics, monitoring)
       └─> YES → LOG ERROR + CONTINUE
           (Observability failure shouldn't block user)
```

**Implementation:**
```python
class BehavioralMiddleware:
    """Behavioral engineering - MUST succeed."""
    
    def wrap(self, handler: Callable) -> Callable:
        def wrapped(request: Request) -> Response:
            try:
                # Generate prepend (behavioral reinforcement)
                prepend = self.generate_prepend(request)
            except Exception as e:
                # FAIL-FAST: Behavioral engineering is mandatory
                raise BehavioralEngineeringError(
                    "Cannot complete request - behavioral reinforcement required",
                    cause=e
                ) from e
            
            # Call next in chain
            response = handler(request)
            
            # Attach prepend to response
            response.prepend = prepend
            return response
        
        return wrapped


class ObservabilityMiddleware:
    """Observability - best effort."""
    
    def wrap(self, handler: Callable) -> Callable:
        def wrapped(request: Request) -> Response:
            try:
                # Log request
                self.logger.info("Request", extra={"request": request})
            except Exception as e:
                # LOG but DON'T FAIL: Observability is best-effort
                self.logger.error("Logging failed", exc_info=e)
            
            # Call next in chain (continue even if logging failed)
            response = handler(request)
            
            try:
                # Log response
                self.logger.info("Response", extra={"response": response})
            except Exception as e:
                self.logger.error("Logging failed", exc_info=e)
            
            return response
        
        return wrapped
```

**Why Distinction Matters:**
- **Behavioral Middleware:** Part of the mission - must work 100%
- **Observability Middleware:** Nice to have - degrade gracefully

---

### Pattern 5: Middleware Testing (Isolation)

**Test Layers Independently:**

```python
# Test middleware in isolation (no tools, no subsystems)
def test_prepend_generator_middleware():
    """Test prepend generation without full stack."""
    # Mock handler (simulates subsystem)
    mock_handler = Mock(return_value=Response(content="results"))
    
    # Create middleware
    middleware = PrependGeneratorMiddleware(
        query_tracker=mock_query_tracker
    )
    
    # Wrap handler
    wrapped = middleware.wrap(mock_handler)
    
    # Execute
    request = Request(query="test", session_id="abc123")
    response = wrapped(request)
    
    # Verify prepend generated
    assert response.prepend.startswith("📊 Queries:")
    assert "💡 Try:" in response.prepend
    
    # Verify handler called
    mock_handler.assert_called_once_with(request)


# Test middleware composition
def test_middleware_stack_execution_order():
    """Test middleware executes in correct order."""
    call_order = []
    
    # Create tracking middlewares
    class TrackingMiddleware:
        def __init__(self, name: str):
            self.name = name
        
        def wrap(self, handler):
            def wrapped(request):
                call_order.append(f"{self.name}_before")
                response = handler(request)
                call_order.append(f"{self.name}_after")
                return response
            return wrapped
    
    # Compose stack
    stack = MiddlewareStack([
        TrackingMiddleware("auth"),
        TrackingMiddleware("tracking"),
        TrackingMiddleware("prepend")
    ])
    
    # Execute
    stack.execute(Request())
    
    # Verify execution order
    assert call_order == [
        "auth_before",      # Outer middleware first
        "tracking_before",
        "prepend_before",
        "prepend_after",    # Inner middleware first on return
        "tracking_after",
        "auth_after"
    ]


# Test fail-fast behavior
def test_behavioral_middleware_fails_request():
    """Test that behavioral middleware failures fail the request."""
    # Create middleware that fails
    middleware = PrependGeneratorMiddleware(
        query_tracker=failing_query_tracker
    )
    
    handler = Mock(return_value=Response(content="results"))
    wrapped = middleware.wrap(handler)
    
    # Execute - should raise
    with pytest.raises(BehavioralEngineeringError) as exc_info:
        wrapped(Request(query="test", session_id="abc123"))
    
    # Verify error message helpful
    assert "behavioral reinforcement required" in str(exc_info.value)
    assert "remediation" in str(exc_info.value).lower()
    
    # Verify handler NOT called (failed before reaching it)
    handler.assert_not_called()
```

---

### Pattern 6: Middleware Configuration

**Configuration Pattern:**
```python
# config/middleware.yaml
middleware:
  behavioral:
    enabled: true
    fail_fast: true  # Fail request on error
    prepend_format: "emoji"  # vs "text"
  
  observability:
    enabled: true
    fail_fast: false  # Log error, continue
    log_level: "INFO"
    metrics_enabled: true
  
  auth:
    enabled: false  # Not needed for local dev
    fail_fast: true
```

**Loading:**
```python
class MiddlewareConfig(BaseModel):
    behavioral: BehavioralConfig
    observability: ObservabilityConfig
    auth: AuthConfig
    
    def build_stack(self) -> MiddlewareStack:
        """Build middleware stack from config."""
        middlewares = []
        
        if self.auth.enabled:
            middlewares.append(AuthMiddleware(
                fail_fast=self.auth.fail_fast
            ))
        
        if self.behavioral.enabled:
            middlewares.append(BehavioralMiddleware(
                fail_fast=self.behavioral.fail_fast,
                format=self.behavioral.prepend_format
            ))
        
        if self.observability.enabled:
            middlewares.append(ObservabilityMiddleware(
                fail_fast=self.observability.fail_fast,
                log_level=self.observability.log_level
            ))
        
        return MiddlewareStack(middlewares)
```

---

### Pattern 7: Middleware Documentation

**Document in Tool Signature:**
```python
@mcp.tool()
async def pos_search_project(
    content_type: Literal["standards", "code"],
    query: str,
    session_id: str,
    **kwargs
) -> str:
    """Search across content types with behavioral reinforcement.
    
    **Middleware Applied (Automatic):**
    - Query classification (detects query angle)
    - Query tracking (logs for behavioral analysis)
    - Prepend generation (gamification progress bars)
    - Performance monitoring (latency, result count)
    
    **Behavioral Engineering:**
    This tool enforces query-first patterns through prepends
    that appear at the top of every search result. If prepend
    generation fails, the request fails (no silent degradation).
    
    **Errors:**
    - BehavioralEngineeringError: Prepend generation failed
      → Check query_tracker, session storage
    - SessionNotFoundError: Invalid session_id
      → Ensure session_id provided from workflow context
    """
    middleware = get_middleware()
    return middleware.search(content_type, query, session_id, **kwargs)
```

---

## 📋 Checklist

**Architecture Checklist:**
- [ ] All tools import only from `subsystems.middleware` (not subsystems directly)
- [ ] Subsystems are not exported in `subsystems/__init__.py`
- [ ] Architectural validation tests enforce import rules
- [ ] One-way dependencies verified (tools → middleware → subsystems)
- [ ] No circular dependencies detected

**Middleware Checklist:**
- [ ] Behavioral middleware uses fail-fast (raises on error)
- [ ] Observability middleware degrades gracefully (logs error, continues)
- [ ] Middleware is composable (MiddlewareStack pattern)
- [ ] Middleware execution order documented
- [ ] Middleware configuration loaded from config file

**Testing Checklist:**
- [ ] Middleware tested in isolation (mocked handler)
- [ ] Middleware composition tested (execution order)
- [ ] Fail-fast behavior tested (errors propagate)
- [ ] Coverage verified (all tool calls flow through middleware)
- [ ] Architectural violations detected by tests

**Documentation Checklist:**
- [ ] Tool signatures document middleware applied
- [ ] Error types documented with remediation
- [ ] Middleware configuration documented
- [ ] Middleware execution order explained

---

## 💡 Examples

### Example 1: Complete Middleware Stack

```python
# middleware/behavioral_stack.py
from typing import Callable
from dataclasses import dataclass

@dataclass
class MiddlewareStack:
    """Compose multiple middleware into single handler."""
    
    def __init__(self):
        self.auth = AuthMiddleware()
        self.classifier = QueryClassifierMiddleware()
        self.tracker = QueryTrackerMiddleware()
        self.prepend = PrependGeneratorMiddleware()
        self.logger = ObservabilityMiddleware()
    
    def search(
        self,
        content_type: str,
        query: str,
        session_id: str,
        **kwargs
    ) -> str:
        """Execute search with full middleware stack."""
        # Build request object
        request = SearchRequest(
            content_type=content_type,
            query=query,
            session_id=session_id,
            kwargs=kwargs
        )
        
        # Compose middleware (outside-in)
        handler = self._subsystem_search
        handler = self.prepend.wrap(handler)
        handler = self.tracker.wrap(handler)
        handler = self.classifier.wrap(handler)
        handler = self.auth.wrap(handler)
        handler = self.logger.wrap(handler)
        
        # Execute composed stack
        response = handler(request)
        
        # Return formatted response
        return response.format()
    
    def _subsystem_search(self, request: SearchRequest) -> SearchResponse:
        """Call actual subsystem (innermost handler)."""
        index_manager = get_index_manager()
        results = index_manager.search(
            request.content_type,
            request.query,
            **request.kwargs
        )
        return SearchResponse(results=results)
```

### Example 2: Middleware with Config

```python
class BehavioralMiddleware:
    def __init__(self, config: BehavioralConfig):
        self.config = config
        self.prepend_gen = PrependGenerator(config.format)
        self.query_tracker = QueryTracker(config.storage_path)
    
    def wrap(self, handler: Callable) -> Callable:
        def wrapped(request: SearchRequest) -> SearchResponse:
            # Classify query
            angle = classify_query(request.query)
            
            # Track query
            try:
                self.query_tracker.log(
                    session_id=request.session_id,
                    query=request.query,
                    angle=angle
                )
            except Exception as e:
                if self.config.fail_fast:
                    raise BehavioralEngineeringError(
                        "Query tracking required", cause=e
                    ) from e
                else:
                    logger.error("Tracking failed", exc_info=e)
            
            # Call subsystem
            response = handler(request)
            
            # Generate prepend
            try:
                history = self.query_tracker.get_history(request.session_id)
                prepend = self.prepend_gen.generate(request.query, history)
                response.prepend = prepend
            except Exception as e:
                if self.config.fail_fast:
                    raise BehavioralEngineeringError(
                        "Prepend generation required", cause=e
                    ) from e
                else:
                    logger.error("Prepend generation failed", exc_info=e)
                    response.prepend = ""  # Degrade gracefully if config allows
            
            return response
        
        return wrapped
```

### Example 3: Architectural Validation

```python
# tests/architecture/test_middleware_enforcement.py
import importlib
import inspect
import sys

def test_tools_only_import_middleware():
    """Verify tools don't bypass middleware."""
    tools_module = importlib.import_module("tools")
    violations = []
    
    # Check each tool
    for name, obj in inspect.getmembers(tools_module):
        if not inspect.isfunction(obj):
            continue
        
        # Get source code
        source = inspect.getsource(obj)
        
        # Check for direct subsystem imports
        if "from subsystems.rag import" in source:
            violations.append(f"{name}: imports subsystems.rag directly")
        if "from subsystems.workflow import" in source:
            violations.append(f"{name}: imports subsystems.workflow directly")
        
        # Should only import middleware
        assert "from subsystems import get_middleware" in source or \
               "from subsystems.middleware import" in source, \
               f"{name}: doesn't use middleware"
    
    assert len(violations) == 0, \
        f"Tools bypass middleware:\n" + "\n".join(violations)


def test_subsystems_dont_export_internals():
    """Verify subsystems only export middleware."""
    import subsystems
    
    # Check __all__
    if hasattr(subsystems, "__all__"):
        for export in subsystems.__all__:
            assert "middleware" in export.lower(), \
                f"Subsystem exports {export} - should only export middleware"
    
    # Check what's actually exported
    exports = [name for name in dir(subsystems) if not name.startswith("_")]
    
    # Should only have middleware-related exports
    allowed = ["get_middleware", "Middleware", "MiddlewareStack"]
    for export in exports:
        assert export in allowed, \
            f"Subsystem exports {export} - creates bypass path"
```

---

## ⚠️ Anti-Patterns

### Anti-Pattern 1: Optional Middleware

❌ **Wrong:**
```python
# Tools can optionally use middleware
@mcp.tool()
def pos_search_project(query: str, use_middleware: bool = True):
    if use_middleware:
        return middleware.search(query)
    else:
        return index_manager.search(query)  # Bypass!
```

✅ **Correct:**
```python
# Middleware is ALWAYS used - no option
@mcp.tool()
def pos_search_project(query: str, session_id: str):
    return middleware.search(query, session_id)  # Only path
```

---

### Anti-Pattern 2: Direct Subsystem Access

❌ **Wrong:**
```python
# Tool imports subsystem directly
from subsystems.rag import IndexManager

@mcp.tool()
def pos_search_project(query: str):
    return IndexManager().search(query)  # Bypasses middleware!
```

✅ **Correct:**
```python
# Tool imports only middleware
from subsystems import get_middleware

@mcp.tool()
def pos_search_project(query: str, session_id: str):
    return get_middleware().search(query, session_id)  # Through middleware
```

---

### Anti-Pattern 3: Business Logic in Middleware

❌ **Wrong:**
```python
class SearchMiddleware:
    def wrap(self, handler):
        def wrapped(request):
            # Business logic in middleware - WRONG LAYER
            if request.query.startswith("how to"):
                results = self.handle_how_to_query(request)
            elif request.query.startswith("what is"):
                results = self.handle_what_is_query(request)
            else:
                results = handler(request)
            
            return results
        return wrapped
```

✅ **Correct:**
```python
class SearchMiddleware:
    def wrap(self, handler):
        def wrapped(request):
            # Middleware: Cross-cutting concerns only
            self.log_request(request)
            self.classify_query(request)
            
            # Business logic in subsystem
            response = handler(request)
            
            # Middleware: Transform response
            response.prepend = self.generate_prepend(request)
            return response
        return wrapped
```

---

### Anti-Pattern 4: Silent Middleware Failures

❌ **Wrong:**
```python
def wrap(self, handler):
    def wrapped(request):
        try:
            self.track_query(request)
        except Exception:
            pass  # Silent failure - no indication tracking failed
        
        return handler(request)
    return wrapped
```

✅ **Correct:**
```python
def wrap(self, handler):
    def wrapped(request):
        try:
            self.track_query(request)
        except Exception as e:
            if self.config.fail_fast:
                raise BehavioralEngineeringError(
                    "Query tracking required", cause=e
                ) from e
            else:
                logger.error("Query tracking failed", exc_info=e)
        
        return handler(request)
    return wrapped
```

---

## 📚 Related Standards

**Query these when implementing middleware:**

- `pos_search_project(content_type="standards", query="behavioral engineering patterns implementation")`
- `pos_search_project(content_type="standards", query="error message design fail-fast patterns")`
- `pos_search_project(content_type="standards", query="structured logging observability")`
- `pos_search_project(content_type="standards", query="Pydantic configuration patterns")`
- `pos_search_project(content_type="standards", query="testing architecture boundaries")`

---

## 📊 When to Query This Standard

| Scenario | Query | Why |
|----------|-------|-----|
| Building new tool | `middleware architecture patterns` | Need middleware integration |
| Adding middleware | `how to structure middleware layers` | Need composition pattern |
| Testing middleware | `testing middleware in isolation` | Need test patterns |
| Debugging bypass | `preventing middleware bypass` | Need architectural enforcement |
| Error handling | `middleware fail-fast patterns` | Need error handling rules |
| Configuration | `middleware configuration patterns` | Need config structure |

---

**Version:** 1.0.0  
**Created:** 2025-11-04  
**Last Updated:** 2025-11-04  
**Next Review:** After Ouroboros implementation

