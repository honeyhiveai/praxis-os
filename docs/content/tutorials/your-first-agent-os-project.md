---
sidebar_position: 3
doc_type: tutorial
---

# Your First Agent OS Enhanced Project

Welcome! This tutorial will guide you through your first spec-driven development cycle with Agent OS Enhanced. By the end, you'll understand why **specification-driven development is THE main vehicle** for AI-assisted software development.

## Learning Goals

By completing this tutorial, you will learn to:

1. Have a design conversation with an AI agent
2. Use the `spec_creation_v1` workflow to create a formal specification
3. Review and understand spec artifacts (SRD, technical specs, implementation plan)
4. Use the `spec_execution_v1` workflow to implement the specification
5. Verify generated code and tests
6. Understand why specs are essential for production-quality AI-generated code

## Time Estimate

**15-20 minutes** for first-time users

## Prerequisites

- Agent OS Enhanced installed in your project ([Installation Guide](./installation))
- A Cursor AI session open in your project

## What You'll Build

A simple **user profile API endpoint** with the following features:
- `GET /api/users/:id` endpoint
- Returns user profile data (name, email, created_at)
- Input validation
- Error handling
- Unit tests with ≥90% coverage

This is a deliberately simple feature so you can focus on **learning the workflow**, not debugging complex code.

---

## Part 1: Design Conversation (3 minutes)

The first step is to have a **conversational design discussion** with your AI agent.

### Step 1: Start the Conversation

In your Cursor chat, say:

```
I want to add a user profile API endpoint. Let's discuss the design before we start.
```

**Expected Response:**

The agent will ask clarifying questions about:
- What data should the user profile include?
- Authentication requirements?
- Response format (JSON)?
- Error handling needs?

**Success Indicator:** ✅ Agent is asking design questions, not writing code immediately

### Step 2: Answer Design Questions

Respond to the agent's questions. For this tutorial, use these answers:

```
- Profile should include: id, name, email, created_at
- No authentication needed for this tutorial
- JSON response format
- Return 404 if user not found, 400 for invalid user ID format
```

**Expected Response:**

The agent will summarize the design and may suggest additional considerations (logging, rate limiting, etc.).

**Success Indicator:** ✅ Agent has a clear understanding of the feature

### Step 3: Request Specification Creation

Now that the design is clear, request a formal specification:

```
Great! Let's create a formal specification for this. Use the spec_creation_v1 workflow.
```

**Expected Response:**

The agent will:
1. Acknowledge the workflow request
2. Start the `spec_creation_v1` workflow
3. Begin creating specification documents

**Success Indicator:** ✅ You see the agent mention "spec_creation_v1" and start creating files in `.agent-os/specs/`

**Why This Matters:**

The design conversation ensures the AI understands your intent **before writing any code**. Jumping straight to code often leads to misaligned implementations that require extensive rework.

---

## Part 2: Create Specification (5 minutes)

The `spec_creation_v1` workflow is **phase-gated**, meaning the AI cannot skip ahead or bypass quality checks.

### What's Happening

The agent will progress through these phases:

1. **Phase 1: Discovery & Requirements** - Analyzes your project and clarifies requirements
2. **Phase 2: System Specification** - Creates technical design documents
3. **Phase 3: Task Breakdown** - Creates detailed implementation plan
4. **Phase 4: Approval & Finalization** - Reviews and finalizes the spec

### What You'll See

The agent will:
- Ask follow-up questions if anything is unclear
- Create files in `.agent-os/specs/YYYY-MM-DD-feature-name/`
- Show you the progress through phases
- Request your approval before finalizing

### Step 4: Monitor Workflow Progress

Watch the chat as the agent progresses through phases. The agent may ask questions like:

- "Should the API return timestamps in ISO 8601 format?"
- "Do you want pagination support for future endpoints?"

Answer based on the feature requirements. For this tutorial:
- **Timestamps:** Yes, ISO 8601
- **Pagination:** Not needed for this simple endpoint

**Expected Output:**

