
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
            "headers": {
                "Authorization": "Bearer token123"
            }
        }
    }
}
```

**Legacy (SSE - Not Recommended)**:
```json
{
    "mcpServers": {
        "legacy-api": {
            "type": "sse",
            "url": "https://legacy.example.com/sse",
            "headers": {
                "Authorization": "Bearer token123"
            }
        }
    }
}
```

### Migrating from SSE to StreamableHTTP

If you have existing SSE configurations, follow these steps:

1. **Identify SSE Servers**: Look for `"type": "sse"` in your config
2. **Check Server Support**: Verify your MCP server supports StreamableHTTP
3. **Update Config**: Change type to `"streamableHttp"`
4. **Update URL if needed**: Some servers use different endpoints
5. **Restart Connection**: Disconnect and reconnect in Cline UI
6. **Verify**: Test that tools work correctly with new transport

**Example Migration**:

Before:
```json
{
    "my-server": {
        "type": "sse",
        "url": "https://api.example.com/sse"
    }
}
```

After:
```json
{
    "my-server": {
        "type": "streamableHttp",
        "url": "https://api.example.com/mcp"
    }
}
```
```

---

#### 2.3. Add Migration Guide Document

**File**: `docs/mcp/migrating-sse-to-streamablehttp.mdx` (NEW FILE)  
**Priority**: Medium  

Create a dedicated migration guide for users with existing SSE setups.

---

### 3. Testing Requirements

#### 3.1. Unit Tests

**New Test File**: `src/services/mcp/__tests__/transport-defaults.test.ts`

```typescript
import { describe, it, expect } from "vitest"
import { ServerConfigSchema } from "../schemas"

describe("MCP Transport Defaults", () => {
    it("should default to streamableHttp for URL-only configs", () => {
        const config = {
            url: "https://example.com/mcp",
        }
        const result = ServerConfigSchema.parse(config)
        expect(result.type).toBe("streamableHttp")
    })

    it("should respect explicit sse type", () => {
        const config = {
            type: "sse",
            url: "https://example.com/sse",
        }
        const result = ServerConfigSchema.parse(config)
        expect(result.type).toBe("sse")
    })

    it("should respect explicit streamableHttp type", () => {
        const config = {
            type: "streamableHttp",
            url: "https://example.com/mcp",
        }
        const result = ServerConfigSchema.parse(config)
        expect(result.type).toBe("streamableHttp")
    })

    it("should default to stdio for command-based configs", () => {
        const config = {
            command: "node",
            args: ["server.js"],
        }
        const result = ServerConfigSchema.parse(config)
        expect(result.type).toBe("stdio")
    })

    it("should handle legacy transportType field", () => {
        const config = {
            transportType: "http",
            url: "https://example.com/mcp",
        }
        const result = ServerConfigSchema.parse(config)
        expect(result.type).toBe("streamableHttp")
    })
})
```

**Update Existing Tests**: `src/services/mcp/__tests__/McpHub.test.ts`

```typescript
describe("addRemoteServer", () => {
    it("should default new remote servers to streamableHttp", async () => {
        const hub = new McpHub(/* dependencies */)
        await hub.addRemoteServer("test-server", "https://example.com/mcp")
        
        const settings = await hub.readAndValidateMcpSettingsFile()
        expect(settings.mcpServers["test-server"].type).toBe("streamableHttp")
    })
})
```

#### 3.2. Integration Tests

**Test File**: `src/services/mcp/__tests__/transport-integration.test.ts`

Tests should verify:
- ✅ StreamableHTTP connections work correctly
- ✅ SSE connections still work (backward compatibility)
- ✅ Tool calls work with all transport types
- ✅ Deprecation warnings appear for SSE usage
- ✅ Schema resolution prioritizes StreamableHTTP

#### 3.3. Manual Testing Checklist

- [ ] Add new remote server via UI → verify StreamableHTTP used
- [ ] Add remote server programmatically → verify StreamableHTTP used
- [ ] Manually configure SSE server → verify it still works
- [ ] Manually configure StreamableHTTP server → verify it works
- [ ] Check console for deprecation warnings when SSE used
- [ ] Test `use_mcp_tool` with StreamableHTTP transport
- [ ] Test `use_mcp_tool` with SSE transport (backward compatibility)
- [ ] Verify existing SSE configs continue working after update

---

## Rollout Plan

### Phase 1: Code Changes (Week 1)

1. ✅ Implement `addRemoteServer()` fix
2. ✅ Reorder schema union
3. ✅ Add deprecation warnings
4. ✅ Update type definitions
5. ✅ Write unit tests
6. ✅ Code review and approval

### Phase 2: Documentation (Week 1)

1. ✅ Update transport mechanisms guide
2. ✅ Update configuration guide
3. ✅ Create migration guide
4. ✅ Update examples in other docs
5. ✅ Review documentation changes

### Phase 3: Testing (Week 2)

1. ✅ Run unit tests
2. ✅ Run integration tests
3. ✅ Manual testing with real MCP servers
4. ✅ Test backward compatibility
5. ✅ Performance testing (if needed)

