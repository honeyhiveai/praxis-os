# Config-Driven Architecture with Dynamic Logic

**Date:** 2025-11-01  
**Audience:** prAxIs OS developers (AI agents + humans)  
**Category:** Architecture patterns, code quality

**Keywords:** config-driven architecture, dynamic logic, static patterns anti-pattern, extensibility, runtime discovery, convention over configuration, user-extensible systems, graceful degradation, importlib dynamic imports, zero-maintenance architecture, semantic patterns, fragile code avoidance

**NOT covered here:** Specific config file formats, YAML syntax, configuration validation

---

## 🎯 TL;DR

**The Core Principle:**
> Config declares intent. Dynamic logic discovers capability. Together, they create extensibility without code changes.

**Anti-pattern:** Moving hardcoded lists from code to config
**Correct pattern:** Config + dynamic discovery + graceful degradation

---

## ❌ The Problem - Static/Fragile Patterns

### What Static Patterns Look Like

```python
# ❌ STATIC/FRAGILE PATTERN
SUPPORTED_LANGUAGES = {
    "python": [".py", ".pyw"],
    "javascript": [".js", ".jsx"],
    "typescript": [".ts", ".tsx"],
}

def process_file(file, language):
    if language not in SUPPORTED_LANGUAGES:
        raise UnsupportedLanguageError(f"{language} not supported")
    
    if language == "python":
        return process_python(file)
    elif language == "javascript":
        return process_javascript(file)
    elif language == "typescript":
        return process_typescript(file)
```

### Why This Is Wrong

**Characteristics of static patterns:**
- ❌ Frozen list at coding time
- ❌ "These are the supported things" mentality
- ❌ Breaks when ecosystem adds new capabilities
- ❌ Requires code updates to add support
- ❌ Gatekeeps what users can do
- ❌ Maintenance burden (list becomes stale)

**User impact:**
```
User: "I want to use Go"
System: "Go is not in SUPPORTED_LANGUAGES"
User: "But Tree-sitter supports Go"
System: "Wait for prAxIs OS update"
→ Friction, delay, user blocked
```

---

## ✅ The Solution - Config + Dynamic Logic

### The Right Pattern

```python
# ✅ DYNAMIC PATTERN
# config.yaml
code:
  languages: [python, javascript, typescript, go, rust]

# code.py
def process_file(file, language):
    """Try to use whatever's configured and available."""
    if parser := try_import_parser(language):
        return parser.process(file)
    else:
        logger.warning(f"No parser for {language}, using fallback")
        return fallback_process(file)

def try_import_parser(language: str):
    """Dynamic import - discovers what's actually installed."""
    try:
        return importlib.import_module(f"tree_sitter_{language}")
    except ImportError:
        return None
```

### Why This Is Right

**Characteristics of dynamic patterns:**
- ✅ Discovers at runtime what's available
- ✅ "Use whatever exists" mentality
- ✅ Adapts to ecosystem changes automatically
- ✅ No code updates needed for new capabilities
- ✅ User-extensible (just edit config + install dependency)
- ✅ Zero-maintenance (conventions handle new cases)

**User impact:**
```
User: "I want to use Go"
User: pip install tree-sitter-go
User: Adds "go" to config
System: Discovers tree-sitter-go, uses it
→ Immediate, no waiting, user empowered
```

---

## 🏗️ Architecture Patterns

### Pattern 1: Dynamic Import

**Use when:** Capability depends on optional dependencies

```python
def get_capability(name: str):
    """Try to import, gracefully degrade if missing."""
    try:
        return importlib.import_module(name)
    except ImportError:
        return None

# Usage
for lang in config["languages"]:
    if parser := get_capability(f"tree_sitter_{lang}"):
        use_parser(parser)
    else:
        logger.info(f"Skipping {lang} (not installed)")
```

### Pattern 2: Convention-Based Discovery

**Use when:** Ecosystem follows predictable naming conventions

