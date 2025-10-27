import React from 'react';
import styles from './StandardsGenerationFlow.module.css';

export default function StandardsGenerationFlow(): React.ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.flow}>
        <div className={styles.file}>
          <div className={styles.fileHeader}>
            <span className={styles.fileIcon}>📄</span>
            <span className={styles.fileName}>universal/standards/concurrency/race-conditions.md</span>
          </div>
          <div className={styles.fileDescription}>
            (Timeless CS fundamentals, 2-3 pages)
          </div>
        </div>

        <div className={styles.arrow}>↓</div>
        <div className={styles.processStep}>LLM generation during install</div>
        <div className={styles.arrow}>↓</div>
        <div className={styles.processStep}>(Analyzes project: language, frameworks, patterns)</div>
        <div className={styles.arrow}>↓</div>

        <div className={`${styles.file} ${styles.fileGenerated}`}>
          <div className={styles.fileHeader}>
            <span className={styles.fileIcon}>✨</span>
            <span className={styles.fileName}>.praxis-os/standards/development/python-concurrency.md</span>
          </div>
          <div className={styles.fileDescription}>
            (Python-specific: threading, asyncio, GIL, pytest)
          </div>
        </div>
      </div>
    </div>
  );
}

