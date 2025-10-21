# Persona Taxonomy Redesign: Core Disciplines vs Specialists

**Key Question**: Should we have micro-specialized personas, or core enterprise disciplines that can consult specialists?

---

## The Problem with Current Approach

### Current: 9 Micro-Specialized Personas

```
1. Workflow Executor (process)
2. Software Architect (system design)
3. Senior Engineer (code implementation)
4. QA Engineer (testing)
5. Code Reviewer (standards)
6. Security Engineer (security)
7. Performance Engineer (optimization)
8. Concurrency Expert (threading)
9. SRE (operations)
```

### Issue: Over-Specialization

**Example: Performance**
- Real Software Architect: DOES think about performance in design
- Real Senior Engineer: DOES optimize code performance
- Real SRE: DOES care about production performance

**So why separate Performance Engineer persona?**

**Example: Concurrency**
- Real Software Architect: DOES design for concurrency
- Real Senior Engineer: DOES write thread-safe code
- Real SRE: DOES handle concurrent load

**So why separate Concurrency Expert persona?**

### User's Insight:

> "Performance/concurrency should be in the domain of architect/engineer/sre... 
> should we come up with core personas of enterprise disciplines, 
> then add specialist personas later if needed?"

**This is correct!** ✅

---

## Proposed: Two-Tier Taxonomy

### **Tier 1: Core Enterprise Disciplines** (Generalists - MVP)

These are the **fundamental roles** that every enterprise software team needs:

```
┌─────────────────────────────────────────────────────────────┐
│                  CORE ENTERPRISE DISCIPLINES                 │
│                  (Every Team Needs These)                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  PROCESS                                                      │
│  └─ 1. Workflow Executor                                     │
│      Role: Process enforcement, phase-gated execution        │
│                                                               │
│  ARCHITECTURE & DESIGN                                       │
│  └─ 2. Software Architect                                    │
│      Role: System design, patterns, scalability              │
│      Scope: Performance architecture, concurrency design,    │
│             API design, system data architecture             │
│                                                               │
│  IMPLEMENTATION                                              │
│  └─ 3. Software Engineer                                     │
│      Role: Code design, implementation, optimization         │
│      Scope: Performance optimization, thread-safety,         │
│             code quality, refactoring, standards             │
│                                                               │
│  DATA & PIPELINES                                            │
│  └─ 4. Data Engineer                                         │
│      Role: Data architecture, pipelines, modeling            │
│      Scope: ETL/ELT, streaming, warehousing, data quality,   │
│             tech stack adaptation, standards population      │
│                                                               │
│  QUALITY ASSURANCE                                           │
│  └─ 5. QA Engineer                                           │
│      Role: Testing strategy, coverage, quality               │
│      Scope: Unit/integration/e2e tests, edge cases           │
│                                                               │
│  SECURITY                                                    │
│  └─ 6. Security Engineer                                     │
│      Role: Security review, threat modeling                  │
│      Scope: Vulnerabilities, OWASP, secure coding            │
│                                                               │
│  OPERATIONS & RELIABILITY                                    │
│  └─ 7. SRE                                                   │
│      Role: Production readiness, operational excellence      │
│      Scope: SLOs, observability, deployments, reliability    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**7 Core Personas** - Every project uses these

---

### **Tier 2: Specialist Disciplines** (Deep Experts - Optional)

These are **optional power-ups** for complex problems:

```
┌─────────────────────────────────────────────────────────────┐
│                   SPECIALIST DISCIPLINES                     │
│              (Add When Complexity Warrants)                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  PERFORMANCE SPECIALISTS                                     │
│  ├─ Performance Engineer (profiling, algorithmic opt)        │
│  └─ Concurrency Expert (race condition forensics)            │
│                                                               │
│  DATABASE SPECIALISTS                                        │
│  └─ Database Expert (complex schema design, query opt)       │
│                                                               │
│  CODE QUALITY SPECIALISTS                                    │
│  └─ Code Reviewer (standards enforcement, docs)              │
│                                                               │
│  ACCESSIBILITY SPECIALISTS                                   │
│  └─ Accessibility Engineer (WCAG, inclusive design)          │
│                                                               │
│  DOMAIN SPECIALISTS                                          │
│  ├─ API Designer (contract design, versioning)               │
│  └─ Frontend Engineer (React/UX patterns)                    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

**6+ Specialist Personas** - Use as needed for deep dives

---

## Benefits of Two-Tier Approach

### ✅ **1. Simpler Mental Model**

**Current** (9 flat personas):
```
"Do I need @architect, @senior-engineer, @performance, @concurrency, or @sre?"
→ Confusing overlap, analysis paralysis
```

**Proposed** (7 core + specialists):
```
"Start with @architect for design, @engineer for implementation, @data for pipelines"
→ Clear starting point, escalate to specialists if needed
```