```python
# Convention: tree-sitter-{lang} package name
def discover_parsers():
    """Discover what's installed using conventions."""
    for lang in config["languages"]:
        module_name = f"tree_sitter_{lang.replace('-', '_')}"
        if parser := try_import(module_name):
            yield lang, parser
```

### Pattern 3: Runtime Introspection

**Use when:** Need to validate availability before use

```python
def get_available_models():
    """Only return what's actually available."""
    requested = config["embedding"]["models"]
    return [m for m in requested if model_exists(m)]
```

### Pattern 4: Graceful Degradation

**Use when:** Fallback behavior is acceptable

```python
def parse_code(source, language):
    """Try best method, fall back to simpler methods."""
    if tree_sitter_available(language):
        return parse_with_ast(source)  # Best
    elif pygments_available(language):
        return parse_with_lexer(source)  # Good
    else:
        return parse_with_keywords(source)  # Acceptable
```

### Pattern 5: Duck Typing / Protocol-Based

**Use when:** Behavior matters more than type

```python
def use_index(index):
    """Don't check type, check capability."""
    # ❌ if isinstance(index, StandardsIndex):
    # ✅ if hasattr(index, 'search'):
    if callable(getattr(index, 'search', None)):
        return index.search(query)
```

---

## 📋 Config-Driven Architecture Principles

### Principle 1: Config Declares Intent, Not Capability

**Config says:** "I want to use these languages"
**Code discovers:** "These are actually available"

```yaml
# Config = User's intent
code:
  languages: [python, go, rust, zig]  # What user wants
```

```python
# Code = Discovery of capability
available = [lang for lang in config["languages"] 
             if parser_exists(lang)]  # What's possible
```

### Principle 2: Conventions Over Hardcoded Mappings

**❌ Don't create frozen mapping files:**
```yaml
# language_mappings.yaml - WRONG!
python:
  extensions: [".py"]
  package: "tree-sitter-python"
javascript:
  extensions: [".js"]
  package: "tree-sitter-javascript"
# ... becomes stale immediately
```

**✅ Use conventions:**
```python
# Rely on ecosystem conventions
# Pattern: tree-sitter-{language}
def get_parser_package(language: str) -> str:
    return f"tree-sitter-{language}"
```

### Principle 3: User Extension Without Code Changes

**Design goal:** Users can extend system by editing config + installing dependencies

```yaml
# User wants to add Zig support
code:
  languages: [python, typescript, zig]  # ← Just add this
  patterns: ["*.py", "*.ts", "*.zig"]   # ← And this
```

```bash
# Then install the dependency
pip install tree-sitter-zig
```

**System automatically:**
- Discovers `tree-sitter-zig` is installed
- Dynamically imports it
- Uses it for parsing

**No prAxIs OS code change required.**

---

## 🎯 How This Applies to prAxIs OS

### Example 1: Language Support

**Config-driven:**
```yaml
code:
  languages: [python, typescript, go]
```

**Dynamic logic:**
```python
for lang in config["code"]["languages"]:
    if parser := importlib.import_module(f"tree_sitter_{lang}"):
        index_language(parser, lang)
```

**Result:** All Tree-sitter languages supported (50+), user picks what they need

### Example 2: File Watching

**Config-driven:**
```yaml
file_watcher:
  code:
    patterns: ["*.py", "*.ts", "*.go"]
```

**Dynamic logic:**
```python
if any(fnmatch(file, p) for p in config["patterns"]):
    trigger_rebuild()
```

**Result:** Any file pattern works, no code knows about languages

### Example 3: Embedding Models

**Config-driven:**
```yaml
vector:
  model: BAAI/bge-small-en-v1.5
```

**Dynamic logic:**
```python
model = SentenceTransformer(config["vector"]["model"])
```

**Result:** Any sentence-transformers model works, user switches by editing config

---

## ⚠️ Common Mistakes

### Mistake 1: Config as Whitelist

**Wrong:**
```python
if feature in config["supported_features"]:
    execute_feature(feature)
else:
    raise Error("Feature not supported")
```

**This just moves hardcoded list to config!**

