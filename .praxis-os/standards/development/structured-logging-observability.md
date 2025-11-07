# Structured Logging for Observability

**Keywords for search**: structured logging, JSON logging, observability, logging patterns, query diversity logging, behavioral metrics, session tracking, correlation IDs, log levels, logging best practices, queryable logs, jq logs, performance logging, error logging, behavioral drift logging, metrics collection

---

## 🚨 TL;DR - Structured Logging Quick Reference

**Core Principle:** Logs should be machine-readable (JSON), queryable (`jq`), and contain context (session_id, timestamp, behavioral metrics) for observability and drift detection.

**The Pattern:**
```python
logger.info(
    "Search completed",
    extra={
        "session_id": session_id,
        "query": query,
        "angle_detected": "implementation",
        "result_count": 5,
        "latency_ms": 45.2,
        "diversity_score": 0.60
    }
)
```

**Output (JSON):**
```json
{
  "timestamp": "2025-11-04T10:30:45.123Z",
  "level": "INFO",
  "message": "Search completed",
  "session_id": "abc123",
  "query": "how to implement X",
  "angle_detected": "implementation",
  "result_count": 5,
  "latency_ms": 45.2,
  "diversity_score": 0.60
}
```

**Critical Requirements:**
- ✅ JSON format (machine-readable)
- ✅ Timestamp in ISO 8601
- ✅ Session ID for correlation
- ✅ Behavioral metrics (query diversity, angle)
- ✅ Performance metrics (latency, counts)
- ✅ Queryable with `jq`

