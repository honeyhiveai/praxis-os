# Claude Code Session Storage Format - Validated

**Date**: 2025-10-25
**Status**: Empirical Validation Complete
**Author**: Research Session

---

## Summary

**Validated**: Claude Code DOES store full conversation history locally in structured JSONL format.

**Key Finding**: Unlike Cursor (which stores only metadata in SQLite), Claude Code stores **complete conversation content** including all messages, tool calls, and token usage.

---

## Storage Location

```
~/.claude/projects/{project-path-escaped}/{session-id}.jsonl
```

**Example**:
```
~/.claude/projects/-Users-josh-src-github-com-honeyhiveai-agent-os-enhanced/abc97593-1886-4e8f-b5f6-6923e029a97e.jsonl
```

**Project path encoding**: Slashes become dashes (`/` → `-`)

---

## File Format

**Format**: JSONL (JSON Lines - one JSON object per line)  
**Encoding**: UTF-8  
**Structure**: One message per line, chronological order

---

## Message Schema

### User Message
```json
{
    "parentUuid": null,
    "isSidechain": true,
    "userType": "external",
    "cwd": "/Users/josh/src/github.com/honeyhiveai/agent-os-enhanced",
    "sessionId": "abc97593-1886-4e8f-b5f6-6923e029a97e",
    "version": "2.0.26",
    "gitBranch": "main",
    "type": "user",
    "message": {
        "role": "user",
        "content": "Warmup"
    },
    "uuid": "ee69cfa4-f4c1-4c7f-a9d2-7e0daeb4936f",
    "timestamp": "2025-10-25T18:55:16.442Z"
}
```

### Assistant Message
```json
{
    "parentUuid": "ee69cfa4-f4c1-4c7f-a9d2-7e0daeb4936f",
    "isSidechain": true,
    "userType": "external",
    "cwd": "/Users/josh/src/github.com/honeyhiveai/agent-os-enhanced",
    "sessionId": "abc97593-1886-4e8f-b5f6-6923e029a97e",
    "version": "2.0.26",
    "gitBranch": "main",
    "message": {
        "model": "claude-haiku-4-5-20251001",
        "id": "msg_012LkDcNCLmg1xxSUEq85FzR",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "I understand the instructions..."
            }
        ],
        "stop_reason": null,
        "stop_sequence": null,
        "usage": {
            "input_tokens": 1325,
            "cache_creation_input_tokens": 0,
            "cache_read_input_tokens": 0,
            "cache_creation": {
                "ephemeral_5m_input_tokens": 0,
                "ephemeral_1h_input_tokens": 0
            },
            "output_tokens": 99,
            "service_tier": "standard"
        }
    },
    "requestId": "req_011CUURd9eFprDy8esfVvXei",
    "type": "assistant",
    "uuid": "d4519fdd-2af7-4604-b80b-c5142c1d7fb3",
    "timestamp": "2025-10-25T18:55:19.424Z"
}
```

---

## Message Types

**Observed in current session (414 messages, 2.1MB)**:
- `user`: 186 messages - User prompts/questions
- `assistant`: 226 messages - AI responses  
- `system`: 2 messages - System events/metadata

---

## Key Fields

### Common Fields (All Messages)
- `sessionId`: UUID for the conversation
- `uuid`: Unique ID for this message
- `timestamp`: ISO 8601 timestamp
- `type`: Message type (`user`, `assistant`, `system`)
- `message`: The actual content
- `cwd`: Working directory at time of message
- `gitBranch`: Git branch at time of message
- `version`: Claude Code version
- `parentUuid`: Links to previous message (conversation threading)

### Assistant-Specific Fields
- `message.model`: Model used (e.g., `claude-haiku-4-5-20251001`)
- `message.usage`: Token usage breakdown
  - `input_tokens`: Tokens in prompt
  - `output_tokens`: Tokens in response
  - Cache metrics (ephemeral_5m, ephemeral_1h)
- `requestId`: Anthropic API request ID

---

## Other Claude Code Files

### Command History
**File**: `~/.claude/history.jsonl`  
**Content**: User command history (prompts only, no AI responses)  
**Format**:
```json
{
    "display": "what mcp servers do you see",
    "pastedContents": {},
    "timestamp": 1761343856281,
    "project": "/Users/josh/src/github.com/honeyhiveai/agent-os-enhanced"
}
```

