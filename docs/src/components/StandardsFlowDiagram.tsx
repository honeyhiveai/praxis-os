import React from 'react';
import styles from './StandardsFlowDiagram.module.css';

export default function StandardsFlowDiagram(): React.ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.tier}>
        <h3 className={styles.tierTitle}>Universal Standards</h3>
        <div className={styles.tierSubtitle}>Static, Timeless</div>
        <div className={styles.grid}>
          <div className={`${styles.card} ${styles.cardBlue}`}>
            <div className={styles.cardIcon}>🔒</div>
            <div className={styles.cardTitle}>Race Conditions</div>
          </div>
          <div className={`${styles.card} ${styles.cardBlue}`}>
            <div className={styles.cardIcon}>🔐</div>
            <div className={styles.cardTitle}>Locking Strategies</div>
          </div>
          <div className={`${styles.card} ${styles.cardBlue}`}>
            <div className={styles.cardIcon}>🧪</div>
            <div className={styles.cardTitle}>Test Pyramid</div>
          </div>
        </div>
      </div>

      <div className={styles.arrow}>
        <div className={styles.arrowLine}></div>
        <div className={styles.arrowLabel}>LLM Generation</div>
        <div className={styles.arrowHead}>→</div>
      </div>

      <div className={styles.tier}>
        <h3 className={styles.tierTitle}>Language-Specific Standards</h3>
        <div className={styles.tierSubtitle}>Generated per Project</div>
        <div className={styles.grid}>
          <div className={`${styles.card} ${styles.cardPurple}`}>
            <div className={styles.cardIcon}>🐍</div>
            <div className={styles.cardTitle}>Python</div>
            <div className={styles.cardDetail}>threading.Lock, asyncio.Lock</div>
          </div>
          <div className={`${styles.card} ${styles.cardGreen}`}>
            <div className={styles.cardIcon}>🔷</div>
            <div className={styles.cardTitle}>Go</div>
            <div className={styles.cardDetail}>sync.Mutex, channels</div>
          </div>
          <div className={`${styles.card} ${styles.cardOrange}`}>
            <div className={styles.cardIcon}>🦀</div>
            <div className={styles.cardTitle}>Rust</div>
            <div className={styles.cardDetail}>Mutex&lt;T&gt;, Arc, RwLock</div>
          </div>
        </div>
      </div>
    </div>
  );
}

