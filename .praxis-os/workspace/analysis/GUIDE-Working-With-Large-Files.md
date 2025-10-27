# Working With Large Files - Strategies

When dealing with files that exceed context window limits (like the 1.7MB session export), use these approaches:

## 1. Chunked Reading (Best for Sequential Analysis)

```bash
# Read first 100 lines to understand structure
head -n 100 other-sessions/cline_task_oct-11-2025_1-16-57-pm.md

# Read last 100 lines to see outcomes
tail -n 100 other-sessions/cline_task_oct-11-2025_1-16-57-pm.md

# Read specific line range (e.g., lines 1000-1100)
sed -n '1000,1100p' other-sessions/cline_task_oct-11-2025_1-16-57-pm.md

# Read middle section
sed -n '25000,25100p' other-sessions/cline_task_oct-11-2025_1-16-57-pm.md
```

## 2. Search-Based Analysis (Best for Finding Specific Content)

```bash
# Find all error messages
grep -n "error\|Error\|ERROR" other-sessions/cline_task_oct-11-2025_1-16-57-pm.md

# Find tool uses with context (5 lines before/after)
grep -A 5 -B 5 "<execute_command>" other-sessions/cline_task_oct-11-2025_1-16-57-pm.md

# Count occurrences of patterns
grep -c "<attempt_completion>" other-sessions/cline_task_oct-11-2025_1-16-57-pm.md

# Find user messages
grep -n "# User Message" other-sessions/cline_task_oct-11-2025_1-16-57-pm.md
```

## 3. Extract Key Sections

```bash
# Get task description (usually near start)
head -n 200 other-sessions/cline_task_oct-11-2025_1-16-57-pm.md | grep -A 20 "<task>"

# Get completion attempts
grep -A 10 "<attempt_completion>" other-sessions/cline_task_oct-11-2025_1-16-57-pm.md

# Get all tool uses summary
grep -o "<[a-z_]*>" other-sessions/cline_task_oct-11-2025_1-16-57-pm.md | sort | uniq -c
```

## 4. Split File into Manageable Chunks

```bash
# Split into 10,000 line chunks
split -l 10000 other-sessions/cline_task_oct-11-2025_1-16-57-pm.md other-sessions/chunk_

# This creates: chunk_aa, chunk_ab, chunk_ac, etc.
# Then read each chunk individually
```

## 5. Create Summary File

```bash
# Extract just the task, user messages, and completions
{
  echo "=== TASK ==="
  head -n 100 other-sessions/cline_task_oct-11-2025_1-16-57-pm.md | grep -A 20 "<task>"
  echo -e "\n=== USER MESSAGES ==="
  grep -B 2 "# User Message" other-sessions/cline_task_oct-11-2025_1-16-57-pm.md | head -n 50
  echo -e "\n=== COMPLETIONS ==="
  grep -A 10 "<attempt_completion>" other-sessions/cline_task_oct-11-2025_1-16-57-pm.md
  echo -e "\n=== ERRORS ==="
  grep -i "error" other-sessions/cline_task_oct-11-2025_1-16-57-pm.md | head -n 30
} > other-sessions/session_summary.md
```

## 6. Progressive Analysis Workflow

1. **Start with structure**: `head -n 100` to see format
2. **Identify sections**: Look for markers like "# User Message", "<task>", etc.
3. **Extract relevant parts**: Use grep/sed to pull specific sections
4. **Analyze in chunks**: Work through file in 100-1000 line sections
5. **Summarize findings**: Create a condensed version with key insights

## 7. Using search_files (When Available)

The `search_files` tool is designed for this - it searches and returns matches with context:

```
search_files(
  path="other-sessions",
  regex="pattern_to_find",
  file_pattern="*.md"
)
```

## Example: Analyzing the 1.7MB Session File

```bash
# Step 1: Understand the structure
echo "=== FILE STRUCTURE ===" && head -n 50 other-sessions/cline_task_oct-11-2025_1-16-57-pm.md

# Step 2: Find the original task
echo -e "\n=== ORIGINAL TASK ===" && head -n 200 other-sessions/cline_task_oct-11-2025_1-16-57-pm.md | grep -A 30 "<task>"

# Step 3: Count interactions
echo -e "\n=== INTERACTION COUNT ===" && grep -c "# User Message" other-sessions/cline_task_oct-11-2025_1-16-57-pm.md

# Step 4: Find errors/issues
echo -e "\n=== ERRORS ===" && grep -in "error\|failed\|issue" other-sessions/cline_task_oct-11-2025_1-16-57-pm.md | head -n 20

# Step 5: See final outcome
echo -e "\n=== FINAL SECTION ===" && tail -n 100 other-sessions/cline_task_oct-11-2025_1-16-57-pm.md
```

## Best Practice

**Never use `read_file` on files over 500KB.** Instead:
1. Use command-line tools for extraction
2. Create targeted summaries
3. Analyze in progressive chunks
4. Use search_files for pattern-based analysis