---

### ✅ **2. Matches Real Team Structure**

**Real Enterprise Teams**:
- Core: Architects, Engineers, QA, Security, SRE (generalists with depth)
- Specialists: Called in for deep problems (performance team, DB team)

**Proposed Model Mirrors Reality** ✅

---

### ✅ **3. Core Personas Are More Valuable**

**Architect reviews cover**:
- Performance architecture (80% of performance issues)
- Concurrency design (80% of concurrency issues)
- API design (80% of API issues)
- Data modeling (70% of database issues)

**One @architect review catches most issues**

vs.

**Specialist reviews cover**:
- Performance: Deep profiling, algorithmic optimization (20% edge cases)
- Concurrency: Complex deadlock analysis (20% edge cases)

**Specialists for the hard 20%**

---

### ✅ **4. Prevents Persona Proliferation**

**Without tiers**:
```
Add Database → 10 personas
Add API Designer → 11 personas
Add Data Engineer → 12 personas
Add Frontend → 13 personas
...eventually 20+ personas
```

**With tiers**:
```
Core: 6 personas (stable, always used)
Specialists: Add as needed (modular, optional)
```

---

### ✅ **5. Better UX: Progressive Disclosure**

**New users**:
```
Start with 6 core personas
Learn: @architect, @engineer, @qa, @security, @sre
Simple, manageable
```

**Power users**:
```
Unlock specialists as needed
"This needs deep performance analysis" → @performance-specialist
"Complex schema design" → @database-specialist
```

---

## Comparison: Scenarios

### Scenario 1: API Design Review

| Approach | Flow | Efficiency |
|----------|------|------------|
| **Current (Flat)** | @architect (system) → @performance (speed) → @concurrency (threading) → @sre (ops) | 4 separate reviews, fragmented |
| **Proposed (Tiered)** | @architect (holistic: system + perf + concurrency + API) → Done in 80% of cases | 1 review covers most issues |

**Winner**: Tiered (more efficient, holistic)

---

### Scenario 2: Complex Deadlock

| Approach | Flow | Result |
|----------|------|--------|
| **Current (Flat)** | User directly invokes @concurrency | Gets specialist immediately |
| **Proposed (Tiered)** | @architect catches basic concurrency issues → recommends @concurrency-specialist for deep analysis | Specialist invoked only when needed |

**Winner**: Tiered (escalation path, avoids over-specialization)

---

### Scenario 3: Database Schema Design

| Approach | Coverage | Gap |
|----------|----------|-----|
| **Current (Flat)** | ⚠️ No database persona (gap) | Must add 10th persona |
| **Proposed (Tiered)** | @architect covers basic schema design (80%) + @database-specialist for complex modeling (20%) | Graceful degradation |

**Winner**: Tiered (handles gaps better with specialists)

---

## Implementation Impact

### Current: 9 Personas to Design & Implement

**Phase 1 (Essential)**:
- ✅ Workflow Executor (done)
- ⏳ Software Architect
- ⏳ Senior Engineer
- ⏳ QA Engineer
- ⏳ Security Engineer
- ✅ SRE (done)

**Phase 2 (Nice-to-have)**:
- ⏳ Code Reviewer
- ⏳ Performance Engineer
- ⏳ Concurrency Expert

**Total**: 9 personas × ~1500 token prompts × design/test = Large effort

---

### Proposed: 7 Core + Specialists on Demand

**MVP (7 Core Personas)**:
- ✅ Workflow Executor (done)
- ⏳ Software Architect (expanded scope: +performance, +concurrency, +API)
- ⏳ Software Engineer (expanded scope: +optimization, +standards)
- ⏳ Data Engineer (data pipelines, modeling, tech stack standards)
- ⏳ QA Engineer
- ⏳ Security Engineer
- ✅ SRE (done)

**Total MVP**: 7 core personas (ship this first)

**Post-MVP (Specialists as Needed)**:
- Add Performance Specialist when users need deep profiling
- Add Concurrency Specialist when deadlocks need forensics
- Add Database Specialist when schema modeling is complex

**Benefit**: Ship MVP faster, add specialists based on user demand

---

## Revised Core Persona Responsibilities

### Architect (Expanded Scope)

**Before** (narrow):
- System design
- Component relationships
- Technology selection

**After** (broad enterprise discipline):
- System design + architecture patterns
- Performance architecture (caching, scaling, indexes)
- Concurrency design (thread pools, async patterns)
- API design (REST, GraphQL, versioning)
- Data architecture (schema basics, modeling)
- **Consults specialists for deep dives**

**Coverage**: 80% of design issues

---

### Software Engineer (Expanded Scope)

**Before** (narrow):
- Code implementation
- Refactoring

