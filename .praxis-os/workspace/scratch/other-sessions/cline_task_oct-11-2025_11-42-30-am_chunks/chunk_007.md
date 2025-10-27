
---

## Approval & Sign-off

**Design Reviewed By**: _______________ Date: ___________  
**Technical Review**: _______________ Date: ___________  
**Documentation Review**: _______________ Date: ___________  
**Approved for Implementation**: _______________ Date: ___________  

---

**Document Version**: 1.0  
**Last Updated**: October 11, 2025  
**Next Review**: After implementation completion


<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
(No open tabs)

# Current Time
10/11/2025, 11:11:47 AM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
79,975 / 200K tokens used (40%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<attempt_completion>
<result>
## Design Document Review - Codebase-Specific Feedback

Based on my detailed analysis of the Cline codebase, here are critical updates and additions needed for the MCP Transport Fix Design Document:

### ✅ ACCURATE SECTIONS

1. **Problem Statement** - Correctly identified
2. **Root Cause Analysis** - Accurate
3. **Primary code fix location** - Lines 1004-1008 in McpHub.ts is correct
4. **Schema union order issue** - Correctly identified in schemas.ts

### 🔧 REQUIRED CORRECTIONS

#### 1. **Missing File: Controller RPC Handler**

**ADD THIS SECTION:**

**File**: `src/core/controller/mcp/addRemoteMcpServer.ts`
**Priority**: Critical (same as McpHub.ts change)

The RPC handler also needs the type field since it creates server configs:

```typescript
// Current implementation calls mcpHub.addRemoteServer()
// which will get the fix, but we should verify the handler
// doesn't have its own config creation logic
```

**Action Required**: Review `src/core/controller/mcp/addRemoteMcpServer.ts` to ensure it delegates to `McpHub.addRemoteServer()` and doesn't create configs independently.

#### 2. **SSE Transport Implementation Details**

**CORRECTION**: The design doc mentions line 271-296 for SSE case, but the actual implementation shows:

- SSE case starts around line 271
- Uses `ReconnectingEventSource` global assignment
- Has specific reconnection options: `max_retry_time: 5000`
- No `TimeoutManager.createFetch()` is used in SSE (that's in the schema transformation)

**Updated Warning Code**:
```typescript
case "sse": {
    // ⚠️ DEPRECATION WARNING
    console.warn(
        `[MCP] Server "${name}" is using deprecated SSE transport. ` +
        `Consider migrating to streamableHttp. ` +
        `See: https://docs.cline.bot/mcp/mcp-transport-mechanisms`
    )
    
    const sseOptions = {
        requestInit: {
            headers: config.headers,
        },
    }
    const reconnectingEventSourceOptions = {
        max_retry_time: 5000,
        withCredentials: !!config.headers?.["Authorization"],
    }
    global.EventSource = ReconnectingEventSource
    transport = new SSEClientTransport(new URL(config.url), {
        ...sseOptions,
        eventSourceInit: reconnectingEventSourceOptions,
    })
    // ... error handlers
}
```

#### 3. **Schema Reordering - Implementation Detail**

The current schema implementation (lines 14-86) uses a factory function `createServerTypeSchema()`. The design doc shows the full implementation but doesn't mention:

**IMPORTANT**: The schema is exported at line 87 as:
```typescript
export const ServerConfigSchema = createServerTypeSchema()
```

This means the reordering must happen within the factory function, not by replacing the export.

#### 4. **Additional File Impact: RPC Methods**

**MISSING SECTION** - These RPC methods also interact with server configs:

1. `updateServerConnectionsRPC()` - Already handles all types correctly
2. `toggleServerDisabledRPC()` - Already handles all types correctly  
3. `restartConnectionRPC()` - Already handles all types correctly
4. `deleteServerRPC()` - Already handles all types correctly

**No changes needed** but should be included in test coverage.

### 🆕 ADDITIONAL RECOMMENDATIONS

#### 5. **Add Telemetry for Transport Type Usage**

**NEW SECTION NEEDED**:

**File**: `src/services/mcp/McpHub.ts`  
**Location**: In `connectToServer()` after successful connection
**Priority**: Medium

```typescript
// After connection succeeds
connection.server.status = "connected"

