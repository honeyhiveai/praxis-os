# Supporting Documents Index

**Spec:** Ouroboros MCP Server  
**Date:** 2025-11-03  
**Status:** Review

---

## Document Inventory

### 1. Design Document: Ouroboros Clean Architecture

**File:** `2025-11-04-ouroboros-clean-architecture.md`  
**Type:** Strategic Design Document  
**Date:** 2025-11-04  
**Size:** 45.4 KB  
**Purpose:** Complete architectural design for the new Ouroboros MCP server

**Summary:**
Strategic design document outlining the mission-driven architecture for Ouroboros, the ground-up rewrite of the prAxIs OS MCP server. Defines the clean architecture centered on behavioral engineering as the primary mission.

**Key Sections:**
- Problem Statement (Broken behavioral engineering in current `mcp_server`)
- Goals & Non-Goals (Prioritized: Praxis > Technical > DX)
- Current State Analysis (30K LOC with deep coupling issues)
- Proposed Design (Mission-Driven Layered Architecture)
- Behavioral Engineering System (Self-reinforcing query loop)
- Success Criteria (Praxis Effectiveness metrics)

**Relevant For:**
- Phase 1: Business goals, user stories (behavioral mission)
- Phase 2: Architecture design, component boundaries
- Phase 3: Implementation phases, task breakdown
- Phase 4: Code patterns, testing strategy
- Phase 5: Success metrics, validation criteria

**Key Insights:**
- Behavioral engineering is PRIMARY mission, not secondary feature
- Domain abstraction + parameter complexity is intentional design
- Middleware must NEVER fail silently (behavioral enforcement required)
- Query prepends are the closing loop of behavioral system
- Current `mcp_server` cannot be salvaged via refactor

---

## Processing Metadata

**Mode:** Embedded (copied)  
**Processed Date:** 2025-11-03  
**Document Count:** 1  
**Total Size:** 45.4 KB  

**Verification:**
- ✅ All documents accessible
- ✅ Files readable and valid
- ✅ No broken references

