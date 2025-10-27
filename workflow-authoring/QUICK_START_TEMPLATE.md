# Workflow Quick Start Template

**Purpose**: Minimal starting point for new AI-assisted workflows  
**Time to Setup**: 1-2 hours for basic workflow  
**Based On**: Agent OS Workflow Creation Guide v1.0

---

## 🚀 **Step 1: Copy Base Structure** (5 minutes)

```bash
# In your target repository
mkdir -p .praxis-os/standards/{your-workflow-name}/core
mkdir -p .praxis-os/standards/{your-workflow-name}/phases/0
mkdir -p .praxis-os/standards/{your-workflow-name}/phases/1
mkdir -p .praxis-os/standards/{your-workflow-name}/phases/2
```

---

## 📋 **Step 2: Copy Command Glossary** (5 minutes)

```bash
# Copy from reference implementation
cp {source-repo}/.praxis-os/standards/command-language-glossary.md \
   .praxis-os/standards/{your-workflow-name}/core/command-language-glossary.md
```

**Or create minimal version**:

```markdown
# Command Language Glossary

🛑 EXECUTE-NOW: [command] - Cannot proceed until executed
⚠️ MUST-READ: [file] - Required reading before proceeding
🎯 NEXT-MANDATORY: [file] - Explicit next step routing
📊 COUNT-AND-DOCUMENT: [metric] - Provide quantified evidence
🛑 VALIDATE-GATE: [criteria] - Verify completion before proceeding
🔄 UPDATE-TABLE: Progress table update required
🚨 WORKFLOW-VIOLATION: Detected shortcut or skip
```

---

## 📝 **Step 3: Create Entry Point** (15 minutes)

**File**: `.praxis-os/standards/{your-workflow-name}/WORKFLOW_ENTRY_POINT.md`

```markdown
# {Workflow Name} - Entry Point

⚠️ MUST-READ: [core/command-language-glossary.md](core/command-language-glossary.md)

---

## 🎯 **What Are You Doing?**

### **Option 1: NEW {Task}**
Creating {thing} from scratch.

🎯 NEXT-MANDATORY: [phases/0/task-1-setup.md](phases/0/task-1-setup.md)

---

### **Option 2: UPDATE {Task}**
Updating existing {thing}.

🎯 NEXT-MANDATORY: [phases/0/task-2-check-existing.md](phases/0/task-2-check-existing.md)

---

## 🛑 **Prerequisites**

🛑 VALIDATE-GATE: Readiness
- [ ] Read command glossary ✅/❌
- [ ] {Required tool/environment} ready ✅/❌

---

## 📊 **Workflow Phases**

| Phase | Purpose | Duration |
|-------|---------|----------|
| 0 | Setup & Prerequisites | 10 min |
| 1 | {Main Task} | 30-60 min |
| 2 | Validation | 15 min |

---

## 🎯 **Begin**

🛑 EXECUTE-NOW: Copy progress table from [progress-tracking.md](progress-tracking.md) to chat

🎯 NEXT-MANDATORY: Select your option above

---

**Version**: 1.0  
**Updated**: {Date}
```

---

## 📊 **Step 4: Create Progress Tracker** (10 minutes)

**File**: `.praxis-os/standards/{your-workflow-name}/progress-tracking.md`

```markdown
# {Workflow Name} - Progress Tracking

**Instructions**: Copy this table to chat at workflow start

---

## 📊 **Progress Table**

| Phase | Status | Tasks | Evidence | Quality Gate |
|-------|--------|-------|----------|--------------|
| 0 | ⏸️ | 0/2 | - | ⏸️ |
| 1 | ⏸️ | 0/3 | - | ⏸️ |
| 2 | ⏸️ | 0/1 | - | ⏸️ |

**Status**: ⏸️ Not started | 🔄 In progress | ✅ Complete | ❌ Failed  
**Quality Gate**: ⏸️ Not started | ⏳ Pending | ✅ Passed | ❌ Failed

---

## 🎯 **Current Phase**: [Will be updated]

## 📊 **Evidence Log**:
[Will be populated with quantified evidence]
```

---

## 📁 **Step 5: Create Phase 0 (Setup)** (20 minutes)

### **Task 1: Setup** (≤100 lines)

**File**: `.praxis-os/standards/{your-workflow-name}/phases/0/task-1-setup.md`

```markdown
# Phase 0: Setup - Task 1: Initialize

⚠️ MUST-READ: [../../core/command-language-glossary.md](../../core/command-language-glossary.md)

---

## 🎯 **Objective**

Initialize {workflow} workspace and verify prerequisites.

---

## 🛑 **Prerequisites**

None - this is the first task.

---

## 📋 **Instructions**

### **Step 1: Create Directory Structure**

🛑 EXECUTE-NOW:
\`\`\`bash
mkdir -p {required-directories}
\`\`\`

📊 EXPECTED-OUTPUT: Directories created

### **Step 2: Verify Tools**

🛑 EXECUTE-NOW:
\`\`\`bash
{tool} --version
\`\`\`

📊 EXPECTED-OUTPUT: Version number displayed

### **Step 3: Initialize Tracking**

🛑 EXECUTE-NOW: Create initial tracking file

---

## 🔄 **Progress Update**

🔄 UPDATE-STATUS: Phase 0, Task 1 → Complete
🔄 EVIDENCE-SUMMARY: Directories created, tools verified

🛑 UPDATE-TABLE: Phase 0 → 1/2 tasks complete

---

## 🛑 **Quality Gate**

🛑 VALIDATE-GATE: Task 1 completion
- [ ] Directories exist ✅/❌
- [ ] Tools verified ✅/❌
- [ ] Table updated ✅/❌

🚨 WORKFLOW-VIOLATION: If proceeding without all ✅

---

## 🎯 **Next Step**

🎯 NEXT-MANDATORY: [task-2-check-existing.md](task-2-check-existing.md)

---

**Version**: 1.0  
**Time**: ~10 minutes
```