// Add telemetry event
this.telemetryService.captureMcpServerConnection(
    name,
    config.type, // Track which transport type
    "connected"
)
```

This will help track migration progress from SSE → StreamableHTTP.

#### 6. **UI/UX Consideration**

**NEW SECTION**:

**File**: UI components (webview-ui)  
**Priority**: Low (future enhancement)

Consider adding visual indicator in MCP server list showing transport type:
- Green dot: StreamableHTTP (modern)
- Yellow dot: SSE (deprecated)
- Blue dot: stdio (local)

This helps users identify which servers need migration.

#### 7. **Error Message Enhancement**

**File**: `src/services/mcp/McpHub.ts`  
**Location**: Error handling in `connectToServer()`

When connection fails, include transport type in error message:
```typescript
catch (error) {
    const connection = this.findConnection(name, source)
    if (connection) {
        connection.server.status = "disconnected"
        this.appendErrorMessage(
            connection, 
            `[${config.type}] ${error instanceof Error ? error.message : String(error)}`
        )
    }
}
```

#### 8. **Testing - Missing Test Cases**

**ADD TO TESTING SECTION**:

```typescript
// Test concurrent server additions
it("should handle multiple remote servers added simultaneously", async () => {
    const hub = new McpHub(/* deps */)
    await Promise.all([
        hub.addRemoteServer("server1", "https://api1.com/mcp"),
        hub.addRemoteServer("server2", "https://api2.com/mcp"),
        hub.addRemoteServer("server3", "https://api3.com/mcp"),
    ])
    
    const settings = await hub.readAndValidateMcpSettingsFile()
    expect(settings.mcpServers["server1"].type).toBe("streamableHttp")
    expect(settings.mcpServers["server2"].type).toBe("streamableHttp")
    expect(settings.mcpServers["server3"].type).toBe("streamableHttp")
})

