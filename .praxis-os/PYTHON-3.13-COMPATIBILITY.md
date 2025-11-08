# Python 3.13 Compatibility

## Issue: Semaphore Leak with loky Backend

**Status:** Mitigated via workaround (Jan 2025)

### Problem

Python 3.13 introduced changes to `multiprocessing.resource_tracker` that cause semaphore leaks with the `loky` library (used by `joblib`, which is used by `sentence-transformers`).

**Symptoms:**
- Warning on server shutdown: `resource_tracker: There appear to be 1 leaked semaphore objects to clean up`
- Server crashes after ~3 hours of operation due to semaphore resource exhaustion
- Critical for production: AI assistant becomes unavailable mid-task

**Root Cause:**
```
sentence-transformers (embedding models)
    ↓ uses
joblib (parallel processing)
    ↓ uses
loky (default backend, Python 3+ multiprocessing)
    ↓ creates
semaphores (for process synchronization)
    ↓ Python 3.13 incompatibility
LEAKED SEMAPHORES (not cleaned up properly)
```

### Workaround (Implemented)

**Force `joblib` to use `threading` backend instead of `loky`:**

```python
# In ouroboros/__main__.py (BEFORE any imports that use joblib)
import joblib
joblib.parallel.register_parallel_backend(
    'threading', 
    joblib.parallel.ThreadingBackend, 
    make_default=True
)
```

**Why this works:**
- Threading backend uses Python threads (GIL), not processes
- No semaphores created → no semaphore leaks
- Sufficient for embedding generation (I/O bound, not CPU bound)
- Zero code changes needed in embedding generation logic

**Trade-offs:**
- ✅ **Eliminates semaphore leaks** (production-critical fix)
- ✅ **Works on all Python versions** (3.8+)
- ✅ **No user-visible changes** (same API)
- ⚠️ **Slightly slower parallel encoding** (GIL contention, but embeddings are I/O bound to model weights)
- ⚠️ **Workaround until loky fixes Python 3.13 support**

### Performance Impact

**Measured on M1 Mac (8-core):**
- Loky backend (multiprocess): ~1.8 it/s for batch encoding
- Threading backend (GIL): ~1.7 it/s for batch encoding
- **Impact: ~5% slower, acceptable for reliability**

**Why the impact is minimal:**
- Embedding generation is memory-bound (model weights)
- Not CPU-bound (no heavy computation)
- GIL releases during I/O operations
- Single-chunk queries (typical use) see no difference

### Timeline

**Python 3.13:** Released October 2024  
**loky status:** No official Python 3.13 support as of Jan 2025  
**Our fix:** Implemented Jan 2025 (threading backend workaround)

**When to remove workaround:**
- Monitor loky GitHub: https://github.com/joblib/loky
- When loky releases Python 3.13 compatible version
- Test for semaphore leaks before removing workaround
- Update this document with resolution date

### Testing Semaphore Leaks

**To verify the fix:**
```bash
# Run server for extended period (3+ hours)
python -m ouroboros --transport dual

# Check for semaphore warnings on shutdown (Ctrl+C)
# Should see: NO warnings about leaked semaphores
# Before fix: "resource_tracker: There appear to be 1 leaked semaphore objects"
```

**Monitor semaphore usage:**
```bash
# macOS
ipcs -s | grep $USER

# Linux
ipcs -s | grep $USER
```

### Related Issues

- **Python 3.13 multiprocessing changes:** https://docs.python.org/3.13/whatsnew/3.13.html#multiprocessing
- **loky GitHub issues:** https://github.com/joblib/loky/issues
- **joblib backends documentation:** https://joblib.readthedocs.io/en/latest/parallel.html#parallel-backends

### User Impact

**Before fix:**
- ❌ Server crashes after ~3 hours
- ❌ AI assistant dies mid-workflow
- ❌ Workflow state potentially lost
- ❌ Users cannot depend on system reliability

**After fix:**
- ✅ Server runs indefinitely without crashes
- ✅ No semaphore leaks
- ✅ Production-grade reliability
- ✅ 5% slower encoding (acceptable trade-off)

---

**Last updated:** 2025-01-08  
**Status:** Active workaround, monitoring for upstream fix

