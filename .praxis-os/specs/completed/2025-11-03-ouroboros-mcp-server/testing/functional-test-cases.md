# Functional Test Cases

**Purpose:** Detailed test cases for all 25 Functional Requirements  
**Date:** 2025-11-06

---

## FR-001: Query Prepend Generation

**Test File:** `tests/ouroboros/middleware/test_prepend_generator.py`

### Test Case 1.1: Prepend includes gamification content
- **Setup:** Create search with session history
- **Action:** Generate prepend for search result
- **Assert:** Prepend contains progress tracking, emoji feedback, angle suggestions
- **Evidence:** FR-001 validated

### Test Case 1.2: Prepend adapts to query diversity
- **Setup:** Session with low diversity (all conceptual queries)
- **Action:** Generate prepend
- **Assert:** Prepend suggests location/implementation angles
- **Evidence:** Behavioral reinforcement working

### Test Case 1.3: First query gets bootstrap prepend
- **Setup:** New session (no history)
- **Action:** Generate prepend
- **Assert:** Prepend includes orientation guidance
- **Evidence:** First-run experience works

---

## FR-002: Query Tracking and Persistence

**Test File:** `tests/ouroboros/middleware/test_query_tracker.py`

### Test Case 2.1: All queries logged to SQLite
- **Setup:** Execute 5 diverse queries
- **Action:** Check query_history.db
- **Assert:** 5 rows present with correct timestamps
- **Evidence:** FR-002 validated

### Test Case 2.2: Session context captured
- **Setup:** Query with session_id
- **Action:** Check logged query
- **Assert:** session_id, conversation_id, client_id present
- **Evidence:** Context tracking works

### Test Case 2.3: Query metadata persisted
- **Setup:** Execute query
- **Action:** Check metadata fields
- **Assert:** query_text, angle, token_count, timestamp captured
- **Evidence:** Complete metadata tracking

---

## FR-003: Query Diversity Classification

**Test File:** `tests/ouroboros/middleware/test_query_classifier.py`

### Test Case 3.1: Conceptual queries classified
- **Setup:** Query "How does workflow system work?"
- **Action:** Classify query
- **Assert:** Angle = "conceptual"
- **Evidence:** Conceptual classification works

### Test Case 3.2: Location queries classified
- **Setup:** Query "Where is FileWatcher initialized?"
- **Action:** Classify query
- **Assert:** Angle = "location"
- **Evidence:** Location classification works

### Test Case 3.3: Implementation queries classified
- **Setup:** Query "Show me the pos_search_project implementation"
- **Action:** Classify query
- **Assert:** Angle = "implementation"
- **Evidence:** Implementation classification works

### Test Case 3.4: Critical path queries classified
- **Setup:** Query "What happens when index is corrupted?"
- **Action:** Classify query
- **Assert:** Angle = "critical"
- **Evidence:** Critical path classification works

### Test Case 3.5: Troubleshooting queries classified
- **Setup:** Query "Why is file watcher not starting?"
- **Action:** Classify query
- **Assert:** Angle = "troubleshooting"
- **Evidence:** Troubleshooting classification works

---

## FR-004: Behavioral Drift Detection

**Test File:** `tests/ouroboros/middleware/test_query_tracker.py`

### Test Case 4.1: Diversity drop detected
- **Setup:** Session with 10 conceptual queries in a row
- **Action:** Calculate diversity score
- **Assert:** Diversity < threshold, drift detected
- **Evidence:** FR-004 validated

### Test Case 4.2: Prepends strengthened on drift
- **Setup:** Diversity drop detected
- **Action:** Generate next prepend
- **Assert:** Prepend emphasizes missing angles
- **Evidence:** Auto-correction working

---

## FR-005: pos_search_project - Unified Search Tool

**Test File:** `tests/ouroboros/tools/test_pos_search.py`

### Test Case 5.1: search_standards action routes to StandardsIndex
- **Setup:** Call pos_search_project(action="search_standards", query="workflow")
- **Action:** Check which index handled query
- **Assert:** StandardsIndex used
- **Evidence:** FR-005.1 validated

### Test Case 5.2: search_code action routes to CodeIndex
- **Setup:** Call pos_search_project(action="search_code", query="FileWatcher")
- **Action:** Check which index handled query
- **Assert:** CodeIndex used
- **Evidence:** FR-005.2 validated

### Test Case 5.3: find_callers action routes to GraphIndex
- **Setup:** Call pos_search_project(action="find_callers", query="start_workflow")
- **Action:** Check which index handled query
- **Assert:** GraphIndex used
- **Evidence:** FR-005.3 validated

