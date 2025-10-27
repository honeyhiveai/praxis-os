# Conversation Intelligence System - Design Specification

**Date**: 2025-10-25
**Status**: Design Phase
**Author**: Claude Code (with Josh)
**Version**: 1.0.0

---

## Executive Summary

**Problem**: Agent platforms handle context compaction differently, causing loss of working context during active sessions. Users experience discontinuity when sessions reset, and there's no unified way to query conversation history across platforms.

**Solution**: Build a conversation intelligence system that:
1. Extracts conversation data from multiple agent platforms (Claude Code, Cursor, Cline)
2. Normalizes to canonical schema with adaptive capability levels
3. Indexes for semantic and temporal querying
4. Provides multiple summarization strategies
5. Enables session continuity across compaction boundaries

**Key Innovation**: Adaptive design that handles variable data completeness across platforms, with explicit capability documentation so users know what works where.

---

## Table of Contents

1. [Background & Motivation](#background--motivation)
2. [Design Goals](#design-goals)
3. [Platform Storage Analysis](#platform-storage-analysis)
4. [System Architecture](#system-architecture)
5. [Canonical Data Schema](#canonical-data-schema)
6. [Platform Adapters](#platform-adapters)
7. [Storage Backend](#storage-backend)
8. [Query Interface](#query-interface)
9. [Summarization Strategies](#summarization-strategies)
10. [Testing Framework](#testing-framework)
11. [Implementation Phases](#implementation-phases)
12. [Open Questions](#open-questions)

---

## Background & Motivation

### The Context Compaction Problem

During this design session, we experienced context compaction **twice**:

**First Compaction** (brutal):
- Lost all working context from the second half of session
- Was mid-investigation of summarization strategies when compaction hit
- Post-reset: Had facts but not the active research state
- **Impact**: Had to restart investigation from scratch

**Second Compaction** (better):
- Preserved working context in structured summary
- Could resume summarization research
- **Key difference**: Compaction timing and content preservation strategy

### Platform Behavioral Differences

**Observed behaviors**:
- **Cursor** (from prior sessions): In-place compaction, conversational continuity maintained
- **Claude Code** (current): Hard session reset with comprehensive summary
- **Impact**: Different user experiences, different continuity models

### User Need

> "I need to be aware of [context compaction], and potentially make some sort of session summarizer that can compress session contents down, sort of like a write append log setup, but the problem becomes when querying that data and presenting a concise summary that will not blow out the context again right away"
>
> — Josh (this session)

**Core requirement**: Store full conversation data, enable multiple query/summarization patterns, work across platforms with different capabilities.

---

## Design Goals

### Primary Goals

1. **Universal Access**: Extract conversation data from all major agent platforms
2. **Adaptive Capability**: Handle platforms with different data completeness levels
3. **Multiple Query Patterns**: Support semantic, temporal, topical, and summary queries
4. **Session Continuity**: Enable resumption across compaction boundaries
5. **Explicit Documentation**: Users know exactly what works on which platform

### Non-Goals

1. **Not controlling agent behavior**: We extract data, don't control how agents work
2. **Not modifying platform storage**: We adapt to what exists, can't change it
3. **Not forcing tool usage**: Agents may or may not use our query tools
4. **Not real-time interception**: Polling/batch extraction, not live streaming
5. **Not replacing platform UI**: Complementary tool, not replacement

### Design Principles

1. **Empirical Validation First**: Don't trust docs, validate actual storage formats
2. **Graceful Degradation**: Work with whatever data is available
3. **Preserve Raw Data**: Always keep original for debugging/reprocessing
4. **Infrastructure Patterns**: Treat like ETL pipeline with capability negotiation
5. **Passive Observer**: Extract from storage, provide tools, hope agents use them

### Critical Constraint

**prAxIs OS controls NONE of these agents**:
- Claude Code: Anthropic's proprietary agent
- Cursor: Cursor's proprietary agent
- Cline: Open source, but we don't control maintainers

**What this means**:
- ✅ We can extract from platform storage (if accessible)
- ✅ We can provide MCP query tools
- ❌ We cannot modify agent behavior
- ❌ We cannot change storage formats
- ❌ We cannot guarantee agents use our tools
- ⚠️ For Cline: Can propose contributions, but no guarantee of acceptance

**Architecture implication**: Pull Model ONLY - extract from what platforms store

---

## Platform Storage Analysis

### Empirical Validation Summary

**Critical Note**: prAxIs OS is a passive observer. We extract from platform storage but control none of these agents.

| Platform | Ownership | Storage Accessibility | Data Completeness | Extraction Strategy |
|----------|-----------|----------------------|-------------------|---------------------|
| **Claude Code** | Anthropic (proprietary) | ✅ Local JSONL files | ✅ 100% (full conversation) | Pull from `~/.claude/projects/` |
| **Cline** | Open source | ✅ Local JSON files | ✅ 100% (full conversation) | Pull from `globalStorage/tasks/` |
| **Cursor** | Cursor Inc (proprietary) | ✅ Local SQLite | ✅ 100% (full conversation) | Pull from global `state.vscdb` (cursorDiskKV table) |

**What we CAN do**: Extract, transform, index, provide query tools via MCP
**What we CANNOT do**: Modify agent behavior, change storage formats, force tool usage

### Claude Code Storage (VALIDATED ✅)

**Location**: `~/.claude/projects/{project-path-escaped}/{session-id}.jsonl`

**Format**: JSONL (one message per line)

**Schema**:
```json
{
  "parentUuid": "previous-message-uuid",
  "sessionId": "abc97593-1886-4e8f-b5f6-6923e029a97e",
  "type": "user" | "assistant" | "system",
  "message": {
    "role": "user" | "assistant",
    "content": "message text" | [{"type": "text", "text": "..."}],
    "model": "claude-sonnet-4-5-20250929",
    "usage": {
      "input_tokens": 1325,
      "output_tokens": 99,
      "cache_creation_input_tokens": 0,
      "cache_read_input_tokens": 0
    }
  },
  "cwd": "/Users/josh/src/...",
  "gitBranch": "main",
  "timestamp": "2025-10-25T18:55:16.442Z",
  "uuid": "ee69cfa4-f4c1-4c7f-a9d2-7e0daeb4936f"
}
```

**Data Available**:
- ✅ Full user messages
- ✅ Full assistant responses
- ✅ Token usage per exchange
- ✅ Timestamps
- ✅ Git branch context
- ✅ Working directory
- ✅ Model version
- ✅ Message threading (parentUuid)

**Reference**: `workspace/analysis/2025-10-25-claude-code-storage-validation.md`

### Cline Storage (VALIDATED ✅)

**Location**: `~/Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/tasks/{task_id}/`

**Files**:
- `api_conversation_history.json` - Full conversation
- `task_metadata.json` - Task metadata
- `context_history.json` - File context (optional)

**Format**: JSON array

**Schema**:
```json
[
  {
    "role": "user",
    "content": [
      {"type": "text", "text": "user message content"}
    ]
  },
  {
    "role": "assistant",
    "content": "assistant response content"
  }
]
```

**Data Available**:
- ✅ Full user messages
- ✅ Full assistant responses
- ✅ Task metadata (separate file)
- ✅ File context tracking
- ❓ Timestamps (needs verification)
- ❓ Token usage (needs verification)

**Reference**: `standards/development/session-history-analysis.md`

### Cursor Storage (VALIDATED ✅)

**Location**: `~/Library/Application Support/Cursor/User/globalStorage/state.vscdb`

**Database**: SQLite (17GB!) with 358,800+ entries

**Critical Discovery**: Initial investigation looked in wrong table. Full conversation data exists in `cursorDiskKV` table, not `ItemTable`.

**Schema Architecture**:

**1. Metadata Storage** (`ItemTable` in workspace-specific db):
```json
// composer.composerData
{
  "composerId": "a0b30d3c-99ac-4ab5-8525-d1f5a143a7e4",
  "name": "Build otel tracer with decorator support",
  "lastUpdatedAt": 1756287217828,
  "createdAt": 1756281508388,
  "unifiedMode": "agent",
  "totalLinesAdded": 21405,
  "totalLinesRemoved": 8762,
  "contextUsagePercent": 87.3
}
```

**2. Full Conversation Storage** (`cursorDiskKV` in global db):
```sql
-- Key format: bubbleId:{composerId}:{messageId}
-- Example: bubbleId:cffb1f56-982c-42c6-844c-620d8374df71:01d50588-9770-4308-8442-0ce22785c4aa

SELECT COUNT(*) FROM cursorDiskKV 
WHERE key LIKE 'bubbleId:cffb1f56-982c-42c6-844c-620d8374df71:%';
-- Result: 2,373 messages in one session
```

**Message Format**:
```json
{
  "type": 1,  // 1 = user, 2 = assistant
  "text": "full message content here",
  "createdAt": "2025-10-25T22:30:15.442Z",
  "bubbleId": "01d50588-9770-4308-8442-0ce22785c4aa"
}
```

**Additional Tables**:
```sql
-- Composer metadata in global db
composerData:{composerId}

-- Individual bubbles (messages)
bubbleId:{composerId}:{messageId}
```

**Data Available**:
- ✅ **Full user messages** (in `cursorDiskKV`)
- ✅ **Full assistant responses** (in `cursorDiskKV`)
- ✅ Session metadata (names, timestamps, stats)
- ✅ Lines added/removed per session
- ✅ Context usage percentages
- ✅ Mode (agent/chat/edit)
- ✅ Message timestamps
- ⚠️ **Token usage** (needs verification)
- ⚠️ **Model version** (needs verification)

**Extraction Strategy**:
```sql
-- Get session metadata
SELECT value FROM ItemTable 
WHERE key='composer.composerData';

-- Get all messages for a session
SELECT value FROM cursorDiskKV 
WHERE key LIKE 'bubbleId:{composerId}:%' 
ORDER BY json_extract(value, '$.createdAt');
```

**Scale Example**: Session "Understanding GitHub Copilot in agent mode"
- **2,373 messages**
- **21,405 lines added**
- **8,762 lines removed**
- **87.3% context usage**

**Status**:
- **INVESTIGATION COMPLETE**: Full conversation storage found and validated
- **Empirical**: 100% message content available in global `state.vscdb`
- **Storage Pattern**: Metadata in workspace db, messages in global db
- **Design Approach**: Build CursorAdapter with full capability parity to Claude Code/Cline

#### Discovery Process (2025-10-26)

**The Problem**: Initial investigation looked only at `ItemTable` and found metadata without message content.

**The Breakthrough**: Systematic database exploration revealed:
1. Global `state.vscdb` is 17GB (far too large for just metadata)
2. Database contains `cursorDiskKV` table with 358,800+ entries
3. Key format: `bubbleId:{composerId}:{messageId}` contains full messages
4. Message type: `1` = user, `2` = assistant

**Validation**:
```sql
-- Count messages in a session
SELECT COUNT(*) FROM cursorDiskKV 
WHERE key LIKE 'bubbleId:cffb1f56-982c-42c6-844c-620d8374df71:%';
-- Result: 2,373 messages

-- Get a single message
SELECT value FROM cursorDiskKV 
WHERE key = 'bubbleId:cffb1f56-...:01d50588-...';
-- Result: Full JSON with type, text, createdAt, bubbleId
```

**Key Learnings**:
- Documentation can be misleading - always validate empirically
- Large database size is a signal to investigate further
- Split-architecture databases require checking multiple tables
- Global vs workspace-specific storage patterns matter

**Praxis Validation**: This discovery itself demonstrates the Conversation Intelligence System's value - the full session history that led to this discovery is now available for future reference.

---

## System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Platform Storage                          │
├──────────────────┬──────────────────┬─────────────────────────┤
│  Claude Code     │     Cline        │       Cursor           │
│  ~/.claude/      │  globalStorage/  │  workspaceStorage/     │
│  JSONL files     │  JSON files      │  SQLite database       │
└────────┬─────────┴────────┬─────────┴───────────┬───────────┘
         │                  │                     │
         ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Platform Adapters (ETL Extract)                │
├──────────────────┬──────────────────┬─────────────────────────┤
│ ClaudeCodeAdapter│  ClineAdapter    │   CursorAdapter        │
│ Capability: FULL │ Capability: FULL │ Capability: FULL       │
└────────┬─────────┴────────┬─────────┴───────────┬───────────┘
         │                  │                     │
         │   Transform to Canonical Schema        │
         │                  │                     │
         ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────────┐
│                 Canonical Storage (ETL Load)                │
├─────────────────────────────────────────────────────────────┤
│  Raw Data Layer:                                            │
│    .praxis-os/.conversations/raw/                            │
│      platform=claude_code/{session}.jsonl                   │
│      platform=cline/{session}.jsonl                         │
│      platform=cursor/{session}.json                         │
│                                                             │
│  Structured Layer:                                          │
│    SQLite: exchanges, sessions, topics tables              │
│    - Temporal queries (ORDER BY timestamp)                  │
│    - Sequential queries (last N turns)                      │
│    - Session metadata                                       │
│                                                             │
│  Semantic Layer:                                            │
│    LanceDB: Vector embeddings                              │
│    - Semantic search ("what did we discuss about X?")      │
│    - Topic-based retrieval                                  │
│    - Cross-session queries                                  │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│              Query & Summarization Layer                    │
├─────────────────────────────────────────────────────────────┤
│  ConversationQueryEngine:                                   │
│    - semantic_search(query)                                 │
│    - recent_turns_summary(n=10)                            │
│    - session_summary(session_id)                            │
│    - topic_summary(topic, all_sessions=True)               │
│    - temporal_query(since, until)                           │
│                                                             │
│  Platform Capability Aware:                                 │
│    - Auto-detects what queries work per platform           │
│    - Graceful degradation for limited platforms            │
│    - Explicit error messages about limitations             │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                    MCP Tool Interface                        │
├─────────────────────────────────────────────────────────────┤
│  @mcp.tool()                                                │
│  async def pos_conversation_query(                          │
│      action: str,                                           │
│      session_id: Optional[str],                             │
│      platform: Optional[str],                               │
│      ...                                                    │
│  )                                                          │
└─────────────────────────────────────────────────────────────┘
```

### Design Pattern: ETL Pipeline (Pull Model Only)

**Extract** → **Transform** → **Load** → **Query** → **Hope Agents Use**

1. **Extract**: Platform adapters read native storage formats (passive observation)
2. **Transform**: Convert to canonical schema (normalize)
3. **Load**: Store in both raw (preserve) and indexed (query) formats
4. **Query**: Multiple interfaces for different use cases
5. **Provide Tools**: Expose via MCP, agents may or may not use them

**Critical**: We are passive observers. We cannot:
- Modify what platforms store
- Force agents to log additional data
- Guarantee agents use our query tools
- Control agent behavior in any way

**Pull Model Only**: No Push Model possible because we don't control any agents.

### Key Architectural Decisions

**1. Hybrid Storage (SQLite + LanceDB)**

*Rationale*:
- SQLite: Excellent for temporal/sequential queries (WHERE timestamp BETWEEN, ORDER BY, LIMIT)
- LanceDB: Built for semantic search (vector similarity)
- Use both: Route queries to appropriate backend

*Alternative considered*: LanceDB only
- *Rejected*: Poor performance for "last 10 turns" type queries

**2. Preserve Raw Data**

*Rationale*:
- Can rebuild indexes with different strategies
- Can upgrade embeddings models (all-MiniLM → bge-small → jina-v2)
- Can debug extraction issues
- Can add new enrichment later

*Pattern*: Data lake (preserve everything) vs data warehouse (transform and discard)

**3. Normalize at Ingestion (not query time)**

*Rationale*:
- Query performance (no transformation overhead)
- Consistent schema for indexing
- Can validate during ingestion

*Trade-off*:
- More ingestion complexity
- But much faster queries

**4. Capability-Based Adapters**

*Rationale*:
- Platforms have different data availability
- System must work with whatever is available
- Users need to know what's possible per platform

*Pattern*: Capability negotiation (like HTTP content negotiation)

---

## Canonical Data Schema

### Design Philosophy

**Variable Completeness**: Not all platforms provide all fields. Schema uses `Optional` types extensively and includes `data_completeness` flag.

**Provenance Preservation**: Always store `raw_data` field with original platform format.

**Enrichment Support**: Fields like `topics`, `decisions_made` computed from content when available.

### Core Schema

```python
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime

class DataCompleteness(Enum):
    """Data availability level for this exchange"""
    FULL = "full"                    # Complete user-assistant exchanges
    METADATA_ONLY = "metadata_only"  # Session info, no message content
    PARTIAL = "partial"              # Some messages, incomplete
    UNKNOWN = "unknown"              # Not yet validated

@dataclass
class ConversationExchange:
    """
    Canonical format for conversation data across all platforms.

    Fields are Optional to support variable platform completeness.

    Always present:
        - exchange_id, session_id, platform, timestamp, data_completeness

    Conditionally present:
        - Content fields (user_message, assistant_response) depend on platform
        - Metrics (tokens) depend on platform
        - Context (git_branch, files) depend on platform
    """

    # ===== Core Identity (ALWAYS PRESENT) =====
    exchange_id: str                              # UUID for this exchange
    session_id: str                               # Session this belongs to
    platform: Literal["claude_code", "cursor", "cline"]
    timestamp: datetime                           # When exchange occurred
    data_completeness: DataCompleteness           # What data level available

    # ===== Sequence (if available) =====
    exchange_number: Optional[int] = None         # Sequence in session (0-indexed)

    # ===== Content (depends on platform capability) =====
    user_message: Optional[str] = None            # User's input (plain text)
    assistant_response: Optional[str] = None      # AI's response (plain text)

    # ===== Session-Level Metadata (most platforms) =====
    session_name: Optional[str] = None            # Human-readable session name
    session_description: Optional[str] = None     # Session summary/description

    # ===== Context (platform-dependent) =====
    git_branch: Optional[str] = None              # Git context
    working_directory: Optional[str] = None       # CWD at time of exchange
    files_referenced: Optional[List[str]] = None  # Files mentioned/modified

    # ===== Enriched Metadata (computed if content available) =====
    topics: Optional[List[str]] = None            # Extracted topics
    decisions_made: Optional[List[str]] = None    # Key decisions identified
    code_snippets: Optional[List[str]] = None     # Code blocks extracted

    # ===== Metrics (platform-dependent) =====
    tokens_input: Optional[int] = None            # User message tokens
    tokens_output: Optional[int] = None           # AI response tokens
    model_used: Optional[str] = None              # Model identifier

    # ===== Code Contribution (Cursor metadata) =====
    lines_added: Optional[int] = None             # Code additions
    lines_removed: Optional[int] = None           # Code deletions

    # ===== Provenance (ALWAYS STORE) =====
    raw_data: Dict[str, Any]                      # Original platform data
    raw_format_version: str                       # Schema version of raw_data
    adapter_version: str                          # Adapter that extracted this
    ingestion_timestamp: datetime                 # When we extracted this

    # ===== Utility Methods =====

    def supports_semantic_search(self) -> bool:
        """Can this exchange be semantically searched?"""
        return (
            self.data_completeness == DataCompleteness.FULL and
            self.user_message is not None and
            self.assistant_response is not None
        )

    def has_content(self) -> bool:
        """Does this exchange have actual conversation content?"""
        return self.user_message is not None or self.assistant_response is not None

    def get_full_text(self) -> str:
        """Get combined text for indexing"""
        parts = []
        if self.user_message:
            parts.append(f"User: {self.user_message}")
        if self.assistant_response:
            parts.append(f"Assistant: {self.assistant_response}")
        return "\n\n".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            "exchange_id": self.exchange_id,
            "session_id": self.session_id,
            "platform": self.platform,
            "timestamp": self.timestamp.isoformat(),
            "data_completeness": self.data_completeness.value,
            "exchange_number": self.exchange_number,
            "user_message": self.user_message,
            "assistant_response": self.assistant_response,
            "session_name": self.session_name,
            "session_description": self.session_description,
            "git_branch": self.git_branch,
            "working_directory": self.working_directory,
            "files_referenced": json.dumps(self.files_referenced) if self.files_referenced else None,
            "topics": json.dumps(self.topics) if self.topics else None,
            "decisions_made": json.dumps(self.decisions_made) if self.decisions_made else None,
            "code_snippets": json.dumps(self.code_snippets) if self.code_snippets else None,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "model_used": self.model_used,
            "lines_added": self.lines_added,
            "lines_removed": self.lines_removed,
            "raw_data": json.dumps(self.raw_data),
            "raw_format_version": self.raw_format_version,
            "adapter_version": self.adapter_version,
            "ingestion_timestamp": self.ingestion_timestamp.isoformat()
        }
```

### Database Schema (SQLite)

```sql
-- Main exchanges table
CREATE TABLE exchanges (
    exchange_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    timestamp DATETIME NOT NULL,
    data_completeness TEXT NOT NULL,
    exchange_number INTEGER,

    -- Content (nullable)
    user_message TEXT,
    assistant_response TEXT,

    -- Session metadata
    session_name TEXT,
    session_description TEXT,

    -- Context
    git_branch TEXT,
    working_directory TEXT,
    files_referenced TEXT,  -- JSON array

    -- Enriched
    topics TEXT,  -- JSON array
    decisions_made TEXT,  -- JSON array
    code_snippets TEXT,  -- JSON array

    -- Metrics
    tokens_input INTEGER,
    tokens_output INTEGER,
    model_used TEXT,

    -- Code contribution
    lines_added INTEGER,
    lines_removed INTEGER,

    -- Provenance
    raw_data TEXT,  -- JSON
    raw_format_version TEXT,
    adapter_version TEXT,
    ingestion_timestamp DATETIME NOT NULL,

    -- Indexes for common queries
    INDEX idx_session (session_id),
    INDEX idx_platform (platform),
    INDEX idx_timestamp (timestamp),
    INDEX idx_session_timestamp (session_id, timestamp)
);

-- Session summary table (computed)
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,
    session_name TEXT,
    first_message DATETIME NOT NULL,
    last_message DATETIME NOT NULL,
    total_exchanges INTEGER NOT NULL,
    total_tokens_input INTEGER,
    total_tokens_output INTEGER,
    topics TEXT,  -- JSON array (aggregated)
    data_completeness TEXT NOT NULL,

    INDEX idx_platform (platform),
    INDEX idx_last_message (last_message)
);

-- Topic index (for fast topic queries)
CREATE TABLE topics (
    topic TEXT NOT NULL,
    session_id TEXT NOT NULL,
    exchange_id TEXT NOT NULL,
    relevance_score FLOAT,

    PRIMARY KEY (topic, exchange_id),
    INDEX idx_topic (topic),
    INDEX idx_session_topic (session_id, topic)
);
```

---

## Platform Adapters

### Adapter Interface

```python
from abc import ABC, abstractmethod
from typing import Iterator, Set, List
from pathlib import Path

class PlatformCapability(Enum):
    """What operations a platform adapter supports"""
    SEMANTIC_SEARCH = "semantic_search"        # Can search message content
    TEMPORAL_QUERY = "temporal_query"          # Can query by time range
    SESSION_SUMMARY = "session_summary"        # Can provide session metadata
    EXCHANGE_RETRIEVAL = "exchange_retrieval"  # Can get full exchanges
    TOKEN_METRICS = "token_metrics"            # Has token usage data
    FILE_CONTEXT = "file_context"              # Tracks files discussed

class PlatformAdapter(ABC):
    """
    Base adapter for extracting conversation data from platform storage.

    Each adapter MUST declare its capabilities so query layer knows
    what operations are supported.
    """

    # Subclass MUST override these
    PLATFORM_NAME: str = "unknown"
    DATA_COMPLETENESS: DataCompleteness = DataCompleteness.UNKNOWN
    CAPABILITIES: Set[PlatformCapability] = set()
    ADAPTER_VERSION: str = "0.0.0"

    @abstractmethod
    def get_storage_location(self) -> Path:
        """Where this platform stores conversation data"""
        pass

    @abstractmethod
    def list_sessions(self) -> Iterator[str]:
        """Yield session IDs available on this platform"""
        pass

    @abstractmethod
    def extract_exchanges(
        self,
        session_id: str,
        since: Optional[datetime] = None
    ) -> Iterator[ConversationExchange]:
        """
        Extract conversation exchanges.

        Returns ConversationExchange objects with fields populated
        based on platform capability.

        Args:
            session_id: Session to extract
            since: Only return exchanges after this timestamp (optional)

        Yields:
            ConversationExchange objects
        """
        pass

    def get_capabilities(self) -> Set[PlatformCapability]:
        """Report what this adapter can do"""
        return self.CAPABILITIES

    def get_completeness(self) -> DataCompleteness:
        """Report data completeness level"""
        return self.DATA_COMPLETENESS

    def describe(self) -> Dict[str, Any]:
        """Human-readable capability description"""
        return {
            "platform": self.PLATFORM_NAME,
            "adapter_version": self.ADAPTER_VERSION,
            "data_completeness": self.DATA_COMPLETENESS.value,
            "capabilities": [c.value for c in self.CAPABILITIES],
            "storage_location": str(self.get_storage_location()),
            "limitations": self._get_limitations()
        }

    @abstractmethod
    def _get_limitations(self) -> List[str]:
        """Document what this adapter CANNOT do"""
        pass
```

### Claude Code Adapter

```python
class ClaudeCodeAdapter(PlatformAdapter):
    """
    Adapter for Claude Code JSONL storage.

    DATA COMPLETENESS: ✅ FULL (empirically validated 2025-10-25)

    Storage format documented in:
    workspace/analysis/2025-10-25-claude-code-storage-validation.md
    """

    PLATFORM_NAME = "claude_code"
    DATA_COMPLETENESS = DataCompleteness.FULL
    CAPABILITIES = {
        PlatformCapability.SEMANTIC_SEARCH,
        PlatformCapability.TEMPORAL_QUERY,
        PlatformCapability.SESSION_SUMMARY,
        PlatformCapability.EXCHANGE_RETRIEVAL,
        PlatformCapability.TOKEN_METRICS,
        PlatformCapability.FILE_CONTEXT,
    }
    ADAPTER_VERSION = "1.0.0"

    def get_storage_location(self) -> Path:
        return Path.home() / ".claude/projects"

    def list_sessions(self) -> Iterator[str]:
        """
        List all session files for all projects.

        Yields session IDs (UUIDs from filename).
        """
        storage = self.get_storage_location()
        for project_dir in storage.iterdir():
            if not project_dir.is_dir():
                continue
            for session_file in project_dir.glob("*.jsonl"):
                session_id = session_file.stem  # Filename without .jsonl
                yield session_id

    def extract_exchanges(
        self,
        session_id: str,
        since: Optional[datetime] = None
    ) -> Iterator[ConversationExchange]:
        """
        Extract from JSONL with full fidelity.

        Reads line-by-line for memory efficiency.
        """
        # Find session file (may be in any project directory)
        session_file = self._find_session_file(session_id)
        if not session_file:
            raise FileNotFoundError(f"Session {session_id} not found")

        exchange_number = 0
        pending_user_message = None

        with session_file.open() as f:
            for line in f:
                msg = json.loads(line)

                # Skip if before 'since' timestamp
                if since:
                    msg_timestamp = datetime.fromisoformat(msg["timestamp"].replace("Z", "+00:00"))
                    if msg_timestamp < since:
                        continue

                # Parse based on message type
                if msg["type"] == "user":
                    pending_user_message = msg

                elif msg["type"] == "assistant" and pending_user_message:
                    # We have a complete exchange
                    exchange = self._parse_exchange(
                        pending_user_message,
                        msg,
                        exchange_number
                    )
                    yield exchange

                    exchange_number += 1
                    pending_user_message = None

    def _parse_exchange(
        self,
        user_msg: dict,
        assistant_msg: dict,
        exchange_number: int
    ) -> ConversationExchange:
        """Parse Claude Code message pair into canonical format"""

        # Extract content (handle both string and array formats)
        user_content = user_msg["message"]["content"]
        if isinstance(user_content, list):
            user_content = user_content[0]["text"] if user_content else ""

        assistant_content = assistant_msg["message"]["content"]
        if isinstance(assistant_content, list):
            # Join text blocks
            assistant_content = "\n".join(
                block["text"] for block in assistant_content
                if block["type"] == "text"
            )

        # Extract token usage
        usage = assistant_msg["message"].get("usage", {})

        return ConversationExchange(
            exchange_id=f"{user_msg['uuid']}_{assistant_msg['uuid']}",
            session_id=user_msg["sessionId"],
            platform="claude_code",
            timestamp=datetime.fromisoformat(user_msg["timestamp"].replace("Z", "+00:00")),
            data_completeness=DataCompleteness.FULL,
            exchange_number=exchange_number,

            # Content
            user_message=user_content,
            assistant_response=assistant_content,

            # Context
            git_branch=user_msg.get("gitBranch"),
            working_directory=user_msg.get("cwd"),

            # Metrics
            tokens_input=usage.get("input_tokens"),
            tokens_output=usage.get("output_tokens"),
            model_used=assistant_msg["message"].get("model"),

            # Provenance
            raw_data={
                "user": user_msg,
                "assistant": assistant_msg
            },
            raw_format_version="claude_code_v1",
            adapter_version=self.ADAPTER_VERSION,
            ingestion_timestamp=datetime.now()
        )

    def _find_session_file(self, session_id: str) -> Optional[Path]:
        """Find session file across all project directories"""
        storage = self.get_storage_location()
        for project_dir in storage.iterdir():
            if not project_dir.is_dir():
                continue
            session_file = project_dir / f"{session_id}.jsonl"
            if session_file.exists():
                return session_file
        return None

    def _get_limitations(self) -> List[str]:
        return []  # No known limitations
```

### Cline Adapter

```python
class ClineAdapter(PlatformAdapter):
    """
    Adapter for Cline JSON task storage.

    DATA COMPLETENESS: ✅ FULL (empirically validated 2025-10-25)

    Storage format documented in:
    standards/development/session-history-analysis.md
    """

    PLATFORM_NAME = "cline"
    DATA_COMPLETENESS = DataCompleteness.FULL
    CAPABILITIES = {
        PlatformCapability.SEMANTIC_SEARCH,
        PlatformCapability.TEMPORAL_QUERY,
        PlatformCapability.SESSION_SUMMARY,
        PlatformCapability.EXCHANGE_RETRIEVAL,
        PlatformCapability.FILE_CONTEXT,
        # Note: Token metrics availability TBD
    }
    ADAPTER_VERSION = "1.0.0"

    def get_storage_location(self) -> Path:
        if platform.system() == "Darwin":  # macOS
            return Path.home() / "Library/Application Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/tasks"
        elif platform.system() == "Linux":
            return Path.home() / ".config/Cursor/User/globalStorage/saoudrizwan.claude-dev/tasks"
        elif platform.system() == "Windows":
            return Path(os.getenv("APPDATA")) / "Cursor/User/globalStorage/saoudrizwan.claude-dev/tasks"
        else:
            raise NotImplementedError(f"Unsupported platform: {platform.system()}")

    def list_sessions(self) -> Iterator[str]:
        """
        List all task directories.

        Task directories are named with timestamps (e.g., 1760215415364).
        """
        storage = self.get_storage_location()
        for task_dir in storage.iterdir():
            if task_dir.is_dir() and task_dir.name.isdigit():
                yield task_dir.name  # Use directory name as session_id

    def extract_exchanges(
        self,
        session_id: str,
        since: Optional[datetime] = None
    ) -> Iterator[ConversationExchange]:
        """
        Extract from Cline JSON conversation history.

        Format: Array of message objects with role/content.
        """
        task_dir = self.get_storage_location() / session_id
        history_file = task_dir / "api_conversation_history.json"

        if not history_file.exists():
            raise FileNotFoundError(f"Task {session_id} has no conversation history")

        with history_file.open() as f:
            messages = json.load(f)

        # Load metadata if available
        metadata = self._load_metadata(task_dir)

        # Parse messages into exchanges (user-assistant pairs)
        exchange_number = 0
        pending_user = None

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            # Extract text from content (may be string or array)
            if isinstance(content, list):
                text = "\n".join(
                    item["text"] for item in content
                    if item.get("type") == "text"
                )
            else:
                text = content

            if role == "user":
                pending_user = (msg, text)

            elif role == "assistant" and pending_user:
                user_msg, user_text = pending_user

                # TODO: Extract timestamp if available in message
                # For now, use metadata or file modification time
                timestamp = self._get_message_timestamp(msg, metadata, task_dir)

                if since and timestamp < since:
                    continue

                exchange = ConversationExchange(
                    exchange_id=f"{session_id}_{exchange_number}",
                    session_id=session_id,
                    platform="cline",
                    timestamp=timestamp,
                    data_completeness=DataCompleteness.FULL,
                    exchange_number=exchange_number,

                    # Content
                    user_message=user_text,
                    assistant_response=text,

                    # Context from metadata
                    files_referenced=metadata.get("files_in_context"),

                    # Provenance
                    raw_data={
                        "user": user_msg,
                        "assistant": msg,
                        "metadata": metadata
                    },
                    raw_format_version="cline_v1",
                    adapter_version=self.ADAPTER_VERSION,
                    ingestion_timestamp=datetime.now()
                )

                yield exchange
                exchange_number += 1
                pending_user = None

    def _load_metadata(self, task_dir: Path) -> Dict[str, Any]:
        """Load task metadata if available"""
        metadata_file = task_dir / "task_metadata.json"
        if metadata_file.exists():
            with metadata_file.open() as f:
                return json.load(f)
        return {}

    def _get_message_timestamp(
        self,
        msg: dict,
        metadata: dict,
        task_dir: Path
    ) -> datetime:
        """
        Extract or infer message timestamp.

        Priority:
        1. Message timestamp field (if present)
        2. Metadata timestamps
        3. File modification time
        """
        # TODO: Check if messages have timestamps
        # For now, use file mtime
        history_file = task_dir / "api_conversation_history.json"
        mtime = history_file.stat().st_mtime
        return datetime.fromtimestamp(mtime)

    def _get_limitations(self) -> List[str]:
        return [
            "Timestamp precision limited (using file mtime, not per-message timestamps)",
            "Token metrics not available in current format",
            "Git context not tracked by Cline"
        ]
```

### Cursor Adapter

```python
class CursorAdapter(PlatformAdapter):
    """
    Adapter for Cursor SQLite storage.

    DATA COMPLETENESS: ✅ FULL (empirically validated 2025-10-26)

    ✅ RESOLVED STATUS:
    - Full conversation history found in global state.vscdb (cursorDiskKV table)
    - Split-database architecture: metadata in workspace db, messages in global db
    - Messages keyed by bubbleId:{composerId}:{messageId} format
    - Both user and assistant messages with full content
    - Message-level timestamps available

    STORAGE ARCHITECTURE:
    - Metadata: ~/Library/Application Support/Cursor/User/workspaceStorage/{hash}/state.vscdb
    - Messages: ~/Library/Application Support/Cursor/User/globalStorage/state.vscdb
    """

    PLATFORM_NAME = "cursor"
    DATA_COMPLETENESS = DataCompleteness.FULL
    CAPABILITIES = {
        PlatformCapability.SESSION_SUMMARY,      # Full session metadata
        PlatformCapability.TEMPORAL_QUERY,       # Message-level timestamps
        PlatformCapability.SEMANTIC_SEARCH,      # Full message content available
        PlatformCapability.EXCHANGE_RETRIEVAL,   # Complete conversations
        PlatformCapability.FILE_CONTEXT,         # File tracking available
        # NEEDS VERIFICATION:
        # - TOKEN_METRICS (per-message token usage)
    }
    ADAPTER_VERSION = "1.0.0"

    def get_storage_location(self) -> Path:
        if platform.system() == "Darwin":  # macOS
            return Path.home() / "Library/Application Support/Cursor/User/workspaceStorage"
        elif platform.system() == "Linux":
            return Path.home() / ".config/Cursor/User/workspaceStorage"
        elif platform.system() == "Windows":
            return Path(os.getenv("APPDATA")) / "Cursor/User/workspaceStorage"
        else:
            raise NotImplementedError(f"Unsupported platform: {platform.system()}")

    def list_sessions(self) -> Iterator[str]:
        """
        List composer sessions from all workspaces.

        Yields composer IDs from composer.composerData in each workspace.
        """
        storage = self.get_storage_location()
        for workspace_dir in storage.iterdir():
            if not workspace_dir.is_dir():
                continue

            db_file = workspace_dir / "state.vscdb"
            if not db_file.exists():
                continue

            # Query SQLite database
            with sqlite3.connect(db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT value FROM ItemTable WHERE key = 'composer.composerData'"
                )
                row = cursor.fetchone()
                if row:
                    data = json.loads(row[0])
                    for composer in data.get("allComposers", []):
                        yield composer["composerId"]

    def extract_exchanges(
        self,
        session_id: str,
        since: Optional[datetime] = None
    ) -> Iterator[ConversationExchange]:
        """
        Extract full conversation exchanges from Cursor.

        ✅ FULL DATA AVAILABLE:
        Returns exchanges with:
        - session_name populated (from workspace db)
        - timestamp populated (message-level from global db)
        - user_message populated (full content from cursorDiskKV)
        - assistant_response populated (full content from cursorDiskKV)

        Uses split-database architecture:
        1. Metadata from workspace-specific state.vscdb
        2. Messages from global state.vscdb (cursorDiskKV table)
        """
        # Find workspace containing this session
        workspace_dir = self._find_workspace_for_session(session_id)
        if not workspace_dir:
            raise FileNotFoundError(f"Session {session_id} not found in any workspace")

        db_file = workspace_dir / "state.vscdb"

        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()

            # Get composer metadata
            cursor.execute(
                "SELECT value FROM ItemTable WHERE key = 'composer.composerData'"
            )
            row = cursor.fetchone()
            if not row:
                return

            data = json.loads(row[0])
            composer = next(
                (c for c in data["allComposers"] if c["composerId"] == session_id),
                None
            )
            if not composer:
                return

            # Get user prompts (if available)
            cursor.execute(
                "SELECT value FROM ItemTable WHERE key = 'aiService.prompts'"
            )
            prompts_row = cursor.fetchone()
            prompts = json.loads(prompts_row[0]) if prompts_row else []

            # Create minimal exchange from metadata
            # Note: This is NOT a real exchange, just metadata representation
            created_ts = datetime.fromtimestamp(composer["createdAt"] / 1000)
            updated_ts = datetime.fromtimestamp(composer["lastUpdatedAt"] / 1000)

            if since and created_ts < since:
                return

            # Now get messages from global db
            global_db = Path.home() / "Library/Application Support/Cursor/User/globalStorage/state.vscdb"
            
            with sqlite3.connect(global_db) as global_conn:
                global_cursor = global_conn.cursor()
                
                # Get all messages for this session
                global_cursor.execute(
                    "SELECT value FROM cursorDiskKV WHERE key LIKE ?",
                    (f"bubbleId:{session_id}:%",)
                )
                
                messages = []
                for row in global_cursor:
                    msg_data = json.loads(row[0])
                    messages.append(msg_data)
                
                # Sort by timestamp
                messages.sort(key=lambda m: m.get("createdAt", ""))
                
                # Pair user/assistant messages into exchanges
                for i in range(0, len(messages), 2):
                    user_msg = messages[i] if i < len(messages) and messages[i].get("type") == 1 else None
                    asst_msg = messages[i+1] if i+1 < len(messages) and messages[i+1].get("type") == 2 else None
                    
                    yield ConversationExchange(
                        exchange_id=f"cursor_{session_id}_{i//2}",
                        session_id=session_id,
                        platform="cursor",
                        timestamp=datetime.fromisoformat(user_msg["createdAt"].replace("Z", "+00:00")),
                        data_completeness=DataCompleteness.FULL,

                        # Session metadata
                        session_name=composer.get("name"),
                        session_description=f"Mode: {composer.get('unifiedMode')}",

                        # Full content (available from cursorDiskKV)
                        user_message=user_msg.get("text") if user_msg else None,
                        assistant_response=asst_msg.get("text") if asst_msg else None,

                        # Provenance
                        raw_data={
                            "composer": composer,
                            "user_bubble": user_msg,
                            "assistant_bubble": asst_msg
                        },
                        raw_format_version="cursor_full_v1",
                        adapter_version=self.ADAPTER_VERSION,
                        ingestion_timestamp=datetime.now()
                    )

    def _find_workspace_for_session(self, session_id: str) -> Optional[Path]:
        """Find workspace directory containing this session"""
        storage = self.get_storage_location()
        for workspace_dir in storage.iterdir():
            if not workspace_dir.is_dir():
                continue

            db_file = workspace_dir / "state.vscdb"
            if not db_file.exists():
                continue

            with sqlite3.connect(db_file) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT value FROM ItemTable WHERE key = 'composer.composerData'"
                )
                row = cursor.fetchone()
                if row:
                    data = json.loads(row[0])
                    if any(c["composerId"] == session_id for c in data.get("allComposers", [])):
                        return workspace_dir

        return None

    def _get_limitations(self) -> List[str]:
        return [
            "✅ RESOLVED: Full conversation history found in global state.vscdb",
            "Storage split across two databases (metadata in workspace, messages in global)",
            "Uses cursorDiskKV table with bubbleId key format",
            "Token usage per message needs verification",
            "Model version tracking needs verification"
        ]
```

### Platform Capability Matrix

Auto-generated documentation showing what works where:

```python
def generate_capability_matrix() -> str:
    """Generate markdown capability matrix for documentation"""

    adapters = [
        ClaudeCodeAdapter(),
        ClineAdapter(),
        CursorAdapter()
    ]

    matrix = """
# Platform Capability Matrix

**Last Updated**: 2025-10-26
**Validation Status**: See notes column

| Capability | Claude Code | Cline | Cursor | Notes |
|------------|-------------|-------|--------|-------|
| **Semantic Search** | ✅ | ✅ | ✅ | All platforms have full message content |
| **Temporal Query** | ✅ | ✅ | ✅ | All platforms have timestamps |
| **Session Summary** | ✅ | ✅ | ✅ | Full metadata available everywhere |
| **Exchange Retrieval** | ✅ | ✅ | ✅ | Full conversation exchanges available |
| **Token Metrics** | ✅ | ⚠️ | ⚠️ | Claude Code has detailed metrics, Cursor needs verification |
| **File Context** | ✅ | ✅ | ✅ | All track files referenced |

## Data Completeness Levels

- **Claude Code**: ✅ `FULL` - Empirically validated 2025-10-25
- **Cline**: ✅ `FULL` - Empirically validated 2025-10-25
- **Cursor**: ✅ `FULL` - Empirically validated 2025-10-26 (cursorDiskKV table discovery)

## Supported Query Patterns by Platform

### Semantic Search ("what did we discuss about X?")
- ✅ **Claude Code**: Full support
- ✅ **Cline**: Full support
- ✅ **Cursor**: Full support (via cursorDiskKV table)

### Recent Turns Summary ("summarize last 10 exchanges")
- ✅ **Claude Code**: Full support
- ✅ **Cline**: Full support
- ✅ **Cursor**: Full support with message-level timestamps

### Topic-Based Cross-Session ("all discussions about embeddings")
- ✅ **Claude Code**: Full support
- ✅ **Cline**: Full support
- ✅ **Cursor**: Full support across all sessions

### Temporal Queries ("what happened last week?")
- ✅ **Claude Code**: Full support
- ✅ **Cline**: Full support (timestamp precision limited)
- ✅ **Cursor**: Full support with message-level timestamps

### Full Session Summary
- ✅ **Claude Code**: Complete conversation summary
- ✅ **Cline**: Complete conversation summary
- ✅ **Cursor**: Complete conversation summary with full metadata

## Platform-Specific Limitations

### Claude Code
- No known limitations
- Full conversation history with all metadata
- Best-in-class data availability

### Cline
- Timestamp precision limited (file mtime, not per-message)
- Token metrics not available in current format
- Git context not tracked

### Cursor
- ✅ **RESOLVED**: Full conversation history available in global state.vscdb
- Split-database architecture (metadata in workspace db, messages in global db)
- Requires querying cursorDiskKV table with bubbleId keys
- Token usage per message needs verification
- Model version tracking needs verification
- Large database size (17GB+ for active development machine)
- Excellent metadata: lines added/removed, context usage percentages
"""

    return matrix
```

---

## Storage Backend

### Hybrid Storage Strategy

**Why Hybrid?**

Different query patterns need different backends:

| Query Type | Best Backend | Rationale |
|------------|-------------|-----------|
| "Last 10 turns" | SQLite | `ORDER BY timestamp DESC LIMIT 10` (fast) |
| "What did we discuss about X?" | LanceDB | Vector similarity search |
| "Messages from 2025-10-24" | SQLite | `WHERE timestamp BETWEEN` (indexed) |
| "All sessions about embeddings" | LanceDB | Semantic cross-session search |
| "Session summary" | SQLite | Aggregate queries, JOINs |

### SQLite Layer (Structured Queries)

**Purpose**: Temporal, sequential, and relational queries

**Schema**: See [Canonical Data Schema](#canonical-data-schema) section above

**Indexes**:
```sql
-- Primary indexes (created with table)
PRIMARY KEY (exchange_id)
INDEX idx_session (session_id)
INDEX idx_platform (platform)
INDEX idx_timestamp (timestamp)
INDEX idx_session_timestamp (session_id, timestamp)

-- Secondary indexes (for common queries)
CREATE INDEX idx_completeness ON exchanges(data_completeness);
CREATE INDEX idx_platform_timestamp ON exchanges(platform, timestamp);
CREATE INDEX idx_session_number ON exchanges(session_id, exchange_number);
```

**Query Examples**:
```python
# Last N turns in a session
SELECT * FROM exchanges
WHERE session_id = ?
ORDER BY exchange_number DESC
LIMIT ?

# All sessions in time range
SELECT DISTINCT session_id, session_name, platform
FROM exchanges
WHERE timestamp BETWEEN ? AND ?
ORDER BY timestamp DESC

# Token usage by platform
SELECT platform,
       SUM(tokens_input) as total_input,
       SUM(tokens_output) as total_output
FROM exchanges
WHERE timestamp >= ?
GROUP BY platform
```

### LanceDB Layer (Semantic Queries)

**Purpose**: Vector similarity search for semantic queries

**Indexing Strategy**:
```python
# Chunk by exchange (not by arbitrary size)
for exchange in exchanges:
    if exchange.supports_semantic_search():
        chunk = {
            "content": exchange.get_full_text(),
            "exchange_id": exchange.exchange_id,
            "session_id": exchange.session_id,
            "platform": exchange.platform,
            "timestamp": exchange.timestamp.isoformat(),
            "topics": exchange.topics,
            "data_completeness": exchange.data_completeness.value
        }

        # Generate embedding with jina-v2 (8192 token context)
        embedding = embedding_model.encode(chunk["content"])
        chunk["vector"] = embedding

        lancedb_table.add([chunk])
```

**Embedding Model Choice**:
- **Current**: all-MiniLM-L6-v2 (384 dim, 512 token context)
- **Recommended Upgrade**: jina-embeddings-v2-base-en (768 dim, 8192 token context)
  - Rationale: Conversation exchanges can be long (multi-paragraph)
  - 8192 token context = ~6000 words (fits most exchanges)
  - Specialized for long-context semantic search

**Query Examples**:
```python
# Semantic search across all platforms
results = lancedb_table.search(
    query="embedding models and vector databases",
    n_results=20
).where("data_completeness = 'full'")

# Topic-based with time filter
results = lancedb_table.search(
    query="RAG optimization strategies",
    n_results=50
).where(f"timestamp >= '{since.isoformat()}'")

# Cross-session topic exploration
results = lancedb_table.search(
    query="context compaction behavior",
    n_results=100
).to_list()

# Group by session
by_session = defaultdict(list)
for result in results:
    by_session[result["session_id"]].append(result)
```

### Raw Data Preservation

**Purpose**:
- Rebuild indexes with different strategies
- Upgrade embedding models
- Debug extraction issues
- Add new enrichment

**Storage Format**: JSONL (append-only)

**Directory Structure**:
```
.praxis-os/.conversations/
├── raw/
│   ├── platform=claude_code/
│   │   ├── session-abc123.jsonl
│   │   └── session-def456.jsonl
│   ├── platform=cline/
│   │   ├── session-1760215415364.jsonl
│   │   └── session-1761002178279.jsonl
│   └── platform=cursor/
│       └── session-a0b30d3c.jsonl  (full conversation)
│
├── index/
│   ├── conversations.db  (SQLite)
│   └── vectors.lance/    (LanceDB)
│
└── metadata/
    └── ingestion_log.jsonl  (when we extracted, from where)
```

**JSONL Format** (normalized):
```jsonl
{"exchange_id":"...", "session_id":"...", "timestamp":"...", "user_message":"...", "assistant_response":"...", ...}
{"exchange_id":"...", "session_id":"...", "timestamp":"...", "user_message":"...", "assistant_response":"...", ...}
```

---

## Query Interface

### ConversationQueryEngine

```python
class ConversationQueryEngine:
    """
    Unified query interface over hybrid storage.

    Automatically routes queries to appropriate backend based on query type.
    Handles platform capability detection and graceful degradation.
    """

    def __init__(
        self,
        sqlite_path: Path,
        lancedb_path: Path,
        adapters: Dict[str, PlatformAdapter]
    ):
        self.sqlite_conn = sqlite3.connect(sqlite_path)
        self.lancedb = lancedb.connect(lancedb_path)
        self.adapters = adapters

        # Log capabilities at startup
        self._log_capabilities()

    def _log_capabilities(self):
        """Log what's possible with current platforms"""
        logger.info("Platform capabilities:")
        for name, adapter in self.adapters.items():
            caps = adapter.describe()
            logger.info(f"  {name}:")
            logger.info(f"    Data: {caps['data_completeness']}")
            logger.info(f"    Capabilities: {', '.join(caps['capabilities'])}")
            if caps['limitations']:
                logger.warning(f"    Limitations: {'; '.join(caps['limitations'])}")

    # ===== Query Methods =====

    def semantic_search(
        self,
        query: str,
        platforms: Optional[List[str]] = None,
        since: Optional[datetime] = None,
        n_results: int = 20
    ) -> Dict[str, Any]:
        """
        Search conversation content semantically.

        **Platform Support**:
        - Claude Code: ✅ Full support
        - Cline: ✅ Full support
        - Cursor: ✅ Full support (via cursorDiskKV table)

        Args:
            query: Natural language query
            platforms: Limit to specific platforms (default: all capable)
            since: Only search after this timestamp
            n_results: Number of results to return

        Returns:
            {
                "results": [
                    {
                        "exchange_id": "...",
                        "session_id": "...",
                        "platform": "...",
                        "user_message": "...",
                        "assistant_response": "...",
                        "relevance_score": 0.85,
                        "timestamp": "..."
                    },
                    ...
                ],
                "platforms_searched": ["claude_code", "cline"],
                "platforms_skipped": {
                    "cursor": "No SEMANTIC_SEARCH capability (metadata_only)"
                },
                "query": "..."
            }
        """
        results = []
        platforms_searched = []
        platforms_skipped = {}

        target_platforms = platforms or self.adapters.keys()

        # Filter to platforms with semantic search capability
        for platform_name in target_platforms:
            adapter = self.adapters[platform_name]

            if PlatformCapability.SEMANTIC_SEARCH not in adapter.CAPABILITIES:
                platforms_skipped[platform_name] = \
                    f"No SEMANTIC_SEARCH capability ({adapter.DATA_COMPLETENESS.value})"
                continue

            platforms_searched.append(platform_name)

        if not platforms_searched:
            return {
                "results": [],
                "platforms_searched": [],
                "platforms_skipped": platforms_skipped,
                "query": query,
                "error": "No platforms support semantic search"
            }

        # Query LanceDB with platform filter
        search = self.lancedb.open_table("exchanges").search(query)

        if platforms_searched:
            platform_filter = " OR ".join(f"platform = '{p}'" for p in platforms_searched)
            search = search.where(platform_filter)

        if since:
            search = search.where(f"timestamp >= '{since.isoformat()}'")

        search = search.limit(n_results)

        # Execute and resolve to full exchanges
        lance_results = search.to_list()

        # Resolve exchange IDs to full data from SQLite
        exchange_ids = [r["exchange_id"] for r in lance_results]
        placeholders = ",".join(["?"] * len(exchange_ids))

        cursor = self.sqlite_conn.cursor()
        cursor.execute(
            f"SELECT * FROM exchanges WHERE exchange_id IN ({placeholders})",
            exchange_ids
        )

        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

        for row in rows:
            exchange_dict = dict(zip(column_names, row))

            # Find relevance score from LanceDB result
            lance_result = next(
                r for r in lance_results
                if r["exchange_id"] == exchange_dict["exchange_id"]
            )
            exchange_dict["relevance_score"] = lance_result.get("_distance", 0.0)

            results.append(exchange_dict)

        return {
            "results": results,
            "platforms_searched": platforms_searched,
            "platforms_skipped": platforms_skipped,
            "query": query
        }

    def recent_turns_summary(
        self,
        session_id: str,
        n_turns: int = 10,
        style: str = "detailed"
    ) -> Dict[str, Any]:
        """
        Summarize last N exchanges in a session.

        **Platform Support**:
        - Claude Code: ✅ Full exchanges
        - Cline: ✅ Full exchanges
        - Cursor: ✅ Full exchanges

        Args:
            session_id: Session to summarize
            n_turns: Number of recent exchanges
            style: "detailed" (70% compression) or "brief" (90% compression)

        Returns:
            {
                "summary": "...",
                "exchanges_summarized": 10,
                "platform": "claude_code",
                "data_completeness": "full",
                "time_range": {"start": "...", "end": "..."}
            }
        """
        # Get recent exchanges from SQLite (efficient ORDER BY + LIMIT)
        cursor = self.sqlite_conn.cursor()
        cursor.execute("""
            SELECT * FROM exchanges
            WHERE session_id = ?
            ORDER BY exchange_number DESC
            LIMIT ?
        """, (session_id, n_turns))

        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        exchanges = [dict(zip(column_names, row)) for row in rows]

        if not exchanges:
            return {
                "summary": None,
                "error": f"No exchanges found for session {session_id}"
            }

        # Reverse to chronological order
        exchanges.reverse()

        platform = exchanges[0]["platform"]
        data_completeness = exchanges[0]["data_completeness"]

        # Generate summary based on data availability
        if data_completeness == "full":
            summary = self._summarize_full_exchanges(exchanges, style)
        else:
            summary = self._summarize_metadata_only(exchanges)

        return {
            "summary": summary,
            "exchanges_summarized": len(exchanges),
            "platform": platform,
            "data_completeness": data_completeness,
            "time_range": {
                "start": exchanges[0]["timestamp"],
                "end": exchanges[-1]["timestamp"]
            }
        }

    def session_summary(
        self,
        session_id: str,
        strategy: str = "hierarchical"
    ) -> Dict[str, Any]:
        """
        Generate comprehensive session summary.

        **Strategies**:
        - "hierarchical": Chunk → summarize chunks → summarize summaries
        - "extractive": Extract key exchanges, summarize those
        - "chronological": Timeline-based narrative

        **Platform Support**: All platforms (adapts to data availability)

        Returns:
            {
                "summary": "...",
                "total_exchanges": 156,
                "platform": "claude_code",
                "topics": ["embeddings", "RAG", "vector databases"],
                "key_decisions": [...],
                "session_name": "...",
                "time_range": {...}
            }
        """
        # Implementation depends on chosen strategy
        pass

    def topic_search(
        self,
        topic: str,
        all_sessions: bool = True,
        since: Optional[datetime] = None,
        platforms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Find all discussions about a topic across sessions.

        **Platform Support**:
        - Claude Code: ✅ Full semantic search
        - Cline: ✅ Full semantic search
        - Cursor: ✅ Full semantic search

        Returns:
            {
                "topic": "embeddings",
                "sessions_found": 3,
                "total_exchanges": 45,
                "by_session": {
                    "session-abc": {
                        "summary": "...",
                        "exchange_count": 12,
                        "time_range": {...}
                    },
                    ...
                },
                "chronological_summary": "..."
            }
        """
        # Semantic search for topic
        search_results = self.semantic_search(
            query=topic,
            platforms=platforms,
            since=since,
            n_results=100
        )

        if not search_results["results"]:
            return {
                "topic": topic,
                "sessions_found": 0,
                "total_exchanges": 0,
                "platforms_skipped": search_results["platforms_skipped"]
            }

        # Group by session
        by_session = defaultdict(list)
        for result in search_results["results"]:
            by_session[result["session_id"]].append(result)

        # Summarize within each session
        session_summaries = {}
        for session_id, exchanges in by_session.items():
            summary = self._summarize_exchanges_for_topic(exchanges, topic)
            session_summaries[session_id] = {
                "summary": summary,
                "exchange_count": len(exchanges),
                "time_range": {
                    "start": exchanges[0]["timestamp"],
                    "end": exchanges[-1]["timestamp"]
                }
            }

        # Generate cross-session summary (evolution over time)
        chronological = self._chronological_topic_summary(session_summaries, topic)

        return {
            "topic": topic,
            "sessions_found": len(session_summaries),
            "total_exchanges": len(search_results["results"]),
            "by_session": session_summaries,
            "chronological_summary": chronological,
            "platforms_searched": search_results["platforms_searched"],
            "platforms_skipped": search_results["platforms_skipped"]
        }

    def temporal_query(
        self,
        since: datetime,
        until: Optional[datetime] = None,
        platforms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        What happened in a time range?

        **Platform Support**: All platforms (uses timestamps)

        Returns:
            {
                "summary": "...",
                "sessions": [...],
                "total_exchanges": 234,
                "time_range": {...},
                "platform_breakdown": {...}
            }
        """
        # Use SQLite for efficient temporal query
        query = "SELECT * FROM exchanges WHERE timestamp >= ?"
        params = [since.isoformat()]

        if until:
            query += " AND timestamp <= ?"
            params.append(until.isoformat())

        if platforms:
            placeholders = ",".join("?" * len(platforms))
            query += f" AND platform IN ({placeholders})"
            params.extend(platforms)

        query += " ORDER BY timestamp"

        cursor = self.sqlite_conn.cursor()
        cursor.execute(query, params)

        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        exchanges = [dict(zip(column_names, row)) for row in rows]

        # Generate chronological narrative
        summary = self._chronological_narrative(exchanges)

        # Group by session for structure
        sessions = self._group_by_session(exchanges)

        # Platform breakdown
        platform_counts = Counter(e["platform"] for e in exchanges)

        return {
            "summary": summary,
            "sessions": sessions,
            "total_exchanges": len(exchanges),
            "time_range": {
                "since": since.isoformat(),
                "until": until.isoformat() if until else "now"
            },
            "platform_breakdown": dict(platform_counts)
        }

    # ===== Helper Methods =====

    def _summarize_full_exchanges(
        self,
        exchanges: List[Dict],
        style: str
    ) -> str:
        """Generate summary from full exchange content"""
        # Use LLM to summarize conversation
        # Compression based on style: detailed=70%, brief=90%
        pass

    def _summarize_metadata_only(self, exchanges: List[Dict]) -> str:
        """Generate summary from metadata (Cursor case)"""
        # Can only describe session name, timestamps, mode
        # No conversation content available
        pass

    def _summarize_exchanges_for_topic(
        self,
        exchanges: List[Dict],
        topic: str
    ) -> str:
        """Summarize exchanges focused on specific topic"""
        # Use LLM with topic-focused prompt
        pass

    def _chronological_topic_summary(
        self,
        session_summaries: Dict,
        topic: str
    ) -> str:
        """Generate narrative of how topic evolved over time"""
        # Order sessions chronologically
        # Summarize evolution/progression
        pass

    def _chronological_narrative(self, exchanges: List[Dict]) -> str:
        """Generate timeline-based narrative"""
        # Group by day/session
        # Create chronological story
        pass

    def _group_by_session(self, exchanges: List[Dict]) -> List[Dict]:
        """Group exchanges by session with metadata"""
        by_session = defaultdict(list)
        for exchange in exchanges:
            by_session[exchange["session_id"]].append(exchange)

        sessions = []
        for session_id, session_exchanges in by_session.items():
            sessions.append({
                "session_id": session_id,
                "session_name": session_exchanges[0]["session_name"],
                "platform": session_exchanges[0]["platform"],
                "exchange_count": len(session_exchanges),
                "time_range": {
                    "start": session_exchanges[0]["timestamp"],
                    "end": session_exchanges[-1]["timestamp"]
                }
            })

        return sessions
```

### MCP Tool Interface

```python
@mcp.tool()
async def pos_conversation_query(
    action: str,
    session_id: Optional[str] = None,
    platform: Optional[str] = None,
    query: Optional[str] = None,
    n_results: Optional[int] = 20,
    n_turns: Optional[int] = 10,
    since: Optional[str] = None,
    until: Optional[str] = None,
    all_sessions: Optional[bool] = True,
    style: Optional[str] = "detailed"
) -> Dict[str, Any]:
    """
    Query conversation history with multiple strategies.

    Actions:
        - "semantic_search": Find by meaning/topic
        - "recent_turns": Summarize last N exchanges
        - "session_summary": Full session digest
        - "topic_search": Find all discussions about topic
        - "temporal": What happened in time range
        - "capabilities": Show what works on which platform

    Examples:
        # Semantic search
        pos_conversation_query(
            action="semantic_search",
            query="embedding models comparison"
        )

        # Recent turns
        pos_conversation_query(
            action="recent_turns",
            session_id="abc123",
            n_turns=10
        )

        # Topic across all sessions
        pos_conversation_query(
            action="topic_search",
            query="RAG optimization",
            all_sessions=True
        )

        # Temporal query
        pos_conversation_query(
            action="temporal",
            since="2025-10-24T00:00:00",
            until="2025-10-25T23:59:59"
        )
    """
    engine = ConversationQueryEngine(...)

    # Parse datetime strings if provided
    since_dt = datetime.fromisoformat(since) if since else None
    until_dt = datetime.fromisoformat(until) if until else None

    if action == "semantic_search":
        if not query:
            return {"error": "query parameter required for semantic_search"}
        return engine.semantic_search(
            query=query,
            platforms=[platform] if platform else None,
            since=since_dt,
            n_results=n_results
        )

    elif action == "recent_turns":
        if not session_id:
            return {"error": "session_id required for recent_turns"}
        return engine.recent_turns_summary(
            session_id=session_id,
            n_turns=n_turns,
            style=style
        )

    elif action == "session_summary":
        if not session_id:
            return {"error": "session_id required for session_summary"}
        return engine.session_summary(session_id=session_id)

    elif action == "topic_search":
        if not query:
            return {"error": "query parameter required for topic_search"}
        return engine.topic_search(
            topic=query,
            all_sessions=all_sessions,
            since=since_dt,
            platforms=[platform] if platform else None
        )

    elif action == "temporal":
        if not since_dt:
            return {"error": "since parameter required for temporal"}
        return engine.temporal_query(
            since=since_dt,
            until=until_dt,
            platforms=[platform] if platform else None
        )

    elif action == "capabilities":
        # Return capability matrix
        return {
            "platforms": {
                name: adapter.describe()
                for name, adapter in engine.adapters.items()
            },
            "capability_matrix": generate_capability_matrix()
        }

    else:
        return {"error": f"Unknown action: {action}"}
```

---

## Summarization Strategies

### Strategy Overview

| Strategy | Use Case | Compression | Quality | Speed |
|----------|----------|-------------|---------|-------|
| **Extractive** | Recent turns, highlights | Low (30-50%) | High fidelity | Fast |
| **Abstractive** | Full session, cross-session | High (80-90%) | Lossy but readable | Slow |
| **Recursive/Rolling** | Session continuity | Medium (60-70%) | Preserves flow | Medium |
| **Map-Reduce** | Large sessions, parallel | High (80-90%) | Good | Fast (parallel) |
| **Hierarchical** | Multi-level (chunk → session → project) | Very high (90%+) | Good structure | Slow |

### 1. Extractive Summarization

**How it works**: Select most important sentences/exchanges from original

**Implementation**:
```python
def extractive_summary(exchanges: List[Dict], ratio: float = 0.3) -> str:
    """
    Extract key exchanges based on importance scoring.

    Scoring factors:
    - Length (longer = more substantive)
    - Keywords (technical terms, decision language)
    - Position (first/last exchanges often important)
    - Questions/answers (user questions + AI answers)
    """
    scores = []
    for i, exchange in enumerate(exchanges):
        score = 0

        # Length score
        text = f"{exchange['user_message']} {exchange['assistant_response']}"
        score += min(len(text) / 1000, 5)  # Cap at 5 points

        # Keyword score
        decision_keywords = ["decided", "choosing", "will use", "let's go with"]
        question_keywords = ["?", "how do", "what is", "why does"]
        score += sum(2 for kw in decision_keywords if kw in text.lower())
        score += sum(1 for kw in question_keywords if kw in text.lower())

        # Position score (first/last are important)
        if i < 3 or i >= len(exchanges) - 3:
            score += 3

        scores.append((score, exchange))

    # Sort by score, take top ratio%
    scores.sort(reverse=True, key=lambda x: x[0])
    n_extract = max(int(len(scores) * ratio), 1)
    selected = [exchange for score, exchange in scores[:n_extract]]

    # Re-sort chronologically
    selected.sort(key=lambda e: e["timestamp"])

    # Format as summary
    summary_parts = []
    for exchange in selected:
        summary_parts.append(f"User: {exchange['user_message'][:200]}...")
        summary_parts.append(f"Assistant: {exchange['assistant_response'][:200]}...")
        summary_parts.append("---")

    return "\n\n".join(summary_parts)
```

**Best for**:
- Recent turns (minimal compression needed)
- Highlighting key moments
- When fidelity is critical

### 2. Abstractive Summarization (LLM-based)

**How it works**: Generate new text that captures essence

**Implementation**:
```python
async def abstractive_summary(
    exchanges: List[Dict],
    style: str = "technical",
    compression: float = 0.1  # 10% of original length
) -> str:
    """
    Use LLM to generate concise summary.

    Styles:
    - "technical": Focus on decisions, architecture, code
    - "narrative": Chronological story
    - "topical": Group by topics
    """
    # Concatenate exchanges
    full_text = []
    for exchange in exchanges:
        full_text.append(f"User: {exchange['user_message']}")
        full_text.append(f"Assistant: {exchange['assistant_response']}")

    conversation = "\n\n".join(full_text)

    # Calculate target length
    target_words = int(len(conversation.split()) * compression)

    # Style-specific prompts
    if style == "technical":
        prompt = f"""
Summarize this technical conversation in approximately {target_words} words.
Focus on:
- Technical decisions made
- Architecture choices
- Code patterns discussed
- Problems solved
- Key insights

Conversation:
{conversation}

Technical Summary:
"""

    elif style == "narrative":
        prompt = f"""
Create a chronological narrative summary of this conversation in approximately {target_words} words.
Tell the story of how the discussion progressed.

Conversation:
{conversation}

Narrative Summary:
"""

    elif style == "topical":
        prompt = f"""
Summarize this conversation in approximately {target_words} words.
Group by major topics discussed.

Conversation:
{conversation}

Topical Summary:
"""

    # Call LLM (use same model as agent, or specialized summarization model)
    summary = await llm_call(prompt)

    return summary
```

**Best for**:
- Full session summaries
- High compression needed
- When new phrasing is acceptable

### 3. Recursive/Rolling Summarization

**How it works**: Iteratively update summary with each new chunk

**Implementation**:
```python
async def recursive_summary(exchanges: List[Dict], chunk_size: int = 20) -> str:
    """
    Build summary incrementally (like context compaction does).

    Process:
    1. Summarize first chunk
    2. For each new chunk: summarize(previous_summary + new_chunk)
    3. Result: Rolling summary that grows but stays bounded
    """
    if not exchanges:
        return ""

    # Chunk exchanges
    chunks = [exchanges[i:i+chunk_size] for i in range(0, len(exchanges), chunk_size)]

    # Summarize first chunk
    current_summary = await abstractive_summary(chunks[0], compression=0.3)

    # Incrementally add each new chunk
    for chunk in chunks[1:]:
        # Format chunk
        chunk_text = []
        for exchange in chunk:
            chunk_text.append(f"User: {exchange['user_message']}")
            chunk_text.append(f"Assistant: {exchange['assistant_response']}")
        chunk_str = "\n\n".join(chunk_text)

        # Update summary: combine previous + new
        prompt = f"""
Current summary:
{current_summary}

New conversation segment:
{chunk_str}

Updated summary (incorporate new information while keeping concise):
"""

        current_summary = await llm_call(prompt)

    return current_summary
```

**Best for**:
- Session continuity (mimics platform compaction)
- Maintaining conversation flow
- Memory-bounded summarization

### 4. Map-Reduce Summarization

**How it works**: Summarize chunks in parallel, then combine

**Implementation**:
```python
async def map_reduce_summary(
    exchanges: List[Dict],
    chunk_size: int = 30
) -> str:
    """
    Parallel summarization for large sessions.

    Map phase: Summarize each chunk independently (parallel)
    Reduce phase: Combine chunk summaries into final summary
    """
    # Chunk exchanges
    chunks = [exchanges[i:i+chunk_size] for i in range(0, len(exchanges), chunk_size)]

    # MAP: Summarize chunks in parallel
    chunk_summaries = await asyncio.gather(*[
        abstractive_summary(chunk, compression=0.3)
        for chunk in chunks
    ])

    # REDUCE: Combine summaries
    combined = "\n\n---\n\n".join([
        f"Part {i+1}:\n{summary}"
        for i, summary in enumerate(chunk_summaries)
    ])

    reduce_prompt = f"""
These are summaries of different parts of a conversation.
Combine them into a unified, coherent summary.

Part summaries:
{combined}

Unified summary:
"""

    final_summary = await llm_call(reduce_prompt)

    return final_summary
```

**Best for**:
- Large sessions (100+ exchanges)
- When speed matters (parallelizable)
- Multi-day sessions

### 5. Hierarchical Summarization

**How it works**: Multiple compression levels (exchange → chunk → session → project)

**Implementation**:
```python
async def hierarchical_summary(
    exchanges: List[Dict],
    levels: int = 3
) -> Dict[str, Any]:
    """
    Multi-level compression for drill-down capability.

    Level 0: Full exchanges (100%)
    Level 1: Chunk summaries (~30%)
    Level 2: Session summary (~10%)
    Level 3: One-paragraph abstract (~2%)
    """
    result = {
        "level_0_full": exchanges,
        "level_1_chunks": [],
        "level_2_session": None,
        "level_3_abstract": None
    }

    # Level 1: Chunk summaries
    chunk_size = 20
    chunks = [exchanges[i:i+chunk_size] for i in range(0, len(exchanges), chunk_size)]

    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        summary = await abstractive_summary(chunk, compression=0.3)
        chunk_summaries.append({
            "chunk_id": i,
            "exchanges": chunk,
            "summary": summary,
            "time_range": {
                "start": chunk[0]["timestamp"],
                "end": chunk[-1]["timestamp"]
            }
        })

    result["level_1_chunks"] = chunk_summaries

    # Level 2: Session summary (combine chunk summaries)
    combined_chunks = "\n\n".join([cs["summary"] for cs in chunk_summaries])
    session_summary = await llm_call(f"""
Summarize this session (from chunk summaries):

{combined_chunks}

Session summary:
""")

    result["level_2_session"] = session_summary

    # Level 3: Abstract (extreme compression)
    abstract = await llm_call(f"""
Create a 2-3 sentence abstract of this session:

{session_summary}

Abstract:
""")

    result["level_3_abstract"] = abstract

    return result
```

**Best for**:
- Drill-down UX (show abstract, expand to session, expand to chunks)
- Multi-session projects
- Dashboard/overview displays

### Strategy Selection Logic

```python
def select_summarization_strategy(
    exchanges: List[Dict],
    use_case: str,
    constraints: Dict[str, Any]
) -> str:
    """
    Choose appropriate summarization strategy based on context.

    Args:
        exchanges: Conversation data
        use_case: "recent_turns" | "session" | "topic" | "temporal"
        constraints: {"max_tokens": int, "max_time_ms": int, "fidelity": str}

    Returns:
        Strategy name
    """
    n_exchanges = len(exchanges)

    # Recent turns: extractive (fast, high fidelity)
    if use_case == "recent_turns" and n_exchanges <= 20:
        return "extractive"

    # Small sessions: abstractive (good quality)
    if use_case == "session" and n_exchanges <= 50:
        return "abstractive"

    # Large sessions: map-reduce (parallel) or hierarchical (structured)
    if n_exchanges > 100:
        if constraints.get("max_time_ms", float("inf")) < 30000:
            return "map_reduce"  # Faster (parallel)
        else:
            return "hierarchical"  # Better structure

    # Topic/temporal: abstractive with topical focus
    if use_case in ["topic", "temporal"]:
        return "abstractive"

    # Default: recursive (good balance)
    return "recursive"
```

---

## Testing Framework

### Design Goals

1. **Trigger compaction programmatically** across platforms
2. **Measure behavior** (what's preserved, what's lost, when triggered)
3. **Validate extraction** (can we recover data post-compaction?)
4. **Benchmark queries** (does our system enable session continuity?)
5. **Document empirically** what each platform does

### Test Scenario Design

```python
from dataclasses import dataclass
from typing import Callable, Optional, List, Dict

@dataclass
class CompactionTestScenario:
    """
    Test scenario designed to trigger context compaction.

    Generates controlled conversation load to study compaction behavior.
    """
    name: str
    description: str
    target_platform: str  # "claude_code", "cursor", "cline"

    # Compaction trigger strategy
    message_count: int              # How many exchanges to generate
    target_tokens: Optional[int]    # Approximate token target (if known)
    time_duration: Optional[int]    # Duration in seconds

    # Content generation
    message_generator: Callable[[], str]  # Function to generate test messages
    include_code: bool = True      # Include code snippets (higher tokens)
    include_files: bool = True     # Reference files (metadata testing)

    # Validation checkpoints
    checkpoint_intervals: List[int] = None  # Snapshot at these message counts

    # Expected outcomes
    expected_compaction: bool = True
    expected_data_loss: Optional[str] = None  # Description

@dataclass
class CompactionObservation:
    """
    Observed behavior during compaction test.
    """
    scenario_name: str
    platform: str
    timestamp: datetime

    # Trigger conditions
    messages_sent: int
    total_tokens_estimated: int
    duration_seconds: float

    # Compaction detection
    compaction_occurred: bool
    compaction_detected_at: Optional[int]  # Message number
    compaction_trigger: Optional[str]  # "token_limit", "time", "manual", "unknown"

    # Data preservation
    pre_compaction_snapshot: Dict  # State before
    post_compaction_snapshot: Dict  # State after
    data_preserved: Dict[str, bool]  # What survived

    # Our system performance
    extraction_success: bool
    extraction_completeness: float  # 0.0-1.0
    query_performance_ms: Dict[str, float]  # Query type -> latency

    # Platform behavior
    platform_behavior: Dict[str, Any]
    storage_changes: Dict[str, Any]

    # Continuity
    conversation_continuity: bool  # Could agent continue?
    context_quality: float  # 0.0-1.0 rating
```

### Test Harness Implementation

```python
class CompactionTestHarness:
    """
    Framework for running controlled compaction tests.

    Process:
    1. Baseline snapshot
    2. Generate conversation load
    3. Monitor for compaction
    4. Post-compaction snapshot
    5. Validate data extraction
    6. Measure query performance
    7. Record observations
    """

    def __init__(
        self,
        platform: str,
        adapter: PlatformAdapter,
        output_dir: Path
    ):
        self.platform = platform
        self.adapter = adapter
        self.output_dir = output_dir
        self.observations: List[CompactionObservation] = []

    def run_scenario(self, scenario: CompactionTestScenario) -> CompactionObservation:
        """Execute compaction test scenario"""

        print(f"\n{'='*60}")
        print(f"Running: {scenario.name}")
        print(f"Platform: {self.platform}")
        print(f"Target: {scenario.message_count} messages")
        print(f"{'='*60}\n")

        observation = CompactionObservation(
            scenario_name=scenario.name,
            platform=self.platform,
            timestamp=datetime.now(),
            messages_sent=0,
            total_tokens_estimated=0,
            duration_seconds=0,
            compaction_occurred=False,
            compaction_detected_at=None,
            compaction_trigger=None,
            pre_compaction_snapshot={},
            post_compaction_snapshot={},
            data_preserved={},
            extraction_success=False,
            extraction_completeness=0.0,
            query_performance_ms={},
            platform_behavior={},
            storage_changes={},
            conversation_continuity=False,
            context_quality=0.0
        )

        start_time = time.time()

        # 1. Baseline snapshot
        print("📸 Taking baseline snapshot...")
        observation.pre_compaction_snapshot = self._take_snapshot()

        # 2. Generate conversation load
        print(f"💬 Generating {scenario.message_count} exchanges...")

        for i in range(scenario.message_count):
            message = scenario.message_generator()
            response = self._send_message(message)

            observation.messages_sent += 1
            observation.total_tokens_estimated += self._estimate_tokens(message, response)

            # Checkpoint if configured
            if scenario.checkpoint_intervals and i in scenario.checkpoint_intervals:
                self._take_checkpoint(i, observation)

            # Detect compaction
            if self._detect_compaction():
                print(f"\n🔄 COMPACTION DETECTED at message {i}")
                observation.compaction_occurred = True
                observation.compaction_detected_at = i
                observation.compaction_trigger = self._identify_compaction_trigger()
                break

            if i % 10 == 0:
                print(f"  Progress: {i}/{scenario.message_count}...")

        observation.duration_seconds = time.time() - start_time

        # 3. Post-compaction snapshot
        print("\n📸 Taking post-compaction snapshot...")
        observation.post_compaction_snapshot = self._take_snapshot()

        # 4. Analyze data preservation
        print("🔍 Analyzing data preservation...")
        observation.data_preserved = self._compare_snapshots(
            observation.pre_compaction_snapshot,
            observation.post_compaction_snapshot
        )

        # 5. Test extraction
        print("📥 Testing conversation extraction...")
        observation.extraction_success, observation.extraction_completeness = \
            self._test_extraction(observation)

        # 6. Benchmark queries
        print("⚡ Measuring query performance...")
        observation.query_performance_ms = self._benchmark_queries(observation)

        # 7. Test continuity
        print("🔗 Testing conversation continuity...")
        observation.conversation_continuity = self._test_continuity()
        observation.context_quality = self._rate_context_quality()

        # 8. Capture platform behavior
        observation.platform_behavior = self._capture_platform_behavior()
        observation.storage_changes = self._analyze_storage_changes(
            observation.pre_compaction_snapshot,
            observation.post_compaction_snapshot
        )

        # Save
        self.observations.append(observation)
        self._save_observation(observation)

        print(f"\n✅ Test complete: {scenario.name}")
        self._print_summary(observation)

        return observation

    # Implementation methods (platform-specific)

    def _send_message(self, message: str) -> str:
        """
        Send message to platform.

        Platform-specific:
        - Claude Code: API or manual paste, monitor ~/.claude/projects/
        - Cursor: Composer API or manual, monitor SQLite
        - Cline: Extension API, monitor tasks/ directory
        """
        raise NotImplementedError(f"Platform integration for {self.platform}")

    def _detect_compaction(self) -> bool:
        """
        Detect if compaction just occurred.

        Detection strategies:
        - Claude Code: New session file created, summary message
        - Cursor: New composer session, database changes
        - Cline: New task directory created
        """
        raise NotImplementedError(f"Compaction detection for {self.platform}")

    def _take_snapshot(self) -> Dict:
        """Capture current state (messages, storage, metadata)"""
        return {
            "messages": self._extract_current_messages(),
            "storage_state": self._capture_storage_state(),
            "session_metadata": self._get_session_metadata(),
            "timestamp": datetime.now().isoformat()
        }

    def _test_extraction(self, observation: CompactionObservation) -> tuple[bool, float]:
        """
        Test if adapter can extract post-compaction.

        Returns: (success, completeness)
        Completeness = messages_extracted / messages_sent
        """
        try:
            session_id = self._get_current_session_id()
            extracted = list(self.adapter.extract_exchanges(session_id))

            completeness = len(extracted) / observation.messages_sent
            return completeness > 0.0, completeness

        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            return False, 0.0

    def _benchmark_queries(self, observation: CompactionObservation) -> Dict[str, float]:
        """
        Measure query performance.

        Tests:
        - semantic_search (if supported)
        - recent_turns
        - session_summary
        - topic_search
        """
        benchmarks = {}

        query_tests = {
            "semantic_search": lambda: self._test_semantic_search(),
            "recent_turns": lambda: self._test_recent_turns(n=10),
            "session_summary": lambda: self._test_session_summary(),
            "topic_search": lambda: self._test_topic_search("testing"),
        }

        for query_type, query_fn in query_tests.items():
            if self._query_supported(query_type):
                start = time.time()
                query_fn()
                latency_ms = (time.time() - start) * 1000
                benchmarks[query_type] = latency_ms
                print(f"  {query_type}: {latency_ms:.2f}ms")
            else:
                benchmarks[query_type] = -1  # Not supported
                print(f"  {query_type}: NOT SUPPORTED")

        return benchmarks
```

### Pre-Built Test Scenarios

```python
def create_token_limit_scenario(platform: str) -> CompactionTestScenario:
    """Scenario to hit token limits"""
    return CompactionTestScenario(
        name=f"{platform}_token_limit_test",
        description="Generate high-token messages to trigger compaction",
        target_platform=platform,
        message_count=200,
        target_tokens=150000,
        time_duration=None,
        message_generator=generate_large_message,
        include_code=True,
        include_files=True,
        checkpoint_intervals=[50, 100, 150],
        expected_compaction=True
    )

def create_multi_compaction_scenario(platform: str) -> CompactionTestScenario:
    """Trigger MULTIPLE compactions in one session"""
    return CompactionTestScenario(
        name=f"{platform}_multi_compaction_test",
        description="Trigger multiple compactions",
        target_platform=platform,
        message_count=500,
        target_tokens=300000,
        time_duration=None,
        message_generator=generate_large_message,
        checkpoint_intervals=list(range(50, 500, 50)),
        expected_compaction=True,
        expected_data_loss="Earlier messages heavily summarized"
    )

def create_working_state_scenario(platform: str) -> CompactionTestScenario:
    """
    Simulate "brutal compaction" problem:
    Compaction hits mid-investigation, can we recover working state?
    """
    return CompactionTestScenario(
        name=f"{platform}_working_state_test",
        description="Compaction during active investigation",
        target_platform=platform,
        message_count=150,
        message_generator=generate_investigation_messages,
        checkpoint_intervals=[140, 145, 150],
        expected_compaction=True,
        expected_data_loss="Active working context (recent findings)"
    )

def generate_large_message() -> str:
    """Generate message with code to maximize tokens"""
    return f"""
I need help analyzing this code:

```python
class DataProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.cache = {{}}

    def process(self, items: List[Dict]) -> List[Dict]:
        results = []
        for item in items:
            transformed = self._transform(item)
            results.append(transformed)
        return results

    def _transform(self, item: Dict) -> Dict:
        # Complex transformation
        output = {{}}
        for key, value in item.items():
            if isinstance(value, str):
                output[key] = value.upper()
            elif isinstance(value, int):
                output[key] = value * 2
        return output
```

What patterns do you see? How would you optimize for performance?
"""

def generate_investigation_messages() -> str:
    """Simulate active research"""
    topics = [
        "embedding models comparison",
        "RAG optimization strategies",
        "vector database performance"
    ]
    topic = random.choice(topics)

    return f"""
I'm investigating {topic}. I've found:
1. Performance varies significantly
2. Trade-offs between accuracy and speed
3. Implementation complexity

Can you help analyze the trade-offs?
"""
```

### Test Execution & Reporting

```python
def run_compaction_validation_suite():
    """
    Run comprehensive tests across all platforms.

    Generates empirical data about compaction behavior.
    """

    output_dir = Path("workspace/validation/compaction-tests")
    output_dir.mkdir(parents=True, exist_ok=True)

    platforms = {
        "claude_code": ClaudeCodeAdapter(),
        "cline": ClineAdapter(),
        "cursor": CursorAdapter()
    }

    scenarios = ["token_limit", "multi_compaction", "working_state"]

    results = {}

    for platform_name, adapter in platforms.items():
        print(f"\n{'='*70}")
        print(f"Testing Platform: {platform_name.upper()}")
        print(f"{'='*70}")

        harness = CompactionTestHarness(
            platform=platform_name,
            adapter=adapter,
            output_dir=output_dir / platform_name
        )

        platform_results = []

        for scenario_name in scenarios:
            if scenario_name == "token_limit":
                scenario = create_token_limit_scenario(platform_name)
            elif scenario_name == "multi_compaction":
                scenario = create_multi_compaction_scenario(platform_name)
            elif scenario_name == "working_state":
                scenario = create_working_state_scenario(platform_name)

            observation = harness.run_scenario(scenario)
            platform_results.append(observation)

        results[platform_name] = platform_results

    # Generate report
    generate_comparison_report(results, output_dir / "comparison-report.md")

    return results

def generate_comparison_report(
    results: Dict[str, List[CompactionObservation]],
    output_path: Path
):
    """Generate markdown report comparing platforms"""

    report = f"""
# Compaction Behavior Validation Report

**Date**: {datetime.now().strftime("%Y-%m-%d")}
**Platforms Tested**: {", ".join(results.keys())}

## Executive Summary

| Platform | Compaction Trigger | Data Preserved | Extraction | Query Performance |
|----------|-------------------|----------------|------------|-------------------|
"""

    for platform, observations in results.items():
        # Use token_limit scenario for summary
        obs = next(o for o in observations if "token_limit" in o.scenario_name)

        trigger = f"{obs.total_tokens_estimated} tokens (msg {obs.compaction_detected_at})" \
                  if obs.compaction_occurred else "Not detected"

        preserved = f"{obs.extraction_completeness:.0%}" if obs.extraction_success else "Failed"

        query_avg = sum(obs.query_performance_ms.values()) / len(obs.query_performance_ms) \
                   if obs.query_performance_ms else 0

        report += f"| {platform} | {trigger} | {preserved} | "
        report += f"{'✅' if obs.extraction_success else '❌'} | "
        report += f"{query_avg:.0f}ms avg |\n"

    report += "\n## Detailed Findings\n\n"

    for platform, observations in results.items():
        report += f"### {platform.title()}\n\n"

        for obs in observations:
            report += f"**{obs.scenario_name}**:\n"
            report += f"- Messages sent: {obs.messages_sent}\n"
            report += f"- Compaction: {'Yes' if obs.compaction_occurred else 'No'}"
            if obs.compaction_occurred:
                report += f" (at message {obs.compaction_detected_at})\n"
            else:
                report += "\n"
            report += f"- Extraction: {obs.extraction_completeness:.0%} completeness\n"
            report += f"- Continuity: {'✅' if obs.conversation_continuity else '❌'}\n"
            report += "\n"

    output_path.write_text(report)
    print(f"\n📄 Report saved to: {output_path}")
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1)

**Goals**: Basic extraction and storage

**Deliverables**:
- ✅ Canonical schema defined
- ✅ Claude Code adapter (validated, working)
- ✅ Cline adapter (validated, working)
- ✅ SQLite storage layer
- ✅ Basic ingestion pipeline
- ⚠️ Cursor adapter (metadata-only, pending investigation)

**Success Criteria**:
- Can extract from Claude Code and Cline
- Can store in SQLite
- Can query by session_id, timestamp

### Phase 2: Querying (Week 2)

**Goals**: Query interface and LanceDB integration

**Deliverables**:
- ✅ LanceDB semantic indexing
- ✅ ConversationQueryEngine
- ✅ semantic_search() implementation
- ✅ recent_turns_summary() implementation
- ✅ temporal_query() implementation
- ✅ MCP tool interface

**Success Criteria**:
- Semantic search works across Claude Code + Cline
- Query performance < 100ms for temporal
- Query performance < 500ms for semantic

### Phase 3: Summarization (Week 3)

**Goals**: Multiple summarization strategies

**Deliverables**:
- ✅ Extractive summarization
- ✅ Abstractive summarization (LLM-based)
- ✅ Recursive/rolling summarization
- ✅ Map-reduce summarization
- ✅ Strategy selection logic

**Success Criteria**:
- Can generate session summaries
- Can generate topic summaries
- Compression ratios meet targets (30%, 70%, 90%)

### Phase 4: Testing & Validation (Week 4)

**Goals**: Empirical validation of platform behavior

**Deliverables**:
- ✅ CompactionTestHarness
- ✅ Test scenarios (token_limit, multi_compaction, working_state)
- ✅ Platform integration (manual or API)
- ✅ Automated test runs
- ✅ Comparison reports

**Success Criteria**:
- Run tests on all 3 platforms
- Document compaction triggers
- Validate extraction completeness
- Measure query performance

### Phase 5: Production (Week 5+)

**Goals**: Polish and deployment

**Deliverables**:
- ✅ Error handling and logging
- ✅ Performance optimization
- ✅ Documentation (user guide)
- ✅ Capability matrix (auto-generated, documents per-platform limitations)
- ✅ Clear messaging about what we control (nothing) vs what we extract

**Success Criteria**:
- Production-ready code quality
- Comprehensive documentation
- All platforms working within their data availability limits
- Users understand: we're passive observers, agents may ignore our tools

**Important Messaging**:
- Document that agents control themselves, not us
- Clarify we're providing optional tools
- No guarantees agents will use query interface
- Best effort extraction from platform storage

---

## Open Questions

### Technical Questions

1. **Cursor Full History** (RESOLVED):
   - Q: Where does Cursor actually store full conversation content?
   - Status: ✅ Investigation complete - not stored locally
   - Finding: Cursor only persists metadata + user prompts locally
   - Decision: Build CursorAdapter for metadata-only extraction
   - Note: This is architectural, not a missing setting

2. **Cline Timestamp Precision**:
   - Q: Are per-message timestamps available in Cline format?
   - Status: Needs deeper format investigation
   - Impact: Affects temporal query accuracy
   - Workaround: Use file mtime for now

3. **Embedding Model Choice**:
   - Q: all-MiniLM-L6-v2 vs jina-v2 vs bge-small?
   - Recommendation: Start with all-MiniLM, test jina-v2 for long contexts
   - Decision point: After Phase 2 (measure query performance)

4. **Summarization Model**:
   - Q: Use same model as agent (Sonnet 4.5) or specialized model?
   - Trade-off: Consistency vs cost vs speed
   - Decision: Start with same model, benchmark alternatives

### Product Questions

1. **User Control**:
   - Q: Should users configure what gets indexed?
   - Options: Index all, index by platform, index by session age
   - Recommendation: Index all by default, add filters later

2. **Privacy**:
   - Q: How to handle sensitive conversations?
   - Options: Encryption at rest, exclude patterns, manual approval
   - Recommendation: Document that data stays local, add encryption in Phase 5

3. **Storage Growth**:
   - Q: What happens with 1000+ sessions?
   - Estimate: 1000 sessions × 200 exchanges × 1KB = 200MB (manageable)
   - Mitigation: Prune old raw data, keep indexes

4. **Multi-Project**:
   - Q: Index conversations across all projects or per-project?
   - Recommendation: Per-project by default, add cross-project in Phase 5

### Design Questions

1. **Ingestion Trigger**:
   - Q: Real-time, periodic polling, or manual?
   - Recommendation: Start manual, add periodic polling in Phase 3
   - Frequency: Daily or on-demand

2. **Query Caching**:
   - Q: Cache expensive queries (summarization)?
   - Trade-off: Freshness vs performance
   - Recommendation: Cache session summaries, invalidate on new data

3. **Platform Priority**:
   - Q: If time-constrained, which platform first?
   - Recommendation: Cursor (primary IDE agent, full data, 17GB of history)
   - Second: Claude Code (secondary agent, full data, validated)
   - Third: Cline (full data, validated, open source)
   - Note: All are Pull Model - we control none of these agents

4. **Open Source Contributions**:
   - Q: Should we try to contribute conversation logging to Cline?
   - Trade-off: Could improve data collection vs no guarantee of acceptance
   - Decision: Extract from existing Cline storage first, contribute later if valuable
   - Reminder: Can propose, can't control maintainers

---

## Appendix: References

### Documents Created This Session

- `workspace/analysis/2025-10-25-claude-code-storage-validation.md` - Claude Code format validation
- `workspace/analysis/2025-10-25-context-compaction-agent-comparison.md` - Platform compaction differences
- `workspace/design/2025-10-25-session-continuity-architecture.md` - Initial architecture sketch

### Existing Standards

- `standards/development/session-history-analysis.md` - Cursor/Cline storage locations
- `standards/universal/database/database-patterns.md` - Database design patterns
- `standards/universal/testing/integration-testing.md` - Testing patterns

### External Research

- Cursor documentation: https://cursor.com/docs/agent/chat/history
- Web searches on conversation summarization techniques
- MTEB benchmark documentation (from earlier embedding discussion)

---

**End of Design Document**

*Status*: Ready for review
*Next Step*: Review with Josh → Decide on Phase 1 implementation start
