import React, { useState } from 'react';
import styles from './MicroPraxisCycle.module.css';

interface Phase {
  number: number;
  title: string;
  subtitle: string;
  content: string[];
  measurable: string;
}

const phases: Phase[] = [
  {
    number: 1,
    title: 'Theory',
    subtitle: 'Foundation + Enhancement',
    content: [
      'AI: search_standards("how to handle concurrent writes")',
      '→ Returns: mutex patterns, race condition detection, testing strategies',
      '',
      'Layer 1 (Foundation): AI knows what mutexes are, basic concurrency concepts',
      'Layer 2 (Enhancement): AI learns YOUR project\'s mutex patterns and conventions'
    ],
    measurable: 'Knowledge available'
  },
  {
    number: 2,
    title: 'Practice',
    subtitle: 'Workflow-Guided Implementation',
    content: [
      'AI follows workflow structure while implementing:',
      '- Plan: Design mutex-protected write operation',
      '- Implement: Write code applying retrieved patterns',
      '- Test: Create unit tests for race conditions',
      '- Validate: Run tests and verify requirements',
      '',
      'Practice = Theory applied through structured process'
    ],
    measurable: 'Does the implementation work correctly?'
  },
  {
    number: 3,
    title: 'Reflection',
    subtitle: 'Evidence-Based Validation',
    content: [
      'Quality check with concrete evidence:',
      '✓ Unit tests pass (locking prevents race conditions)',
      '✓ Code review checklist complete',
      '✓ Performance benchmarks within requirements',
      '✓ Pre-commit hooks pass'
    ],
    measurable: 'Does the output meet quality standards?'
  },
  {
    number: 4,
    title: 'Learning',
    subtitle: 'Knowledge Capture',
    content: [
      'IF pattern is reusable AND not documented:',
      '  Create new standard documenting the approach',
      '  → Enhances Layer 2 (theory) for future cycles',
      'ELSE:',
      '  Reinforce existing standard through successful application',
      '',
      'Result: Next cycle starts with richer theory'
    ],
    measurable: 'Can future tasks reuse this knowledge?'
  }
];

export default function MicroPraxisCycle(): React.ReactElement {
  const [expandedPhase, setExpandedPhase] = useState<number | null>(null);

  const togglePhase = (phaseNumber: number) => {
    setExpandedPhase(expandedPhase === phaseNumber ? null : phaseNumber);
  };

  return (
    <div className={styles.container}>
      <div className={styles.phasesContainer}>
        {phases.map((phase) => (
          <div key={phase.number} className={styles.phaseCard}>
            <button
              className={`${styles.phaseHeader} ${expandedPhase === phase.number ? styles.expanded : ''}`}
              onClick={() => togglePhase(phase.number)}
              aria-expanded={expandedPhase === phase.number}
            >
              <div className={styles.phaseNumber}>{phase.number}</div>
              <div className={styles.phaseHeaderContent}>
                <div className={styles.phaseTitle}>{phase.title}</div>
                <div className={styles.phaseSubtitle}>({phase.subtitle})</div>
              </div>
              <div className={styles.expandIcon}>
                {expandedPhase === phase.number ? '−' : '+'}
              </div>
            </button>

            {expandedPhase === phase.number && (
              <div className={styles.phaseContent}>
                <div className={styles.contentBlock}>
                  {phase.content.map((line, idx) => (
                    <div key={idx} className={styles.contentLine}>
                      {line}
                    </div>
                  ))}
                </div>
                <div className={styles.measurableBox}>
                  <strong>Measurable by:</strong> {phase.measurable}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className={styles.infoBox}>
        <strong>💡 Tip:</strong> Click any phase to expand and see details. Each phase is measurable and leads to the next.
      </div>
    </div>
  );
}

