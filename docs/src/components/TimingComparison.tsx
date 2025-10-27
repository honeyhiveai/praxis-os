import React from 'react';
import styles from './TimingComparison.module.css';

export default function TimingComparison(): React.ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.approaches}>
        {/* Traditional Approach */}
        <div className={styles.approach}>
          <div className={styles.approachHeader}>
            <span className={styles.approachBadge}>❌ Traditional Approach</span>
          </div>
          <div className={styles.timeline}>
            <div className={styles.timelineItem}>
              <div className={styles.timelineLabel}>Start of conversation:</div>
              <div className={styles.timelineSteps}>
                <div className={styles.step}>→ Load all documentation (200KB)</div>
                <div className={styles.step}>→ Context at 80%</div>
                <div className={styles.step}>→ Agent works with degraded attention</div>
                <div className={styles.step}>→ By message 20, can barely remember anything</div>
              </div>
            </div>
          </div>
        </div>

        {/* RAG Approach */}
        <div className={`${styles.approach} ${styles.approachGood}`}>
          <div className={styles.approachHeader}>
            <span className={`${styles.approachBadge} ${styles.approachBadgeGood}`}>✅ RAG Approach</span>
          </div>
          <div className={styles.timeline}>
            <div className={styles.timelineItem}>
              <div className={styles.timelineLabel}>Start of conversation:</div>
              <div className={styles.timelineSteps}>
                <div className={styles.step}>→ Minimal initial context (5KB)</div>
                <div className={styles.step}>→ Context at 5%</div>
              </div>
            </div>

            <div className={styles.timelineItem}>
              <div className={styles.timelineLabel}>Message 5 - needs concurrency guidance:</div>
              <div className={styles.timelineSteps}>
                <div className={styles.step}>→ Query "race conditions"</div>
                <div className={styles.step}>→ Retrieve 2KB chunk</div>
                <div className={styles.step}>→ Context at 7%</div>
                <div className={styles.step}>→ Implement correctly</div>
              </div>
            </div>

            <div className={styles.timelineItem}>
              <div className={styles.timelineLabel}>Message 15 - needs error handling:</div>
              <div className={styles.timelineSteps}>
                <div className={styles.step}>→ Query "error handling patterns"</div>
                <div className={styles.step}>→ Retrieve 3KB chunk</div>
                <div className={styles.step}>→ Context at 12%</div>
                <div className={styles.step}>→ Implement correctly</div>
              </div>
            </div>

            <div className={styles.timelineItem}>
              <div className={styles.timelineLabel}>Message 30 - still fresh context:</div>
              <div className={styles.timelineSteps}>
                <div className={styles.step}>→ Context at 20%</div>
                <div className={styles.step}>→ Attention quality still 95%</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

