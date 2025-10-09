# Python Concurrency Standards
# Generated for: agent-os-enhanced

## Universal Concurrency Principles

> **See universal standards:**
> - [Race Conditions](../../universal/concurrency/race-conditions.md)
> - [Deadlocks](../../universal/concurrency/deadlocks.md)
> - [Locking Strategies](../../universal/concurrency/locking-strategies.md)
> - [Shared State Analysis](../../universal/concurrency/shared-state-analysis.md)

These universal standards contain timeless CS fundamentals. This document applies them to Python-specific contexts.

---

## The GIL (Global Interpreter Lock)

### What is the GIL?

The **Global Interpreter Lock (GIL)** is a mutex in CPython that protects access to Python objects, preventing multiple threads from executing Python bytecode simultaneously.

### Why Does the GIL Exist?

- **Memory management safety**: CPython's memory management is not thread-safe
- **Simplifies C extension integration**: Makes single-threaded assumptions safe
- **Performance**: Faster for single-threaded code (no lock overhead everywhere)

### When the GIL Matters

| Task Type | GIL Impact | Performance |
|-----------|------------|-------------|
| **CPU-bound** (computations) | GIL prevents true parallelism | ❌ Threading doesn't help |
| **I/O-bound** (network, disk, database) | GIL released during I/O | ✅ Threading works well |
| **Mixed workloads** | Varies by operation | ⚠️ Profile first |

---

## Python Concurrency Models

Python offers three distinct concurrency models:

### 1. Threading (`threading` module)

**Best for:** I/O-bound tasks where GIL is released

```python
import threading
import requests

def fetch_url(url):
    """GIL released during network I/O"""
    response = requests.get(url)
    return response.text

urls = ["https://api1.com", "https://api2.com", "https://api3.com"]
threads = [threading.Thread(target=fetch_url, args=(url,)) for url in urls]

for thread in threads:
    thread.start()
for thread in threads:
    thread.join()
```

**When to use:**
- Network requests
- File I/O operations
- Database queries
- External API calls

### 2. Multiprocessing (`multiprocessing` module)

**Best for:** CPU-bound tasks that need true parallelism

```python
from multiprocessing import Pool

def compute_intensive(data):
    """Bypasses GIL - true parallelism"""
    return sum(x**2 for x in data)

data_chunks = [range(1000), range(1000, 2000), range(2000, 3000)]

with Pool(processes=4) as pool:
    results = pool.map(compute_intensive, data_chunks)
```

**When to use:**
- Heavy computations
- Data processing
- Image/video processing
- Scientific computing

### 3. Asyncio (`asyncio` module)

**Best for:** High-concurrency I/O with cooperative multitasking

```python
import asyncio
import aiohttp

async def fetch_url(session, url):
    """Single-threaded cooperative concurrency"""
    async with session.get(url) as response:
        return await response.text()

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

asyncio.run(main())
```

**When to use:**
- High-concurrency I/O (1000+ connections)
- WebSocket servers
- Async web frameworks (FastAPI, aiohttp)
- Event-driven architecture

---

## Python Locking Primitives

Mapping universal concepts to Python:

| Universal Concept | Python Implementation | When to Use |
|-------------------|----------------------|-------------|
| **Mutex** | `threading.Lock` | Simple mutual exclusion |
| **Reentrant Lock** | `threading.RLock` | Nested function calls with same lock |
| **Semaphore** | `threading.Semaphore` | Resource pooling (e.g., connection pool) |
| **Event** | `threading.Event` | Signaling between threads |
| **Condition Variable** | `threading.Condition` | Complex synchronization patterns |
| **Read-Write Lock** | *(not built-in)* Use `threading.RLock` + custom logic |

---

## Code Examples

### Thread-Safe Counter (Basic Locking)

