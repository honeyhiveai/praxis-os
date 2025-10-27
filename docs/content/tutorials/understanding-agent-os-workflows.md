---
sidebar_position: 4
doc_type: tutorial
---

# Understanding prAxIs OS Workflows

In [Tutorial 1](./your-first-agent-os-project), you experienced spec-driven development hands-on. Now you'll learn **what workflows actually are** and why they're critical to prAxIs OS's approach.

## Learning Goals

By completing this tutorial, you will learn to:

1. Understand workflows as **phase-gated tools**, not general processes
2. Experience checkpoint validation (trying to skip ahead vs. providing evidence)
3. Check workflow state and understand resumption
4. Know when and why to use workflows
5. Understand how workflows enforce quality in code

## Time Estimate

**10-15 minutes**

## Prerequisites

- [Tutorial 1: Your First prAxIs OS Project](./your-first-agent-os-project) completed
- Basic understanding of spec-driven development

## What You'll Learn

By the end of this tutorial, you'll understand:

- **Workflows are tools, not processes** - They're executable enforcement mechanisms
- **Phase gating works in code** - AI literally cannot skip phases
- **Evidence-based progression** - Checkpoints require proof, not promises
- **Workflow state is persistent** - Resume from any point, never lose progress

---

## Part 1: What Are Workflows? (2 minutes)

Let's start with the mental model.

### Workflows Are NOT General Processes

When most people hear "workflow," they think:
- ❌ A checklist of steps to follow
- ❌ A suggested best practice
- ❌ A process documented in a diagram
- ❌ Something you can skip if you know what you're doing

**prAxIs OS workflows are different.**

### Workflows Are Phase-Gated Tools

prAxIs OS workflows are:
- ✅ **Executable code** that enforces progression
- ✅ **Hard gates** that AI cannot bypass
- ✅ **Validation engines** that check evidence
- ✅ **State machines** with defined transitions

Think of a workflow like a **TSA security checkpoint**:
- You cannot board the plane (next phase) until you pass through security (checkpoint)
- Showing your boarding pass (evidence) allows you to proceed
- The gate physically blocks you - it's not a suggestion

### The Two Main Workflows

You've already used both of these in Tutorial 1:

**1. `spec_creation_v1` - Specification Creation**

Creates comprehensive specifications through 6 phases:
- **Phase 0:** Supporting Documents Integration (optional)
- **Phase 1:** Requirements Gathering (creates `srd.md`)
- **Phase 2:** Technical Design (creates `specs.md`)
- **Phase 3:** Task Breakdown (creates `tasks.md`)
- **Phase 4:** Implementation Guidance (creates `implementation.md`)
- **Phase 5:** Finalization (creates `README.md`)

Each phase has a **validation gate** with required evidence.

**2. `spec_execution_v1` - Specification Execution**

Implements specifications through dynamic phases:
- **Phase 0:** Spec Analysis & Planning (parses `tasks.md`)
- **Phases 1-N:** Dynamic phases from your spec's task breakdown

The number of phases depends on your spec. The workflow **parses your `tasks.md`** and creates phases dynamically.

### Key Insight

The workflow engine enforces progression through **code**, not through prompt engineering or hoping the AI "remembers" to do things correctly.

---

## Part 2: Experience Checkpoint Validation (4 minutes)

Let's experience how phase gates actually work by checking workflow state.

### Step 1: Start a New Workflow

Open Cursor chat and say:

```
Let's create a spec for a simple feature: a health check endpoint at /health that returns {"status": "ok"}. Use spec_creation_v1 workflow.
```

**Expected Response:**

The agent will:
1. Acknowledge the workflow request
2. Start `spec_creation_v1` workflow
3. Begin Phase 0 (or skip to Phase 1 if no supporting docs)

**Success Indicator:** ✅ Agent mentions starting the workflow and the current phase

### Step 2: Check Current Workflow State

While the workflow is running, ask:

```
What's the current workflow state? What phase are we in and what evidence is required?
```

**Expected Response:**

The agent will show you:
```
Current Workflow: spec_creation_v1
Session ID: [some-id]
Current Phase: 1 (Requirements Gathering)

Required Evidence for Phase 1 Checkpoint:
- srd_created
- business_goals_defined
- user_stories_documented
- functional_requirements_listed
- nfr_defined
- out_of_scope_clarified

Progress: Phase 1 in progress
```

**Success Indicator:** ✅ You see the specific evidence items required

### Step 3: Let the Workflow Progress Naturally