### Test Case 5.4: find_dependencies action routes correctly
- **Setup:** Call pos_search_project(action="find_dependencies", query="IndexManager")
- **Action:** Verify routing
- **Assert:** GraphIndex used with dependencies query
- **Evidence:** FR-005.4 validated

### Test Case 5.5: find_call_paths action routes correctly
- **Setup:** Call pos_search_project(action="find_call_paths", query="A", to_symbol="B")
- **Action:** Verify routing
- **Assert:** GraphIndex used with path query
- **Evidence:** FR-005.5 validated

### Test Case 5.6: search_ast action routes to ASTIndex
- **Setup:** Call pos_search_project(action="search_ast", query="pattern")
- **Action:** Check which index handled query
- **Assert:** ASTIndex used
- **Evidence:** FR-005.6 validated

---

## FR-006: pos_workflow - Workflow Execution Tool

**Test File:** `tests/server/tools/test_workflow_tools.py`

### Test Case 6.1: start action creates new workflow session
- **Setup:** Call pos_workflow(action="start", workflow_type="spec_execution_v1", target_file="spec.md")
- **Action:** Check session created
- **Assert:** Returns session_id, phase=1
- **Evidence:** FR-006.1 validated

### Test Case 6.2: get_phase action returns current phase
- **Setup:** Workflow in phase 2
- **Action:** Call pos_workflow(action="get_phase", session_id=X)
- **Assert:** Returns phase 2 details
- **Evidence:** FR-006.2 validated

### Test Case 6.3: complete_phase with evidence gate
- **Setup:** Phase with evidence requirements
- **Action:** Call complete_phase with incomplete evidence
- **Assert:** Gate blocks, error returned
- **Evidence:** FR-006.3 validated

---

## FR-007: pos_browser - Browser Automation Tool

**Test File:** `tests/ouroboros/integration/test_browser_flow.py`

### Test Case 7.1: navigate action works
- **Setup:** Call pos_browser(action="navigate", url="https://example.com")
- **Action:** Check page loaded
- **Assert:** Page title returned
- **Evidence:** FR-007.1 validated

### Test Case 7.2: Sessions isolated per conversation
- **Setup:** Two conversations, both call pos_browser
- **Action:** Check session_ids
- **Assert:** Different session_ids, isolated contexts
- **Evidence:** FR-007.2 validated

---

## FR-008: pos_filesystem - File Operations Tool

**Test File:** `tests/ouroboros/tools/test_pos_filesystem.py`

### Test Case 8.1: Path traversal attempts blocked
- **Setup:** Call pos_filesystem(action="read", path="../../../etc/passwd")
- **Action:** Execute
- **Assert:** Error raised, path rejected
- **Evidence:** FR-008.1 validated

### Test Case 8.2: Gitignore respected by default
- **Setup:** Try to write to .gitignored file
- **Action:** Call pos_filesystem(action="write", path=".gitignored_file")
- **Assert:** Error raised (unless override_gitignore=True)
- **Evidence:** FR-008.2 validated

### Test Case 8.3: Safe defaults enforced
- **Setup:** Try delete directory without recursive=True
- **Action:** Call pos_filesystem(action="delete", path="dir/")
- **Assert:** Error raised
- **Evidence:** FR-008.3 validated

---

## FR-009: get_server_info - Server Status Tool

**Test File:** `tests/unit/test_server_info_tools.py`

### Test Case 9.1: status action returns runtime info
- **Setup:** Server running
- **Action:** Call get_server_info(action="status")
- **Assert:** Returns uptime, config, subsystems_initialized
- **Evidence:** FR-009.1 validated

### Test Case 9.2: health action returns index health
- **Setup:** Indexes initialized
- **Action:** Call get_server_info(action="health")
- **Assert:** Returns index health status
- **Evidence:** FR-009.2 validated

---

## FR-010: Tool Auto-Discovery and Registration

**Test File:** `tests/ouroboros/tools/test_tool_registry.py`

### Test Case 10.1: Tools discovered from directory
- **Setup:** Drop new tool in tools/ directory
- **Action:** Restart server
- **Assert:** Tool registered in ToolRegistry
- **Evidence:** FR-010 validated

---

## FR-011: Standards Search (Hybrid)

**Test File:** `tests/ouroboros/integration/test_search_flow.py`

### Test Case 11.1: Hybrid search combines vector + FTS
- **Setup:** Index with standards docs
- **Action:** Search query with both semantic and keyword relevance
- **Assert:** Results combine both search methods
- **Evidence:** FR-011.1 validated

### Test Case 11.2: RRF fusion applied
- **Setup:** Query returns results from both vector and FTS
- **Action:** Check result ordering
- **Assert:** RRF scores calculated, results fused
- **Evidence:** FR-011.2 validated

