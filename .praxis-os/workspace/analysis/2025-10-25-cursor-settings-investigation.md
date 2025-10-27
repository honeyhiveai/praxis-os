# Cursor Settings Investigation - Conversation Storage

**Date**: 2025-10-25
**Status**: Investigation Complete
**Finding**: No conversation storage settings found

---

## Current Cursor Settings

**Your `settings.json`** (11 settings total):
```json
{
    "python.analysis.typeCheckingMode": "standard",
    "workbench.editor.wrapTabs": true,
    "security.workspace.trust.untrustedFiles": "open",
    "explorer.confirmDelete": false,
    "makefile.configureOnOpen": false,
    "containers.containerClient": "com.microsoft.visualstudio.containers.docker",
    "containers.orchestratorClient": "com.microsoft.visualstudio.orchestrators.dockercompose",
    "cursorpyright.analysis.typeCheckingMode": "standard",
    "git.autofetch": true,
    "biome.suggestInstallingGlobally": false,
    "editor.accessibilitySupport": "on"
}
```

**Notable absence**: No `cursor.*` namespace settings configured

---

## What Cursor Settings Control

Based on documentation search, Cursor provides settings for:

### 1. **Agent Modes** (UI-based, not settings.json)
- Agent Mode (complex coding tasks)
- Ask Mode (read-only exploration)
- Manual Mode (explicit control)
- Custom Mode (user-defined workflows)
- Switched via UI or `Ctrl+.`

### 2. **Agent Security** (May have settings.json equivalents)
- Tool call approvals (require user approval for risky actions)
- Network request restrictions
- Workspace trust

### 3. **Enterprise Policies** (Admin-controlled)
- Allowed extensions
- Allowed team IDs
- Centrally managed via device management

### 4. **Background Agents** (environment.json, not settings.json)
- Environment setup
- Install/startup commands
- GitHub integration

---

## Missing: Conversation/History Storage Settings

### What We Looked For
- `cursor.chat.*` - Not found
- `cursor.composer.*` - Not found
- `cursor.history.*` - Not found
- `cursor.storage.*` - Not found
- `cursor.conversation.*` - Not found

### What the Database Shows

**Cursor stores**:
1. User prompts (`aiService.prompts`)
2. Generation metadata (`aiService.generations`)
3. Session metadata (`composer.composerData`)

**Cursor does NOT store**:
- Full AI responses
- Complete conversation threads

### Implications

**This appears to be a design decision, not a configurable setting.**

Cursor's architecture:
- Stores enough to show session stats (lines changed, context usage)
- Stores user prompts (for history/reuse)
- Does NOT persist full conversation locally
- Likely relies on:
  - In-memory conversation during session
  - Context compaction happens in-memory
  - Only metadata persists to disk

---

## Comparison: Cursor vs Claude Code

| Aspect | Cursor | Claude Code |
|--------|--------|-------------|
| **Philosophy** | Ephemeral conversation + metadata | Full conversation persistence |
| **Storage** | User prompts + stats | Every message, complete content |
| **Size** | ~100KB total | 2.1MB per session |
| **Settings** | No conversation storage options | JSONL by default |
| **Use Case** | IDE-focused (metadata sufficient) | CLI-focused (full history needed) |

---

## Conclusion

**No Cursor settings control conversation storage** - this is architectural.

**Why Cursor likely does this**:
1. **Performance**: Smaller database, faster lookups
2. **Privacy**: Full conversations not on disk
3. **Design**: IDE session is temporary, metadata is permanent
4. **Context compaction**: Happens in-memory, not from stored history

**For your Pull Model**:
- Cursor: Would need Push Model (explicit logging) or accept metadata-only
- Claude Code: Pull Model works perfectly (full history available)

**Alternative for Cursor**: 
- Could build MCP tool that logs conversations as they happen (Push Model)
- Agent explicitly calls `log_conversation()` after each exchange
- Gives you full history even though Cursor doesn't persist it

---

## Recommendation

**Accept platform differences**:

1. **Claude Code**: Use Pull Model
   - Extract from `~/.claude/projects/`
   - Full conversation available retroactively
   - All summarization strategies possible

2. **Cursor**: Use Push Model OR Metadata-Only
   - **Option A**: MCP tool for explicit logging
   - **Option B**: Extract what's available (prompts + metadata)
   - **Option C**: Rely on Cursor's in-memory compaction

**Most pragmatic**: Start with Claude Code (proven viable), add Cursor support later if needed.

---

**Status**: Investigation complete - No hidden settings found
**Next**: Decide on implementation strategy given platform differences

