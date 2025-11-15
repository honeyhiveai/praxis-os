import React from 'react';
import styles from './CompactDiagram.module.css';

export default function AgentWithoutPraxis(): React.ReactElement {
  return (
    <div className={styles.compactFlow}>
      <div className={styles.flowBox}>
        <span className={styles.flowIcon}>🤖</span>
        <span className={styles.flowLabel}>Your Coding Agent</span>
      </div>
      
      <span className={styles.flowArrow}>→</span>
      
      <div className={styles.flowBox}>
        <span className={styles.flowIcon}>📁</span>
        <span className={styles.flowLabel}>Your Codebase</span>
      </div>
    </div>
  );
}

