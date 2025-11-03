# Date Usage Policy - prAxIs OS

**Category**: AI Safety  
**Priority**: Critical  
**Enforcement**: Mandatory for all AI-generated content

---

## 🎯 TL;DR - Date Usage Policy Quick Reference

**Keywords for search**: date usage, current date, AI date errors, date format, ISO date, current_date tool, date consistency, date policy

**Core Principle:** AI assistants MUST use the `current_date` MCP tool for ALL date-related operations. NEVER hardcode or assume dates.

**The Problem:**
- AI uses wrong dates from training data
- Inconsistent date formats in same document
- Hardcoded dates instead of querying system
- Creates confusion and maintenance issues

**The Solution:**
```python
result = await current_date()
date = result["iso_date"]  # "2025-10-06" - Use this for everything
```

**Mandatory Usage:**
- ✅ Creating specs → Call `current_date` first for directory names
- ✅ Documentation headers → Use ISO format from tool
- ✅ Version history → Query current date, don't assume
- ✅ Any timestamp → Always call tool first

**Standard Format:**
- **ISO 8601**: YYYY-MM-DD (e.g., "2025-10-06")
- **Directory names**: YYYY-MM-DD-feature-name
- **Headers**: `**Date**: 2025-10-06`
- **NEVER**: "Jan 30, 2025", "01/30/2025", "10-06-2025"

**Enforcement:**
- Code review flags hardcoded dates
- Validation fails on inconsistent formats
- Specs without correct date headers rejected

**Common Scenarios:**
- Creating spec → `current_date()` → `.praxis-os/specs/{iso_date}-feature/`
- Adding header → `current_date()` → `**Date**: {iso_date}`
- Version history → `current_date()` → `### v1.0.0 ({iso_date})`

**Why This Matters:**
- Professional appearance
- Accurate documentation
- Easy sorting/filtering
- No manual corrections needed

---

## ❓ Questions This Answers

1. "How do I get the current date?"
2. "What date format should I use?"
3. "Can I hardcode dates?"
4. "How do I create date-based directory names?"
5. "What is the current_date tool?"
6. "Why do AI assistants use wrong dates?"
7. "How do I format dates in documentation?"
8. "What date format for specs?"
9. "How to ensure date consistency?"
10. "What happens if I use wrong date?"

---

## Problem Statement

AI assistants (LLMs) consistently make date-related errors due to knowledge cutoff dates and lack of real-time awareness. This manifests as:

1. **Wrong Dates**: Using old dates from training data (e.g., "2025-01-30" when current is "2025-10-06")
2. **Inconsistent Formats**: Mixing date formats within same document
3. **Hardcoded Values**: Manually typing dates instead of querying system
4. **Context Confusion**: Uncertain about current date during generation

These errors create confusion, unprofessional appearance, and maintenance issues.

---

## How to Get the Current Date? (current_date Tool)

prAxIs OS provides a `current_date` MCP tool that AI assistants MUST use when dealing with dates.

### Tool Usage

```python
# Call the MCP tool
result = await current_date()

# Primary field for all uses:
date = result["iso_date"]  # "2025-10-06"

# Other available fields:
result["iso_datetime"]       # "2025-10-06T14:30:00.123456"
result["day_of_week"]        # "Monday"
result["month"]              # "October"
result["year"]               # 2025
result["formatted"]["header"]  # "**Date**: 2025-10-06"
```

---

## What Are the Mandatory Usage Patterns?

These patterns MUST be followed for all date-related operations.

### Pattern 1: Creating Specifications

**ALWAYS call `current_date` first:**

```markdown
# ✅ Correct
1. Call current_date tool → get "2025-10-06"
2. Create directory: .praxis-os/specs/2025-10-06-feature-name/
3. Add header: **Date**: 2025-10-06

# ❌ Wrong
1. Assume date is 2025-01-30
2. Create directory with wrong date
3. User has to correct manually
```

### Pattern 2: Documentation Headers

```markdown
# ✅ Correct
**Date**: 2025-10-06
**Last Updated**: 2025-10-06
**Review Date**: 2025-11-06

# ❌ Wrong
**Date**: January 30, 2025  (wrong format)
**Last Updated**: 01/30/2025  (wrong format and date)
```

### Pattern 3: Directory Naming

```bash
# ✅ Correct
.praxis-os/specs/2025-10-06-api-design/
.praxis-os/specs/2025-10-06-testing-framework/

# ❌ Wrong
.praxis-os/specs/2025-01-30-new-feature/  (wrong date)
.praxis-os/specs/oct-6-2025-feature/  (wrong format)
```

---

## What Is the Standard Date Format?

Always use ISO 8601 format for consistency and machine readability.

**Use ISO 8601 format exclusively:**
- **Format**: `YYYY-MM-DD`
- **Example**: `2025-10-06`
- **Rationale**: Sortable, unambiguous, internationally recognized

**Never use:**
- ❌ `MM/DD/YYYY` (US format, ambiguous)
- ❌ `DD-MM-YYYY` (European format, ambiguous)
- ❌ `Month Day, Year` (verbose, hard to parse)
- ❌ `YYYY/MM/DD` (uses slashes, harder to parse in filenames)

