# Workspace - Temporary Development Artifacts

🚨 **This directory contains ephemeral documents that are NOT tracked in git.**

## 🎯 What Is This?

Workspace is your "working memory" for development - a designated place for temporary files, design explorations, research, and experiments that are not yet ready to commit.

## 📁 Directory Structure

```
workspace/
├── README.md       # This file
├── design/         # Phase 1 conversational design explorations
├── analysis/       # Research and investigation documents
└── scratch/        # Quick experiments and temporary notes
```

## ✅ What Belongs Here

**design/** - Phase 1 design documents (before creating formal spec)
- Conversational design explorations
- Trade-off analysis
- Approach proposals
- User feedback iterations

**analysis/** - Research and investigation
- Comparison documents (e.g., "Redis vs PostgreSQL")
- Technical research
- Performance analysis
- Security investigations
- Feasibility studies

**scratch/** - Temporary notes and experiments
- Session notes
- Quick experiments
- WIP documents
- Brainstorming notes
- Anything truly temporary

## ❌ What DOESN'T Belong Here

- ❌ Formal specifications (use `.praxis-os/specs/`)
- ❌ Standards documents (use `.praxis-os/standards/`)
- ❌ Completed workflow definitions (use `.praxis-os/workflows/`)
- ❌ Anything you want to commit to git

## 🔄 Lifecycle

### Phase 1 → Phase 2 Transition

```
1. CREATE (Phase 1)
   workspace/design/2025-10-21-feature.md
   ↓ Iterate with user through conversation
   ↓ Refine approach based on feedback

2. TRIGGER
   User says: "create the spec" or "this looks good, spec it"
   ↓

3. FORMALIZE (Phase 2)
   .praxis-os/specs/2025-10-21-feature/
   ↓ Extract insights from workspace doc
   ↓ Create structured spec files

4. CLEANUP
   Delete workspace/design/2025-10-21-feature.md
   OR move to specs/2025-10-21-feature/supporting-docs/
```

### General Workflow

1. **Create** - Put temporary work here
2. **Refine** - Iterate until ready to formalize
3. **Promote** - Create formal spec/doc in appropriate location
4. **Clean** - Delete or archive workspace file

## 📝 File Naming Convention

**Recommended format:** `YYYY-MM-DD-topic-name.md`

**Examples:**
```
✅ design/2025-10-21-authentication-system.md
✅ analysis/2025-10-21-cache-strategy-comparison.md
✅ scratch/2025-10-21-api-experiment.md

❌ design/auth.md                    # No date
❌ design/DRAFT-auth.md              # Date should be prefix
❌ design/authentication_system.md   # No date
```

## 🔍 Quick Reference

**Starting new feature?**
→ Create `workspace/design/YYYY-MM-DD-feature-name.md`

**Need to research approaches?**
→ Create `workspace/analysis/YYYY-MM-DD-research-topic.md`

**Quick experiment?**
→ Create `workspace/scratch/YYYY-MM-DD-experiment.md`

**User says "create the spec"?**
→ Create formal spec in `.praxis-os/specs/`, then delete workspace file

**Unsure where something goes?**
→ If not ready to commit, it goes in workspace!

## 🚫 Git Safety

**This directory is .gitignored** - you cannot accidentally commit workspace content.

```bash
# This will have no effect (workspace is ignored):
git add .praxis-os/workspace/

# Only commit formal specs:
git add .praxis-os/specs/2025-10-21-feature/
```

## 📚 Related Documentation

For detailed guidelines, see:
- `.praxis-os/standards/universal/installation/workspace-organization.md`
- `.praxis-os/standards/universal/ai-assistant/agent-os-development-process.md`

## ❓ Questions?

**Q: When do I delete workspace files?**
A: After promoting content to formal spec, or when the exploration is complete.

**Q: Can I keep workspace files forever?**
A: No - workspace is for temporary work. If something is valuable long-term, formalize it into a spec or standard.

**Q: What if I want to save historical context?**
A: Move the workspace file to the formal spec's `supporting-docs/` directory before deleting.

**Q: Can I create subdirectories within design/analysis/scratch/?**
A: Generally no - keep flat structure. If you need organization, you probably need a formal spec.

---

**Remember:** Workspace = temporary, specs = permanent. When in doubt, start in workspace and promote when ready!