You'll see files being created:
```
.agent-os/specs/2025-10-12-user-profile-endpoint/
  ├── README.md           # Specification overview
  ├── srd.md             # Software Requirements Document
  ├── specs.md           # Technical specification
  ├── tasks.md           # Implementation tasks
  └── implementation.md  # Implementation guidance
```

**Success Indicator:** ✅ All 5 specification files created in `.agent-os/specs/`

**Why This Matters:**

The specification serves as a **contract** between you and the AI. It ensures everyone (humans and AI) agrees on what will be built before a single line of code is written.

---

## Part 3: Review Specification (3 minutes)

Now that the spec is created, take a moment to review it. This step is **critical** - it's much easier to catch issues now than after code is written.

### Step 5: Open and Review `README.md`

Open `.agent-os/specs/[date]-user-profile-endpoint/README.md`

**What to Look For:**

- **Objectives:** Does it match your feature request?
- **Deliverables:** Are all expected artifacts listed?
- **Success Metrics:** Are the success criteria clear?

**Success Indicator:** ✅ Objectives align with your intent

### Step 6: Skim `srd.md` (Software Requirements Document)

Open `srd.md` and check:

- **Functional Requirements:** Are all the behaviors you discussed captured?
- **Non-Functional Requirements:** Performance, security, maintainability
- **Constraints:** Any technical limitations noted?

**Success Indicator:** ✅ All key requirements from your design conversation are documented

### Step 7: Skim `tasks.md` (Implementation Plan)

Open `tasks.md` to see the breakdown of work:

**What You'll See:**

```markdown
## Phase 1: API Endpoint Setup
### Task 1.1: Create Route Handler
- Define GET /api/users/:id endpoint
- Set up request validation
- Time estimate: 30 minutes

### Task 1.2: Implement Business Logic
...
```

**Success Indicator:** ✅ Tasks are broken down into small, clear units of work

### Step 8: Approve or Request Changes

If everything looks good:

```
Looks great! Approve the specification.
```

If you see issues:

```
In the srd.md, I notice the email validation is missing. Can we add a requirement for valid email format?
```

The agent will update the spec and show you the changes.

**Why This Matters:**

Reviewing the spec takes 3-5 minutes but can save **hours of rework**. It's the phase-gate where you ensure the AI truly understands what you want.

---

## Part 4: Implement Specification (5 minutes)

Now that the spec is approved, it's time to implement it!

### Step 9: Request Spec Execution

In Cursor chat, say:

```
Perfect! Let's implement this spec using spec_execution_v1 workflow.
```

**Expected Response:**

The agent will:
1. Load the specification from `.agent-os/specs/`
2. Start the `spec_execution_v1` workflow
3. Begin executing tasks from `tasks.md`

**Success Indicator:** ✅ Agent mentions "spec_execution_v1" and starts creating code files

### What's Happening

The agent will:
- Work through each task in `tasks.md` sequentially
- Create source files, tests, and documentation
- Follow the technical design from `specs.md`
- Cannot skip tasks or bypass quality gates

### What You'll See

```
✅ Task 1.1 complete: Create Route Handler
   Created: src/api/routes/users.ts

✅ Task 1.2 complete: Implement Business Logic
   Created: src/services/user-profile-service.ts

✅ Task 1.3 complete: Add Input Validation
   Updated: src/api/routes/users.ts

✅ Task 1.4 complete: Implement Error Handling
   Updated: src/api/routes/users.ts
   Updated: src/services/user-profile-service.ts

✅ Task 1.5 complete: Write Unit Tests
   Created: tests/api/routes/users.test.ts
   Created: tests/services/user-profile-service.test.ts
```

### Step 10: Watch for Checkpoints

The workflow has **validation gates** between phases. The agent will:
- Run tests
- Check code coverage
- Validate against the spec
- Show you the results

You may see:

```
✅ Phase 1 validation passed:
   - All tests passing (12/12)
   - Code coverage: 94.2%
   - All acceptance criteria met
```

**Success Indicator:** ✅ All validation gates pass, implementation complete

**Why This Matters:**

The phase-gated workflow ensures the AI **cannot cut corners**. Tests, coverage, and acceptance criteria are enforced by the workflow engine, not by hoping the AI "remembers" to do them.

---

