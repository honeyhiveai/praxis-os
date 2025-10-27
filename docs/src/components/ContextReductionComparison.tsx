import React from 'react';
import styles from './ContextReductionComparison.module.css';

export default function ContextReductionComparison(): React.ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.comparison}>
        {/* Before */}
        <div className={styles.approach}>
          <div className={styles.approachHeader}>
            <span className={styles.badge}>❌ Before (Cursor Rules)</span>
          </div>
          <div className={styles.approachContent}>
            <div className={styles.metric}>
              <span className={styles.metricLabel}>Context:</span>
              <span className={styles.metricValue}>50KB standards file</span>
            </div>
            <div className={styles.metric}>
              <span className={styles.metricLabel}>Relevant:</span>
              <span className={styles.metricValue}>2KB (4%)</span>
            </div>
            <div className={styles.metric}>
              <span className={styles.metricLabel}>Irrelevant:</span>
              <span className={styles.metricValue}>48KB (96%)</span>
            </div>
            <div className={styles.metric}>
              <span className={styles.metricLabel}>Attention quality:</span>
              <span className={styles.metricValue}>~60%</span>
            </div>
            <div className={styles.metric}>
              <span className={styles.metricLabel}>Success rate:</span>
              <span className={styles.metricValue}>70%</span>
            </div>
          </div>
        </div>

        {/* After */}
        <div className={`${styles.approach} ${styles.approachGood}`}>
          <div className={styles.approachHeader}>
            <span className={`${styles.badge} ${styles.badgeGood}`}>✅ After (MCP/RAG)</span>
          </div>
          <div className={styles.approachContent}>
            <div className={styles.metric}>
              <span className={styles.metricLabel}>Context:</span>
              <span className={styles.metricValue}>3 chunks × 800 tokens = 2.4KB</span>
            </div>
            <div className={styles.metric}>
              <span className={styles.metricLabel}>Relevant:</span>
              <span className={styles.metricValue}>2.3KB (95%)</span>
            </div>
            <div className={styles.metric}>
              <span className={styles.metricLabel}>Irrelevant:</span>
              <span className={styles.metricValue}>0.1KB (5%)</span>
            </div>
            <div className={styles.metric}>
              <span className={styles.metricLabel}>Attention quality:</span>
              <span className={styles.metricValue}>~95%</span>
            </div>
            <div className={styles.metric}>
              <span className={styles.metricLabel}>Success rate:</span>
              <span className={styles.metricValue}>92%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

