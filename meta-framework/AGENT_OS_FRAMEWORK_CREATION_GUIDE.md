# Agent OS Framework Creation Guide

**Version**: 1.0  
**Purpose**: Portable methodology for creating deterministic, high-quality AI-assisted workflows  
**Transferability**: Apply to any repository or domain requiring systematic AI execution  
**Source**: Distilled from python-sdk Agent OS methodologies and V3 framework success patterns

---

## 🎯 **What Is This?**

A **meta-framework** for creating frameworks - a systematic approach to designing AI-assisted workflows that achieve:
- **85-95% execution consistency** (vs 60-70% without frameworks)
- **2-3x better context efficiency** (15-25% vs 50-75% utilization)
- **Automated quality enforcement** (100% validation coverage)
- **Scalable complexity management** (linear growth, not exponential)

**Use Cases**:
- Schema extraction frameworks
- Code generation workflows
- Documentation creation systems
- Testing automation frameworks
- Migration/refactoring processes
- Research and analysis workflows

---

## 📊 **Core Engineering Principles**

### **Principle 1: LLM Constraint Awareness**

**Context Window Optimization**:
| Context Use | File Size | Attention Quality | AI Success Rate |
|-------------|-----------|-------------------|-----------------|
| Optimal | ≤100 lines | 95%+ | 85%+ |
| Degraded | 200-500 lines | 70-85% | 60-75% |
| Failure | >500 lines | <70% | <50% |

**Key Insight**: Small, focused files compensate for LLM attention limitations.

---

### **Principle 2: Three-Tier Architecture**

**Tier 1: Side-Loaded Context** (AI reads during execution)
- **Size**: ≤100 lines per file
- **Purpose**: Execution instructions with binding commands
- **Pattern**: Single-responsibility, phase-specific guidance
- **Examples**: `phase-1-analysis.md`, `task-2-validation.md`

**Tier 2: Active Read Context** (AI reads on-demand)
- **Size**: 200-500 lines per file
- **Purpose**: Comprehensive methodology and architecture
- **Pattern**: Foundation documents, complete specifications
- **Examples**: `README.md`, `METHODOLOGY.md`, `framework-core.md`

**Tier 3: Output Artifacts** (AI generates, never re-consumes)
- **Size**: Unlimited
- **Purpose**: Generated deliverables
- **Pattern**: Code, schemas, documentation, reports
- **Examples**: Generated test files, extracted schemas, analysis reports

**Critical**: AI must NEVER re-read Tier 3 outputs (context pollution).

---

### **Principle 3: Command Language Interface**

**Problem**: Natural language is ambiguous and non-binding  
**Solution**: Standardized command symbols that create obligations

**Command Categories**:
```markdown
🛑 BLOCKING COMMANDS (Cannot proceed until executed)
⚠️ WARNING COMMANDS (Strong guidance)
🎯 NAVIGATION COMMANDS (Cross-file routing)
📊 EVIDENCE COMMANDS (Quantified validation)
🔄 PROGRESS COMMANDS (Status tracking)
🚨 VIOLATION DETECTION (Error prevention)
```

**Impact**: 10:1 token compression, 25-35% compliance improvement

---

### **Principle 4: Horizontal Task Decomposition**

**Problem**: Monolithic instructions cause context overflow  
**Solution**: Break into focused, single-responsibility modules

**Decomposition Pattern**:
```
Large Complex Task (2000 lines)
↓
Phase Breakdown (8 phases × 100 lines each)
↓
Task Breakdown (30 tasks × 50 lines each)
↓
Optimal Context Utilization (15-25%)
```

---

### **Principle 5: Validation Gate Enforcement**

**Problem**: AI claims completion without thorough validation  
**Solution**: Programmatic quality gates at every boundary

**Gate Pattern**:
```markdown
🛑 VALIDATE-GATE: [Phase Name]
- [ ] Criterion 1 ✅/❌
- [ ] Criterion 2 ✅/❌
- [ ] Criterion 3 ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without ✅ on all criteria
```

---

## 🏗️ **Framework Creation Process**

### **Phase 1: Domain Analysis (Week 1)**

**🛑 EXECUTE-NOW: Answer these questions**

#### **1.1 Problem Definition**
```markdown
What complex task needs deterministic AI execution?
- Current pain points with ad-hoc approaches?
- What constitutes high-quality output?
- What are key success metrics?
```

