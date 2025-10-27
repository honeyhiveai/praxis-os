import React from 'react';
import styles from './KnowledgeCompoundingFlow.module.css';

export default function KnowledgeCompoundingFlow(): React.ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.flow}>
        <div className={styles.step}>AI starting new task</div>
        <div className={styles.arrow}>↓</div>
        
        <div className={styles.step}>Queries standards (discovers reusable patterns)</div>
        <div className={styles.arrow}>↓</div>
        
        <div className={styles.step}>Implements following established patterns</div>
        <div className={styles.arrow}>↓</div>
        
        <div className={styles.conditional}>
          <div className={styles.conditionLabel}>If needs historical context:</div>
          <div className={styles.conditionAction}>→ Reads relevant spec to understand "why"</div>
        </div>
        <div className={styles.arrow}>↓</div>
        
        <div className={styles.step}>Creates spec for new work (documents decisions)</div>
        <div className={styles.arrow}>↓</div>
        
        <div className={styles.step}>Identifies reusable pattern</div>
        <div className={styles.arrow}>↓</div>
        
        <div className={styles.step}>Creates standard (makes pattern discoverable)</div>
        <div className={styles.arrow}>↓</div>
        
        <div className={styles.step}>Both committed to git</div>
        <div className={styles.arrow}>↓</div>
        
        <div className={`${styles.step} ${styles.stepFinal}`}>
          <strong>Knowledge compounds over time</strong>
        </div>
      </div>
    </div>
  );
}

