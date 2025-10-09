import React from 'react';
import styles from './CompactDiagram.module.css';

export default function DataFlowDiagram(): React.ReactElement {
  return (
    <div className={styles.compactFlow}>
      <div className={styles.flowBox}>
        <span className={styles.flowIcon}>🤖</span>
        <span className={styles.flowLabel}>Cursor Agent</span>
      </div>
      
      <span className={styles.flowArrow}>→</span>
      
      <div className={`${styles.flowBox} ${styles.flowBoxWide}`}>
        <div className={styles.splitBox}>
          <div className={styles.splitItem}>
            <span className={styles.flowIcon}>🔍</span>
            <span className={styles.flowLabel}>RAG Engine</span>
          </div>
          <div className={styles.splitDivider}></div>
          <div className={styles.splitItem}>
            <span className={styles.flowIcon}>⚙️</span>
            <span className={styles.flowLabel}>Workflow Engine</span>
          </div>
        </div>
      </div>
      
      <span className={styles.flowArrow}>→</span>
      
      <div className={styles.flowBox}>
        <span className={styles.flowIcon}>📁</span>
        <span className={styles.flowLabel}>.agent-os/</span>
      </div>
    </div>
  );
}