### Test Case 11.3: Reranking optional
- **Setup:** Search with rerank=True
- **Action:** Check if reranker called
- **Assert:** Reranker applied to results
- **Evidence:** FR-011.3 validated

---

## FR-012: Code Semantic Search

**Test File:** `tests/ouroboros/subsystems/rag/test_code_index.py`

### Test Case 12.1: CodeBERT embeddings used
- **Setup:** Index code files
- **Action:** Search for semantic concept
- **Assert:** CodeBERT embeddings generated, search works
- **Evidence:** FR-012 validated

---

## FR-013: Code Graph Traversal

**Test File:** `tests/ouroboros/subsystems/rag/test_graph_index.py`

### Test Case 13.1: find_callers uses recursive CTE
- **Setup:** Call graph indexed
- **Action:** Query find_callers("function_name")
- **Assert:** Returns all callers (recursive)
- **Evidence:** FR-013.1 validated

### Test Case 13.2: find_dependencies uses recursive CTE
- **Setup:** Call graph indexed
- **Action:** Query find_dependencies("function_name")
- **Assert:** Returns all dependencies (recursive)
- **Evidence:** FR-013.2 validated

### Test Case 13.3: find_call_paths finds full paths
- **Setup:** Call graph indexed
- **Action:** Query find_call_paths("A", "B")
- **Assert:** Returns all paths from A to B
- **Evidence:** FR-013.3 validated

---

## FR-014: AST Structural Search

**Test File:** `tests/ouroboros/subsystems/rag/test_ast_index.py`

### Test Case 14.1: Tree-sitter parser used
- **Setup:** Index code files
- **Action:** Run AST query
- **Assert:** Tree-sitter parser executed, AST indexed
- **Evidence:** FR-014 validated

---

## FR-015: File Watcher (Incremental Index Updates)

**Test File:** `tests/ouroboros/subsystems/rag/test_file_watcher.py` **← CRITICAL: CURRENTLY MISSING**

### Test Case 15.1: Watcher detects new file creation
- **Setup:** Start FileWatcher monitoring .praxis-os/standards/
- **Action:** Create new file in standards/
- **Assert:** File change event detected
- **Evidence:** FR-015.1 validated

### Test Case 15.2: Watcher detects file modifications
- **Setup:** FileWatcher running
- **Action:** Modify existing file
- **Assert:** Modification event detected
- **Evidence:** FR-015.2 validated

### Test Case 15.3: Watcher detects file deletions
- **Setup:** FileWatcher running
- **Action:** Delete file
- **Assert:** Deletion event detected
- **Evidence:** FR-015.3 validated

### Test Case 15.4: Watcher triggers incremental index update
- **Setup:** FileWatcher running, index initialized
- **Action:** Create new standards file with unique term "XYZTESTTERM"
- **Assert:** Within 5s, search for "XYZTESTTERM" returns the new file
- **Evidence:** FR-015.4 validated (hot reload works)

### Test Case 15.5: Watcher uses path_mappings correctly
- **Setup:** FileWatcher with path_mappings = {"/standards": ["standards"], "/code": ["code", "ast", "graph"]}
- **Action:** Modify file in /standards
- **Assert:** Only standards index updated, not code indexes
- **Evidence:** FR-015.5 validated

### Test Case 15.6: Watcher debounces rapid changes
- **Setup:** FileWatcher running
- **Action:** Make 10 rapid edits to same file
- **Assert:** Only 1 index update triggered (debounced)
- **Evidence:** FR-015.6 validated

### Test Case 15.7: Watcher initialization on server start
- **Setup:** Start Ouroboros server with config.indexes.file_watcher.enabled=True
- **Action:** Check logs for "FileWatcher started"
- **Assert:** FileWatcher initialized and started
- **Evidence:** FR-015.7 validated (prevents production bug)

### Test Case 15.8: Watcher graceful failure if IndexManager unavailable
- **Setup:** Start server with IndexManager disabled
- **Action:** Check FileWatcher behavior
- **Assert:** FileWatcher skips initialization gracefully, warning logged
- **Evidence:** FR-015.8 validated

---

## FR-016: Index Health Checks and Auto-Repair

**Test File:** `tests/ouroboros/subsystems/rag/test_index_manager.py`

### Test Case 16.1: Corrupted index detected
- **Setup:** Corrupt index files
- **Action:** Run health check
- **Assert:** Corruption detected
- **Evidence:** FR-016.1 validated

### Test Case 16.2: Auto-repair triggered
- **Setup:** Detected corrupted index
- **Action:** Trigger auto-repair
- **Assert:** Index rebuilt successfully
- **Evidence:** FR-016.2 validated

---

## FR-017: Phase-Gated Execution

**Test File:** `tests/ouroboros/integration/test_workflow_flow.py`

