import React from 'react';
import styles from './QualityProgression.module.css';

export default function QualityProgression(): React.ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.title}>The Ultimate Metric: Measurable Quality Improvement</div>
      
      <div className={styles.comparison}>
        <div className={styles.approach}>
          <div className={styles.approachHeader} style={{ backgroundColor: 'var(--ifm-color-danger)' }}>
            <div className={styles.approachTitle}>Traditional AI Development</div>
            <div className={styles.approachSubtitle}>No systematic learning</div>
          </div>
          <div className={styles.approachContent}>
            <div className={styles.sessions}>
              <div className={styles.session}>
                <div className={styles.sessionLabel}>Session 1:</div>
                <div className={styles.sessionFormula}>
                  <span className={styles.component}>[AI capability]</span>
                  <span className={styles.operator}>→</span>
                  <span className={styles.result}>70% quality</span>
                </div>
              </div>
              <div className={styles.sessionDivider}>⋮</div>
              <div className={styles.session}>
                <div className={styles.sessionLabel}>Session 50:</div>
                <div className={styles.sessionFormula}>
                  <span className={styles.component}>[AI capability]</span>
                  <span className={styles.operator}>→</span>
                  <span className={styles.result}>70% quality</span>
                </div>
              </div>
            </div>
            <div className={styles.outcome}>
              <div className={styles.outcomeIcon}>📉</div>
              <div className={styles.outcomeText}>No improvement</div>
            </div>
          </div>
        </div>
        
        <div className={styles.approach}>
          <div className={styles.approachHeader} style={{ backgroundColor: 'var(--ifm-color-success)' }}>
            <div className={styles.approachTitle}>Praxis-Driven Development</div>
            <div className={styles.approachSubtitle}>Continuous knowledge compounding</div>
          </div>
          <div className={styles.approachContent}>
            <div className={styles.sessions}>
              <div className={styles.session}>
                <div className={styles.sessionLabel}>Session 1:</div>
                <div className={styles.sessionFormula}>
                  <span className={styles.component}>[AI capability]</span>
                  <span className={styles.operator}>+</span>
                  <span className={styles.component}>[0 standards]</span>
                  <span className={styles.operator}>→</span>
                  <span className={styles.result}>70% quality</span>
                </div>
              </div>
              <div className={styles.session}>
                <div className={styles.sessionLabel}>Session 10:</div>
                <div className={styles.sessionFormula}>
                  <span className={styles.component}>[AI capability]</span>
                  <span className={styles.operator}>+</span>
                  <span className={styles.component}>[25 standards]</span>
                  <span className={styles.operator}>→</span>
                  <span className={styles.result} style={{ color: 'var(--ifm-color-info)' }}>85% quality</span>
                </div>
              </div>
              <div className={styles.session}>
                <div className={styles.sessionLabel}>Session 50:</div>
                <div className={styles.sessionFormula}>
                  <span className={styles.component}>[AI capability]</span>
                  <span className={styles.operator}>+</span>
                  <span className={styles.component}>[95 standards]</span>
                  <span className={styles.operator}>→</span>
                  <span className={styles.result} style={{ color: 'var(--ifm-color-success)' }}>95% quality</span>
                </div>
              </div>
            </div>
            <div className={styles.outcome}>
              <div className={styles.outcomeIcon}>📈</div>
              <div className={styles.outcomeText}>Continuous improvement</div>
            </div>
          </div>
        </div>
      </div>
      
      <div className={styles.insight}>
        The AI doesn't get smarter. <strong>The system does.</strong>
      </div>
    </div>
  );
}

