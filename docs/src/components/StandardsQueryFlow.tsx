import React from 'react';
import styles from './StandardsQueryFlow.module.css';

export default function StandardsQueryFlow(): React.ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.flow}>
        <div className={styles.step}>
          <div className={styles.stepIcon}>🤖</div>
          <div className={styles.stepText}>AI starting new task</div>
        </div>

        <div className={styles.arrow}>↓</div>

        <div className={styles.step}>
          <div className={styles.stepIcon}>🔍</div>
          <div className={styles.stepText}>Queries: search_standards("how to X")</div>
        </div>

        <div className={styles.arrow}>↓</div>

        <div className={styles.step}>
          <div className={styles.stepIcon}>📚</div>
          <div className={styles.stepText}>Discovers patterns</div>
        </div>

        <div className={styles.arrow}>↓</div>

        <div className={styles.step}>
          <div className={styles.stepIcon}>✨</div>
          <div className={styles.stepText}>Implements using established patterns</div>
        </div>

        <div className={styles.arrow}>↓</div>

        <div className={styles.keyBox}>
          <div className={styles.keyText}>AI <em>always</em> queries before implementing. This is the foundation of the system.</div>
        </div>
      </div>
    </div>
  );
}

