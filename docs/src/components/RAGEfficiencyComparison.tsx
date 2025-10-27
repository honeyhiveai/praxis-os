import React from 'react';
import styles from './RAGEfficiencyComparison.module.css';

export default function RAGEfficiencyComparison(): React.ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.title}>Context Efficiency: The 90% Reduction</div>
      
      <div className={styles.comparison}>
        {/* Option A */}
        <div className={styles.option}>
          <div className={styles.optionHeader}>
            <span className={styles.optionBadge}>❌ Option A</span>
            <span className={styles.optionTitle}>Static Instructions</span>
          </div>
          <div className={styles.optionContent}>
            <div className={styles.problem}>
              <div className={styles.label}>Problem:</div>
              <div className={styles.text}>Initial instructions (15K tokens)</div>
            </div>
            <div className={styles.flow}>
              <span className={styles.flowText}>As conversation grows</span>
              <span className={styles.flowArrow}>→</span>
              <span className={styles.flowText}>Statistical influence drops to &lt;1%</span>
            </div>
            <div className={styles.result}>
              <div className={styles.label}>Result:</div>
              <div className={styles.text}>Agent "forgets" patterns, quality degrades</div>
            </div>
          </div>
        </div>

        {/* Option B */}
        <div className={styles.option}>
          <div className={styles.optionHeader}>
            <span className={styles.optionBadge}>❌ Option B</span>
            <span className={styles.optionTitle}>Read Everything</span>
          </div>
          <div className={styles.optionContent}>
            <div className={styles.problem}>
              <div className={styles.label}>Problem:</div>
              <div className={styles.text}>Read entire standards files (50KB each)</div>
            </div>
            <div className={styles.flow}>
              <span className={styles.flowText}>Context fills to 90%+</span>
              <span className={styles.flowArrow}>→</span>
              <span className={styles.flowText}>Attention quality drops to &lt;70%</span>
            </div>
            <div className={styles.result}>
              <div className={styles.label}>Result:</div>
              <div className={styles.text}>Poor performance, missed details, failures</div>
            </div>
          </div>
        </div>

        {/* RAG Solution */}
        <div className={`${styles.option} ${styles.optionGood}`}>
          <div className={styles.optionHeader}>
            <span className={`${styles.optionBadge} ${styles.optionBadgeGood}`}>✅ RAG Solution</span>
            <span className={styles.optionTitle}>Targeted Retrieval</span>
          </div>
          <div className={styles.optionContent}>
            <div className={styles.stats}>
              <div className={styles.stat}>
                <div className={styles.statLabel}>Query retrieves:</div>
                <div className={styles.statValue}>2-5KB targeted chunks (vs 50KB files)</div>
              </div>
              <div className={styles.stat}>
                <div className={styles.statLabel}>Context utilization:</div>
                <div className={styles.statValue}>15-25% (vs 90%+)</div>
              </div>
              <div className={styles.stat}>
                <div className={styles.statLabel}>Attention quality:</div>
                <div className={styles.statValue}>95%+ (vs &lt;70%)</div>
              </div>
              <div className={styles.stat}>
                <div className={styles.statLabel}>Token efficiency:</div>
                <div className={styles.statValue}>90% reduction (12,500 → 625 tokens)</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

