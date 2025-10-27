<regex>StreamableHTTP|streamableHttp</regex>
<file_pattern>*.ts</file_pattern>
<task_progress>
- [x] Search for streaminghttp references in codebase
- [x] Search for SSE/server-sent events references
- [x] Read McpHub.ts to understand MCP transport implementation
- [x] Search for StreamableHTTP usage patterns
- [ ] Identify the bug in streaminghttp mode for tool calls
- [ ] Implement fix for streaminghttp mode
- [ ] Test the fix
- [ ] Verify MCP tool calls work correctly
</task_progress>
</search_files>

[Response interrupted by a tool use result. Only one tool may be used at a time and should be placed at the end of the message.]

---

**User:**

[search_files for 'StreamableHTTP|streamableHttp' in '*.ts'] Result:
Found 12 results.

src/services/mcp/constants.ts
│----
│import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js"
│export const TYPE_ERROR_MESSAGE = "Server type must be one of: 'stdio', 'sse', or 'streamableHttp'"
│----

src/services/mcp/types.ts
│----
│import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js"
│import { McpServer } from "@shared/mcp"
│
│----
│export type Transport = StdioClientTransport | SSEClientTransport | StreamableHTTPClientTransport
│
│		BaseConfigSchema.extend({
│----

src/services/mcp/schemas.ts
│----
│			type: z.literal("streamableHttp").optional(),
│			transportType: z.string().optional(), // Support legacy field
│				// Support both type and transportType fields
│----
│				// Note: legacy transportType was "http" not "streamableHttp"
│----
│				const finalType = data.type || (data.transportType === "http" ? "streamableHttp" : undefined) || "streamableHttp"
│				return {
│					...data,
│----
│					type: finalType as "streamableHttp",
│					// Remove the legacy field after transformation
│			})
│----
│import { getDefaultEnvironment, StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js"
│			.refine((data) => data.type === "streamableHttp", {
│				message: TYPE_ERROR_MESSAGE,
│----

src/services/mcp/McpHub.ts
│----
│import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js"
│import {
│
│----
│			let transport: StdioClientTransport | SSEClientTransport | StreamableHTTPClientTransport
│
│				}
│----
│				case "streamableHttp": {
│----
│					transport = new StreamableHTTPClientTransport(new URL(config.url), {
│						requestInit: {
│----
<environment_details>
# Cursor Visible Files
CONTRIBUTING.md

# Cursor Open Tabs
CONTRIBUTING.md

# Current Time
10/11/2025, 11:07:08 AM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
53,262 / 200K tokens used (27%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**



[Response interrupted by user]

---

**User:**

[TASK RESUMPTION] This task was interrupted just now. It may or may not be complete, so please reassess the task context. Be aware that the project state may have changed since then. The current working directory is now '/Users/josh/src/github.com/cline/cline'. If the task has not been completed, retry the last step before interruption and proceed with completing the task.

Note: If you previously attempted a tool use that the user did not provide a result for, you should assume the tool use was not successful and assess whether you should retry. If the last tool was a browser_action, the browser has been closed and you must launch a new browser if needed.

IMPORTANT: If the last tool use was a replace_in_file or write_to_file that was interrupted, the file was reverted back to its original state before the interrupted edit, and you do NOT need to re-read the file as you already have its up-to-date contents.
New instructions for task continuation:
<user_message>
cursor built 'MCP_TRANSPORT_ANALYSIS.md' (see below for file content) and 'MCP_TRANSPORT_FIX_DESIGN.md' (see below for file content) your thoughts?
</user_message>

<file_content path="MCP_TRANSPORT_ANALYSIS.md">
# MCP Transport Analysis: SSE Deprecation Issue

## Executive Summary

The Cline codebase **does support** the modern StreamableHTTP transport for MCP servers, but there are critical issues with its implementation and documentation:

1. **Default Behavior Problem**: When adding remote MCP servers via `addRemoteServer()`, the system defaults to using the **deprecated SSE transport** instead of the modern **StreamableHTTP transport**
2. **Documentation Gap**: Official documentation only mentions STDIO and SSE transports, completely omitting StreamableHTTP
3. **Schema Resolution Issue**: The Zod schema union resolution prioritizes SSE over StreamableHTTP for URL-based configs

## Background

According to the Model Context Protocol specification (as of March 2025), **Server-Sent Events (SSE) is a legacy/deprecated transport mechanism**. The modern standard is **Streamable HTTP**, which simplifies communication by using a single HTTP endpoint for bidirectional messaging.

## Current Implementation Status

### Supported Transports

The codebase supports three transport types:

| Transport | Status | Location in Code |
|-----------|--------|------------------|
| `stdio` | ✅ Current - for local servers | `StdioClientTransport` |
| `sse` | ⚠️ **DEPRECATED** - but still default for remote servers | `SSEClientTransport` |
| `streamableHttp` | ✅ Modern standard - but underutilized | `StreamableHTTPClientTransport` |

### Key Files Analysis

#### 1. `/src/services/mcp/McpHub.ts`

**Lines 1-7**: All three transports are imported
```typescript
import { SSEClientTransport } from "@modelcontextprotocol/sdk/client/sse.js"
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js"
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js"
```

**Lines 213-317**: `connectToServer()` method handles all three transport types
- Line 214-269: `stdio` case (local process communication)
- Line 271-296: `sse` case (deprecated remote communication)
- Line 298-313: `streamableHttp` case (modern remote communication)

**Lines 988-1033**: `addRemoteServer()` method - **THE PROBLEM**
```typescript
const serverConfig = {
    url: serverUrl,
    disabled: false,
    autoApprove: [],
}
// No 'type' field specified! Will default to 'sse' due to schema resolution
```

#### 2. `/src/services/mcp/schemas.ts`

**Lines 14-87**: Schema definition using Zod union

The problem is in the union order and default behavior:

```typescript
return z.union([
    // 1. Stdio config (requires 'command' field)
    BaseConfigSchema.extend({ 
        type: z.literal("stdio").optional(),
        command: z.string(),
        // ...
    }),
    
    // 2. SSE config (requires 'url' field) ⚠️ COMES BEFORE streamableHttp
    BaseConfigSchema.extend({
        type: z.literal("sse").optional(),
        url: z.string().url(),
        // ...
    })
    .transform((data) => {
        // Line 52: DEFAULTS TO 'sse' if no type specified!
        const finalType = data.type || (data.transportType === "sse" ? "sse" : undefined) || "sse"
        // ...
    }),
    
    // 3. Streamable HTTP config (also requires 'url' field)
    BaseConfigSchema.extend({
        type: z.literal("streamableHttp").optional(),
        url: z.string().url(),
        // ...
    })
    .transform((data) => {
        // Line 75: Defaults to 'streamableHttp' if no type specified
        const finalType = data.type || (data.transportType === "http" ? "streamableHttp" : undefined) || "streamableHttp"
        // ...
    }),
])
```

**The Issue**: When a config object has a `url` field but no `type` field:
1. Zod tries to match against `stdio` → fails (no `command` field)
2. Zod tries to match against `sse` → **succeeds!** (has `url` field)
3. The transform sets `type: "sse"` as the default
4. Zod never tries the `streamableHttp` schema

#### 3. `/src/services/mcp/types.ts`

**Line 9**: Type definition includes all three transports
```typescript
export type Transport = StdioClientTransport | SSEClientTransport | StreamableHTTPClientTransport
```

**Line 17**: Type alias only mentions two transports (documentation gap)
```typescript
export type McpTransportType = "stdio" | "sse" | "http"
```
Note: Should be `"stdio" | "sse" | "streamableHttp"` to match actual usage

#### 4. `/src/services/mcp/constants.ts`

**Line 10**: Error message correctly mentions all three types
```typescript
export const TYPE_ERROR_MESSAGE = "Server type must be one of: 'stdio', 'sse', or 'streamableHttp'"
```

### Documentation Analysis

#### `/docs/mcp/mcp-transport-mechanisms.mdx`

**Title**: "Learn about the **two** primary transport mechanisms..."

**Content Coverage**:
- ✅ STDIO transport (comprehensive)
- ✅ SSE transport (comprehensive, but no deprecation warning)
- ❌ StreamableHTTP transport (completely missing)

**Lines 5-6**:
> Model Context Protocol (MCP) supports two primary transport mechanisms for communication between Cline and MCP servers: Standard Input/Output (STDIO) and Server-Sent Events (SSE).

**Problem**: This is outdated and misleading. It should mention three transports and note that SSE is deprecated.

#### `/docs/mcp/configuring-mcp-servers.mdx`

**Lines 84-128**: Only documents STDIO and SSE transports, no mention of StreamableHTTP

## Impact Assessment

### For Users

1. **Invisible Degradation**: Users adding remote MCP servers unknowingly use deprecated SSE transport
2. **Compatibility Risk**: As MCP servers migrate away from SSE support, connections may break
3. **Missing Features**: StreamableHTTP may offer better performance or features users can't access
4. **Manual Workaround Required**: Users must manually edit JSON config to use StreamableHTTP

### For Server Developers

1. **Confusion**: Documentation suggests only STDIO and SSE are supported
2. **SSE Support Burden**: May continue supporting deprecated SSE because Cline appears to default to it
3. **Testing Gap**: StreamableHTTP endpoints may not be tested with Cline

## Root Cause Analysis

### Primary Issue: Schema Resolution Logic

The Zod union schema tries alternatives in order until one succeeds. Both `sse` and `streamableHttp` schemas accept configs with a `url` field, but `sse` comes first, so it always matches.

### Contributing Factors

1. **No explicit type in addRemoteServer**: The `addRemoteServer()` method doesn't set a `type` field
2. **Default fallback in transforms**: Both schemas have default fallbacks in their transforms
3. **Union order**: SSE schema is checked before StreamableHTTP schema
4. **Lack of deprecation markers**: No code comments or runtime warnings about SSE being deprecated

## Verification of use_mcp_tool

The `use_mcp_tool` functionality itself is **transport-agnostic**:

### Tool Handler Flow

1. **`UseMcpToolHandler.execute()`** (`src/core/task/tools/handlers/UseMcpToolHandler.ts`)
   - Validates parameters (server_name, tool_name, arguments)
   - Calls `config.services.mcpHub.callTool()`

2. **`McpHub.callTool()`** (`src/services/mcp/McpHub.ts:813-888`)
   - Finds the connection by server name
   - Calls `connection.client.request()`
   - The client uses whatever transport was configured during `connectToServer()`

3. **Transport Layer**
   - The MCP SDK client handles protocol details transparently
   - `use_mcp_tool` doesn't know or care which transport is used

**Conclusion**: The tool calling mechanism works correctly with any transport. The issue is solely about which transport gets selected during server configuration.

## Recommended Solutions

### Priority 1: Fix Default Transport (Critical)

**File**: `src/services/mcp/McpHub.ts`
**Method**: `addRemoteServer()` (lines 988-1033)

**Change**:
```typescript
const serverConfig = {
    type: "streamableHttp",  // ← ADD THIS LINE
    url: serverUrl,
    disabled: false,
    autoApprove: [],
}
```

**Impact**: All newly added remote servers will use StreamableHTTP by default

### Priority 2: Reorder Schema Union (High)

**File**: `src/services/mcp/schemas.ts`
**Lines**: 14-87

**Change**: Move `streamableHttp` schema before `sse` schema in the union array

**Rationale**: Prioritize the modern standard over the deprecated one

### Priority 3: Add Deprecation Warnings (High)

**Multiple Locations**:

1. Add JSDoc comment to SSE case in `McpHub.ts`:
```typescript
case "sse": {
    // ⚠️ WARNING: SSE transport is deprecated. Use 'streamableHttp' for new servers.
    // This case is maintained for backward compatibility only.
```

2. Add runtime console warning when SSE is used:
```typescript
console.warn(`[MCP] Server "${name}" is using deprecated SSE transport. Consider migrating to streamableHttp.`)
```

3. Update type definition in `types.ts`:
```typescript
export type McpTransportType = 
    | "stdio"        // Local process communication
    | "sse"          // @deprecated Use 'streamableHttp' instead
    | "streamableHttp" // Modern HTTP-based transport (recommended)
```

### Priority 4: Update Documentation (High)

**File**: `docs/mcp/mcp-transport-mechanisms.mdx`

**Changes**:
1. Update title and intro to mention three transports
2. Add new section for StreamableHTTP transport
3. Add deprecation notice to SSE section
4. Update comparison table
5. Add migration guide from SSE to StreamableHTTP

**Suggested Content**:
```markdown
## StreamableHTTP Transport (Recommended)

StreamableHTTP is the modern standard for remote MCP server communication, introduced in March 2025.

### How StreamableHTTP Works

1. The client makes HTTP POST requests to a single endpoint
2. Responses are streamed back using HTTP chunked transfer encoding
3. Bidirectional communication happens over a single connection
4. No need for separate event stream and message endpoints (unlike SSE)

### StreamableHTTP Characteristics

- **Simplicity**: Single endpoint for all communication
- **Efficiency**: Better connection management than SSE
- **Standard**: Uses standard HTTP without special protocols
- **Modern**: Official recommended transport as of MCP specification v1.0

### When to Use StreamableHTTP

StreamableHTTP is the **recommended choice** for all remote MCP servers:
- New remote server deployments
- Existing SSE servers (migrate when possible)
- Production services requiring reliability
- Cloud-hosted MCP servers

### Configuration Example

```json
{
    "mcpServers": {
        "my-remote-server": {
            "type": "streamableHttp",
            "url": "https://api.example.com/mcp",
            "headers": {
                "Authorization": "Bearer YOUR_TOKEN"
            }
        }
    }
}
```

### Migration from SSE to StreamableHTTP

If you have existing servers using SSE transport:

1. Check if your MCP server supports StreamableHTTP (most modern servers do)
2. Update your config to set `"type": "streamableHttp"`
3. Restart the connection in Cline

**Note**: SSE transport is deprecated and maintained only for backward compatibility.
```

**File**: `docs/mcp/configuring-mcp-servers.mdx`

Add StreamableHTTP example and update comparison table.

### Priority 5: Type Safety Improvements (Medium)

**File**: `src/services/mcp/schemas.ts`

Consider making the schemas more explicit:
```typescript
const StdioConfigSchema = BaseConfigSchema.extend({
    type: z.literal("stdio"),
    command: z.string(),
    // ...
}).refine(/* validation */)

const StreamableHttpConfigSchema = BaseConfigSchema.extend({
    type: z.literal("streamableHttp"),
    url: z.string().url(),
    // ...
}).refine(/* validation */)

const SseConfigSchema = BaseConfigSchema.extend({
    type: z.literal("sse"),
    url: z.string().url(),
    // ...
}).refine(/* validation */)

export const ServerConfigSchema = z.union([
    StdioConfigSchema,
    StreamableHttpConfigSchema,  // Modern standard first
    SseConfigSchema,              // Deprecated last
])
```

This makes the schema order more explicit and easier to maintain.

### Priority 6: User Migration Path (Medium)

Add a feature to detect and migrate existing SSE configs:

1. Add a method to scan for SSE-configured servers
2. Check if those servers support StreamableHTTP
3. Offer to migrate them in the UI
4. Log recommendations in console

## Testing Recommendations

### Unit Tests
- Test schema resolution with various config combinations
- Verify `addRemoteServer()` sets correct transport type
- Test backward compatibility with existing SSE configs

### Integration Tests
- Connect to a test MCP server via StreamableHTTP
- Verify `use_mcp_tool` works correctly with StreamableHTTP transport
- Test SSE-to-StreamableHTTP migration path

### Manual Testing
- Add a remote server via UI, verify it uses StreamableHTTP
- Edit config to explicitly use SSE, verify it still works (backward compatibility)
- Test with real MCP servers supporting both transports

## Implementation Checklist

- [ ] Update `addRemoteServer()` to default to `streamableHttp`
- [ ] Reorder schema union to prioritize StreamableHTTP
- [ ] Add deprecation warnings for SSE usage
- [ ] Update documentation to include StreamableHTTP
- [ ] Add migration guide in documentation
- [ ] Update type definitions with deprecation notices
- [ ] Add console warnings when SSE is detected
- [ ] Write unit tests for new default behavior
- [ ] Test backward compatibility with existing SSE configs
- [ ] Update error messages and user-facing text
- [ ] Consider adding UI indicator for deprecated transports
- [ ] Add telemetry to track transport type usage

## Backward Compatibility Notes

All changes should maintain backward compatibility:
- Existing SSE configs should continue to work
- Users with manually configured SSE servers shouldn't break
- Schema should still accept legacy `transportType` field
- Only default behavior changes, not existing behavior

## Timeline Estimate

- **Priority 1 (Fix default)**: 1-2 hours
- **Priority 2 (Schema reorder)**: 1 hour
- **Priority 3 (Deprecation warnings)**: 2-3 hours
- **Priority 4 (Documentation)**: 4-6 hours
- **Priority 5 (Type improvements)**: 2-3 hours
- **Priority 6 (Migration feature)**: 4-6 hours
- **Testing**: 4-6 hours

**Total**: 18-27 hours of development work

## Conclusion

The Cline codebase has full support for the modern StreamableHTTP transport, but a schema resolution bug causes it to default to deprecated SSE transport. This is a **critical issue** that should be fixed before it causes widespread compatibility problems as the MCP ecosystem moves away from SSE.

The fix is relatively straightforward (adding one line to `addRemoteServer()`), but comprehensive documentation updates are also needed to properly guide users and server developers.

## Appendix: Related Files

### Core Implementation
- `src/services/mcp/McpHub.ts` - Main MCP connection manager
- `src/services/mcp/schemas.ts` - Configuration schemas
- `src/services/mcp/types.ts` - Type definitions
- `src/services/mcp/constants.ts` - Constants

### Tool Implementation
- `src/core/task/tools/handlers/UseMcpToolHandler.ts` - Tool handler
- `src/core/prompts/system-prompt/tools/use_mcp_tool.ts` - Tool definition

### Controllers
- `src/core/controller/mcp/addRemoteMcpServer.ts` - RPC handler

### Documentation
- `docs/mcp/mcp-transport-mechanisms.mdx` - Transport explanation
- `docs/mcp/configuring-mcp-servers.mdx` - Configuration guide

---

**Analysis Date**: October 11, 2025  
**Cline Version**: main branch (latest)  
**Analyst**: AI Code Analysis


</file_content>

<file_content path="MCP_TRANSPORT_FIX_DESIGN.md">
# MCP Transport Fix Design Document

**Date**: October 11, 2025  
**Issue**: Remote MCP servers default to deprecated SSE transport instead of modern StreamableHTTP  
**Status**: Design Phase  
**Target Version**: Next Release  

---

## Problem Statement

When users add remote MCP servers via the `addRemoteServer()` method, the system incorrectly defaults to the **deprecated SSE transport** instead of the **modern StreamableHTTP transport**. This happens despite the codebase fully supporting StreamableHTTP.

### Root Cause

1. **Missing Type Declaration**: `addRemoteServer()` creates a server config without a `type` field (lines 1004-1008 in `McpHub.ts`)
2. **Schema Resolution Order**: The Zod union schema checks `sse` before `streamableHttp`, causing SSE to match first for URL-based configs
3. **Default Fallbacks**: Both SSE and StreamableHTTP schemas have default fallback logic that assigns a type when none is specified

---

## Design Goals

### Primary Goals

1. ✅ **Default to Modern Transport**: All new remote server connections should use StreamableHTTP by default
2. ✅ **Backward Compatibility**: Existing SSE configurations must continue to work without changes
3. ✅ **Explicit Configuration**: Users should be able to explicitly choose any transport type
4. ✅ **Deprecation Awareness**: Developers and users should be warned when using deprecated SSE transport

### Secondary Goals

5. ✅ **Type Safety**: Schema validation should be clear and maintainable
6. ✅ **Documentation**: All transports should be documented with usage recommendations
7. ✅ **Migration Path**: Provide guidance for migrating from SSE to StreamableHTTP
8. ✅ **Future-Proof**: Design should accommodate future transport types easily

---

## Proposed Solution

### Solution Overview

The fix involves **four coordinated changes**:

1. **Code Fix**: Update `addRemoteServer()` to explicitly set `type: "streamableHttp"`
2. **Schema Fix**: Reorder union to prioritize StreamableHTTP over SSE
3. **Deprecation Warnings**: Add runtime warnings when SSE is detected
4. **Documentation Updates**: Fully document all three transports with recommendations

---

## Detailed Implementation Plan

### 1. Code Changes

#### 1.1. Update `addRemoteServer()` Method

**File**: `src/services/mcp/McpHub.ts`  
**Lines**: 1004-1008  
**Priority**: Critical  

**Current Code**:
```typescript
const serverConfig = {
    url: serverUrl,
    disabled: false,
    autoApprove: [],
}
```

**Proposed Code**:
```typescript
const serverConfig = {
    type: "streamableHttp",  // Explicitly set modern transport
    url: serverUrl,
    disabled: false,
    autoApprove: [],
}
```

**Rationale**: This ensures all new remote servers use the modern transport by default.

**Impact**: 
- ✅ All newly added remote servers will use StreamableHTTP
- ✅ No breaking changes to existing servers
- ✅ Users can still manually configure SSE in settings if needed

---

#### 1.2. Reorder Schema Union

**File**: `src/services/mcp/schemas.ts`  
**Lines**: 14-86  
**Priority**: High  

**Current Order**:
```typescript
z.union([
    StdioSchema,      // 1st: Requires 'command' field
    SSESchema,        // 2nd: Requires 'url' field  ⚠️ Matches first!
    StreamableHttpSchema, // 3rd: Also requires 'url' field
])
```

**Proposed Order**:
```typescript
z.union([
    StdioSchema,            // 1st: Requires 'command' field
    StreamableHttpSchema,   // 2nd: Modern transport, check first ✅
    SSESchema,              // 3rd: Deprecated transport, check last
])
```

**Rationale**: 
- When both SSE and StreamableHTTP schemas match, prioritize the modern one
- This provides better defaults when configs lack explicit `type` fields
- Maintains backward compatibility since explicit `type: "sse"` still works

**Implementation**:
```typescript
const createServerTypeSchema = () => {
    return z.union([
        // 1. Stdio config (requires 'command' field)
        BaseConfigSchema.extend({
            type: z.literal("stdio").optional(),
            transportType: z.string().optional(),
            command: z.string(),
            args: z.array(z.string()).optional(),
            cwd: z.string().optional(),
            env: z.record(z.string()).optional(),
            url: z.string().optional(),
            headers: z.record(z.string()).optional(),
        })
            .transform((data) => {
                const finalType = data.type || (data.transportType === "stdio" ? "stdio" : undefined) || "stdio"
                return {
                    ...data,
                    type: finalType as "stdio",
                    transportType: undefined,
                }
            })
            .refine((data) => data.type === "stdio", { message: TYPE_ERROR_MESSAGE }),

        // 2. Streamable HTTP config (MODERN - check before SSE)
        BaseConfigSchema.extend({
            type: z.literal("streamableHttp").optional(),
            transportType: z.string().optional(),
            url: z.string().url("URL must be a valid URL format"),
            headers: z.record(z.string()).optional(),
            command: z.string().optional(),
            args: z.array(z.string()).optional(),
            env: z.record(z.string()).optional(),
        })
            .transform((data) => {
                const finalType = data.type || (data.transportType === "http" ? "streamableHttp" : undefined) || "streamableHttp"
                return {
                    ...data,
                    type: finalType as "streamableHttp",
                    transportType: undefined,
                }
            })
            .refine((data) => data.type === "streamableHttp", {
                message: TYPE_ERROR_MESSAGE,
            }),

        // 3. SSE config (DEPRECATED - check last)
        BaseConfigSchema.extend({
            type: z.literal("sse").optional(),
            transportType: z.string().optional(),
            url: z.string().url("URL must be a valid URL format"),
            headers: z.record(z.string()).optional(),
            command: z.string().optional(),
            args: z.array(z.string()).optional(),
            env: z.record(z.string()).optional(),
        })
            .transform((data) => {
                const finalType = data.type || (data.transportType === "sse" ? "sse" : undefined) || "sse"
                return {
                    ...data,
                    type: finalType as "sse",
                    transportType: undefined,
                }
            })
            .refine((data) => data.type === "sse", { message: TYPE_ERROR_MESSAGE }),
    ])
}
```

---

#### 1.3. Add Deprecation Warnings

**File**: `src/services/mcp/McpHub.ts`  
**Location**: In `connectToServer()` method, SSE case (around line 271)  
**Priority**: High  

**Current Code** (lines 271-296):
```typescript
case "sse": {
    const transport = new SSEClientTransport(
        new URL(serverConfig.url),
        headers,
        TimeoutManager.createFetch(serverConfig.timeout * 1000),
    )
    // ... rest of connection logic
}
```

**Proposed Code**:
```typescript
case "sse": {
    // ⚠️ DEPRECATION WARNING: SSE transport is deprecated as of MCP specification v1.0
    // Modern servers should use 'streamableHttp' transport for better performance and reliability
    // This case is maintained for backward compatibility only
    console.warn(
        `[MCP] Server "${name}" is using deprecated SSE transport. ` +
        `Consider migrating to streamableHttp for better compatibility. ` +
        `See: https://docs.cline.bot/mcp/mcp-transport-mechanisms`
    )
    
    const transport = new SSEClientTransport(
        new URL(serverConfig.url),
        headers,
        TimeoutManager.createFetch(serverConfig.timeout * 1000),
    )
    // ... rest of connection logic
}
```

**Additional Warning Location**: `addRemoteServer()` method

Add a check after parsing the config to warn if it resolved to SSE:

```typescript
const parsedConfig = ServerConfigSchema.parse(serverConfig)

// Warn if schema resolved to SSE (shouldn't happen with our fix, but safety check)
if (parsedConfig.type === "sse") {
    console.warn(
        `[MCP] Remote server "${serverName}" resolved to deprecated SSE transport. ` +
        `This may indicate a configuration issue. StreamableHTTP is recommended.`
    )
}
```

---

#### 1.4. Update Type Definitions

**File**: `src/services/mcp/types.ts`  
**Lines**: 17  
**Priority**: Low (documentation improvement)  

**Current Code**:
```typescript
export type McpTransportType = "stdio" | "sse" | "http"
```

**Proposed Code**:
```typescript
/**
 * MCP transport types
 * - stdio: Local process communication via standard input/output
 * - streamableHttp: Modern HTTP-based transport (RECOMMENDED for remote servers)
 * - sse: Server-Sent Events transport (DEPRECATED, use streamableHttp instead)
 */
export type McpTransportType = "stdio" | "streamableHttp" | "sse"

// Legacy type alias for backward compatibility
/** @deprecated Use "streamableHttp" instead */
export type LegacyMcpTransportType = "stdio" | "sse" | "http"
```

**Note**: Changed order to reflect recommendation priority.

---

### 2. Documentation Changes

#### 2.1. Update Transport Mechanisms Guide

**File**: `docs/mcp/mcp-transport-mechanisms.mdx`  
**Priority**: High  
**Estimated Lines**: +150 lines  

**Changes Required**:

1. **Update Title and Introduction**:
   - Change "two primary transport mechanisms" → "three transport mechanisms"
   - Add note about deprecation

2. **Add New Section: StreamableHTTP Transport**

```markdown
## StreamableHTTP Transport (Recommended for Remote Servers)

StreamableHTTP is the modern standard for remote MCP server communication, introduced in the MCP specification v1.0 (March 2025).

### Overview

StreamableHTTP simplifies remote communication by using a single HTTP endpoint for bidirectional messaging, eliminating the complexity of SSE's dual-endpoint architecture.

### How It Works

1. **Single Endpoint**: All communication happens through one HTTP POST endpoint
2. **Bidirectional Streaming**: Both requests and responses use HTTP chunked transfer encoding
3. **Standard HTTP**: No special protocols or event streaming required
4. **Better Error Handling**: Standard HTTP status codes and error responses

### Configuration

```json
{
    "mcpServers": {
        "my-remote-server": {
            "type": "streamableHttp",
            "url": "https://api.example.com/mcp",
            "headers": {
                "Authorization": "Bearer YOUR_API_KEY"
            }
        }
    }
}
```

### When to Use StreamableHTTP

- ✅ **All new remote server deployments**
- ✅ **Production services requiring reliability**
- ✅ **Cloud-hosted MCP servers**
- ✅ **Any server supporting modern MCP specification**

### Benefits

| Feature | StreamableHTTP | SSE (Deprecated) |
|---------|----------------|------------------|
| **Endpoints** | Single endpoint | Two endpoints (SSE + POST) |
| **Complexity** | Low | Medium |
| **Error Handling** | Standard HTTP | Custom event parsing |
| **Browser Support** | Excellent | Good |
| **Spec Status** | ✅ Current standard | ⚠️ Deprecated |

### Migration from SSE

If you have existing servers using SSE:

1. **Check Server Support**: Most modern MCP servers support StreamableHTTP
2. **Update Configuration**: Change `"type": "sse"` to `"type": "streamableHttp"`
3. **Update URL**: Ensure URL points to StreamableHTTP endpoint (may differ from SSE)
4. **Test Connection**: Restart Cline and verify connection works
5. **Remove SSE Config**: Once confirmed working, the old SSE config can be removed
```

3. **Update SSE Section with Deprecation Notice**

Add at the beginning of the SSE section:

```markdown
## Server-Sent Events (SSE) Transport

> ⚠️ **DEPRECATION NOTICE**: SSE transport is deprecated as of MCP specification v1.0 (March 2025). 
> For new remote servers, use **StreamableHTTP** instead. SSE support is maintained only for backward compatibility.

SSE was the original transport mechanism for remote MCP servers but has been superseded by StreamableHTTP.

### Why SSE is Deprecated

- More complex architecture (requires two endpoints)
- Less standard HTTP error handling
- Superseded by simpler StreamableHTTP approach
- MCP specification now recommends StreamableHTTP

### Legacy Support

Existing SSE configurations will continue to work:

```json
{
    "mcpServers": {
        "legacy-server": {
            "type": "sse",
            "url": "https://legacy.example.com/sse"
        }
    }
}
```

**Recommendation**: Migrate to StreamableHTTP when your server supports it.
```

4. **Update Comparison Table**

Add comprehensive comparison:

```markdown
## Transport Comparison

| Feature | STDIO | StreamableHTTP | SSE (Deprecated) |
|---------|-------|----------------|------------------|
| **Use Case** | Local servers | Remote servers | Legacy remote |
| **Connection** | Process stdin/stdout | HTTP POST | HTTP SSE + POST |
| **Performance** | Excellent | Very Good | Good |
| **Setup Complexity** | Medium | Low | Medium |
| **Authentication** | N/A | HTTP headers | HTTP headers |
| **Firewall Friendly** | Yes | Yes | Yes |
| **Spec Status** | ✅ Current | ✅ Current | ⚠️ Deprecated |
| **Recommendation** | Local only | ✅ Remote (default) | Migration needed |
```

---

#### 2.2. Update Configuration Guide

**File**: `docs/mcp/configuring-mcp-servers.mdx`  
**Priority**: High  

**Changes**:

1. Add StreamableHTTP examples
2. Update "Adding Remote Servers" section
3. Add migration guide section

```markdown
## Adding Remote MCP Servers

When adding remote servers, Cline defaults to the modern **StreamableHTTP** transport:

### Via UI

1. Click the MCP icon in the sidebar
2. Click "Add Server"
3. Select "Remote Server"
4. Enter server name and URL
5. The system automatically uses StreamableHTTP

### Via Configuration File

**Recommended (StreamableHTTP)**:
```json
{
    "mcpServers": {
        "my-api": {
            "type": "streamableHttp",
            "url": "https://api.example.com/mcp",
