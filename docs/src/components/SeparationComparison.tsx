import React from 'react';
import styles from './SeparationComparison.module.css';

export default function SeparationComparison(): React.ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.comparison}>
        {/* Without Separation */}
        <div className={styles.scenario}>
          <div className={styles.scenarioHeader}>
            <span className={styles.scenarioBadge}>❌ Without Separation</span>
          </div>
          <div className={styles.scenarioContent}>
            <div className={styles.structure}>
              <div className={styles.structureLabel}>Single 5000-line file</div>
            </div>
            <div className={styles.flow}>
              <div className={styles.flowStep}>
                <span className={styles.arrow}>→</span>
                <span className={styles.flowText}>Agent must read entire file to find one pattern</span>
              </div>
              <div className={styles.flowStep}>
                <span className={styles.arrow}>→</span>
                <span className={styles.flowText}>Context at 90%+</span>
              </div>
              <div className={styles.flowStep}>
                <span className={styles.arrow}>→</span>
                <span className={styles.flowText}>Attention quality &lt;70%</span>
              </div>
              <div className={styles.flowStep}>
                <span className={styles.arrow}>→</span>
                <span className={styles.flowText}>Failure rate 40%+</span>
              </div>
            </div>
          </div>
        </div>

        {/* With Separation */}
        <div className={`${styles.scenario} ${styles.scenarioGood}`}>
          <div className={styles.scenarioHeader}>
            <span className={`${styles.scenarioBadge} ${styles.scenarioBadgeGood}`}>✅ With Separation</span>
          </div>
          <div className={styles.scenarioContent}>
            <div className={styles.structure}>
              <div className={styles.structureLabel}>50 × 100-line files</div>
            </div>
            <div className={styles.flow}>
              <div className={styles.flowStep}>
                <span className={styles.arrow}>→</span>
                <span className={styles.flowText}>Agent queries for specific pattern</span>
              </div>
              <div className={styles.flowStep}>
                <span className={styles.arrow}>→</span>
                <span className={styles.flowText}>Retrieves one 100-line file</span>
              </div>
              <div className={styles.flowStep}>
                <span className={styles.arrow}>→</span>
                <span className={styles.flowText}>Context at 15%</span>
              </div>
              <div className={styles.flowStep}>
                <span className={styles.arrow}>→</span>
                <span className={styles.flowText}>Attention quality 95%+</span>
              </div>
              <div className={styles.flowStep}>
                <span className={styles.arrow}>→</span>
                <span className={styles.flowText}>Success rate 85%+</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className={styles.insight}>
        <strong>Result:</strong> 3-4x improvement in success rate through context efficiency.
      </div>
    </div>
  );
}

