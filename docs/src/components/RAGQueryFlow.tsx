import React from 'react';
import styles from './CompactDiagram.module.css';

export default function RAGQueryFlow(): React.ReactElement {
  return (
    <div className={styles.compactFlow}>
      <div className={styles.flowBox}>
        <span className={styles.flowIcon}>🤖</span>
        <span className={styles.flowLabel}>AI Agent</span>
      </div>
      
      <span className={styles.flowArrow}>→</span>
      
      <div className={styles.flowBox}>
        <span className={styles.flowIcon}>🔍</span>
        <span className={styles.flowLabel}>MCP Server</span>
      </div>
      
      <span className={styles.flowArrow}>→</span>
      
      <div className={styles.flowBox}>
        <span className={styles.flowIcon}>📊</span>
        <span className={styles.flowLabel}>Vector Index</span>
      </div>
      
      <span className={styles.flowArrow}>→</span>
      
      <div className={styles.flowBox}>
        <span className={styles.flowIcon}>✨</span>
        <span className={styles.flowLabel}>2-5KB Context</span>
      </div>
    </div>
  );
}


