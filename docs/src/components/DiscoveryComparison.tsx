import React from 'react';
import styles from './DiscoveryComparison.module.css';

export default function DiscoveryComparison(): React.ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.comparison}>
        {/* Wrong Approach */}
        <div className={styles.approach}>
          <div className={styles.approachHeader}>
            <span className={styles.badge}>❌ Static Instruction (Wrong)</span>
          </div>
          <div className={styles.approachContent}>
            <div className={styles.example}>
              "For race conditions, always use mutexes with proper error handling"
            </div>
            <div className={styles.section}>
              <div className={styles.sectionLabel}>Problem:</div>
              <ul className={styles.list}>
                <li>May not apply to this situation</li>
                <li>Agent can't remember after 20 messages</li>
                <li>Doesn't teach the skill</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Right Approach */}
        <div className={`${styles.approach} ${styles.approachGood}`}>
          <div className={styles.approachHeader}>
            <span className={`${styles.badge} ${styles.badgeGood}`}>✅ Dynamic Discovery (Right)</span>
          </div>
          <div className={styles.approachContent}>
            <div className={styles.example}>
              "When you encounter shared state, query standards:
              <div className={styles.codeSnippet}>
                <div>→ search_standards('race conditions shared state')</div>
                <div>→ Apply patterns from results"</div>
              </div>
            </div>
            <div className={styles.section}>
              <div className={styles.sectionLabel}>Benefit:</div>
              <ul className={styles.list}>
                <li>Agent learns to query</li>
                <li>Gets context-specific guidance</li>
                <li>Skill reinforces itself</li>
                <li>Works at any conversation depth</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

