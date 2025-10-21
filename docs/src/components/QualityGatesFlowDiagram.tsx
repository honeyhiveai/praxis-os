import React from 'react';
import styles from './QualityGatesFlowDiagram.module.css';

export default function QualityGatesFlowDiagram(): React.ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.flowBox}>
        <div className={styles.stepLabel}>AI commits (at user approval)</div>
        <div className={styles.arrow}>↓</div>
        <div className={styles.stepLabel}>Pre-commit hooks run</div>
        <div className={styles.arrow}>↓</div>
        <div className={styles.decisionBox}>
          <div className={styles.decisionLabel}>Pass?</div>
        </div>
        <div className={styles.branchContainer}>
          <div className={styles.branchLeft}>
            <div className={styles.branchLabel}>YES</div>
            <div className={styles.arrow}>↓</div>
            <div className={`${styles.resultBox} ${styles.resultSuccess}`}>
              ✅ Commit succeeds
            </div>
          </div>
          <div className={styles.branchRight}>
            <div className={styles.branchLabel}>NO</div>
            <div className={styles.arrow}>↓</div>
            <div className={`${styles.resultBox} ${styles.resultBlocked}`}>
              🚫 Commit blocked
              <div className={styles.resultDetails}>
                • Error message<br />
                • Remediation steps
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