**Common Anti-Patterns:**
- ❌ String concatenation ("User abc123 searched for X")
- ❌ No structured data (can't query)
- ❌ Missing session ID (can't correlate)
- ❌ Missing timestamps (can't order events)
- ❌ No behavioral metrics (can't detect drift)

---

## ❓ Questions This Answers

1. "How do I implement structured logging?"
2. "What should be in log records?"
3. "How do I log behavioral metrics?"
4. "How do I track query diversity in logs?"
5. "How do I correlate logs across requests?"
6. "How do I make logs queryable with jq?"
7. "What log levels should I use?"
8. "How do I log performance metrics?"
9. "How do I log errors with context?"
10. "How do I format log timestamps?"
11. "How do I log session-to-session data?"
12. "What fields are required in logs?"
13. "How do I query logs for behavioral analysis?"
14. "How do I detect behavioral drift from logs?"
15. "How do I structure log files?"

---

## 🎯 Purpose

Define patterns for structured logging that enables observability, behavioral drift detection, and performance analysis through machine-readable, queryable log data.

**Key Distinction:** Structured vs Unstructured Logs
- **Structured:** JSON, queryable, contains metrics (this standard)
- **Unstructured:** Text strings, grep-able, hard to analyze

**Why This Matters:** Behavioral engineering requires measuring query diversity, session-to-session improvement, and drift detection. String logs ("User searched for X") don't provide structured data for analysis. JSON logs enable `jq` queries for metrics extraction.

---

## ❌ The Problem

**Without structured logging:**

1. **Unqueryable Logs**
   ```python
   logger.info(f"User {session_id} searched for {query} and got {count} results")
   ```
   - Can't extract session_id reliably
   - Can't calculate query diversity
   - Can't detect behavioral drift
   - Regex parsing is fragile

2. **No Behavioral Metrics**
   ```python
   logger.info("Search completed")
   ```
   - What angle was queried?
   - How many times this session?
   - What's the diversity score?
   - Can't measure compounding

3. **No Correlation**
   ```python
   logger.info("Query: X")
   # ... 50 lines later ...
   logger.info("Results: 5")
   ```
   - Which query do these results belong to?
   - Different session?
   - Can't correlate events

4. **No Performance Data**
   ```python
   logger.info("Search done")
   ```
   - How long did it take?
   - How many results?
   - What was the latency?

---

## ✅ The Standard

### Pattern 1: JSON Structured Logging

**Setup:**
```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Format logs as JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add extra fields (context data)
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

# Configure logger
logger = logging.getLogger("praxis_os")
handler = logging.FileHandler(".praxis-os/logs/mcp-server.jsonl")
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

**Usage:**
```python
logger.info(
    "Search completed",
    extra={
        "session_id": "abc123",
        "query": "how to implement X",
        "content_type": "standards",
        "result_count": 5,
        "latency_ms": 45.2
    }
)
```

**Output:**
```json
{
  "timestamp": "2025-11-04T10:30:45.123Z",
  "level": "INFO",
  "logger": "praxis_os.middleware.search",
  "message": "Search completed",
  "module": "behavioral_middleware",
  "function": "wrap_search",
  "line": 42,
  "session_id": "abc123",
  "query": "how to implement X",
  "content_type": "standards",
  "result_count": 5,
  "latency_ms": 45.2
}
```

---

### Pattern 2: Required Fields

**Always Include:**

1. **Timestamp** (ISO 8601 UTC)
   ```python
   datetime.utcnow().isoformat() + "Z"
   ```

2. **Level** (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   ```python
   "level": "INFO"
   ```

3. **Session ID** (for correlation)
   ```python
   "session_id": "abc123"
   ```

4. **Component** (which part of system)
   ```python
   "component": "behavioral_middleware"
   ```

**Implementation:**
```python
def log_event(
    message: str,
    level: str,
    session_id: str,
    **extra
):
    """Log event with required fields."""
    logger.log(
        getattr(logging, level),
        message,
        extra={
            "session_id": session_id,
            "component": get_component_name(),
            **extra
        }
    )
```

---

### Pattern 3: Behavioral Metrics Logging

**Query Tracking:**
```python
logger.info(
    "Query classified",
    extra={
        "session_id": session_id,
        "query": query,
        "angle_detected": "implementation",  # 📖📍🔧⭐⚠️
        "query_count_session": 4,
        "unique_queries_session": 3,
        "angles_used": ["conceptual", "implementation"],
        "diversity_score": 0.40  # 2 of 5 angles
    }
)

logger.info(
    "Prepend generated",
    extra={
        "session_id": session_id,
        "query_count": 4,
        "unique_count": 3,
        "diversity_score": 0.40,
        "suggestion_provided": "Where is X implemented?",
        "generation_time_ms": 2.1
    }
)
```

**Session Metrics:**
```python
logger.info(
    "Session summary",
    extra={
        "session_id": session_id,
        "total_queries": 8,
        "unique_queries": 6,
        "angles_used": ["conceptual", "implementation", "location"],
        "diversity_score": 0.60,  # 3 of 5 angles
        "avg_latency_ms": 42.5,
        "session_duration_seconds": 180
    }
)
```

---

### Pattern 4: Performance Logging

**Latency Tracking:**
```python
import time

start = time.time()
result = perform_search(query)
latency_ms = (time.time() - start) * 1000

logger.info(
    "Search completed",
    extra={
        "session_id": session_id,
        "query": query,
        "latency_ms": latency_ms,
        "result_count": len(result),
        "index_type": "standards"
    }
)
```

**Operation Timing:**
```python
with Timer() as timer:
    index.rebuild()

logger.info(
    "Index rebuilt",
    extra={
        "index_type": "standards",
        "duration_seconds": timer.elapsed,
        "document_count": index.count(),
        "index_size_mb": index.size_mb
    }
)
```

---

### Pattern 5: Error Logging with Context

**Log Errors with Full Context:**
```python
try:
    result = generate_prepend(query, session_id)
except Exception as e:
    logger.error(
        "Prepend generation failed",
        extra={
            "session_id": session_id,
            "query": query,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "query_count": query_tracker.count(session_id),
            "component": "prepend_generator"
        },
        exc_info=True  # Include stack trace
    )
    raise  # Re-raise after logging
```

**Output:**
```json
{
  "timestamp": "2025-11-04T10:30:45.123Z",
  "level": "ERROR",
  "message": "Prepend generation failed",
  "session_id": "abc123",
  "query": "how to implement X",
  "error_type": "SessionStorageError",
  "error_message": "Session file not found",
  "query_count": 4,
  "component": "prepend_generator",
  "exception": "Traceback (most recent call last):\n  File ..."
}
```

---

### Pattern 6: Queryable Logs (jq Patterns)

**Log Files:**
- `.praxis-os/logs/mcp-server.jsonl` (JSONL = one JSON object per line)
- `.praxis-os/logs/queries/session-{id}.jsonl` (per-session)
- `.praxis-os/logs/behavioral-{date}.jsonl` (daily rotation)

**Query Examples:**
```bash
# Get all queries from a session
jq -r 'select(.session_id == "abc123") | .query' logs/mcp-server.jsonl

# Calculate query diversity for a session
jq -s 'map(select(.session_id == "abc123" and .angle_detected)) | 
       map(.angle_detected) | unique | length' logs/mcp-server.jsonl

# Average latency per session
jq -s 'map(select(.latency_ms)) | 
       group_by(.session_id) | 
       map({session: .[0].session_id, avg_latency: (map(.latency_ms) | add / length)})' \
       logs/mcp-server.jsonl

# Detect behavioral drift (query frequency over time)
jq -s 'group_by(.session_id) | 
       map({session: .[0].session_id, query_count: length})' \
       logs/mcp-server.jsonl
```

---

### Pattern 7: Log Levels

**Use Appropriate Levels:**

```python
# DEBUG: Detailed diagnostic info (development only)
logger.debug(
    "Query classified",
    extra={
        "query": query,
        "angle": "implementation",
        "confidence": 0.95
    }
)

# INFO: General informational messages (normal operations)
logger.info(
    "Search completed",
    extra={
        "session_id": session_id,
        "query": query,
        "result_count": 5
    }
)

# WARNING: Something unexpected but handled
logger.warning(
    "Query tracker storage near capacity",
    extra={
        "storage_used_mb": 950,
        "storage_limit_mb": 1000,
        "sessions_stored": 10000
    }
)

# ERROR: Error that needs attention (but recovered)
logger.error(
    "Query classification failed, using default",
    extra={
        "query": query,
        "error": str(e),
        "default_angle": "conceptual"
    }
)

# CRITICAL: System failure (cannot continue)
logger.critical(
    "Behavioral engineering failed - prepend generation required",
    extra={
        "session_id": session_id,
        "query": query,
        "error": str(e)
    }
)
```

---

### Pattern 8: Session-to-Session Tracking

**Log Session Lifecycle:**
```python
# Session start
logger.info(
    "Session started",
    extra={
        "session_id": session_id,
        "workflow_type": workflow_type,
        "timestamp": datetime.utcnow().isoformat()
    }
)

# Session activity
logger.info(
    "Query executed",
    extra={
        "session_id": session_id,
        "query_number": 4,
        "angle": "implementation"
    }
)

# Session end
logger.info(
    "Session completed",
    extra={
        "session_id": session_id,
        "total_queries": 8,
        "diversity_score": 0.60,
        "duration_seconds": 180,
        "workflow_completed": True
    }
)
```

**Analyze Across Sessions:**
```bash
# Compare diversity across sessions
jq -s 'map(select(.message == "Session completed")) | 
       map({session: .session_id, diversity: .diversity_score}) | 
       sort_by(.diversity)' logs/mcp-server.jsonl
```

---

## 📋 Checklist

**Format Checklist:**
- [ ] Logs are JSON (one object per line)
- [ ] Timestamp in ISO 8601 UTC
- [ ] Level included (DEBUG/INFO/WARNING/ERROR/CRITICAL)
- [ ] Component/module identified
- [ ] Session ID for correlation

**Content Checklist:**
- [ ] Behavioral metrics logged (angle, diversity, query count)
- [ ] Performance metrics logged (latency, result count)
- [ ] Errors include context (session, query, component)
- [ ] Stack traces for exceptions
- [ ] Success/failure status clear

**Query Checklist:**
- [ ] Logs queryable with `jq`
- [ ] Can extract session metrics
- [ ] Can calculate diversity scores
- [ ] Can detect drift patterns
- [ ] Can analyze performance

---

## 💡 Examples

See Pattern sections above for comprehensive examples.

---

## ⚠️ Anti-Patterns

### Anti-Pattern 1: String Concatenation

❌ **Wrong:**
```python
logger.info(f"User {session_id} searched for {query}")
```

✅ **Correct:**
```python
logger.info(
    "Search executed",
    extra={"session_id": session_id, "query": query}
)
```

---

### Anti-Pattern 2: Missing Session ID

❌ **Wrong:**
```python
logger.info("Query completed", extra={"query": query})
```

✅ **Correct:**
```python
logger.info(
    "Query completed",
    extra={"session_id": session_id, "query": query}
)
```

---

### Anti-Pattern 3: No Metrics

❌ **Wrong:**
```python
logger.info("Search done")
```

✅ **Correct:**
```python
logger.info(
    "Search completed",
    extra={
        "latency_ms": 45.2,
        "result_count": 5,
        "diversity_score": 0.60
    }
)
```

---

## 📚 Related Standards

- `pos_search_project(content_type="standards", query="behavioral engineering metrics tracking")`
- `pos_search_project(content_type="standards", query="query diversity calculation patterns")`
- `pos_search_project(content_type="standards", query="error logging with context")`

---

## 📊 When to Query This Standard

| Scenario | Query | Why |
|----------|-------|-----|
| Setting up logging | `structured logging patterns` | Need JSON logger setup |
| Behavioral metrics | `logging query diversity metrics` | Need metric patterns |
| Performance | `logging latency performance metrics` | Need timing patterns |
| Error logging | `error logging with context` | Need error patterns |
| Analysis | `querying logs with jq` | Need query patterns |

---

**Version:** 1.0.0  
**Created:** 2025-11-04  
**Last Updated:** 2025-11-04  
**Next Review:** After Ouroboros logging implementation