### Phase 4: Release (Week 2)

1. ✅ Merge to main branch
2. ✅ Update CHANGELOG with migration notes
3. ✅ Release notes highlighting the change
4. ✅ Monitor for issues in first week
5. ✅ Respond to user questions

---

## Backward Compatibility

### What Continues to Work

✅ Existing SSE configurations in `mcp_settings.json`  
✅ Manually configured SSE servers  
✅ Legacy `transportType` field  
✅ All existing tool calls  
✅ All existing connections  

### What Changes

⚠️ **New remote servers** will default to StreamableHTTP instead of SSE  
⚠️ **Console warnings** will appear for SSE usage  
⚠️ **Documentation** now recommends StreamableHTTP  

### Breaking Changes

❌ **NONE** - This is a non-breaking change

---

## Risk Assessment

### Low Risk ✅

- **Change is minimal**: One line added to `addRemoteServer()`
- **Schema reorder**: Doesn't break existing configs with explicit types
- **Warnings only**: No functional changes to SSE support
- **Well tested**: Comprehensive test coverage

### Mitigation Strategies

1. **Extensive Testing**: Unit + integration + manual tests
2. **Gradual Rollout**: Monitor closely after release
3. **Clear Documentation**: Migration guide and examples
4. **Backward Compatibility**: Maintain full SSE support
5. **Easy Rollback**: Single-line change can be reverted quickly

---

## Success Metrics

### Primary Metrics

1. ✅ **Default Transport**: 100% of new remote servers use StreamableHTTP
2. ✅ **Zero Breakage**: No existing SSE configurations break
3. ✅ **Deprecation Awareness**: Users see warnings for SSE usage

### Secondary Metrics

4. ✅ **Documentation Coverage**: All three transports documented
5. ✅ **Migration Rate**: Track users migrating from SSE to StreamableHTTP
6. ✅ **Support Tickets**: No increase in MCP-related issues

---

## Future Considerations

### Short Term (3-6 months)

- Monitor adoption of StreamableHTTP vs SSE usage
- Track deprecation warnings in telemetry
- Gather feedback on migration experience

### Medium Term (6-12 months)

- Consider UI indicator showing transport type
- Add migration tool in UI to automatically convert SSE → StreamableHTTP
- Enhance error messages for transport-specific issues

### Long Term (12+ months)

- Evaluate removing SSE support entirely (if ecosystem supports it)
- Consider auto-migration for SSE configs at startup
- Potentially remove SSE from schema union (breaking change)

---

## Appendix: Files to Modify

### Core Implementation Files

| File | Lines | Change Type | Priority |
|------|-------|-------------|----------|
| `src/services/mcp/McpHub.ts` | 1004-1008 | Add type field | Critical |
| `src/services/mcp/schemas.ts` | 14-86 | Reorder union | High |
| `src/services/mcp/McpHub.ts` | 271-296 | Add warnings | High |
| `src/services/mcp/types.ts` | 17 | Update types | Low |
| `src/services/mcp/constants.ts` | N/A | No changes | N/A |

### Documentation Files

| File | Change Type | Priority |
|------|-------------|----------|
| `docs/mcp/mcp-transport-mechanisms.mdx` | Major update | High |
| `docs/mcp/configuring-mcp-servers.mdx` | Update examples | High |
| `docs/mcp/migrating-sse-to-streamablehttp.mdx` | New file | Medium |
| `CHANGELOG.md` | Add entry | High |

### Test Files

| File | Change Type | Priority |
|------|-------------|----------|
| `src/services/mcp/__tests__/transport-defaults.test.ts` | New file | High |
| `src/services/mcp/__tests__/McpHub.test.ts` | Add tests | High |
| `src/services/mcp/__tests__/transport-integration.test.ts` | New file | Medium |

---

## Questions & Answers

### Q: Why not remove SSE support entirely?

**A**: Many existing MCP servers still use SSE. Removing it would be a breaking change affecting users immediately. The deprecation path allows ecosystem to migrate gracefully.

### Q: What if a server only supports SSE?

**A**: Users can manually configure `"type": "sse"` in their settings. The system will continue to support SSE connections indefinitely.

### Q: Will existing users see any changes?

**A**: Existing configurations won't change. Only new servers added via UI will default to StreamableHTTP. Users may see deprecation warnings if they're using SSE.

### Q: How do users know which transport their server uses?

**A**: Currently, this isn't visible in the UI. Future enhancement could add a transport type indicator in the server list.

### Q: What if the schema reordering breaks something?

**A**: The schema order only affects configs without an explicit `type` field. All existing configs should have types (either set explicitly or transformed from previous defaults). Testing will verify this.

### Q: Is this change telemetry-tracked?

**A**: Not in this initial implementation, but adding telemetry for transport type usage would be valuable for tracking migration progress.

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

</final_file_content>

IMPORTANT: For any future changes to this file, use the final_file_content shown above as your reference. This content reflects the current state of the file, including any auto-formatting (e.g., if you used single quotes but the formatter converted them to double quotes). Always base your SEARCH/REPLACE operations on this final version to ensure accuracy.


