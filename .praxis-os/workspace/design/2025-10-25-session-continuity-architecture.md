# Session Continuity Architecture: Platform-Agnostic Design

**Date**: 2025-10-25
**Status**: Design Phase - Brainstorming
**Author**: Claude Code + Joshua Paul
**Challenge**: Extract and index session data across different agent platforms using only MCP tooling

---

## The Core Problem

**Your Insight**: "A unified experience for all Agent OS Enhanced users should be the goal"

**The Constraint**: MCP tools are **stateless request-response** - they don't have access to the ongoing conversation

```
Agent Platform (Cursor/Claude Code/Cline)
  ↓ Has: Full conversation history
  ↓ Sends: Individual tool requests
  ↓
MCP Server (Agent OS Enhanced)
  ↓ Receives: search_standards("query")
  ↓ Has: NO access to conversation context
  ↓ Problem: Can't extract session to index it
```

**What we need to extract**:
- User messages
- AI responses
- Timestamps
- Session ID
- Topic/theme

**What we can't access from MCP tools**:
- The conversation history
- Session metadata
- Platform-specific state

---

## Constraint Analysis: What MCP Gives Us

### MCP Protocol Reality

**Request-Response Model**:
```python
# What MCP server receives:
@mcp.tool()
async def search_standards(query: str, n_results: int = 5):
    # We get: query string
    # We DON'T get:
    # - Who asked the question
    # - Previous conversation
    # - Session context
    # - Platform information
```

**No Session Access**:
- MCP servers are **stateless by design**
- Each tool call is independent
- No conversation history provided
- No platform metadata

**What we CAN access** (currently):
```python
# From the query tracker (your existing code)
session_id = extract_session_id_from_context(None)

# This extracts session ID from:
# - Request headers (if platform provides)
# - Call stack inspection (fragile)
# - Heuristics (unreliable)

# But NOT the actual conversation content
```

---

## Platform-Specific Session Storage

### Where Conversations Actually Live

**Cursor**:
```
Location: ~/Library/Application Support/Cursor/User/workspaceStorage/
Format: SQLite database (state.vscdb)
Tables:
  - composerData (conversation history)
  - composerSnapshot (state snapshots)
Access: File system (when Cursor is closed) or SQLite queries
```

**Claude Code** (VS Code Extension):
```
Location: Unknown (VS Code extension storage)
Format: Unknown (likely JSON or SQLite)
Access: Via VS Code Extension API (not accessible from MCP)
Session Management: Built-in summary generation on context limit
```

**Cline** (VS Code Extension):
```
Location: ~/.vscode/extensions/saoudrizwan.claude-dev-*/
Format: JSON files per conversation
Access: File system (easier than Cursor)
```

**The Pattern**:
- Each platform stores differently
- None expose via MCP protocol
- All require platform-specific extraction

---

## Architectural Options

### Option 1: Pull Model (MCP Server Reads Platform Storage)

**Concept**: MCP server directly reads platform-specific session storage

```
Agent Platform (Cursor)
  ↓ Stores conversation in SQLite
  ↓
File System
  └── ~/Library/.../state.vscdb
       ↑
MCP Server
  └── Reads directly (when safe)
  └── Extracts exchanges
  └── Indexes in vector DB
```

**Implementation**:
```python
# New MCP tool: extract_session_history
@mcp.tool()
async def extract_session_history(
    platform: str,  # "cursor", "claude-code", "cline"
    workspace_id: Optional[str] = None
):
    """
    Extract conversation history from platform storage.

    Only works when:
    - Platform stores locally (Cursor, Cline)
    - Agent has file system access
    - Storage format is known/stable
    """
    if platform == "cursor":
        db_path = find_cursor_workspace_db(workspace_id)
        return extract_from_cursor_sqlite(db_path)

    elif platform == "cline":
        json_path = find_cline_conversations()
        return extract_from_cline_json(json_path)

    elif platform == "claude-code":
        # Problem: Don't know where it stores
        raise NotImplementedError("Claude Code storage location unknown")
```