---

## How Is Date Policy Enforced?

Multiple enforcement mechanisms ensure compliance with date usage standards.

### Rule 1: No Hardcoded Dates
**NEVER** hardcode dates in generated content. Always query `current_date` tool.

```python
# ❌ FORBIDDEN
date = "2025-01-30"  # Hardcoded!

# ✅ REQUIRED
result = await current_date()
date = result["iso_date"]
```

### Rule 2: Consistent Format
All dates in a single generation session MUST use the same format.

### Rule 3: Validate Before Use
After calling `current_date`, verify the returned date makes sense:
- Is it Monday when expected to be Monday?
- Is it October when expected to be October?

If something seems wrong, alert the user.

---

## What Are Common Date Usage Scenarios?

Real-world examples of proper date usage with the current_date tool.

### Scenario 1: Creating New Spec Directory

```python
# Step 1: Get current date
result = await current_date()
date = result["iso_date"]  # "2025-10-06"

# Step 2: Create directory
spec_name = "authentication-redesign"
directory = f".praxis-os/specs/{date}-{spec_name}"
os.makedirs(directory)

# Step 3: Create README with date header
readme_content = f"""# Specification: {spec_name}

{result['formatted']['header']}
**Status**: Draft
**Last Updated**: {date}

## Overview
...
"""
```

### Scenario 2: Updating Existing Documentation

```python
# Get current date for "Last Updated" field
result = await current_date()
last_updated = result["iso_date"]

# Update header
content = f"""
**Created**: 2025-09-15  (preserve original)
**Last Updated**: {last_updated}  (use current)
"""
```

### Scenario 3: Planning Future Dates

```python
# Get current date
result = await current_date()
today = result["iso_date"]

# For future dates, explain the calculation
# Don't just add days blindly - be explicit
review_date = "2025-11-06"  # 30 days from 2025-10-06

content = f"""
**Created**: {today}
**Review Date**: {review_date}  (30 days from creation)
"""
```

---

## What Errors Does current_date Prevent?

Understanding the errors prevented by proper date usage.

### Pre-Generation Checklist
Before generating any content with dates:
- [ ] Call `current_date` tool
- [ ] Store result in variable
- [ ] Verify date makes sense
- [ ] Use ISO 8601 format
- [ ] Apply consistently

### Post-Generation Validation
After generating content with dates:
- [ ] All dates use ISO 8601 format
- [ ] All dates are correct (not from training data)
- [ ] Directory names match file headers
- [ ] Future dates have explanation

---

## What Is the Impact of This Policy?

Following this policy:
- ✅ **Eliminates date errors**: No more wrong dates in specs
- ✅ **Professional appearance**: Consistent, correct formatting
- ✅ **Easy maintenance**: Clear audit trail of changes
- ✅ **Better organization**: Sortable, chronological structure

---

## 🔍 When to Query This Standard

| Situation | Example Query |
|-----------|---------------|
| **Getting date** | `pos_search(content_type="standards", query="how to get current date")` |
| **Date format** | `pos_search(content_type="standards", query="what date format to use")` |
| **Creating specs** | `pos_search(content_type="standards", query="date format for specs")` |
| **current_date tool** | `pos_search(content_type="standards", query="current_date tool")` |
| **Date consistency** | `pos_search(content_type="standards", query="date consistency AI")` |
| **Hardcoding dates** | `pos_search(content_type="standards", query="can I hardcode dates")` |
| **ISO format** | `pos_search(content_type="standards", query="ISO date format")` |
| **Date errors** | `pos_search(content_type="standards", query="AI date errors")` |

---

## 🔗 Related Standards

**Query workflow for date usage:**

1. **Start with date policy** → `pos_search(content_type="standards", query="date usage policy")` (this document)
2. **Learn MCP tools** → `pos_search(content_type="standards", query="MCP usage guide")` → `usage/mcp-usage-guide.md`
3. **Understand specs** → `pos_search(content_type="standards", query="creating specs")` → `usage/creating-specs.md`
4. **Learn production rules** → `pos_search(content_type="standards", query="production code checklist")` → `standards/ai-safety/production-code-checklist.md`

**By Category:**

**AI Safety:**
- `standards/ai-safety/credential-file-protection.md` - File protection rules → `pos_search(content_type="standards", query="credential file protection")`
- `standards/ai-safety/production-code-checklist.md` - Production requirements → `pos_search(content_type="standards", query="production code checklist")`
- `standards/ai-safety/git-safety-rules.md` - Git operation safety → `pos_search(content_type="standards", query="git safety rules")`

**Usage:**
- `usage/creating-specs.md` - Specification creation → `pos_search(content_type="standards", query="creating specs")`
- `usage/mcp-usage-guide.md` - MCP tools usage → `pos_search(content_type="standards", query="MCP usage guide")`

**AI Assistant:**
- `standards/ai-assistant/MCP-TOOLS-GUIDE.md` - Complete MCP tools reference → `pos_search(content_type="standards", query="MCP tools guide")`

---

## Version History

- **2025-10-06**: Initial policy created with `current_date` tool