#### **1.2 LLM Capability Assessment**
```markdown
Which aspects can AI handle well?
Which weaknesses need systematic compensation?
What are context and complexity constraints?
Where are highest-risk failure points?
```

#### **1.3 Complexity Estimation**
```markdown
How many logical phases? (Target: 5-10)
How many tasks per phase? (Target: 2-5)
Expected file count? (Target: ≤100 lines each)
What validation is needed? (Target: Automated gates)
```

📊 **Deliverables**:
- [ ] Problem statement (1 page)
- [ ] Success criteria (quantified metrics)
- [ ] Failure risk assessment
- [ ] Estimated phase breakdown

---

### **Phase 2: Architecture Design (Week 1-2)**

#### **2.1 Three-Tier Structure Design**

**🎯 CREATE: Directory structure**
```
.agent-os/
├── standards/
│   └── {framework-name}/
│       ├── core/
│       │   ├── command-language-glossary.md     # Tier 1 (≤100)
│       │   └── framework-core.md                # Tier 2 (250-400)
│       ├── phases/
│       │   ├── 0/
│       │   │   ├── task-1-*.md                  # Tier 1 (≤100)
│       │   │   ├── task-2-*.md                  # Tier 1 (≤100)
│       │   │   └── shared-analysis.md           # Tier 1 (≤50)
│       │   ├── 1/
│       │   │   └── ...
│       │   └── N/
│       │       └── ...
│       ├── methodology/                         # Optional Tier 2
│       │   ├── architecture.md                  # (200-500)
│       │   └── patterns.md                      # (200-500)
│       ├── FRAMEWORK_ENTRY_POINT.md             # Tier 1 (≤100)
│       ├── README.md                            # Tier 2 (200-500)
│       ├── progress-tracking.md                 # Tier 1 (≤100)
│       └── COMMON_PITFALLS.md                   # Tier 2 (200-400)
```

#### **2.2 Command Language Glossary**

**🛑 EXECUTE-NOW: Copy template**
```bash
cp {source-repo}/.agent-os/standards/ai-assistant/code-generation/tests/v3/core/command-language-glossary.md \
   {target-repo}/.agent-os/standards/command-language-glossary.md
```

**⚠️ MUST-CUSTOMIZE**:
- Adapt command categories to domain
- Add domain-specific violation patterns
- Define framework-specific evidence types

#### **2.3 Discovery Flow Design**

**Navigation Architecture**:
```
User Request
  ↓
.cursorrules (Entry routing) [Optional]
  ↓
compliance-checking.md (Standards validation) [Optional]
  ↓
ai-assistant/README.md (Task routing hub) [Optional]
  ↓
{framework-name}/README.md (Methodology overview) [Tier 2]
  ↓
FRAMEWORK_ENTRY_POINT.md (Execution start) [Tier 1]
  ↓
phases/*/task-*.md (Systematic execution) [Tier 1]
```

📊 **Deliverables**:
- [ ] Directory structure created
- [ ] Command glossary customized
- [ ] Discovery flow documented
- [ ] File size budget allocated

---

### **Phase 3: Phase Decomposition (Week 2)**

#### **3.1 Phase Identification**

**Pattern**: Each phase should:
- Have clear input/output boundaries
- Be independently validatable
- Take 15-60 minutes to execute
- Produce quantifiable evidence

**Example Phase Structures**:

**Analysis-Heavy Framework**:
```
0. Setup & Prerequisites
1. Source Discovery
2. Data Collection
3. Analysis & Categorization
4. Validation
5. Documentation
```

**Generation-Heavy Framework**:
```
0. Requirements Gathering
1. Pattern Analysis
2. Template Selection
3. Generation
4. Quality Validation
5. Integration Testing
```

#### **3.2 Task Breakdown Within Phases**

**🎯 CREATE: Task files (≤100 lines each)**