**Pros**:
- ✅ Works for Cursor (SQLite is accessible)
- ✅ Works for Cline (JSON files accessible)
- ✅ No platform changes needed
- ✅ Can extract full history retroactively

**Cons**:
- ❌ Platform-specific (need code for each)
- ❌ Storage formats may change (fragile)
- ❌ Doesn't work for Claude Code (unknown storage)
- ❌ File system race conditions (reading while platform writes)
- ❌ Privacy concerns (direct DB access)

---

### Option 2: Push Model (Agent Explicitly Logs)

**Concept**: Agent actively logs conversation to MCP tool

```
Agent Platform (Any)
  ↓ After each exchange
  ↓
Agent calls: log_conversation_exchange(user_msg, ai_msg, metadata)
  ↓
MCP Server
  └── Stores in conversation DB
  └── Indexes for search
  └── Available for resumption
```

**Implementation**:
```python
# New MCP tool: log_exchange
@mcp.tool()
async def log_conversation_exchange(
    user_message: str,
    ai_response: str,
    session_id: str,
    timestamp: str,
    metadata: Optional[Dict] = None
):
    """
    Log a conversation exchange for future retrieval.

    Agent explicitly calls this after each exchange.
    Enables session continuity across context resets.
    """
    # Store in conversation history DB
    conversation_db.add_exchange({
        "session_id": session_id,
        "user_message": user_message,
        "ai_response": ai_response,
        "timestamp": timestamp,
        "metadata": metadata or {}
    })

    # Embed for semantic search (using jina-embeddings-v2 for long context)
    exchange_text = f"User: {user_message}\n\nAI: {ai_response}"
    embedding = jina_model.encode(exchange_text)

    # Index in vector DB
    conversation_vector_db.add({
        "text": exchange_text,
        "vector": embedding,
        "session_id": session_id,
        "timestamp": timestamp
    })

    return {"status": "logged", "exchange_id": generate_id()}
```

**How agents would use it**:
```
Agent workflow:
1. User asks question
2. Agent generates response
3. Agent calls: log_conversation_exchange(user_q, agent_response, session_id)
4. Continue conversation

On context reset:
1. New session starts
2. Agent calls: search_conversation_history(session_id, query)
3. Retrieve relevant past exchanges
4. Include in context for continuity
```

