import React from 'react';
import styles from './KnowledgeProgressionTimeline.module.css';

export default function KnowledgeProgressionTimeline(): React.ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.timeline}>
        {/* Week 1 */}
        <div className={styles.milestone}>
          <div className={styles.milestoneHeader}>
            <span className={styles.week}>Week 1</span>
            <span className={styles.phase}>Foundation</span>
          </div>
          <div className={styles.stats}>
            <div className={styles.stat}>
              <span className={styles.statLabel}>Universal standards:</span>
              <span className={styles.statValue}>100 documents</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statLabel}>Project standards:</span>
              <span className={styles.statValue}>0 documents</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statLabel}>Project specs:</span>
              <span className={styles.statValue}>0 specs</span>
            </div>
          </div>
          <div className={styles.knowledge}>
            <strong>AI knowledge:</strong> Generic best practices only
          </div>
        </div>

        <div className={styles.arrow}>↓</div>

        {/* Week 4 */}
        <div className={styles.milestone}>
          <div className={styles.milestoneHeader}>
            <span className={styles.week}>Week 4</span>
            <span className={styles.phase}>Project Awareness</span>
          </div>
          <div className={styles.stats}>
            <div className={styles.stat}>
              <span className={styles.statLabel}>Universal standards:</span>
              <span className={styles.statValue}>100 documents</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statLabel}>Project standards:</span>
              <span className={styles.statValue}>15 documents</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statLabel}>Project specs:</span>
              <span className={styles.statValue}>3 specs (authentication, API design, database schema)</span>
            </div>
          </div>
          <div className={styles.knowledge}>
            <strong>AI knowledge:</strong> Your conventions + context on major decisions
          </div>
        </div>

        <div className={styles.arrow}>↓</div>

        {/* Week 12 */}
        <div className={styles.milestone}>
          <div className={styles.milestoneHeader}>
            <span className={styles.week}>Week 12</span>
            <span className={styles.phase}>Project Expertise</span>
          </div>
          <div className={styles.stats}>
            <div className={styles.stat}>
              <span className={styles.statLabel}>Universal standards:</span>
              <span className={styles.statValue}>100 documents</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statLabel}>Project standards:</span>
              <span className={styles.statValue}>50 documents</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statLabel}>Project specs:</span>
              <span className={styles.statValue}>12 specs (major features documented)</span>
            </div>
          </div>
          <div className={styles.knowledge}>
            <strong>AI knowledge:</strong> Deep understanding of your patterns + full history
          </div>
        </div>

        <div className={styles.arrow}>↓</div>

        {/* Week 24 */}
        <div className={`${styles.milestone} ${styles.milestoneFinal}`}>
          <div className={styles.milestoneHeader}>
            <span className={styles.week}>Week 24</span>
            <span className={styles.phase}>Organizational Memory</span>
          </div>
          <div className={styles.stats}>
            <div className={styles.stat}>
              <span className={styles.statLabel}>Universal standards:</span>
              <span className={styles.statValue}>100 documents</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statLabel}>Project standards:</span>
              <span className={styles.statValue}>100+ documents</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statLabel}>Project specs:</span>
              <span className={styles.statValue}>25+ specs (comprehensive history)</span>
            </div>
          </div>
          <div className={styles.knowledge}>
            <strong>AI knowledge:</strong> Expert-level on your project + complete decision history
          </div>
        </div>
      </div>
    </div>
  );
}

