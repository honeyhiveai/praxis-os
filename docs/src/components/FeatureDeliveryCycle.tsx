import React, { useState } from 'react';
import styles from './FeatureDeliveryCycle.module.css';

interface PhaseProps {
  title: string;
  icon: string;
  content: React.ReactNode;
}

const Phase: React.FC<PhaseProps> = ({ title, icon, content }) => (
  <div className={styles.phase}>
    <div className={styles.phaseIcon}>{icon}</div>
    <div className={styles.phaseContent}>
      <div className={styles.phaseTitle}>{title}</div>
      {content}
    </div>
  </div>
);

interface CycleProps {
  number: number;
  title: string;
  subtitle: string;
  phases: Array<{
    title: string;
    icon: string;
    content: React.ReactNode;
  }>;
}

const Cycle: React.FC<CycleProps> = ({ number, title, subtitle, phases }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className={styles.cycle}>
      <button className={styles.cycleHeader} onClick={() => setIsOpen(!isOpen)}>
        <div className={styles.cycleNumber}>Cycle {number}</div>
        <div className={styles.cycleText}>
          <div className={styles.cycleTitle}>{title}</div>
          <div className={styles.cycleSubtitle}>{subtitle}</div>
        </div>
        <div className={styles.toggleIcon}>{isOpen ? '▼' : '▶'}</div>
      </button>
      {isOpen && (
        <div className={styles.cycleContent}>
          {phases.map((phase, idx) => (
            <Phase key={idx} {...phase} />
          ))}
        </div>
      )}
    </div>
  );
};

export default function FeatureDeliveryCycle(): React.ReactElement {
  return (
    <div className={styles.container}>
      <Cycle
        number={1}
        title="Conversation → Design Doc"
        subtitle="Explore ideas and create high-level approach"
        phases={[
          {
            title: 'Theory (Query Standards)',
            icon: '📚',
            content: (
              <pre className={styles.code}>
{`AI: search_standards("project structure patterns")
AI: search_standards("how to organize feature design")
→ Returns: Your project's conventions, patterns, lessons learned`}
              </pre>
            ),
          },
          {
            title: 'Practice (Iterative Conversation)',
            icon: '💬',
            content: (
              <pre className={styles.code}>
{`Multiple back-and-forth exchanges:
- AI proposes approach using standards
- Human provides context
- AI refines based on feedback
- Repeat until aligned`}
              </pre>
            ),
          },
          {
            title: 'Reflection (Review)',
            icon: '🔍',
            content: (
              <pre className={styles.code}>
{`Human reviews design doc:
✓ Does this approach make sense?
✓ Have we missed edge cases?
✓ Is this aligned with project goals?`}
              </pre>
            ),
          },
          {
            title: 'Learning (Capture)',
            icon: '💾',
            content: (
              <pre className={styles.code}>
{`Design doc written to: .agent-os/workspace/design/YYYY-MM-DD-feature.md
Preserves: Why this approach, what alternatives considered, key decisions`}
              </pre>
            ),
          },
        ]}
      />

      <Cycle
        number={2}
        title="Design → Spec (via spec_creation_v1)"
        subtitle="Break design into detailed, executable plan"
        phases={[
          {
            title: 'Theory (Query Standards Again)',
            icon: '📚',
            content: (
              <pre className={styles.code}>
{`AI: search_standards("how to write specifications")
AI: search_standards("testing requirements patterns")
→ Returns: Spec structure, acceptance criteria patterns`}
              </pre>
            ),
          },
          {
            title: 'Practice (Workflow Breaks Design Into Executable Plans)',
            icon: '⚙️',
            content: (
              <pre className={styles.code}>
{`spec_creation_v1 workflow guides AI through phases:
1. Plan: Break design into components
2. Structure: Organize into detailed requirements
3. Acceptance Criteria: Define success metrics
4. Review Gates: Validate completeness at each phase

Result: Detailed, executable specification`}
              </pre>
            ),
          },
          {
            title: 'Reflection (Review Spec)',
            icon: '🔍',
            content: (
              <pre className={styles.code}>
{`Human reviews spec:
✓ Does this align with design intent?
✓ Are requirements complete and testable?
✓ Will this deliver expected outcome?
✓ Can AI execute this plan?`}
              </pre>
            ),
          },
          {
            title: 'Learning (Capture)',
            icon: '💾',
            content: (
              <pre className={styles.code}>
{`Spec written to: .agent-os/specs/YYYY-MM-DD-feature-spec.md
If new patterns emerge → Update standards for next time`}
              </pre>
            ),
          },
        ]}
      />

      <Cycle
        number={3}
        title="Spec → Implementation (via spec_execution_v1)"
        subtitle="Execute plan with quality validation"
        phases={[
          {
            title: 'Theory (Query Standards for Implementation)',
            icon: '📚',
            content: (
              <pre className={styles.code}>
{`AI: search_standards("testing patterns")
AI: search_standards("error handling conventions")
AI: search_standards("code organization")
→ Returns: YOUR project's implementation patterns`}
              </pre>
            ),
          },
          {
            title: 'Practice (Workflow Executes Based on Plan)',
            icon: '⚡',
            content: (
              <pre className={styles.code}>
{`spec_execution_v1 workflow enforces quality:
1. Plan: Review spec, identify tasks
2. Implement: Write code per spec requirements
3. Test: Create tests per acceptance criteria
4. Validate: Run quality gates (tests, linting, type checking)

Workflow CANNOT skip phases - enforced in code`}
              </pre>
            ),
          },
          {
            title: 'Reflection (Quality Gates)',
            icon: '✅',
            content: (
              <pre className={styles.code}>
{`Evidence-based validation:
✓ All tests pass
✓ Pre-commit hooks pass
✓ Spec acceptance criteria met
✓ Code review checklist complete`}
              </pre>
            ),
          },
          {
            title: 'Learning (Capture & Compound)',
            icon: '📈',
            content: (
              <pre className={styles.code}>
{`Spec updated with:
- What actually worked
- What didn't work as expected
- Patterns that emerged

IF pattern is reusable:
  Create new standard documenting the approach
  → Next feature benefits immediately`}
              </pre>
            ),
          },
        ]}
      />
    </div>
  );
}

