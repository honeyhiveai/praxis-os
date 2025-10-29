import React from 'react';
import styles from './SpecsProgression.module.css';

interface MilestoneProps {
  period: string;
  specs: string;
  context: string;
  impact: string;
}

const Milestone: React.FC<MilestoneProps> = ({ period, specs, context, impact }) => (
  <div className={styles.milestone}>
    <div className={styles.milestoneHeader}>
      <span className={styles.period}>{period}</span>
    </div>
    <div className={styles.milestoneContent}>
      <div className={styles.row}>
        <span className={styles.label}>Specs:</span>
        <span className={styles.value}>{specs}</span>
      </div>
      <div className={styles.row}>
        <span className={styles.label}>Context:</span>
        <span className={styles.value}>{context}</span>
      </div>
    </div>
    <div className={styles.impact}>{impact}</div>
  </div>
);

export default function SpecsProgression(): React.ReactElement {
  return (
    <div className={styles.container}>
      <Milestone
        period="Week 1"
        specs="0 specs"
        context="No historical context"
        impact="Building from zero"
      />
      
      <div className={styles.arrow}>↓</div>
      
      <Milestone
        period="Month 1"
        specs="3 specs (auth, API design, database schema)"
        context="Major decisions documented"
        impact="Foundation decisions preserved"
      />
      
      <div className={styles.arrow}>↓</div>
      
      <Milestone
        period="Month 3"
        specs="10 specs (core features documented)"
        context="Architecture rationale preserved"
        impact="System design clear"
      />
      
      <div className={styles.arrow}>↓</div>
      
      <Milestone
        period="Month 6"
        specs="20 specs (most features have specs)"
        context="Comprehensive decision history"
        impact="Why and how preserved"
      />
      
      <div className={styles.arrow}>↓</div>
      
      <Milestone
        period="Year 1"
        specs="40+ specs"
        context="Complete project evolution documented"
        impact="Full organizational memory"
      />
    </div>
  );
}

