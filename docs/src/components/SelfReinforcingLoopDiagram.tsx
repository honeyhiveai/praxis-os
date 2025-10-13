import React from 'react';
import styles from './SelfReinforcingLoopDiagram.module.css';

export default function SelfReinforcingLoopDiagram(): React.ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.loopFlow}>
        <div className={styles.step}>
          <div className={styles.stepNumber}>1</div>
          <div className={styles.stepText}>Content teaches "query for guidance"</div>
        </div>

        <div className={styles.arrow}>↓</div>

        <div className={styles.step}>
          <div className={styles.stepNumber}>2</div>
          <div className={styles.stepText}>Agent queries and finds helpful content</div>
        </div>

        <div className={styles.arrow}>↓</div>

        <div className={styles.step}>
          <div className={styles.stepNumber}>3</div>
          <div className={styles.stepText}>Content reinforces "query liberally" message</div>
        </div>

        <div className={styles.arrow}>↓</div>

        <div className={styles.step}>
          <div className={styles.stepNumber}>4</div>
          <div className={styles.stepText}>Agent queries more frequently</div>
        </div>

        <div className={styles.arrow}>↓</div>

        <div className={styles.step}>
          <div className={styles.stepNumber}>5</div>
          <div className={styles.stepText}>More queries = more reinforcement = stronger pattern</div>
        </div>

        <div className={styles.arrow}>↓</div>

        <div className={styles.resultBox}>
          <div className={styles.resultIcon}>✓</div>
          <div className={styles.resultText}>Querying becomes default behavior</div>
        </div>

        <div className={styles.loopBack}>
          <div className={styles.loopArrow}>↻</div>
          <div className={styles.loopLabel}>Cycle continues</div>
        </div>
      </div>

      <div className={styles.whyBox}>
        <div className={styles.whyTitle}>Why This Works:</div>
        <ul className={styles.whyList}>
          <li>Each query retrieves the "query more" message</li>
          <li>Repeated exposure strengthens the pattern</li>
          <li>Pattern becomes self-sustaining through repetition</li>
          <li>Works <strong>with</strong> AI's probabilistic nature, not against it</li>
        </ul>
      </div>
    </div>
  );
}