**Template**:
```markdown
# Phase {N}: {Phase Name} - Task {M}: {Task Name}

⚠️ MUST-READ: [../core/command-language-glossary.md](../core/command-language-glossary.md)

---

## 🎯 **Task Objective**

[1-2 sentence clear objective]

---

## 🛑 **Prerequisites**

🛑 VALIDATE-GATE: Previous task complete
- [ ] [Specific prerequisite 1] ✅/❌
- [ ] [Specific prerequisite 2] ✅/❌

---

## 📋 **Instructions**

### **Step 1: [Action]**
🛑 EXECUTE-NOW: [Specific command]
📊 EXPECTED-OUTPUT: [What success looks like]

### **Step 2: [Action]**
🛑 EXECUTE-NOW: [Specific command]
📊 COUNT-AND-DOCUMENT: [Quantifiable metric]

### **Step 3: [Action]**
🛑 UPDATE-TABLE: Progress tracker with evidence

---

## 🔄 **Progress Update**

🔄 UPDATE-STATUS: Phase {N}, Task {M} → Complete
🔄 EVIDENCE-SUMMARY: [Specific evidence collected]

---

## 🛑 **Quality Gate**

🛑 VALIDATE-GATE: Task completion
- [ ] All commands executed ✅/❌
- [ ] Evidence documented ✅/❌
- [ ] Output validated ✅/❌

🚨 FRAMEWORK-VIOLATION: If proceeding without all ✅

---

## 🎯 **Next Step**

🎯 NEXT-MANDATORY: [phases/{N}/task-{M+1}.md] OR [phases/{N+1}/task-1.md]

---

**Task Version**: 1.0  
**Estimated Time**: {X} minutes  
**Automation**: {Manual/Semi-automated/Automated}
```

📊 **Deliverables**:
- [ ] All phases identified (5-10 phases)
- [ ] All tasks created (≤100 lines each)
- [ ] Dependencies mapped
- [ ] Time estimates provided

---

### **Phase 4: Validation Infrastructure (Week 2-3)**

#### **4.1 Progress Tracking Table**

**🎯 CREATE: progress-tracking.md**
```markdown
# {Framework Name} - Progress Tracking

**Instructions**: Copy this table to chat at framework start

---

## 📊 **Progress Table**

| Phase | Status | Tasks | Evidence | Quality Gate |
|-------|--------|-------|----------|--------------|
| 0 | ⏸️ | 0/4 | - | ⏸️ |
| 1 | ⏸️ | 0/6 | - | ⏸️ |
| 2 | ⏸️ | 0/3 | - | ⏸️ |
| ... | ... | ... | ... | ... |

**Status Key**:
- ⏸️ Not started
- 🔄 In progress
- ✅ Complete
- ❌ Failed

**Quality Gate Key**:
- ⏸️ Not started
- ⏳ Pending validation
- ✅ Passed
- ❌ Failed

---

## 🎯 **Current Phase**: {Will be updated}

## 📊 **Evidence Log**: {Will be populated}
```

#### **4.2 Automated Validation Scripts**

**Pattern**: Create validation scripts for quality gates

**Example (Go validator)**:
```go
// cmd/validate-{framework}/main.go
package main

func main() {
    result := ValidateFrameworkOutput(args)
    if result.HasErrors() {
        fmt.Printf("❌ Validation Failed: %d errors\n", result.ErrorCount)
        os.Exit(1)
    }
    fmt.Println("✅ Validation Passed")
    os.Exit(0)
}
```

**Example (Python validator)**:
```python
# scripts/validate_{framework}.py
def validate():
    errors = []
    # Validation logic
    if errors:
        print(f"❌ Validation Failed: {len(errors)} errors")
        sys.exit(1)
    print("✅ Validation Passed")
    sys.exit(0)
```

#### **4.3 Quality Gate Definitions**

**🎯 CREATE: Quality gate checklist for each phase**
```markdown
## Phase {N} Quality Gates

### Gate {N}.1: {Name}
**Validation Method**: {Automated script/Manual check}
**Command**: `{validation command}`
**Success Criteria**: {Specific, measurable}
**Failure Action**: {What to do if fails}

### Gate {N}.2: {Name}
...
```

📊 **Deliverables**:
- [ ] Progress tracking template created
- [ ] Validation scripts implemented
- [ ] Quality gates defined for all phases
- [ ] Exit code enforcement (0=success, 1=failure)

---

### **Phase 5: Documentation (Week 3)**

#### **5.1 FRAMEWORK_ENTRY_POINT.md**

