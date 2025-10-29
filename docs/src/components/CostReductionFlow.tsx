import React from 'react';
import styles from './CostReductionFlow.module.css';

export default function CostReductionFlow(): React.ReactElement {
  return (
    <div className={styles.container}>
      {/* Compact visual flow */}
      <div className={styles.compactFlow}>
        <div className={styles.flowBox}>
          <span className={styles.flowIcon}>🔍</span>
          <span className={styles.flowLabel}>Query Standards</span>
        </div>
        
        <span className={styles.flowArrow}>→</span>
        
        <div className={styles.flowBox}>
          <span className={styles.flowIcon}>✅</span>
          <span className={styles.flowLabel}>Fewer Mistakes</span>
        </div>
        
        <span className={styles.flowArrow}>→</span>
        
        <div className={styles.flowBox}>
          <span className={styles.flowIcon}>🔄</span>
          <span className={styles.flowLabel}>Less Rework</span>
        </div>
        
        <span className={styles.flowArrow}>→</span>
        
        <div className={styles.flowBox}>
          <span className={styles.flowIcon}>📊</span>
          <span className={styles.flowLabel}>-71% Messages</span>
        </div>
        
        <span className={styles.flowArrow}>→</span>
        
        <div className={styles.flowBox}>
          <span className={styles.flowIcon}>💰</span>
          <span className={styles.flowLabel}>-54% Cost</span>
        </div>
      </div>

      {/* Detailed explanation */}
      <div className={styles.explanation}>
        <div className={styles.explanationTitle}>The Compounding Mechanism</div>
        <div className={styles.steps}>
          <div className={styles.explanationStep}>
            <strong>Query standards before implementing</strong>
            <span className={styles.stepArrow}>↓</span>
            Fewer implementation mistakes
          </div>
          <div className={styles.explanationStep}>
            <strong>Fewer mistakes</strong>
            <span className={styles.stepArrow}>↓</span>
            Fewer "let me fix that" correction cycles
          </div>
          <div className={styles.explanationStep}>
            <strong>Fewer correction cycles</strong>
            <span className={styles.stepArrow}>↓</span>
            44.5% reduction in rework
          </div>
          <div className={styles.explanationStep}>
            <strong>Less rework</strong>
            <span className={styles.stepArrow}>↓</span>
            71% fewer messages needed to complete work
          </div>
          <div className={styles.explanationStep}>
            <strong>Fewer messages</strong>
            <span className={styles.stepArrow}>↓</span>
            72% fewer tokens, 54% cost reduction
          </div>
        </div>
        <div className={styles.insight}>
          <strong>Key Insight:</strong> Each decision to query standards prevents errors. Fewer errors mean fewer correction cycles. 
          Fewer cycles mean dramatically fewer messages. The cost savings compound with every avoided mistake.
        </div>
      </div>
    </div>
  );
}