**After** (broad enterprise discipline):
- Code design + implementation
- Performance optimization (algorithm, query tuning)
- Thread-safety (locks, atomics, race condition fixes)
- Code quality + standards
- Refactoring + technical debt
- **Consults specialists for deep dives**

**Coverage**: 80% of implementation issues

---

### Data Engineer (NEW - Core Discipline)

**Why This is Core, Not Specialist**:
- Most modern apps have data pipelines (streaming, ETL, analytics)
- Data architecture is distinct from software architecture
- Different concerns: data quality, lineage, governance vs system design
- Different tech stacks: Kafka, Airflow, dbt, Spark vs application frameworks

**Responsibilities**:
- Data pipeline architecture (ETL/ELT, streaming)
- Data modeling (warehouses, lakes, star schema)
- Data quality and validation
- Data tech stack selection and integration
- **Standards population for chosen tech** ← Key differentiator

**Unique Value: Tech Stack Standards Population**

Example: Project uses Kafka + Airflow + dbt

**Current approach** (no data persona):
```
User: "We're using Kafka for streaming"
AI: "I'll write Kafka code based on universal patterns"
→ Generic implementation, no project-specific standards
→ Each engineer implements Kafka differently
→ Inconsistent patterns across codebase
```

**With Data Engineer persona**:
```
User: "We're using Kafka + Airflow + dbt"

AI (Data Engineer):
"I'll establish data standards for your stack:

1. Kafka Patterns
   - Topic naming: {domain}.{entity}.{version} (e.g. users.created.v1)
   - Serialization: Avro with schema registry
   - Consumer groups: {service}-{consumer-name}
   - Error handling: Dead letter queues with retry logic

2. Airflow Patterns
   - DAG naming: {frequency}_{domain}_{pipeline}
   - Task idempotency: Required for all operators
   - SLA monitoring: Define per DAG
   - Secret management: Use Airflow Connections

3. dbt Patterns
   - Model structure: staging/ → intermediate/ → marts/
   - Naming: stg_{source}__{entity}, int_{domain}, dim_/fct_
   - Testing: Every model has at least uniqueness test
   - Documentation: description + column docs required

Creating these as .agent-os/standards/data/kafka-patterns.md...
All future AI assistance will follow these project standards."
```

**Benefit**: Consistent data patterns across entire project

**Coverage**:
- Data pipeline design (80%)
- Streaming architectures (80%)
- Data quality patterns (80%)
- Warehouse modeling basics (70%)
- **Consults Database Specialist for complex schema design**

---

## Recommendation

### ✅ **Adopt Two-Tier Taxonomy**

**Tier 1: 7 Core Personas (MVP)**
1. Workflow Executor ✅
2. Software Architect (expanded)
3. Software Engineer (expanded)
4. Data Engineer (NEW - standards population)
5. QA Engineer
6. Security Engineer
7. SRE ✅

**Ship these first** - Covers 80%+ of needs

---

**Tier 2: Specialists (Post-MVP, on-demand)**
8. Performance Engineer (deep profiling)
9. Concurrency Expert (deadlock forensics)
10. Database Expert (complex schema design)
11. Code Reviewer (standards enforcement)
12. Accessibility Engineer (WCAG compliance)
13. (Add more as user demand dictates)

**Add these based on real user needs**

---

## Next Steps

1. **Redesign Architect persona** with expanded scope:
   - Add: Performance architecture section
   - Add: Concurrency design section
   - Add: API design section
   - Add: Data architecture basics
   - Add: "When to consult specialists" guidance

2. **Redesign Software Engineer persona** with expanded scope:
   - Add: Performance optimization section
   - Add: Thread-safety section
   - Add: Code quality/standards section

3. **Design Data Engineer persona**:
   - Add: Data pipeline architecture section
   - Add: Streaming/ETL patterns section
   - Add: Tech stack standards population capability
   - Add: Data quality and validation section

4. **Ship 7-persona MVP**

5. **Collect feedback**, add specialists as needed

---

**Advantages**:
- ✅ Simpler (7 core vs 9+ flat)
- ✅ Mirrors real teams (core + specialists)
- ✅ Better UX (progressive disclosure)
- ✅ Includes data discipline (critical for modern apps)
- ✅ Standards population (Data Engineer populates tech-specific standards)
- ✅ Prevents proliferation (specialists are opt-in)
- ✅ More holistic reviews (Architect covers 80%)

**Disadvantages**:
- ⚠️ Core persona prompts are larger (more scope)
- ⚠️ Core personas need RAG for specialist topics

**Trade-off**: Worth it for simplicity and real-world alignment

---

**Status**: ✅ Recommend two-tier taxonomy (7 core + specialists)

**Key Addition**: Data Engineer persona - adapts to any data stack, populates project-specific standards