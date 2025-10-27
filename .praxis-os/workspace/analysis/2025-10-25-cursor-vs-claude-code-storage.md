# Cursor vs Claude Code: Session Storage Comparison

**Date**: 2025-10-25
**Status**: Empirical Investigation
**Author**: Research Session

---

## Key Finding

**Claude Code**: ✅ Stores FULL conversation content locally (2.1MB for 414 messages)  
**Cursor**: ❓ SQLite only contains metadata (543 bytes) - **FULL CONTENT LOCATION UNKNOWN**

---

## Claude Code Storage (VALIDATED)

### Location
```
~/.claude/projects/{project-path-escaped}/{session-id}.jsonl
```

### Content
- **Format**: JSONL (one message per line)
- **Completeness**: 100% - Every user prompt and AI response
- **Size**: 2.1MB for current session (414 messages)
- **Metadata**: Tokens, model, timestamps, request IDs

### Example Record
```json
{
    "type": "assistant",
    "message": {
        "model": "claude-haiku-4-5-20251001",
        "content": [{"type": "text", "text": "..."}],
        "usage": {
            "input_tokens": 1325,
            "output_tokens": 99
        }
    },
    "timestamp": "2025-10-25T18:55:19.424Z",
    "sessionId": "abc97593-1886-4e8f-b5f6-6923e029a97e"
}
```

---

## Cursor Storage (INCOMPLETE PICTURE)

### What We Found

**SQLite Database Location**:
```
~/Library/Application Support/Cursor/User/workspaceStorage/{workspace-hash}/state.vscdb
```

**Database Size**: 60-200KB (across various workspaces)

**Content**: METADATA ONLY
```json
{
    "allComposers": [
        {
            "composerId": "44b1051e-af49-4b8e-8e9f-7b18d911af17",
            "name": "Generate python-sdk for honeyhive",
            "lastUpdatedAt": 1756329605895,
            "createdAt": 1756318187658,
            "unifiedMode": "agent",
            "hasUnreadMessages": false
        }
    ]
}
```

**Size**: 543 bytes for `composer.composerData` key

---

## What Cursor SQLite Contains

### Tables
- `ItemTable` - Key-value storage
- `cursorDiskKV` - Additional key-value data

### Largest Keys (by data size)
1. `aiService.generations` - 5657 bytes
2. `terminal.integrated.environmentVariableCollectionsV2` - 2499 bytes
3. `aiService.prompts` - 1741 bytes
4. `composer.composerData` - 543 bytes (session metadata)

### What's in `composer.composerData`
- ❌ No conversation messages
- ❌ No user prompts
- ❌ No AI responses
- ✅ Session IDs
- ✅ Session names/titles
- ✅ Timestamps (created, updated)
- ✅ Mode (chat/agent/edit)

---

## Where Is Cursor's Full Conversation?

### Hypothesis 1: Ephemeral (Not Persisted)
**Theory**: Cursor keeps conversation in memory, only persists metadata  
**Evidence**: Database is too small for full content  
**Problem**: Contradicts documentation claiming "history panel" access

### Hypothesis 2: Different Storage Location
**Theory**: Full content stored somewhere else (not in SQLite)  
**Checked**:
- ❌ No `.jsonl` files in Cursor directories
- ❌ No large conversation files found
- ❌ History directory contains code file versions, not conversations
- ❌ No obvious conversation database

**Unchecked**:
- ? Cloud storage (Cursor sync service)
- ? IndexedDB (browser-style storage)
- ? Proprietary binary format
- ? Encrypted storage

### Hypothesis 3: Context Compaction ≠ Storage
**Theory**: Cursor's "context compaction" is in-memory only  
**Implication**: Sessions aren't fully persisted; only summaries/metadata  
**Aligns with**: Our observation that SQLite only has metadata

---

## Practical Implications

### For Pull Model

**Claude Code**: ✅ **IDEAL CANDIDATE**
- Full conversation accessible
- Easy extraction (JSONL format)
- Retroactive access to all history
- No platform-specific API needed

**Cursor**: ❌ **PROBLEMATIC**
- Full conversation location unknown
- May not be persisted at all
- SQLite only has metadata
- Would need platform API or reverse engineering

### For Session Continuity

**Claude Code**:
- Can extract full history any time
- Build any summarization strategy
- Index conversation for RAG
- Support all your use cases

**Cursor**:
- May rely on Cursor's internal compaction
- Cannot extract full retroactive history
- Would need Push Model (explicit logging)
- Or use Cursor's API if one exists

---

## Size Comparison

| Platform | Storage Type | Content | Size (414 msg session) |
|----------|-------------|---------|----------------------|
| **Claude Code** | JSONL | Full conversation | 2.1MB |
| **Cursor** | SQLite | Metadata only | 543 bytes |
| **Ratio** | - | - | **3,800x difference** |

The size difference suggests Cursor either:
1. Doesn't persist full conversations locally
2. Stores them in a location we haven't found
3. Uses aggressive compression/summarization

---

## Questions for Further Investigation

1. **Does Cursor actually persist full conversations?**
   - Documentation says yes
   - Our investigation shows only metadata
   - Contradiction needs resolution

2. **Where is Cursor's conversation data?**
   - Cloud-only storage?
   - Different file format we missed?
   - Truly ephemeral (memory-only)?

3. **Can Cursor API provide conversation history?**
   - Does Cursor expose an API to extensions?
   - Could an MCP tool query it?

4. **What happens at context compaction in Cursor?**
   - Is full history consulted?
   - Or just metadata/summaries?
   - Does it access cloud storage?

---

## Recommendation

**Given current findings**:

1. **Start with Claude Code** - We have confirmed full access to conversation data
2. **Build extraction + summarization tools** for Claude Code first
3. **Test different summarization strategies** on known data
4. **Investigate Cursor more deeply** or accept Push Model for Cursor users

**Next steps**:
1. ✅ Validated Claude Code storage (complete)
2. ⏳ Determine if Cursor full content is accessible
3. ⏳ Design extraction API based on what's available
4. ⏳ Implement summarization tools

---

**Status**: Claude Code validated, Cursor investigation incomplete

