---

**User:**

[ERROR] You did not use a tool in your previous response! Please retry with a tool use.

# Reminder: Instructions for Tool Use

Tool uses are formatted using XML-style tags. The tool name is enclosed in opening and closing tags, and each parameter is similarly enclosed within its own set of tags. Here's the structure:

<tool_name>
<parameter1_name>value1</parameter1_name>
<parameter2_name>value2</parameter2_name>
...
</tool_name>

For example:

<attempt_completion>
<result>
I have completed the task...
</result>
</attempt_completion>

Always adhere to this format for all tool uses to ensure proper parsing and execution.

# Next Steps

If you have completed the user's task, use the attempt_completion tool. 
If you require additional information from the user, use the ask_followup_question tool. 
Otherwise, if you have not completed the task and do not need additional information, then proceed with the next step of the task. 
(This is an automated message, so do not respond to it conversationally.)
<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
(No open tabs)

# Current Time
10/11/2025, 11:09:45 AM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
78,382 / 200K tokens used (39%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<ask_followup_question>
<question>I've now learned about Agent OS Enhanced and understand its MCP/RAG architecture, phase-gated workflows, and human-AI partnership model. What would you like to do next?</question>
<options>["Install Agent OS Enhanced in this Cline project", "Proceed with the MCP transport fix (streamableHttp bug)", "Create a spec for the MCP transport fix using Agent OS workflow", "Something else"]</options>
</ask_followup_question>

---

**User:**

[ask_followup_question for 'I've now learned about Agent OS Enhanced and understand its MCP/RAG architecture, phase-gated workflows, and human-AI partnership model. What would you like to do next?'] Result:
<answer>
since you cannot access the mcp yet, you cannot make proper use of agent os enhanced
</answer>


				# TODO LIST UPDATE REQUIRED - You MUST include the task_progress parameter in your NEXT tool call.

				**Current Progress: 2/7 items completed (29%)**

				- [x] Review MCP_TRANSPORT_ANALYSIS.md
- [x] Review MCP_TRANSPORT_FIX_DESIGN.md  
- [ ] Fix addRemoteServer() to default to streamableHttp
- [ ] Reorder schema union to prioritize StreamableHTTP
- [ ] Add deprecation warnings for SSE usage
- [ ] Test changes
- [ ] Update documentation (can be separate PR)

				

				

1. To create or update a todo list, include the task_progress parameter in the next tool call

2. Review each item and update its status:

   - Mark completed items with: - [x]

   - Keep incomplete items as: - [ ]

   - Add new items if you discover additional steps

3. Modify the list as needed:

		- Add any new steps you've discovered

		- Reorder if the sequence has changed

4. Ensure the list accurately reflects the current state



**Remember:** Keeping the todo list updated helps track progress and ensures nothing is missed.

				

**Note:** 29% of items are complete.

				
<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
(No open tabs)

# Current Time
10/11/2025, 11:10:19 AM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
78,820 / 200K tokens used (39%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<replace_in_file>
<path>src/services/mcp/McpHub.ts</path>
<diff>
------- SEARCH
		const serverConfig = {
			url: serverUrl,
			disabled: false,
			autoApprove: [],
		}
=======
		const serverConfig = {
			type: "streamableHttp" as const,
			url: serverUrl,
			disabled: false,
			autoApprove: [],
		}
+++++++ REPLACE
</diff>
<task_progress>
- [x] Review MCP_TRANSPORT_ANALYSIS.md
- [x] Review MCP_TRANSPORT_FIX_DESIGN.md
- [x] Learn about Agent OS Enhanced (not yet configured)
- [ ] Fix addRemoteServer() to default to streamableHttp
- [ ] Reorder schema union to prioritize StreamableHTTP
- [ ] Add deprecation warnings for SSE usage
- [ ] Test changes
- [ ] Update documentation (can be separate PR)
</task_progress>
</replace_in_file>

---

**User:**

The user provided the following feedback:
<feedback>
but you should understand your own code base better than cursor, so i am having you review the design doc for needed updates, then cursor will use agent os enhanced to create the spec to implement the fix, once you review that, cursor will use the agent os enhanced workflow to execute the spec
</feedback>
[replace_in_file for 'src/services/mcp/McpHub.ts'] Result:
The user denied this operation. The file was not updated, and maintains its original contents.
<environment_details>
# Cursor Visible Files
(No visible files)

# Cursor Open Tabs
(No open tabs)

# Current Time
10/11/2025, 11:11:40 AM (America/Los_Angeles, UTC-7:00)

# Context Window Usage
79,692 / 200K tokens used (40%)

# Current Mode
ACT MODE
</environment_details>

---

**Assistant:**

[Unexpected content type]

<read_file>
<path>MCP_TRANSPORT_FIX_DESIGN.md</path>
<task_progress>
- [x] Review MCP_TRANSPORT_ANALYSIS.md
- [x] Review MCP_TRANSPORT_FIX_DESIGN.md
- [x] Learn about Agent OS Enhanced
- [ ] Provide detailed review of design doc with codebase-specific feedback
- [ ] Cursor creates spec using Agent OS Enhanced
- [ ] Review the spec created by Cursor
- [ ] Cursor implements using Agent OS Enhanced workflow
- [ ] Final verification
</task_progress>
</read_file>

[Response interrupted by a tool use result. Only one tool may be used at a time and should be placed at the end of the message.]

---

**User:**

[read_file for 'MCP_TRANSPORT_FIX_DESIGN.md'] Result:
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