## Part 5: Review Implementation (2 minutes)

The implementation is complete! Now verify the work.

### Step 11: Review Generated Files

Check that the expected files were created:

```
src/api/routes/users.ts              # Route handler
src/services/user-profile-service.ts  # Business logic
tests/api/routes/users.test.ts        # Route tests
tests/services/user-profile-service.test.ts  # Service tests
```

**Success Indicator:** ✅ All files exist and are not empty

### Step 12: Run the Tests

In your terminal:

```bash
npm test
# or
pytest  # (Python)
cargo test  # (Rust)
```

**Expected Output:**

```
✅ All tests passed (12/12)
Code coverage: 94.2%
```

**Success Indicator:** ✅ All tests pass with >90% coverage

### Step 13: Try the API

If you have a dev server running:

```bash
curl http://localhost:3000/api/users/123
```

**Expected Response:**

```json
{
  "id": "123",
  "name": "John Doe",
  "email": "john@example.com",
  "created_at": "2025-10-12T10:30:00Z"
}
```

**Success Indicator:** ✅ API responds correctly

**Why This Matters:**

The generated code is **production-ready**, not prototype code. Tests, error handling, and validation are built in because the spec required them.

---

## What You Learned

Congratulations! You just completed your first spec-driven development cycle. Here are the key takeaways:

### 1. **Specification-Driven Development is THE Main Vehicle**

You learned that Agent OS Enhanced is built around a core principle:

> **Design → Specify → Implement**

Not:

> ~~Ask AI to write code directly~~

### 2. **Workflows Enforce Quality**

The phase-gated workflows (`spec_creation_v1`, `spec_execution_v1`) **enforce** best practices:
- Requirements gathering cannot be skipped
- Tests are not optional
- Coverage thresholds are checked
- Acceptance criteria are validated

### 3. **Specifications Save Time**

The 5 minutes spent reviewing the spec **saved hours** of potential rework. Catching misunderstandings early is exponentially cheaper than fixing them later.

### 4. **AI Cannot Cut Corners**

The workflow engine enforces gates **in code**, not through prompt engineering. The AI literally cannot advance to the next phase without meeting checkpoint criteria.

### 5. **Production-Ready Output**

The generated code includes:
- ✅ Tests
- ✅ Error handling  
- ✅ Input validation
- ✅ Documentation
- ✅ >90% coverage

This is not prototype code - it's ready for production.

---

## Next Steps

Now that you understand the basic workflow, continue learning:

- **Tutorial 2: Understanding Agent OS Enhanced Workflows** (Coming in Phase 2) - Deep dive into workflow mechanics, phases, and gates
- **How-To: Create Custom Specifications** (Coming in Phase 3) - Learn to customize spec templates
- **How-To: Debug Workflow Execution** (Coming in Phase 3) - Troubleshooting workflow issues
- **[Reference: Workflows](../reference/workflows)** - Complete workflow reference

---

## Troubleshooting

### Issue: Agent starts writing code without creating a spec

**Solution:**

Explicitly request the workflow:

```
Stop. Let's create a specification first using spec_creation_v1 workflow.
```

### Issue: Workflow seems stuck on a phase

**Solution:**

Ask for the current status:

```
What's the current workflow status? What phase are we in?
```

### Issue: Generated code doesn't match the spec

**Solution:**

This should not happen (the workflow enforces spec compliance), but if it does:

```
The implementation doesn't match task 2.3 in tasks.md. Please review and correct.
```

---

## Summary

In this tutorial, you:

1. ✅ Had a design conversation with the AI
2. ✅ Created a formal specification using `spec_creation_v1`
3. ✅ Reviewed spec artifacts (SRD, technical specs, tasks)
4. ✅ Implemented the spec using `spec_execution_v1`
5. ✅ Verified generated code and tests

**Time taken:** 15-20 minutes

**Result:** Production-ready user profile API endpoint with tests and >90% coverage

You now understand why **specification-driven development is the main vehicle** in Agent OS Enhanced. The spec is not "extra documentation" - it's the **contract** that ensures AI-generated code meets your requirements.

Welcome to specification-driven development! 🎉