<environment_details>
# Cursor Visible Files
MCP_TRANSPORT_FIX_DESIGN.md

# Cursor Open Tabs
MCP_TRANSPORT_FIX_DESIGN.md

# Current Time
10/11/2025, 11:13:52 AM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
99,646 / 200K tokens used (50%)

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
=======
#### 1.4. Add Telemetry for Transport Type Usage

**File**: `src/services/mcp/McpHub.ts`  
**Location**: In `connectToServer()` after successful connection (around line 380)  
**Priority**: Medium  

**Proposed Code**:
```typescript
// After connection succeeds
connection.server.status = "connected"
connection.server.error = ""

// Add telemetry event to track transport type usage
this.telemetryService.capture("mcp.server.connected", {
    server_name: name,
    transport_type: config.type,
    has_auth: !!config.headers?.["Authorization"],
})
```

**Rationale**: This helps track:
- Adoption rate of StreamableHTTP vs SSE
- Migration progress from deprecated transports
- Transport type usage patterns
- Authentication usage patterns

**Note**: The telemetry service may need a new event type added if `mcp.server.connected` doesn't exist.

---

#### 1.5. Enhance Error Messages with Transport Type

**File**: `src/services/mcp/McpHub.ts`  
**Location**: Error handling in `connectToServer()` catch blocks  
**Priority**: Low  

**Current Pattern**:
```typescript
catch (error) {
    const connection = this.findConnection(name, source)
    if (connection) {
        connection.server.status = "disconnected"
        this.appendErrorMessage(connection, error instanceof Error ? error.message : String(error))
    }
    throw error
}
```

**Proposed Enhancement**:
```typescript
catch (error) {
    const connection = this.findConnection(name, source)
    if (connection) {
        connection.server.status = "disconnected"
        // Include transport type in error message for better debugging
        const errorMsg = error instanceof Error ? error.message : String(error)
        this.appendErrorMessage(
            connection, 
            `[${config.type}] ${errorMsg}`
        )
    }
    throw error
}
```

**Rationale**: Including the transport type in error messages helps users and support diagnose connection issues more quickly.

---

#### 1.6. Update Type Definitions

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
+++++++ REPLACE
</diff>
<task_progress>
- [x] Review MCP_TRANSPORT_ANALYSIS.md
- [x] Review MCP_TRANSPORT_FIX_DESIGN.md
- [x] Learn about prAxIs OS
- [x] Provide detailed review of design doc
- [x] Update design doc with SSE implementation corrections
- [x] Add telemetry and error message enhancements
- [ ] Add additional test cases
- [ ] Add refined implementation order
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
    
    transport.onerror = async (error) => {
        console.error(`Transport error for "${name}":`, error)
        const connection = this.findConnection(name, source)
        if (connection) {
            connection.server.status = "disconnected"
            this.appendErrorMessage(connection, error instanceof Error ? error.message : `${error}`)
        }
        await this.notifyWebviewOfServerChanges()
    }
    break
}
```

**Note**: The actual SSE implementation uses `ReconnectingEventSource` with specific options, not `TimeoutManager.createFetch()` as originally documented.

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

#### 1.4. Add Telemetry for Transport Type Usage

**File**: `src/services/mcp/McpHub.ts`  
**Location**: In `connectToServer()` after successful connection (around line 380)  
**Priority**: Medium  

**Proposed Code**:
```typescript
// After connection succeeds
connection.server.status = "connected"
connection.server.error = ""

// Add telemetry event to track transport type usage
this.telemetryService.capture("mcp.server.connected", {
    server_name: name,
    transport_type: config.type,
    has_auth: !!config.headers?.["Authorization"],
})
```

**Rationale**: This helps track:
- Adoption rate of StreamableHTTP vs SSE
- Migration progress from deprecated transports
- Transport type usage patterns
- Authentication usage patterns

**Note**: The telemetry service may need a new event type added if `mcp.server.connected` doesn't exist.

---

#### 1.5. Enhance Error Messages with Transport Type

**File**: `src/services/mcp/McpHub.ts`  
**Location**: Error handling in `connectToServer()` catch blocks  
**Priority**: Low  

**Current Pattern**:
```typescript
catch (error) {
    const connection = this.findConnection(name, source)
    if (connection) {
        connection.server.status = "disconnected"
        this.appendErrorMessage(connection, error instanceof Error ? error.message : String(error))
    }
    throw error
}
```

**Proposed Enhancement**:
```typescript
catch (error) {
    const connection = this.findConnection(name, source)
    if (connection) {
        connection.server.status = "disconnected"
        // Include transport type in error message for better debugging
        const errorMsg = error instanceof Error ? error.message : String(error)
        this.appendErrorMessage(
            connection, 
            `[${config.type}] ${errorMsg}`
        )
    }
    throw error
}
```

**Rationale**: Including the transport type in error messages helps users and support diagnose connection issues more quickly.

---

#### 1.6. Update Type Definitions

**File**: `src/services/mcp/types.ts`  
**Lines**: 17  