// Test schema fallback for malformed configs
it("should handle configs missing required fields gracefully", () => {
    const config = { url: "https://example.com" } // No type
    const result = ServerConfigSchema.parse(config)
    expect(result.type).toBe("streamableHttp") // Should default correctly
})
```

### 📝 DOCUMENTATION - ADDITIONAL FILES

**MISSING**: These doc files should also be updated:

1. **docs/mcp/mcp-overview.mdx** - If it exists, update transport mentions
2. **README.md** - If MCP is mentioned, update transport info
3. **CHANGELOG.md** - Add detailed entry with migration notes

### 🎯 IMPLEMENTATION ORDER REFINEMENT

**Revised Order** (based on dependencies):

1. **Phase 1A**: Schema reordering (do this FIRST)
   - Reason: Affects how configs are parsed everywhere
   
2. **Phase 1B**: Update `addRemoteServer()` 
   - Reason: Now correctly defaults to streamableHttp after schema fix
   
3. **Phase 1C**: Add deprecation warnings
   - Reason: Non-breaking, can be done anytime
   
4. **Phase 1D**: Add telemetry
   - Reason: Helps track migration
   
5. **Phase 2**: Documentation updates
   - Can be parallel to Phase 1

6. **Phase 3**: Testing
   - After all code changes

### ⚠️ CRITICAL CONSIDERATIONS

#### Type Safety Issue

**FOUND**: In line 1006, the design doc shows:
```typescript
type: "streamableHttp",  // Explicitly set modern transport
```

But TypeScript may require:
```typescript
type: "streamableHttp" as const,  // Type assertion for literal
```

Verify this during implementation to avoid type errors.

#### Backward Compatibility - Edge Case

**SCENARIO**: User has manually edited `mcp_settings.json` with invalid type:
```json
{
    "my-server": {
        "type": "http",  // Legacy transportType value
        "url": "https://example.com"
    }
}
```

**SOLUTION**: The schema transform already handles this (line 75):
```typescript
const finalType = data.type || (data.transportType === "http" ? "streamableHttp" : undefined) || "streamableHttp"
```

But should add validation test for this case.

### ✨ SUMMARY

The design document is **95% accurate** but needs these additions:

1. ✅ Verify RPC handler doesn't create configs independently
2. ✅ Correct SSE warning code implementation details  
3. ✅ Add telemetry for transport type tracking
4. ✅ Add concurrent server addition test
5. ✅ Consider type assertion (`as const`) for type field
6. ✅ Update implementation order (schema first, then addRemoteServer)

**RECOMMENDATION**: Design doc is solid and ready for spec creation with these minor additions. The core approach is sound and maintains backward compatibility correctly.

**NEXT STEP**: Cursor should create prAxIs OS spec incorporating these corrections.
</result>
<task_progress>
- [x] Review MCP_TRANSPORT_ANALYSIS.md
- [x] Review MCP_TRANSPORT_FIX_DESIGN.md
- [x] Learn about prAxIs OS
- [x] Provide detailed review of design doc with codebase-specific feedback
- [ ] Cursor creates spec using prAxIs OS
- [ ] Review the spec created by Cursor
- [ ] Cursor implements using prAxIs OS workflow
- [ ] Final verification
</task_progress>
</attempt_completion>

---

**User:**

[attempt_completion] Result:
The user has provided feedback on the results. Consider their input to continue the task, and then attempt completion again.
<feedback>
update the design doc
</feedback>
<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
(No open tabs)

# Current Time
10/11/2025, 11:12:52 AM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
89,311 / 200K tokens used (45%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<replace_in_file>
<path>MCP_TRANSPORT_FIX_DESIGN.md</path>
<diff>
------- SEARCH
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
=======
## Detailed Implementation Plan

### 1. Code Changes

#### 1.0. Verify RPC Handler (Investigation Required)

**File**: `src/core/controller/mcp/addRemoteMcpServer.ts`  
**Priority**: Critical  

**Action Required**: Verify that the RPC handler delegates to `McpHub.addRemoteServer()` and doesn't create server configs independently. If it does create configs, it will also need the `type: "streamableHttp"` field.

**Why Critical**: This is the entry point when adding servers via the UI/gRPC API.

---

#### 1.1. Reorder Schema Union (DO THIS FIRST)

**File**: `src/services/mcp/schemas.ts`  
**Lines**: 14-87  
**Priority**: Critical (Must be done BEFORE 1.2)  

**Rationale**: Schema reordering must happen first because it affects how all configs are parsed throughout the system. If we update `addRemoteServer()` first but the schema still prioritizes SSE, the type field might get overridden during parsing.

**Current Order**:
```typescript
const createServerTypeSchema = () => {
    return z.union([
        StdioSchema,      // 1st: Requires 'command' field
        SSESchema,        // 2nd: Requires 'url' field  ⚠️ Matches first!
        StreamableHttpSchema, // 3rd: Also requires 'url' field
    ])
}
```

**Proposed Order**:
```typescript
const createServerTypeSchema = () => {
    return z.union([
        StdioSchema,            // 1st: Requires 'command' field
        StreamableHttpSchema,   // 2nd: Modern transport, check first ✅
        SSESchema,              // 3rd: Deprecated transport, check last
    ])
}
```

**Note**: The schema is exported at line 87 as `export const ServerConfigSchema = createServerTypeSchema()`, so changes must be within the factory function.

---

#### 1.2. Update `addRemoteServer()` Method

**File**: `src/services/mcp/McpHub.ts`  
**Lines**: 1004-1008  
**Priority**: Critical (Do AFTER 1.1)  

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
    type: "streamableHttp" as const,  // Explicitly set modern transport (use 'as const' for type safety)
    url: serverUrl,
    disabled: false,
    autoApprove: [],
}
```

**Rationale**: This ensures all new remote servers use the modern transport by default. The `as const` assertion ensures TypeScript treats this as the literal type `"streamableHttp"` rather than `string`.

**Impact**: 
- ✅ All newly added remote servers will use StreamableHTTP
- ✅ No breaking changes to existing servers
- ✅ Users can still manually configure SSE in settings if needed

**Additional Check**: After parsing, add a safety warning if schema unexpectedly resolves to SSE:

```typescript
const parsedConfig = ServerConfigSchema.parse(serverConfig)

// Safety check: warn if schema resolved to SSE (shouldn't happen with our fixes)
if (parsedConfig.type === "sse") {
    console.warn(
        `[MCP] Remote server "${serverName}" unexpectedly resolved to deprecated SSE transport. ` +
        `This may indicate a configuration issue. StreamableHTTP is recommended.`
    )
}
```
+++++++ REPLACE
</diff>
<task_progress>
- [x] Review MCP_TRANSPORT_ANALYSIS.md
- [x] Review MCP_TRANSPORT_FIX_DESIGN.md
- [x] Learn about prAxIs OS
- [x] Provide detailed review of design doc
- [ ] Update design doc with corrections (in progress)
- [ ] Cursor creates spec using prAxIs OS
- [ ] Review the spec created by Cursor
- [ ] Cursor implements using prAxIs OS workflow
- [ ] Final verification
</task_progress>
</replace_in_file>

---

**User:**

[replace_in_file for 'MCP_TRANSPORT_FIX_DESIGN.md'] Result:
The content was successfully saved to MCP_TRANSPORT_FIX_DESIGN.md.

Here is the full, updated content of the file that was saved:

<final_file_content path="MCP_TRANSPORT_FIX_DESIGN.md">
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

#### 1.0. Verify RPC Handler (Investigation Required)

**File**: `src/core/controller/mcp/addRemoteMcpServer.ts`  
**Priority**: Critical  

**Action Required**: Verify that the RPC handler delegates to `McpHub.addRemoteServer()` and doesn't create server configs independently. If it does create configs, it will also need the `type: "streamableHttp"` field.

**Why Critical**: This is the entry point when adding servers via the UI/gRPC API.

---

#### 1.1. Reorder Schema Union (DO THIS FIRST)

**File**: `src/services/mcp/schemas.ts`  
**Lines**: 14-87  
**Priority**: Critical (Must be done BEFORE 1.2)  

**Rationale**: Schema reordering must happen first because it affects how all configs are parsed throughout the system. If we update `addRemoteServer()` first but the schema still prioritizes SSE, the type field might get overridden during parsing.

**Current Order**:
```typescript
const createServerTypeSchema = () => {
    return z.union([
        StdioSchema,      // 1st: Requires 'command' field
        SSESchema,        // 2nd: Requires 'url' field  ⚠️ Matches first!
        StreamableHttpSchema, // 3rd: Also requires 'url' field
    ])
}
```

**Proposed Order**:
```typescript
const createServerTypeSchema = () => {
    return z.union([
        StdioSchema,            // 1st: Requires 'command' field
        StreamableHttpSchema,   // 2nd: Modern transport, check first ✅
        SSESchema,              // 3rd: Deprecated transport, check last
    ])
}
```

**Note**: The schema is exported at line 87 as `export const ServerConfigSchema = createServerTypeSchema()`, so changes must be within the factory function.

---

#### 1.2. Update `addRemoteServer()` Method

**File**: `src/services/mcp/McpHub.ts`  
**Lines**: 1004-1008  
**Priority**: Critical (Do AFTER 1.1)  

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
    type: "streamableHttp" as const,  // Explicitly set modern transport (use 'as const' for type safety)
    url: serverUrl,
    disabled: false,
    autoApprove: [],
}
```

**Rationale**: This ensures all new remote servers use the modern transport by default. The `as const` assertion ensures TypeScript treats this as the literal type `"streamableHttp"` rather than `string`.

**Impact**: 
- ✅ All newly added remote servers will use StreamableHTTP
- ✅ No breaking changes to existing servers
- ✅ Users can still manually configure SSE in settings if needed

**Additional Check**: After parsing, add a safety warning if schema unexpectedly resolves to SSE:

```typescript
const parsedConfig = ServerConfigSchema.parse(serverConfig)

// Safety check: warn if schema resolved to SSE (shouldn't happen with our fixes)
if (parsedConfig.type === "sse") {
    console.warn(
        `[MCP] Remote server "${serverName}" unexpectedly resolved to deprecated SSE transport. ` +
        `This may indicate a configuration issue. StreamableHTTP is recommended.`
    )
}
```

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