**Right:**
```python
for feature in config["requested_features"]:
    if impl := discover_implementation(feature):
        execute_feature(impl)
    else:
        log_warning(f"No implementation for {feature}")
```

### Mistake 2: Per-Type Logic

**Wrong:**
```python
if language == "python":
    return process_python()
elif language == "javascript":
    return process_javascript()
# Add new language = add new elif
```

**Right:**
```python
if processor := get_processor(language):
    return processor.process()
# Add new language = install module + edit config
```

### Mistake 3: Frozen Data Structures

**Wrong:**
```python
LANGUAGE_MAPPINGS = {
    "python": {"ext": ".py", "parser": "tree-sitter-python"},
    # ... frozen at coding time
}
```

**Right:**
```python
def get_parser(language):
    """Use conventions, discover at runtime."""
    return try_import(f"tree_sitter_{language}")
```

---

## 🔍 How to Recognize Static Patterns in Your Code

**Ask yourself:**

1. **"If the ecosystem adds X, does my code need to change?"**
   - Yes = Static pattern, needs refactor
   - No = Dynamic pattern, good

2. **"Can users extend this without waiting for a prAxIs OS update?"**
   - No = Static pattern, needs refactor
   - Yes = Dynamic pattern, good

3. **"Am I checking against a hardcoded list?"**
   - Yes = Static pattern, use discovery instead

4. **"Will this mapping file become stale?"**
   - Yes = Don't create it, use conventions

5. **"Am I using if/elif chains for types/categories?"**
   - Yes = Use dynamic dispatch/import instead

---

## ✅ Decision Checklist

**When designing a feature, prefer:**

- ✅ Runtime discovery over compile-time enumeration
- ✅ Conventions over hardcoded mappings
- ✅ Dynamic imports over static imports
- ✅ Duck typing over type checking
- ✅ Graceful degradation over hard failures
- ✅ User-extensible over framework-gated
- ✅ Config declares intent over config as whitelist

---

## 📊 Real-World Impact

### Before (Static Pattern)

**Code:**
```python
SUPPORTED = ["python", "javascript", "typescript"]
if lang not in SUPPORTED:
    raise Error()
```

**User experience:**
- Wants to use Go → blocked
- Waits for framework update → weeks/months
- Framework updates code → new release
- User upgrades → finally works

**Timeline:** Weeks to months

### After (Dynamic Pattern)

**Code:**
```python
if parser := try_import(f"tree_sitter_{lang}"):
    use_parser(parser)
```

**User experience:**
- Wants to use Go → edits config
- `pip install tree-sitter-go` → done
- System discovers & uses it → works immediately

**Timeline:** Minutes

---

## 🎓 The Philosophy

**Traditional thinking:**
> "What should we support? Let's enumerate all cases."

**prAxIs OS thinking:**
> "What conventions can we rely on? Let's discover what exists."

**Result:**
- Users aren't blocked by framework limitations
- Framework doesn't need constant updates
- Ecosystem evolution benefits users immediately
- Zero maintenance for new capabilities

**This is praxis:**
- Config (theory) declares what to try
- Dynamic code (practice) discovers what works
- System learns and adapts (compounding knowledge)

---

## ❓ Questions This Answers

1. "Why don't we have a list of supported languages?"
2. "How do I add support for a new language?"
3. "Why use importlib instead of static imports?"
4. "What if a dependency isn't installed?"
5. "How does prAxIs OS stay future-proof?"
6. "Why avoid hardcoded mappings?"
7. "What makes code 'dynamic' vs 'static'?"
8. "How to design user-extensible features?"
9. "What's wrong with checking against SUPPORTED_X lists?"
10. "How to make features config-driven?"

---

## 🔗 Related Standards

- `dogfooding-model.md` - Local-first development, real paths validation
- `meta-development-patterns.md` - Framework author mindset vs consumer mindset

---

**Version:** 1.0.0  
**Created:** 2025-11-01  
**Last Updated:** 2025-11-01  
**Next Review:** After first implementation using this pattern