### Test Case 17.1: Cannot skip phases
- **Setup:** Workflow in phase 1
- **Action:** Try to complete phase 2
- **Assert:** Error raised, phase 2 not current phase
- **Evidence:** FR-017 validated

---

## FR-018: Evidence Validation (Multi-Layer)

**Test File:** `tests/integration/test_evidence_validation_integration.py`

### Test Case 18.1: Field validation layer
- **Setup:** Evidence missing required field
- **Action:** Validate evidence
- **Assert:** Field validation error raised
- **Evidence:** FR-018.1 validated

### Test Case 18.2: Type validation layer
- **Setup:** Evidence with wrong type (string instead of boolean)
- **Action:** Validate evidence
- **Assert:** Type validation error raised
- **Evidence:** FR-018.2 validated

### Test Case 18.3: Custom validator layer
- **Setup:** Evidence fails custom validator (e.g., file doesn't exist)
- **Action:** Validate evidence
- **Assert:** Custom validation error raised
- **Evidence:** FR-018.3 validated

### Test Case 18.4: Cross-field validation layer
- **Setup:** Evidence with contradictory fields
- **Action:** Validate evidence
- **Assert:** Cross-field validation error raised
- **Evidence:** FR-018.4 validated

### Test Case 18.5: Artifact validation layer
- **Setup:** Evidence references artifact that doesn't exist
- **Action:** Validate evidence
- **Assert:** Artifact validation error raised
- **Evidence:** FR-018.5 validated

---

## FR-019: Hidden Evidence Schemas

**Test File:** `tests/ouroboros/subsystems/workflow/test_checkpoint_loader.py`

### Test Case 19.1: Schemas not exposed to agents
- **Setup:** Request workflow metadata
- **Action:** Check returned data
- **Assert:** gate-definition.yaml contents not included
- **Evidence:** FR-019 validated

---

## FR-020: Workflow State Persistence

**Test File:** `tests/unit/test_workflow_session.py`

### Test Case 20.1: State persists across restarts
- **Setup:** Start workflow, complete phase 1
- **Action:** Restart server, resume workflow
- **Assert:** Workflow resumes at phase 2
- **Evidence:** FR-020 validated

---

## FR-021: Isolated Playwright Sessions

**Test File:** `tests/ouroboros/integration/test_browser_flow.py`

### Test Case 21.1: Per-conversation isolation
- **Setup:** Two conversations
- **Action:** Both open browsers
- **Assert:** Separate Playwright sessions
- **Evidence:** FR-021 validated

---

## FR-022: Browser Actions

**Test File:** `tests/integration/test_browser_tools.py`

### Test Case 22.1: navigate action
- **Setup:** Call browser_navigate(url)
- **Action:** Check page loaded
- **Assert:** URL changed
- **Evidence:** FR-022.1 validated

### Test Case 22.2: click action
- **Setup:** Page loaded, call browser_click(selector)
- **Action:** Check element clicked
- **Assert:** Click event fired
- **Evidence:** FR-022.2 validated

### Test Case 22.3: type action
- **Setup:** Input field present, call browser_type(selector, text)
- **Action:** Check text entered
- **Assert:** Input value updated
- **Evidence:** FR-022.3 validated

---

## FR-023: Pydantic v2 Schema Validation

**Test File:** `tests/ouroboros/config/test_config_validation.py`

### Test Case 23.1: Config validates on load
- **Setup:** Load valid config/mcp.yaml
- **Action:** Parse with Pydantic
- **Assert:** MCPConfig object created
- **Evidence:** FR-023 validated

### Test Case 23.2: Invalid config fails fast
- **Setup:** Invalid config (missing required field)
- **Action:** Try to load
- **Assert:** Validation error raised immediately
- **Evidence:** FR-023 fail-fast validated

---

## FR-024: Config-Driven Language Support

**Test File:** `tests/ouroboros/config/test_language_config.py`

### Test Case 24.1: Add language via YAML only
- **Setup:** Add new language to config/mcp.yaml
- **Action:** Restart server
- **Assert:** Language parser available
- **Evidence:** FR-024 validated

---

## FR-025: Fail-Fast Validation

**Test File:** `tests/ouroboros/config/test_config_validation.py`

### Test Case 25.1: All validation at startup
- **Setup:** Config with multiple errors
- **Action:** Start server
- **Assert:** All errors reported at once
- **Evidence:** FR-025 validated

---

## Test Summary

- **Total Functional Requirements:** 25
- **Total Test Cases Defined:** 75
- **Critical Test Cases (FR-015):** 8 test cases for FileWatcher

**Most Critical Gap:** FR-015 (FileWatcher) had ZERO tests before this analysis. The 8 test cases above would have caught the initialization bug.