```python
import threading

class ThreadSafeCounter:
    """Thread-safe counter using Lock."""
    
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()
    
    def increment(self):
        """Increment counter atomically."""
        with self._lock:  # Context manager ensures release
            self._value += 1
    
    def decrement(self):
        """Decrement counter atomically."""
        with self._lock:
            self._value -= 1
    
    def get_value(self):
        """Get current value atomically."""
        with self._lock:
            return self._value

# Usage
counter = ThreadSafeCounter()

threads = [threading.Thread(target=counter.increment) for _ in range(1000)]
for thread in threads:
    thread.start()
for thread in threads:
    thread.join()

print(counter.get_value())  # Guaranteed to be 1000
```

### Resource Pool with Semaphore

```python
import threading
import time

class ConnectionPool:
    """Connection pool with max concurrency limit."""
    
    def __init__(self, max_connections=5):
        self._semaphore = threading.Semaphore(max_connections)
        self._connections = []
        self._lock = threading.Lock()
    
    def acquire_connection(self):
        """Acquire connection from pool (blocks if pool full)."""
        self._semaphore.acquire()
        with self._lock:
            conn = self._create_connection()
            self._connections.append(conn)
            return conn
    
    def release_connection(self, conn):
        """Release connection back to pool."""
        with self._lock:
            self._connections.remove(conn)
            conn.close()
        self._semaphore.release()
    
    def _create_connection(self):
        """Create new connection (placeholder)."""
        return object()

# Usage
pool = ConnectionPool(max_connections=3)

def worker():
    conn = pool.acquire_connection()
    try:
        time.sleep(0.1)  # Simulate work
    finally:
        pool.release_connection(conn)

# Only 3 workers can have connections at once
threads = [threading.Thread(target=worker) for _ in range(10)]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

### Event Signaling Between Threads

```python
import threading
import time

# Event for signaling
ready_event = threading.Event()

def worker():
    """Worker waits for ready signal."""
    print("Worker: Waiting for ready signal...")
    ready_event.wait()  # Blocks until set()
    print("Worker: Received signal, starting work!")
    # Do work

def coordinator():
    """Coordinator prepares and signals."""
    print("Coordinator: Preparing...")
    time.sleep(2)  # Simulate preparation
    print("Coordinator: Ready! Signaling workers.")
    ready_event.set()  # Wake up all waiting threads

# Start workers first
workers = [threading.Thread(target=worker) for _ in range(3)]
for w in workers:
    w.start()

# Coordinator signals when ready
threading.Thread(target=coordinator).start()

for w in workers:
    w.join()
```

---

## Your Project Context: agent-os-enhanced

### Detected Patterns

✅ **Threading usage detected**: `mcp_server/agent_os_rag.py`, `mcp_server/rag_engine.py`  
❌ **No asyncio detected**: Consider adding async support for I/O operations  
✅ **File watching**: Uses `watchdog` for monitoring standards changes  
✅ **MCP server**: Long-running server process with concurrent tool invocations

### Concurrency Considerations for This Project

#### 1. File Watcher Thread Safety

The `AgentOSFileWatcher` uses threading for monitoring file changes:

```python
# From agent_os_rag.py
class AgentOSFileWatcher(FileSystemEventHandler):
    def __init__(self, ...):
        self._rebuild_lock = threading.Lock()
        self._last_rebuild = 0
    
    def on_modified(self, event):
        with self._rebuild_lock:  # ✅ Proper locking
            # Rebuild index
```

**Best practice:** Always use locks when modifying shared state in file system event handlers.

#### 2. RAG Engine Thread Safety

Vector database queries may be called concurrently from multiple MCP tool invocations:

```python
# Ensure LanceDB queries are thread-safe
class RAGEngine:
    def __init__(self, ...):
        self._query_lock = threading.RLock()  # Reentrant for nested calls
    
    def search(self, query: str, ...):
        with self._query_lock:
            # Vector search
```

**Recommendation:** LanceDB operations should be protected with locks if called from multiple threads.

#### 3. Workflow State Management

The `StateManager` persists workflow state to disk:

```python
class StateManager:
    def __init__(self, ...):
        self._state_lock = threading.Lock()
    
    def save_state(self, session_id, state):
        with self._state_lock:  # ✅ Prevent concurrent writes
            # Write to disk