**Pros**:
- ✅ Platform-agnostic (works with any MCP client)
- ✅ Explicit contract (agent controls what's logged)
- ✅ No platform storage dependencies
- ✅ Privacy-preserving (agent decides what to share)
- ✅ Clean separation of concerns

**Cons**:
- ❌ Requires agent cooperation (must call the tool)
- ❌ No retroactive extraction (can't get old conversations)
- ❌ Depends on agent implementation (Cursor won't call this automatically)
- ❌ Extra tool calls add latency

---

### Option 3: Hybrid Model (Pull + Push)

**Concept**: Combine both approaches based on platform capabilities

```
Platform Detection:
├── Cursor → Use Pull (SQLite extraction)
├── Cline → Use Pull (JSON extraction)
├── Claude Code → Use Push (explicit logging)
└── Unknown → Use Push (fallback)

Result: Best of both worlds
```

**Implementation**:
```python
# Unified API
@mcp.tool()
async def sync_conversation_history(
    session_id: str,
    mode: str = "auto"  # "auto", "pull", "push"
):
    """
    Sync conversation history using best available method.

    Auto mode detects platform and chooses optimal strategy.
    """
    if mode == "auto":
        platform = detect_platform()

        if platform in ["cursor", "cline"]:
            # Pull from file system
            return await pull_from_platform(platform, session_id)
        else:
            # Require explicit logging
            return {
                "status": "push_required",
                "message": "Platform requires explicit logging. Use log_conversation_exchange()."
            }

    elif mode == "pull":
        return await pull_from_platform(detect_platform(), session_id)

    elif mode == "push":
        return {"status": "ready", "message": "Use log_conversation_exchange() to log."}
```

**Pros**:
- ✅ Works across all platforms
- ✅ Optimal for each platform
- ✅ Graceful degradation

**Cons**:
- ❌ Most complex to implement
- ❌ Most complex to maintain (two code paths)

---

## Recommended Architecture: File-Based Contract

### The Insight: Use the File System as Message Bus

**Your infrastructure background suggests this**: Treat file system like a message queue

```
Agent Platform
  ↓
Writes: .praxis-os/.conversations/session-abc123.jsonl
  ↓
File Watcher (MCP Server)
  └── Detects new lines
  └── Parses exchanges
  └── Indexes automatically
```

**Why this works**:
- ✅ Platform-agnostic (all platforms can write files)
- ✅ No platform storage access needed
- ✅ Asynchronous (agent writes, server processes later)
- ✅ Append-only log (JSONL format)
- ✅ Fault-tolerant (files persist if server crashes)
- ✅ Observable (humans can read/debug)

**The Protocol**:

```jsonl
// .praxis-os/.conversations/session-abc123.jsonl

{"type":"exchange","timestamp":"2025-10-25T14:30:00Z","user":"What are embeddings?","ai":"Embeddings are...","session_id":"abc123"}
{"type":"exchange","timestamp":"2025-10-25T14:31:15Z","user":"Tell me about MTEB","ai":"MTEB is...","session_id":"abc123"}
{"type":"context_reset","timestamp":"2025-10-25T15:00:00Z","reason":"context_limit","session_id":"abc123"}
{"type":"session_resume","timestamp":"2025-10-25T15:01:00Z","previous_session":"abc123","new_session":"def456"}
```

**MCP Server Implementation**:
```python
# File watcher in MCP server startup
def watch_conversation_logs():
    """
    Watch .praxis-os/.conversations/ for new exchanges.
    Index them automatically for semantic search.
    """
    watcher = FileSystemWatcher(".praxis-os/.conversations/")

    @watcher.on_modified
    async def on_new_exchange(filepath):
        # Read new lines (since last processed)
        new_lines = read_new_lines(filepath, last_position)

        for line in new_lines:
            exchange = json.loads(line)

            if exchange["type"] == "exchange":
                # Embed and index
                text = f"User: {exchange['user']}\n\nAI: {exchange['ai']}"
                embedding = jina_model.encode(text)

                conversation_db.add({
                    "text": text,
                    "vector": embedding,
                    "session_id": exchange["session_id"],
                    "timestamp": exchange["timestamp"]
                })
```

**Agent-side (minimal integration)**:

For Cursor (via .cursorrules or user instruction):
```markdown
After each exchange, append to conversation log:

echo '{"type":"exchange","timestamp":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","user":"<USER_MESSAGE>","ai":"<AI_RESPONSE>","session_id":"<SESSION_ID>"}' >> .praxis-os/.conversations/current-session.jsonl
```

For Claude Code (via MCP tool):
```python
@mcp.tool()
async def log_exchange_to_file(user_msg: str, ai_msg: str, session_id: str):
    """
    Simple file-based logging (no DB required).
    Agent calls this after each exchange.
    """
    log_file = Path(".praxis-os/.conversations") / f"session-{session_id}.jsonl"
    log_file.parent.mkdir(exist_ok=True)

    entry = {
        "type": "exchange",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user": user_msg,
        "ai": ai_msg,
        "session_id": session_id
    }

    with log_file.open("a") as f:
        f.write(json.dumps(entry) + "\n")

    return {"status": "logged"}
```

**Pros**:
- ✅ Simple protocol (JSONL append)
- ✅ Platform-agnostic (any agent can write files)
- ✅ Async processing (no latency impact on agent)
- ✅ Observable (tail -f to watch live)
- ✅ Git-friendly (can commit for debugging)
- ✅ Fault-tolerant (file survives crashes)

**Cons**:
- ⚠️ Requires agent cooperation (must log to file)
- ⚠️ Not automatic for Cursor (needs instruction or hook)
- ⚠️ File format versioning needed

---

## Proposed Implementation: Minimal Viable Product

### Phase 1: File-Based Logging (This Week)

**Step 1**: Create conversation log directory structure
```bash
.praxis-os/
├── .conversations/
│   ├── README.md (explains the protocol)
│   └── .gitignore (don't commit conversation content)
└── .cache/
    └── conversation_index/ (vector DB for conversations)
```

**Step 2**: MCP tool for logging
```python
# mcp_server/server/tools/conversation_tools.py

@mcp.tool()
async def log_conversation_exchange(
    user_message: str,
    ai_response: str,
    session_id: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Log a conversation exchange to file for later indexing.

    Creates append-only JSONL log in .praxis-os/.conversations/
    File watcher automatically indexes for semantic search.

    Args:
        user_message: User's question/request
        ai_response: AI's response
        session_id: Unique session identifier
        metadata: Optional metadata (tags, topic, etc.)

    Returns:
        Status and log location
    """
    log_dir = Path(".praxis-os/.conversations")
    log_dir.mkdir(exist_ok=True)

    log_file = log_dir / f"session-{session_id}.jsonl"

    entry = {
        "type": "exchange",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user": user_message,
        "ai": ai_response,
        "session_id": session_id,
        "metadata": metadata or {}
    }

    with log_file.open("a") as f:
        f.write(json.dumps(entry) + "\n")

    return {
        "status": "logged",
        "log_file": str(log_file),
        "exchange_count": count_lines(log_file)
    }
```

**Step 3**: File watcher for automatic indexing
```python
# mcp_server/monitoring/conversation_watcher.py

class ConversationWatcher:
    """
    Watch .praxis-os/.conversations/ for new exchanges.
    Automatically index them for semantic search.
    """

    def __init__(self, conversations_dir: Path, index_path: Path):
        self.conversations_dir = conversations_dir
        self.jina_model = SentenceTransformer("jinaai/jina-embeddings-v2-base-en")
        self.db = lancedb.connect(str(index_path))

        # Track last processed position per file
        self.file_positions = {}

    async def watch(self):
        """Watch for new conversation log entries."""
        while True:
            for log_file in self.conversations_dir.glob("session-*.jsonl"):
                await self.process_new_lines(log_file)

            await asyncio.sleep(5)  # Check every 5 seconds

    async def process_new_lines(self, log_file: Path):
        """Process new lines in conversation log."""
        last_pos = self.file_positions.get(str(log_file), 0)

        with log_file.open("r") as f:
            f.seek(last_pos)
            new_lines = f.readlines()
            current_pos = f.tell()

        for line in new_lines:
            try:
                exchange = json.loads(line)
                if exchange["type"] == "exchange":
                    await self.index_exchange(exchange)
            except Exception as e:
                logger.error(f"Failed to process exchange: {e}")

        self.file_positions[str(log_file)] = current_pos

    async def index_exchange(self, exchange: Dict):
        """Index exchange in vector DB."""
        text = f"User: {exchange['user']}\n\nAI: {exchange['ai']}"

        # Use jina-embeddings-v2 for long context
        embedding = self.jina_model.encode(text)

        # Store in LanceDB
        table_name = "conversation_history"
        if table_name not in self.db.table_names():
            self.db.create_table(table_name, [
                {
                    "text": text,
                    "vector": embedding.tolist(),
                    "session_id": exchange["session_id"],
                    "timestamp": exchange["timestamp"],
                    "user_message": exchange["user"],
                    "ai_response": exchange["ai"]
                }
            ])
        else:
            table = self.db.open_table(table_name)
            table.add([{
                "text": text,
                "vector": embedding.tolist(),
                "session_id": exchange["session_id"],
                "timestamp": exchange["timestamp"],
                "user_message": exchange["user"],
                "ai_response": exchange["ai"]
            }])
```

**Step 4**: Search tool for conversation history
```python
@mcp.tool()
async def search_conversation_history(
    query: str,
    session_id: Optional[str] = None,
    n_results: int = 3
) -> Dict[str, Any]:
    """
    Search past conversation exchanges semantically.

    Enables session continuity by retrieving relevant past exchanges.

    Args:
        query: What to search for (natural language)
        session_id: Optional filter to specific session
        n_results: Number of exchanges to return

    Returns:
        Relevant past exchanges with timestamps
    """
    # Generate query embedding
    query_embedding = jina_model.encode(query)

    # Search conversation history
    table = db.open_table("conversation_history")
    search_query = table.search(query_embedding).limit(n_results)

    if session_id:
        search_query = search_query.where(f"session_id = '{session_id}'")

    results = search_query.to_list()

    return {
        "query": query,
        "exchanges": [
            {
                "user": r["user_message"],
                "ai": r["ai_response"],
                "timestamp": r["timestamp"],
                "session_id": r["session_id"]
            }
            for r in results
        ]
    }
```

---

### Phase 2: Platform Integration (Next Month)

**Cursor Integration** (via .cursorrules):
```markdown
# .cursorrules addition

After completing each task or answering questions:
1. Call log_conversation_exchange() to preserve this exchange
2. Include user question and your response
3. Use consistent session_id for the conversation

This enables session continuity when context resets.
```

**Claude Code Integration** (native - YOU can do this now):
```
Just call log_conversation_exchange() after each response.
Since you have direct MCP access, this works immediately.
```

**Cline Integration** (user instruction):
```
Similar to Cursor - document in their workflow
```

---

### Phase 3: Automatic Session Resumption (Next Quarter)

**On session start, check for history**:
```python
@mcp.tool()
async def resume_session_context(
    current_query: str,
    session_id: str,
    max_context_tokens: int = 2000
) -> Dict[str, Any]:
    """
    Retrieve relevant past exchanges for session continuity.

    Call this at session start to get context from previous sessions.
    """
    # Search for relevant past exchanges
    relevant_exchanges = await search_conversation_history(
        query=current_query,
        session_id=session_id,
        n_results=5
    )

    # Build context summary within token budget
    context = []
    tokens_used = 0

    for exchange in relevant_exchanges["exchanges"]:
        exchange_text = f"User: {exchange['user']}\nAI: {exchange['ai']}\n\n"
        exchange_tokens = len(exchange_text.split())  # Rough estimate

        if tokens_used + exchange_tokens <= max_context_tokens:
            context.append(exchange)
            tokens_used += exchange_tokens
        else:
            break

    return {
        "context_exchanges": context,
        "tokens_used": tokens_used,
        "message": f"Found {len(context)} relevant past exchanges"
    }
```

---

## Decision Points

**For You to Decide**:

1. **Approach**: File-based logging vs. Pull from platform storage?
   - File-based: Universal but requires agent cooperation
   - Pull: Works for Cursor/Cline but platform-specific

2. **Embedding model**: Use jina-v2 for long context?
   - Pro: Handles full exchanges (no chunking)
   - Con: Larger model, slightly lower quality than bge-small

3. **Privacy**: Log conversations locally or offer cloud option?
   - Local: Privacy-preserving, but requires storage
   - Cloud: Enables cross-device, but privacy concerns

4. **Rollout**: Start with which platform?
   - Claude Code (you can test immediately)
   - Cursor (largest user base)
   - Cline (easiest file access)

**My Recommendation**:

**Week 1**: Implement file-based logging (Option 2) with file watcher
**Week 2**: Test with Claude Code (you can use it now)
**Week 3**: Document for Cursor users (via .cursorrules instruction)
**Month 2**: Measure impact - does it actually help continuity?

**Want me to implement the MVP?** I can build the file-based logging + watcher right now.