**Template** (≤100 lines):
```markdown
# {Framework Name} - Entry Point

⚠️ MUST-READ: [core/command-language-glossary.md](core/command-language-glossary.md)

---

## 🎯 **What Are You Doing?**

### **Option 1: NEW {Task Type}**
[Description]

🎯 NEXT-MANDATORY: [phases/0/task-1-*.md]

### **Option 2: UPDATE {Task Type}**
[Description]

🎯 NEXT-MANDATORY: [phases/0/task-2-*.md]

---

## 🛑 **Prerequisites**

🛑 VALIDATE-GATE: Framework readiness
- [ ] Read command glossary ✅/❌
- [ ] {Domain-specific prerequisite} ✅/❌
- [ ] {Tool/environment setup} ✅/❌

---

## 📊 **Framework Overview**

| Phase | Purpose | Duration |
|-------|---------|----------|
| 0 | {Purpose} | {Time} |
| 1 | {Purpose} | {Time} |
| ... | ... | ... |

---

## 🎯 **Begin Framework**

🛑 EXECUTE-NOW: Copy progress table to chat
⚠️ MUST-READ: [progress-tracking.md](progress-tracking.md)

🎯 NEXT-MANDATORY: Select your option above

---

**Framework Version**: 1.0
**Last Updated**: {Date}
```

#### **5.2 README.md**

**Template** (200-500 lines):
```markdown
# {Framework Name}

**Purpose**: {1-2 sentence description}

---

## 📋 **Overview**

{Comprehensive framework description}

---

## 🎯 **Purpose**

{Why this framework exists, what problems it solves}

---

## 📊 **Framework Structure**

{Directory tree, file organization}

---

## 🚀 **Quick Start**

1. Read command glossary
2. Execute entry point
3. Follow phase-by-phase guidance
4. Complete all quality gates

---

## 🏗️ **Architecture**

{Three-tier architecture explanation}

---

## 📈 **Success Metrics**

{Expected improvements, quantified results}

---

## 🚨 **Common Pitfalls**

{See COMMON_PITFALLS.md}

---

## 📞 **Support**

{Where to get help, references}
```

#### **5.3 COMMON_PITFALLS.md**

**Template** (200-400 lines):
```markdown
# {Framework Name} - Common Pitfalls

---

## Pitfall 0: {Most Common/Critical}

### **Problem**
{Description}

### **Symptoms**
- {Observable indicator 1}
- {Observable indicator 2}

### **Root Cause**
{Why it happens}

### **Prevention**
{How to avoid}

### **Detection**
{How to identify}

### **Fix**
{How to correct}

---

[Repeat for each pitfall]
```

📊 **Deliverables**:
- [ ] Entry point created (≤100 lines)
- [ ] README comprehensive (200-500 lines)
- [ ] Common pitfalls documented
- [ ] Cross-references validated

---

### **Phase 6: Testing & Iteration (Week 3-4)**

#### **6.1 Pilot Execution**

**🛑 EXECUTE-NOW: Test framework with AI**
```markdown
1. Start fresh chat session
2. Execute framework from entry point
3. Document ALL deviations, confusions, shortcuts
4. Record time per phase
5. Measure quality gate pass/fail rates
```

#### **6.2 Metrics Collection**

**📊 QUANTIFY-RESULTS**:
```yaml
execution_consistency:
  total_runs: 10
  successful_completions: {count}
  average_quality_score: {score}
  
context_efficiency:
  average_file_size: {lines}
  largest_file: {lines}
  context_utilization: {percentage}
  
quality_enforcement:
  automated_gates: {count}
  manual_checks: {count}
  automation_percentage: {percentage}
```

#### **6.3 Iterative Refinement**

**Optimization Targets**:
- File size compliance: 95%+ files within tier limits
- Command language adoption: 80%+ instructions use commands
- Quality gate coverage: 100% phases have gates
- Execution consistency: 85%+ success rate

📊 **Deliverables**:
- [ ] 10+ pilot runs completed
- [ ] Metrics collected and analyzed
- [ ] Refinements documented
- [ ] Success criteria met

---

## 📦 **Portable Framework Package**

### **Minimal Viable Framework**

**Files Required** (Can start here):
```
{framework-name}/
├── core/
│   └── command-language-glossary.md     # Copy from template
├── phases/
│   └── 0/
│       └── task-1-start.md              # First execution file
├── FRAMEWORK_ENTRY_POINT.md             # Routing
├── README.md                            # Overview
└── progress-tracking.md                 # Status table
```

### **Full Framework Package**

**Complete Structure**:
```
{framework-name}/
├── core/
│   ├── command-language-glossary.md
│   └── framework-core.md                # Optional deep dive
├── phases/
│   ├── 0/ ... N/                        # All execution phases
├── methodology/                         # Optional Tier 2 context
│   ├── architecture.md
│   └── patterns.md
├── FRAMEWORK_ENTRY_POINT.md
├── README.md
├── progress-tracking.md
├── COMMON_PITFALLS.md
└── CHANGELOG.md
```