```

**Critical:** File I/O operations must be synchronized to prevent corruption.

### Recommendations for This Project

1. **Audit all shared state**: Use [Shared State Analysis](../../universal/concurrency/shared-state-analysis.md) framework
2. **Consider asyncio**: If adding web endpoints or high-concurrency I/O
3. **Test with concurrent clients**: Simulate multiple Cursor agents calling MCP tools simultaneously
4. **Use `threading.RLock` for nested calls**: If methods call each other while holding locks
5. **Profile under load**: Identify whether GIL is a bottleneck (likely not for I/O-heavy MCP operations)

---

## Testing Concurrency in Python

### Race Condition Detection

```python
import threading
import time

def test_race_condition():
    """Test for race conditions by running many iterations."""
    counter = [0]  # Mutable shared state
    
    def increment():
        for _ in range(1000):
            # INTENTIONALLY UNSAFE (for demonstration)
            temp = counter[0]
            time.sleep(0.00001)  # Force context switch
            counter[0] = temp + 1
    
    threads = [threading.Thread(target=increment) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Expected: 10,000
    # Actual: Much less (race condition!)
    assert counter[0] == 10000, f"Race condition detected: {counter[0]}"
```

### Deadlock Detection

```python
import threading
import time

def test_deadlock():
    """Detect deadlocks using timeout."""
    lock1 = threading.Lock()
    lock2 = threading.Lock()
    
    def thread1():
        with lock1:
            time.sleep(0.1)
            # Try to acquire lock2 with timeout
            if not lock2.acquire(timeout=1.0):
                raise RuntimeError("Deadlock detected in thread1")
            lock2.release()
    
    def thread2():
        with lock2:
            time.sleep(0.1)
            if not lock1.acquire(timeout=1.0):
                raise RuntimeError("Deadlock detected in thread2")
            lock1.release()
    
    t1 = threading.Thread(target=thread1)
    t2 = threading.Thread(target=thread2)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
```

---

## Common Pitfalls in Python Concurrency

### ❌ Pitfall 1: Assuming Threading Speeds Up CPU-Bound Code

```python
# DON'T: Threading for CPU-bound work
import threading

def cpu_bound():
    return sum(i**2 for i in range(10_000_000))

threads = [threading.Thread(target=cpu_bound) for _ in range(4)]
# This will be SLOWER than single-threaded due to GIL!
```

✅ **Use multiprocessing instead:**

```python
from multiprocessing import Pool

def cpu_bound():
    return sum(i**2 for i in range(10_000_000))

with Pool(processes=4) as pool:
    results = pool.map(cpu_bound, range(4))
# True parallelism - 4x faster!
```

### ❌ Pitfall 2: Forgetting to Release Locks

```python
# DON'T: Manual lock management
lock = threading.Lock()
lock.acquire()
do_work()  # If this raises, lock never released!
lock.release()
```

✅ **Use context managers:**

```python
with lock:  # Guaranteed release even on exceptions
    do_work()
```

### ❌ Pitfall 3: Shared Mutable State Without Locking

```python
# DON'T: Unprotected shared list
shared_list = []

def append_items():
    for i in range(1000):
        shared_list.append(i)  # RACE CONDITION!
```

✅ **Use locks or thread-safe collections:**

```python
from queue import Queue

shared_queue = Queue()  # Thread-safe built-in

def append_items():
    for i in range(1000):
        shared_queue.put(i)  # Safe!
```

---

## References

- [Python `threading` documentation](https://docs.python.org/3/library/threading.html)
- [Python `multiprocessing` documentation](https://docs.python.org/3/library/multiprocessing.html)
- [Python `asyncio` documentation](https://docs.python.org/3/library/asyncio.html)
- [Universal Race Conditions Standard](../../universal/concurrency/race-conditions.md)
- [Universal Deadlocks Standard](../../universal/concurrency/deadlocks.md)
- [Universal Locking Strategies](../../universal/concurrency/locking-strategies.md)

---

**Generated for agent-os-enhanced MCP server project. This document applies universal concurrency principles to Python-specific contexts.**
