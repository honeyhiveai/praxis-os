import React from 'react';
import styles from './RAGDecisionFlowDiagram.module.css';

export default function RAGDecisionFlowDiagram(): React.ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.comparisonRow}>
        {/* Without RAG */}
        <div className={styles.scenarioBox}>
          <div className={styles.scenarioHeader}>Without RAG</div>
          
          <div className={styles.decisionBox}>
            <div className={styles.decisionLabel}>Decision:</div>
            <div className={styles.decisionText}>
              Should I implement this race condition handler?
            </div>
          </div>

          <div className={styles.contextBox}>
            <div className={styles.contextLabel}>Recent context:</div>
            <div className={styles.contextText}>Generic programming patterns</div>
          </div>

          <div className={styles.probabilitiesBox}>
            <div className={styles.probability}>
              <span className={styles.probLabel}>Probability of querying standards:</span>
              <span className={styles.probValue}>20%</span>
            </div>
            <div className={styles.probability}>
              <span className={styles.probLabel}>Probability of guessing:</span>
              <span className={styles.probValue}>80%</span>
            </div>
          </div>

          <div className={`${styles.resultBox} ${styles.resultBad}`}>
            <div className={styles.resultLabel}>Result:</div>
            <div className={styles.resultText}>Likely guesses, may be wrong</div>
          </div>
        </div>

        {/* With RAG */}
        <div className={styles.scenarioBox}>
          <div className={`${styles.scenarioHeader} ${styles.scenarioHeaderGood}`}>
            With RAG
          </div>
          
          <div className={styles.decisionBox}>
            <div className={styles.decisionLabel}>Decision:</div>
            <div className={styles.decisionText}>
              Should I implement this race condition handler?
            </div>
          </div>

          <div className={styles.contextBox}>
            <div className={styles.contextLabel}>Recent context:</div>
            <div className={styles.contextText}>Just queried "race conditions"</div>
            <div className={styles.contextText}>Retrieved "query before implementing"</div>
            <div className={styles.contextText}>Reminder: "AI agents should verify patterns"</div>
          </div>

          <div className={styles.probabilitiesBox}>
            <div className={styles.probability}>
              <span className={styles.probLabel}>Probability of querying standards:</span>
              <span className={`${styles.probValue} ${styles.probValueGood}`}>85%</span>
            </div>
            <div className={styles.probability}>
              <span className={styles.probLabel}>Probability of guessing:</span>
              <span className={styles.probValue}>15%</span>
            </div>
          </div>

          <div className={`${styles.resultBox} ${styles.resultGood}`}>
            <div className={styles.resultLabel}>Result:</div>
            <div className={styles.resultText}>Likely queries, gets correct pattern</div>
          </div>
        </div>
      </div>

      <div className={styles.insight}>
        <strong>Key Insight:</strong> Each query changes the statistical distribution of the next decision by injecting high-relevance behavioral tokens into recent context.
      </div>
    </div>
  );
}