Allow the agent to complete Phase 1. It will:
- Ask clarifying questions
- Create the `srd.md` file
- Collect all required evidence
- Present the Software Requirements Document

**Expected Output:**

```
✅ Phase 1 Complete: Requirements Gathering

Created: .agent-os/specs/2025-10-12-health-check-endpoint/srd.md

Evidence Collected:
✓ srd_created
✓ business_goals_defined
✓ user_stories_documented
✓ functional_requirements_listed
✓ nfr_defined
✓ out_of_scope_clarified

Ready to advance to Phase 2: Technical Design
```

**Success Indicator:** ✅ All evidence items checked off

### Step 4: Understand What Just Happened

The workflow engine just:
1. **Tracked required evidence** from the checkpoint definition
2. **Verified evidence was collected** (the `srd.md` file exists and contains required sections)
3. **Allowed progression to next phase** only after validation passed

If the agent had tried to skip Phase 1 or advance without creating the SRD, the workflow engine would have **blocked** the transition.

### Why This Matters

Without workflows, an AI might say:

> "I've gathered the requirements mentally, let's start coding!"

With workflows, the AI **must** produce the `srd.md` file with all required sections before it can proceed. The gate is enforced in code.

---

## Part 3: Workflow State and Resumption (2 minutes)

Workflows maintain **persistent state**, which means you can resume from any point.

### Step 5: Check Workflow State Again

Ask the agent:

```
Show me the full workflow state, including completed phases.
```

**Expected Response:**

```
Workflow: spec_creation_v1
Session ID: wf-spec-creation-[timestamp]

Phase Progress:
✅ Phase 0: Supporting Documents Integration (skipped)
✅ Phase 1: Requirements Gathering (complete)
🔄 Phase 2: Technical Design (in progress)
⏹️ Phase 3: Task Breakdown (pending)
⏹️ Phase 4: Implementation Guidance (pending)
⏹️ Phase 5: Finalization (pending)

Completed Phases History:
- Phase 1 completed at 2025-10-12 10:30:15
  Evidence: srd_created, business_goals_defined, ...
  Artifact: .agent-os/specs/.../srd.md
```

**Success Indicator:** ✅ You see phase history with timestamps and evidence

### What This State Enables

The workflow state is saved to disk after each phase completion. This means:

1. **Crash Recovery:** If the MCP server restarts mid-workflow, you can resume
2. **Session Interruption:** If you close Cursor and come back tomorrow, the workflow remembers where you were
3. **Audit Trail:** You have a complete history of what was done and when

### Step 6: Complete or Cancel the Workflow

You can either:

**Option A: Complete the workflow**

```
Continue with the workflow to completion.
```

The agent will progress through all remaining phases.

**Option B: Cancel and clean up**

```
Cancel this workflow, we were just learning how they work.
```

The agent will clean up the partial spec files.

**Success Indicator:** ✅ Agent acknowledges and takes appropriate action

### Why State Management Matters

Traditional AI assistance loses context when:
- The conversation gets too long
- You start a new chat
- The IDE restarts

Workflows maintain state **persistently on disk**, so none of those issues apply.

---

## Part 4: When to Use Workflows (2 minutes)

Now that you understand how workflows work, when should you use them?

### Use Workflows For:

**✅ Complex, multi-phase work**
- Creating specifications (>30 min of work)
- Implementing features with multiple components
- Refactoring with many steps
- Generating comprehensive test suites

**✅ When quality gates matter**
- Production code where tests are mandatory
- Documentation that must be complete
- Architecture decisions that need review
- Migrations with validation steps

**✅ When you want resumability**
- Work spanning multiple sessions
- Tasks that might be interrupted
- Long-running implementations
- Collaborative work (hand off to another developer)

### Don't Use Workflows For:

**❌ Simple, one-step tasks**
- "Fix this typo"
- "Add a log statement here"
- "Update this comment"

**❌ Exploratory work**
- "Show me 3 ways to solve X"
- "Explain how this code works"
- "What are the trade-offs of Y?"

**❌ When you need maximum flexibility**
- Rapid prototyping with frequent pivots
- Experimental code you might throw away
- Ad-hoc queries and research

### The Rule of Thumb

If the task would take **>30 minutes** and has **quality requirements** (tests, docs, validation), use a workflow.

If it's quick or exploratory, conversational mode is fine.

---

## Part 5: Creating Custom Workflows (Optional, 2 minutes)

You're not limited to `spec_creation_v1` and `spec_execution_v1`. You can create custom workflows.

### When to Create a Custom Workflow

Create a custom workflow when you have:

1. **A repeatable process** with multiple phases
2. **Quality gates** that must be enforced
3. **Complex validation** that AI might skip
4. **State that needs to persist** across sessions

### Examples of Custom Workflows

Real workflows in prAxIs OS:
- `test_generation_v3` - Generate comprehensive test suites
- `agent_os_upgrade_v1` - Upgrade prAxIs OS installations

You could create workflows for:
- Database migrations with validation
- API documentation generation from code
- Security audit processes
- Performance optimization procedures

### How to Create a Custom Workflow

This is beyond the scope of this tutorial, but the process involves:

1. Define workflow structure in `metadata.json`
2. Create phase files (`phase.md`) for each phase
3. Define validation gates (required evidence for each phase)
4. Create task files for detailed guidance
5. Test end-to-end with the workflow engine

**For More:** See the How-To guide "Create Custom Workflows" (coming in Phase 3) or read the meta-workflow standards.

---

## What You Learned

Congratulations! You now understand the prAxIs OS workflow system. Here are the key takeaways:

### 1. **Workflows Are Enforcement Tools**

Workflows are **not suggestions or checklists**. They are:
- Executable code that enforces progression
- Phase gates that AI cannot bypass
- Validation engines that check evidence

### 2. **Phase Gating Works in Code**

The workflow engine checks:
- ✅ Required files exist
- ✅ Required sections are present
- ✅ Tests are passing
- ✅ Evidence is collected

Only then does it allow progression to the next phase.

### 3. **Evidence Over Promises**

The workflow doesn't trust the AI's word that something is done. It verifies:
- Files exist on disk
- Tests run and pass
- Coverage thresholds are met
- Validation checks succeed

### 4. **State is Persistent**

Workflows maintain state on disk, enabling:
- Resume from any point after interruption
- Audit trail of what was done
- Recovery from crashes or restarts
- Handoff between developers or sessions

### 5. **Use Workflows for Complex Work**

Use workflows when:
- Task will take >30 minutes
- Quality gates are important (tests, docs, validation)
- You want resumability and state tracking
- Multiple phases with dependencies exist

---

## Next Steps

Now that you understand workflows, continue learning:

- **How-To: Create Custom Workflows** (Coming in Phase 3) - Build your own phase-gated workflows
- **How-To: Debug Workflow Execution** (Coming in Phase 3) - Troubleshoot workflow issues
- **How-To: Resume Interrupted Workflows** (Coming in Phase 3) - Recover and continue
- **[Reference: Workflows](../reference/workflows)** - Complete workflow system reference
- **[Explanation: Architecture](../explanation/architecture)** - How the workflow engine works

---

## Troubleshooting

### Issue: Agent advances phase without completing checkpoint

**This should not happen.** If it does:

```
Stop. Show me the current workflow state and evidence collected for the checkpoint.
```

The workflow engine enforces checkpoints in code, so if this happens, there may be a bug. Report it.

### Issue: Cannot find workflow state

**Solution:**

Workflow state is stored in the workflow engine's internal state. Ask:

```
What's the current workflow status? Use get_workflow_state() to check.
```

### Issue: Want to restart a workflow from beginning

**Solution:**

```
Cancel the current workflow and start a new session.
```

Workflow state is tied to a session ID. Starting a new workflow creates a new session.

---

## Summary

In this tutorial, you:

1. ✅ Learned workflows are phase-gated tools, not processes
2. ✅ Experienced checkpoint validation and evidence requirements
3. ✅ Checked workflow state and understood persistence
4. ✅ Learned when to use (and not use) workflows
5. ✅ Understood how to create custom workflows

**Time taken:** 10-15 minutes

**Key Insight:** Workflows enforce quality through **code**, not through hoping AI "remembers" best practices. Phase gates are real barriers that require evidence to pass.

You now understand why prAxIs OS workflows are essential for production-quality AI-assisted development! 🎉

---

## Test Your Understanding

Answer these questions to verify your understanding:

1. **What is the difference between a workflow and a checklist?**
   - Answer: A workflow enforces progression through code with validation gates. A checklist is a suggestion that can be ignored.

2. **Can an AI skip a phase in a workflow?**
   - Answer: No. The workflow engine blocks phase transitions until checkpoint evidence is validated.

3. **What happens to workflow state if the MCP server restarts?**
   - Answer: The state persists on disk and can be resumed from the last completed checkpoint.

4. **When should you use a workflow vs. conversational mode?**
   - Answer: Use workflows for complex, multi-phase work (>30 min) with quality requirements. Use conversational mode for quick tasks and exploration.

If you can answer these confidently, you understand workflows! 🎓