### Session Environment
**Directory**: `~/.claude/session-env/`  
**Content**: Session-specific environment data (one directory per session UUID)  
**Purpose**: Unknown (directories are empty in current observation)

### Shell Snapshots
**Directory**: `~/.claude/shell-snapshots/`  
**Content**: Shell environment snapshots (large .sh files, ~200KB each)  
**Size**: 3.8MB total across ~20 snapshots

### Todos
**Directory**: `~/.claude/todos/`  
**Content**: Per-session TODO tracking  
**Format**: JSON files named `{session-id}-agent-{session-id}.json`

---

## Comparison with Cursor Storage

| Aspect | Claude Code | Cursor |
|--------|-------------|--------|
| **Format** | JSONL (full messages) | SQLite (metadata only) |
| **Content** | Complete conversation | Summary statistics |
| **Messages** | Every user/assistant exchange | Aggregated session info |
| **Tokens** | Per-message usage tracking | Total session usage |
| **Size** | 2.1MB for 414 messages | ~5KB per session |
| **Extractability** | Easy (line-by-line JSONL) | Medium (SQL query required) |
| **Completeness** | 100% - Full conversation | ~10% - Statistics only |

---

## Implications for Pull Model

### ✅ **Claude Code is IDEAL for Pull Model**

1. **Full conversation history available** - No need for logging
2. **Structured format** - JSONL is trivial to parse
3. **Complete metadata** - Timestamps, tokens, model versions all captured
4. **Easy extraction** - No database required, just read JSONL
5. **Retroactive access** - Can process historical sessions

### Extraction Strategy

```python
def extract_claude_code_session(session_id: str, project_path: str) -> List[Dict]:
    """Extract full conversation from Claude Code storage."""
    
    # Construct file path
    project_escaped = project_path.replace("/", "-")
    session_file = Path(f"~/.claude/projects/{project_escaped}/{session_id}.jsonl").expanduser()
    
    # Parse JSONL
    messages = []
    with session_file.open() as f:
        for line in f:
            messages.append(json.loads(line))
    
    return messages

def get_user_assistant_pairs(messages: List[Dict]) -> List[Tuple[str, str]]:
    """Extract user-assistant exchange pairs."""
    
    pairs = []
    for i, msg in enumerate(messages):
        if msg["type"] == "user":
            # Find next assistant response
            for j in range(i+1, len(messages)):
                if messages[j]["type"] == "assistant":
                    user_content = msg["message"]["content"]
                    ai_content = messages[j]["message"]["content"][0]["text"]
                    pairs.append((user_content, ai_content))
                    break
    
    return pairs
```

---

## Summarization Options

Given full conversation access, we can build multiple summarization tools:

### 1. **Full Session Summary**
- Process all 414 messages
- Generate comprehensive overview
- Extract key decisions, code changes, topics

### 2. **Windowed Summary** 
- "Summarize last N messages"
- "Summarize messages from timestamp X to Y"
- Useful for understanding recent context

### 3. **Topic-Based Summary**
- Group messages by semantic topic
- Summarize each topic cluster
- Create hierarchical summary

### 4. **Decision Point Extraction**
- Identify architectural decisions
- Track problem-solving paths
- Document key insights

### 5. **Token Usage Analysis**
- Track token consumption over time
- Identify expensive queries
- Optimize prompting strategies

---

## Next Steps

1. **Build extraction tool** - Python utility to read Claude Code sessions
2. **Test summarization** - Try different prompts/approaches on full session
3. **Compare with Cursor** - Extract Cursor metadata, compare what's possible
4. **Design unified API** - Abstract over platform differences
5. **Implement MCP tools** - On-demand summarization via MCP

---

## Questions for Josh

1. **Priority**: Which summarization mode is most useful?
   - Full session digest?
   - Last N turns?
   - Contextual "what did we discuss about X"?

2. **Use case**: When would you invoke summarization?
   - Before context compaction?
   - On session resume?
   - On-demand when you need to recall?

3. **Storage**: Should summaries be:
   - Indexed in RAG?
   - Stored as markdown files?
   - Ephemeral (generate on demand)?

4. **Cross-platform**: Start with Claude Code (easiest) or build unified from the start?

---

**Status**: Ready for implementation once strategy is decided.