---

## 📁 **Step 6: Create Phase 1 (Main Work)** (30 minutes)

**Create 2-5 task files** following the same template pattern:
- Each file ≤100 lines
- Clear objective (1-2 sentences)
- Executable steps with 🛑 EXECUTE-NOW
- Quantified evidence with 📊
- Validation gate
- Explicit next step routing

---

## 📝 **Step 7: Create README** (20 minutes)

**File**: `.praxis-os/standards/{your-workflow-name}/README.md`

```markdown
# {Workflow Name}

**Purpose**: {1-2 sentence description}  
**Status**: Active  
**Version**: 1.0

---

## 🎯 **Overview**

{Comprehensive description of what this workflow does, why it exists, and what problems it solves.}

---

## 🚀 **Quick Start**

1. Read [core/command-language-glossary.md](core/command-language-glossary.md)
2. Execute [WORKFLOW_ENTRY_POINT.md](WORKFLOW_ENTRY_POINT.md)
3. Follow systematic phase-by-phase execution
4. Complete all quality gates

---

## 📊 **Workflow Structure**

\`\`\`
{workflow-name}/
├── core/
│   └── command-language-glossary.md
├── phases/
│   ├── 0/ (Setup)
│   ├── 1/ (Main work)
│   └── 2/ (Validation)
├── WORKFLOW_ENTRY_POINT.md
├── progress-tracking.md
└── README.md
\`\`\`

---

## 🏗️ **Architecture**

**Three-Tier Design**:
- **Tier 1** (Execution): Small task files (≤100 lines)
- **Tier 2** (Methodology): This README (200-500 lines)
- **Tier 3** (Output): Generated artifacts (unlimited)

---

## 📈 **Success Metrics**

Expected improvements vs ad-hoc approaches:
- Execution consistency: 85-95% (vs 60-70%)
- Context efficiency: 15-25% utilization (vs 50-75%)
- Quality enforcement: 100% automated (vs manual)

---

## 🚨 **Common Pitfalls**

### **Pitfall 1: Skipping Command Glossary**
**Problem**: Not reading the command language glossary leads to misunderstanding binding obligations.  
**Fix**: Always read glossary first (linked at top of entry point).

### **Pitfall 2: Claiming Completion Without Evidence**
**Problem**: Saying "done" without quantified evidence.  
**Fix**: Every task requires 📊 COUNT-AND-DOCUMENT or specific output.

---

## 📞 **Support**

- **Documentation**: Start with WORKFLOW_ENTRY_POINT.md
- **Issues**: Document in COMMON_PITFALLS.md as discovered
- **Updates**: Track in CHANGELOG.md

---

**Version**: 1.0  
**Last Updated**: {Date}
```

---

## ✅ **Validation Checklist**

After creating your workflow, validate:

### **File Size Compliance**
```bash
# Check all phase files are ≤100 lines
find .praxis-os/standards/{workflow}/phases -name "*.md" -exec sh -c 'lines=$(wc -l < "$1"); if [ $lines -gt 100 ]; then echo "❌ $1: $lines lines"; else echo "✅ $1: $lines lines"; fi' _ {} \;
```

### **Command Language Integration**
- [ ] 80%+ of instructions use command symbols
- [ ] All phase files reference command glossary
- [ ] All transitions use 🎯 NEXT-MANDATORY
- [ ] All gates use 🛑 VALIDATE-GATE

### **Navigation Completeness**
- [ ] Entry point routes to first phase
- [ ] Every task file has next-step routing
- [ ] No dead-end files
- [ ] Progress table is referenceable

### **Quality Gate Coverage**
- [ ] Every phase has quality gates
- [ ] Every task has evidence requirements
- [ ] Validation criteria are specific and measurable

---

## 🎯 **Minimal Viable Workflow** (1 hour)

**Absolute minimum to start**:
```
{workflow-name}/
├── core/
│   └── command-language-glossary.md  # Copy from template
├── phases/
│   └── 0/
│       └── task-1-start.md           # First execution file
├── WORKFLOW_ENTRY_POINT.md          # Routing only
└── progress-tracking.md              # Status table
```

**This is enough to**:
- Start systematic execution
- Enforce binding commands
- Track progress
- Iterate and expand

---

## 🚀 **Next Steps After Creation**

1. **Test with AI** (3-5 pilot runs)
2. **Collect metrics** (success rate, time per phase)
3. **Refine** (split large files, add gates)
4. **Document pitfalls** (create COMMON_PITFALLS.md)
5. **Iterate** (aim for 85%+ consistency)

---

## 📦 **Package for Distribution**

**To share workflow across repositories**:

```bash
# Create portable package
tar -czf {workflow-name}-v1.0.tar.gz \
  .praxis-os/standards/{workflow-name}/

# Transfer to new repo
cd {new-repo}
tar -xzf {workflow-name}-v1.0.tar.gz

# Customize for new repo
# (Adapt entry point, phase tasks to new domain)
```

---

## 🔗 **References**

- **Full Guide**: [AGENT_OS_WORKFLOW_CREATION_GUIDE.md](AGENT_OS_WORKFLOW_CREATION_GUIDE.md)
- **Source Methodologies**: `/python-sdk/.praxis-os/standards/ai-assistant/`
- **Example Workflows**: 
  - `provider-schema-extraction/` (This repo)
  - `code-generation/tests/v3/` (python-sdk repo)

---

**Template Version**: 1.0  
**Time to Setup**: 1-2 hours for basic workflow  
**Customization Time**: Additional 1-2 hours for domain-specific content

