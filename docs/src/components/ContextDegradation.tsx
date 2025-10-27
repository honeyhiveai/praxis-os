import React from 'react';
import styles from './ContextDegradation.module.css';

export default function ContextDegradation(): React.ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.comparison}>
        {/* Message 1 */}
        <div className={styles.scenario}>
          <div className={styles.scenarioTitle}>Message 1</div>
          <div className={styles.breakdown}>
            <div className={styles.item}>
              <div className={styles.itemLabel}>Initial orientation:</div>
              <div className={styles.itemValue}>15,000 tokens (75% of context)</div>
            </div>
            <div className={styles.item}>
              <div className={styles.itemLabel}>User message:</div>
              <div className={styles.itemValue}>5,000 tokens (25%)</div>
            </div>
          </div>
          <div className={styles.result}>
            <span className={styles.arrow}>→</span>
            <span className={styles.resultText}>Rules have <strong>HIGH</strong> statistical influence</span>
          </div>
        </div>

        {/* Arrow */}
        <div className={styles.evolutionArrow}>↓</div>

        {/* Message 30 */}
        <div className={styles.scenario}>
          <div className={styles.scenarioTitle}>Message 30</div>
          <div className={styles.breakdown}>
            <div className={styles.item}>
              <div className={styles.itemLabel}>Initial orientation:</div>
              <div className={styles.itemValue}>15,000 tokens (still 15k)</div>
            </div>
            <div className={styles.item}>
              <div className={styles.itemLabel}>29 messages:</div>
              <div className={styles.itemValue}>2,485,000 tokens (99.4%)</div>
            </div>
            <div className={styles.item}>
              <div className={styles.itemLabel}>Latest message:</div>
              <div className={styles.itemValue}>5,000 tokens</div>
            </div>
          </div>
          <div className={styles.result}>
            <span className={styles.arrow}>→</span>
            <span className={styles.resultText}>Rules have <strong>NEGLIGIBLE</strong> influence (0.6%)</span>
          </div>
        </div>
      </div>

      <div className={styles.insight}>
        <strong>Mathematical Reality:</strong> Initial guidance fades to noise. Static instructions don't scale.
      </div>
    </div>
  );
}