---

## 🚀 **Quick Start: New Framework**

### **Week 1 Checklist**
```markdown
🛑 Day 1-2: Problem Analysis
- [ ] Define problem and success criteria
- [ ] Assess LLM capabilities vs constraints
- [ ] Estimate complexity (phases, tasks, files)

🛑 Day 3-4: Architecture Design
- [ ] Create directory structure
- [ ] Copy/customize command glossary
- [ ] Design discovery flow

🛑 Day 5: Phase Breakdown
- [ ] Identify 5-10 logical phases
- [ ] Map dependencies
- [ ] Allocate time budgets
```

### **Week 2 Checklist**
```markdown
🛑 Day 1-3: Task Creation
- [ ] Create task files for Phase 0-2 (≤100 lines each)
- [ ] Integrate command language
- [ ] Add validation gates

🛑 Day 4-5: Validation Infrastructure
- [ ] Create progress tracking template
- [ ] Implement quality gate scripts
- [ ] Define success criteria
```

### **Week 3 Checklist**
```markdown
🛑 Day 1-2: Documentation
- [ ] Write FRAMEWORK_ENTRY_POINT.md
- [ ] Write comprehensive README.md
- [ ] Start COMMON_PITFALLS.md

🛑 Day 3-5: Testing
- [ ] Run 3-5 pilot executions
- [ ] Collect metrics
- [ ] Refine based on findings
```

### **Week 4: Polish & Deploy**
```markdown
🛑 Day 1-3: Iteration
- [ ] Complete all remaining phase files
- [ ] Achieve 95%+ file size compliance
- [ ] Finalize quality gates

🛑 Day 4-5: Validation
- [ ] Run 10+ executions
- [ ] Achieve 85%+ success rate
- [ ] Document lessons learned
```

---

## 📊 **Quality Assurance Checklist**

### **File Size Compliance**
- [ ] 95%+ Tier 1 files ≤100 lines
- [ ] 100% Tier 2 files ≤500 lines
- [ ] Tier 3 has no limits (output only)

### **Command Language Adoption**
- [ ] 80%+ instructions use command language
- [ ] All phase transitions have 🎯 NEXT-MANDATORY
- [ ] All gates have 🛑 VALIDATE-GATE
- [ ] All evidence has 📊 COUNT-AND-DOCUMENT

### **Validation Coverage**
- [ ] 100% phases have quality gates
- [ ] 100% gates have automated validation
- [ ] 100% tasks have evidence requirements
- [ ] Progress table updated systematically

### **Navigation Completeness**
- [ ] Every file has explicit next-step routing
- [ ] Cross-file dependencies documented
- [ ] Discovery flow tested end-to-end
- [ ] No dead-end files (all have exit paths)

---

## 🎯 **Success Metrics**

**Target Improvements** (vs ad-hoc approaches):

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| **Execution Consistency** | 60-70% | 85-95% | Success rate across 10+ runs |
| **Context Efficiency** | 50-75% | 15-25% | Average context utilization |
| **Quality Enforcement** | Manual | 100% Automated | Percentage of gates automated |
| **Evidence Tracking** | Ad-hoc | 100% Systematic | Percentage of claims with evidence |

---

## 🔗 **References**

- **Source Methodologies**: `/python-sdk/.agent-os/standards/ai-assistant/`
  - `LLM-WORKFLOW-ENGINEERING-METHODOLOGY.md`
  - `DETERMINISTIC-LLM-OUTPUT-METHODOLOGY.md`
  - `code-generation/tests/v3/` (V3 framework implementation)

- **Case Studies**:
  - Python SDK V3 Test Generation Framework (80%+ success rate)
  - Provider Schema Extraction Framework (systematic schema extraction)

---

## 📝 **Framework Maintenance**

### **Versioning**
- Increment version on breaking changes
- Document all updates in CHANGELOG.md
- Track framework-level improvements

### **Continuous Improvement**
- Collect metrics from every execution
- Document new pitfalls as discovered
- Refine file sizes based on usage
- Update command glossary as needed

### **Cross-Repository Transfer**
- Command glossary is portable (copy as-is)
- Three-tier architecture applies universally
- Validation pattern is reusable
- Progress tracking template is generic

---

**Guide Version**: 1.0  
**Last Updated**: 2025-10-02  
**Status**: Production-Ready  
**Transferability**: Universal (any domain, any repository)

