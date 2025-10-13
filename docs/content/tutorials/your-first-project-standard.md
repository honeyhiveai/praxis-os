---
sidebar_position: 5
doc_type: tutorial
---

# Your First Project Standard

Let's create your first project-specific standard together. By the end of this tutorial, you'll understand how to document patterns that make Agent OS Enhanced smarter about *your* project over time.

**What you'll learn:**
- When a pattern is worth documenting
- How AI creates a standard (with heavy querying)
- How to verify it's discoverable via RAG
- The immediate benefit of having documented it

**Time:** ~15 minutes

---

## The Scenario

You're building an API and you've just implemented error handling for the third time. Each time, you've used the same pattern:

```python
# Endpoint 1
try:
    result = process_user()
except ValueError as e:
    return {"error_code": "VALIDATION_ERROR", "message": str(e)}

# Endpoint 2  
try:
    result = process_order()
except ValueError as e:
    return {"error_code": "VALIDATION_ERROR", "message": str(e)}

# Endpoint 3
try:
    result = process_payment()
except ValueError as e:
    return {"error_code": "VALIDATION_ERROR", "message": str(e)}
```

You notice the pattern. **This should be documented as a standard.**

---

## Step 1: Identify the Pattern (Human Decision)

**You say to the AI:**

> "I've noticed we're handling API errors consistently with error_code and message fields. We should create a standard for this so future work follows the same pattern."

**Why this works:**
- You recognize the reusable pattern (used 3 times)
- You make the strategic decision to document it
- You provide the context AI needs

---

## Step 2: AI Queries to Learn How (AI Process)

The AI agent doesn't just write the standard immediately. Instead, it queries to learn the proper approach:

### Query 1: Understanding Standard Structure

```python
search_standards("how to create standards structure required sections")
```

**AI discovers:**
- Purpose section (why it exists)
- Problem section (what happens without it)
- Standard section (the actual rules)
- Examples section (real code)
- Anti-patterns section (common mistakes)

### Query 2: RAG Optimization

```python
search_standards("RAG content optimization discoverability")
```

**AI discovers:**
- Include TL;DR section at top
- Add keywords for search
- Use natural language headers
- Include query hooks (questions this answers)

### Query 3: Query Construction Patterns

```python
search_standards("query construction patterns how agents search")
```

**AI discovers:**
- How future queries will be phrased
- What keywords to include
- Content-specific phrases that match semantic search

---

## Step 3: AI Creates the Standard

The AI writes the standard file:

**File:** `.agent-os/standards/development/api-error-handling.md`

```markdown
# API Error Handling Standard

**Keywords for search**: API errors, error handling, error responses, exception handling, error format, validation errors, API exceptions

---

## 🎯 TL;DR - API Error Handling Quick Reference

**Core Principle:** All API errors return structured responses with error_code and message fields for consistent client handling.

**Required fields:**
- `error_code`: String constant (UPPER_SNAKE_CASE)
- `message`: Human-readable error description

**Optional fields:**
- `details`: Additional structured context

**Example:**
```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Invalid email format",
  "details": {"field": "email", "value": "notanemail"}
}
```

---

## 🎯 Purpose

Define consistent error response format across all API endpoints. This enables:
- Predictable client-side error handling
- Consistent user experience
- Easier debugging and monitoring
- Type-safe error responses

**Questions This Answers:**
- How should I format API error responses?
- What fields are required in error objects?
- How do I handle different types of errors (validation, business logic, system)?
- What error codes should I use?

---

## ⚠️ The Problem Without This Standard

**Without consistent error format:**

```python
# Endpoint 1
return {"error": str(e)}

# Endpoint 2  
return {"message": str(e), "code": 400}

