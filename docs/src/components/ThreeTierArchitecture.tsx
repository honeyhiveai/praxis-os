import React from 'react';
import styles from './ThreeTierArchitecture.module.css';

export default function ThreeTierArchitecture(): React.ReactElement {
  return (
    <div className={styles.container}>
      {/* Tier 1 */}
      <div className={styles.tier}>
        <div className={styles.tierHeader}>
          <span className={styles.tierBadge}>Tier 1</span>
          <h3 className={styles.tierTitle}>Execution Files (≤100 lines)</h3>
        </div>
        <div className={styles.tierContent}>
          <div className={styles.fileTree}>
            <div className={styles.directory}>workflows/spec_creation_v1/phases/1/</div>
            <div className={styles.fileList}>
              <div className={styles.fileItem}>
                <span className={styles.fileIcon}>📄</span>
                <span className={styles.fileNameSmall}>task-1-business-goals.md</span>
                <span className={styles.fileSize}>65 lines</span>
              </div>
              <div className={styles.fileItem}>
                <span className={styles.fileIcon}>📄</span>
                <span className={styles.fileNameSmall}>task-2-user-stories.md</span>
                <span className={styles.fileSize}>78 lines</span>
              </div>
              <div className={styles.fileItem}>
                <span className={styles.fileIcon}>📄</span>
                <span className={styles.fileNameSmall}>task-3-functional-requirements.md</span>
                <span className={styles.fileSize}>92 lines</span>
              </div>
              <div className={styles.fileItem}>
                <span className={styles.fileIcon}>📄</span>
                <span className={styles.fileNameSmall}>task-4-nonfunctional-requirements.md</span>
                <span className={styles.fileSize}>88 lines</span>
              </div>
            </div>
          </div>
          <div className={styles.tierMeta}>
            <div className={styles.metaItem}>
              <strong>Purpose:</strong> Immediate execution guidance
            </div>
            <div className={styles.metaItem}>
              <strong>Consumed:</strong> Every time task runs
            </div>
            <div className={styles.metaItem}>
              <strong>Contains:</strong> Commands, steps, examples, acceptance criteria
            </div>
            <div className={styles.metaItem}>
              <strong>Size:</strong> ≤100 lines (optimal attention)
            </div>
          </div>
        </div>
      </div>

      {/* Tier 2 */}
      <div className={styles.tier}>
        <div className={styles.tierHeader}>
          <span className={styles.tierBadge}>Tier 2</span>
          <h3 className={styles.tierTitle}>Methodology Files (200-500 lines)</h3>
        </div>
        <div className={styles.tierContent}>
          <div className={styles.fileTree}>
            <div className={styles.directory}>workflows/spec_creation_v1/core/</div>
            <div className={styles.fileList}>
              <div className={styles.fileItem}>
                <span className={styles.fileIcon}>📄</span>
                <span className={styles.fileNameSmall}>srd-template.md</span>
                <span className={styles.fileSize}>320 lines</span>
              </div>
              <div className={styles.fileItem}>
                <span className={styles.fileIcon}>📄</span>
                <span className={styles.fileNameSmall}>specs-template.md</span>
                <span className={styles.fileSize}>280 lines</span>
              </div>
              <div className={styles.fileItem}>
                <span className={styles.fileIcon}>📄</span>
                <span className={styles.fileNameSmall}>tasks-template.md</span>
                <span className={styles.fileSize}>210 lines</span>
              </div>
            </div>
          </div>
          <div className={styles.tierMeta}>
            <div className={styles.metaItem}>
              <strong>Purpose:</strong> Comprehensive guidance (referenced, not always loaded)
            </div>
            <div className={styles.metaItem}>
              <strong>Consumed:</strong> When explicitly requested or first-time context
            </div>
            <div className={styles.metaItem}>
              <strong>Contains:</strong> Methodology, principles, complete templates
            </div>
            <div className={styles.metaItem}>
              <strong>Size:</strong> 200-500 lines (acceptable for active reading)
            </div>
          </div>
        </div>
      </div>

      {/* Tier 3 */}
      <div className={`${styles.tier} ${styles.tierOutput}`}>
        <div className={styles.tierHeader}>
          <span className={`${styles.tierBadge} ${styles.tierBadgeOutput}`}>Tier 3</span>
          <h3 className={styles.tierTitle}>Output Files (Unlimited)</h3>
        </div>
        <div className={styles.tierContent}>
          <div className={styles.fileTree}>
            <div className={styles.directory}>.agent-os/specs/2025-10-12-user-auth/</div>
            <div className={styles.fileList}>
              <div className={styles.fileItem}>
                <span className={styles.fileIcon}>✨</span>
                <span className={styles.fileNameSmall}>README.md</span>
                <span className={styles.fileSize}>Generated (3KB)</span>
              </div>
              <div className={styles.fileItem}>
                <span className={styles.fileIcon}>✨</span>
                <span className={styles.fileNameSmall}>srd.md</span>
                <span className={styles.fileSize}>Generated (15KB)</span>
              </div>
              <div className={styles.fileItem}>
                <span className={styles.fileIcon}>✨</span>
                <span className={styles.fileNameSmall}>specs.md</span>
                <span className={styles.fileSize}>Generated (25KB)</span>
              </div>
              <div className={styles.fileItem}>
                <span className={styles.fileIcon}>✨</span>
                <span className={styles.fileNameSmall}>tasks.md</span>
                <span className={styles.fileSize}>Generated (8KB)</span>
              </div>
            </div>
          </div>
          <div className={styles.tierMeta}>
            <div className={styles.metaItem}>
              <strong>Purpose:</strong> AI-generated artifacts
            </div>
            <div className={styles.metaItem}>
              <strong>Consumed:</strong> By humans or AI for reference
            </div>
            <div className={styles.metaItem}>
              <strong>Contains:</strong> Specs, designs, implementation plans
            </div>
            <div className={styles.metaItem}>
              <strong>Size:</strong> Unlimited (generated output)
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