# Endpoint 3
raise HTTPException(detail=str(e))
```

**Problems:**
- Clients must handle multiple error formats
- No machine-readable error codes
- Inconsistent debugging experience
- Type safety impossible
- Error monitoring fragmented

---

## ✅ The Standard

### Required Response Format

All API errors MUST return this JSON structure:

```json
{
  "error_code": "<ERROR_CODE>",
  "message": "<human-readable-message>",
  "details": <optional-structured-data>
}
```

### Error Codes

Use UPPER_SNAKE_CASE constants:

```python
VALIDATION_ERROR     # Invalid input data
BUSINESS_LOGIC_ERROR # Business rule violation
NOT_FOUND            # Resource doesn't exist
UNAUTHORIZED         # Authentication required
FORBIDDEN            # Insufficient permissions
INTERNAL_ERROR       # System/unexpected errors
```

### Implementation Pattern

```python
# Define custom exception
class APIError(Exception):
    def __init__(self, code: str, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details

# Use in endpoints
@app.post("/users")
def create_user(data: UserCreate):
    try:
        # Validation
        if not is_valid_email(data.email):
            raise APIError(
                code="VALIDATION_ERROR",
                message="Invalid email format",
                details={"field": "email", "value": data.email}
            )
        
        # Business logic
        if email_exists(data.email):
            raise APIError(
                code="BUSINESS_LOGIC_ERROR",
                message="Email already registered",
                details={"field": "email"}
            )
        
        return create_user_record(data)
    
    except APIError as e:
        return JSONResponse(
            status_code=400,
            content={
                "error_code": e.code,
                "message": e.message,
                "details": e.details
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error_code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": None
            }
        )
```

---

## 📋 Checklist

Before merging code that handles errors:

- [ ] All errors return JSON with `error_code` and `message` fields
- [ ] Error codes use UPPER_SNAKE_CASE constants
- [ ] Validation errors use `VALIDATION_ERROR` code
- [ ] Business logic errors use `BUSINESS_LOGIC_ERROR` code
- [ ] System errors use `INTERNAL_ERROR` code
- [ ] Optional `details` field used for additional context
- [ ] Error responses are type-safe
- [ ] Tests verify error response format

---

## ❌ Anti-Patterns

**Don't return raw exceptions:**
```python
❌ return {"error": str(e)}
❌ raise HTTPException(detail=str(e))
```

**Don't use inconsistent formats:**
```python
❌ return {"message": str(e)}        # Missing error_code
❌ return {"code": 400, "error": e}  # Wrong field names
```

**Don't use vague error codes:**
```python
❌ "ERROR"           # Too generic
❌ "error_1"         # Not descriptive
❌ "InvalidInput"    # Wrong case format
```

**Don't expose internal details:**
```python
❌ return {"error": str(exception), "trace": traceback.format_exc()}
```

---

## 🧪 Testing

Verify error handling:

```python
def test_validation_error_format():
    response = client.post("/users", json={"email": "invalid"})
    assert response.status_code == 400
    data = response.json()
    assert "error_code" in data
    assert "message" in data
    assert data["error_code"] == "VALIDATION_ERROR"

def test_business_logic_error_format():
    response = client.post("/users", json={"email": "exists@example.com"})
    data = response.json()
    assert data["error_code"] == "BUSINESS_LOGIC_ERROR"
    assert "details" in data
```

---

**Version:** 1.0.0  
**Created:** 2025-10-12  
**Last Updated:** 2025-10-12  
**Next Review:** When error handling patterns change
```

**What happened:**
- AI queried heavily (3+ times) to learn proper structure
- AI created RAG-optimized content (keywords, TL;DR, query hooks)
- AI included all required sections
- AI optimized for its own future discovery

---

## Step 4: Verify RAG Indexing

The file watcher automatically detects the new standard. Within ~5 seconds, it's indexed.

**You can verify by asking AI:**

> "Search for our API error handling standards"

**AI queries:**

```python
search_standards("API error handling")
```

**Result:** Returns your new standard in top 3 results! ✅

---

## Step 5: See It in Action

Now when AI works on a new API endpoint:

**You say:**

> "Create a new endpoint POST /products that validates product data"

**AI automatically:**

```python
# AI queries before implementing
search_standards("API error handling")
# Discovers your standard

# Implements following your pattern
@app.post("/products")
def create_product(data: ProductCreate):
    try:
        if not data.name:
            raise APIError(
                code="VALIDATION_ERROR",
                message="Product name is required",
                details={"field": "name"}
            )
        
        if data.price < 0:
            raise APIError(
                code="VALIDATION_ERROR",
                message="Price must be positive",
                details={"field": "price", "value": data.price}
            )
        
        return create_product_record(data)
    
    except APIError as e:
        return JSONResponse(
            status_code=400,
            content={
                "error_code": e.code,
                "message": e.message,
                "details": e.details
            }
        )
```

**Notice:**
- AI followed your standard automatically
- No need to explain the error format
- Consistent with existing endpoints
- **This is knowledge compounding in action!**

---

## What You Accomplished

✅ **Identified a reusable pattern** (after 3rd usage)

✅ **Collaborated with AI** (you decided, AI created)

✅ **AI queried heavily** (learned proper structure and optimization)

✅ **Created discoverable standard** (RAG-optimized with keywords)

✅ **Verified it works** (AI found it via search)

✅ **Saw immediate benefit** (next endpoint used it automatically)

**Most importantly:** This standard will benefit every future API endpoint in your project. You solved the problem once, documented it, and it compounds forever.

---

## Key Takeaways

### 1. Pattern Recognition

Look for patterns that appear 2-3+ times:
- Error handling formats
- Naming conventions
- Code organization patterns
- Integration approaches
- Testing strategies

### 2. Human-AI Collaboration

- **Human decides**: "This should be documented"
- **AI creates**: Queries heavily, writes properly formatted standard
- **Result**: High-quality, discoverable documentation

### 3. Query-Driven Quality

AI creates good standards because it queries:
- How to structure standards
- How to optimize for RAG
- How future queries will search

This ensures consistency and discoverability.

### 4. Immediate ROI

The very next task that touches this area benefits. No waiting, no "someday this will be useful"—it's useful immediately.

### 5. Compounds Over Time

- **Today**: 1 standard (API errors)
- **Next week**: 5 standards
- **Next month**: 20 standards
- **Next quarter**: AI is an expert in your codebase

---

## Next Steps

**Practice More:**
- Create a standard for database query patterns
- Document your testing conventions
- Capture your naming standards

**Learn the Complete Process:**
- Read [Creating Project Standards](../how-to-guides/creating-project-standards) for comprehensive guide
- See [Standards Reference](../reference/standards) for more examples

**Understand Why It Works:**
- Read [Knowledge Compounding](../explanation/knowledge-compounding) for the full concept

**Remember:** Every standard makes the next 10 tasks better. Keep documenting patterns as you discover them.

---

## Troubleshooting

### "AI can't find my standard via search"

**Likely causes:**
- RAG hasn't re-indexed yet (wait 5-10 seconds)
- Missing keywords in the standard
- Query not matching content

**Fix:** Ask AI to query: `search_standards("exact title of your standard")`

### "Standard isn't being followed automatically"

**Likely causes:**
- AI didn't query before implementing
- Query didn't return your standard (not in top 3 results)
- Standard lacks clear examples

**Fix:** 
1. Ask AI: "Did you search for our [topic] standards?"
2. Improve standard with more keywords/examples
3. Query: `search_standards("RAG optimization")` to learn how to improve discoverability

### "Not sure if pattern is worth documenting"

**Ask yourself:**
- Will I use this 2-3+ more times? → Document it
- Does this need to be consistent across the project? → Document it
- Would future AI benefit from knowing this? → Document it
- Is this project-specific (not universal)? → Document it

When in doubt, document it. The cost is low, the benefit compounds.

---

## Related Documentation

- **[Creating Project Standards](../how-to-guides/creating-project-standards)** - Complete how-to guide
- **[Knowledge Compounding](../explanation/knowledge-compounding)** - Why this works
- **[Standards Reference](../reference/standards)** - Browse existing standards

