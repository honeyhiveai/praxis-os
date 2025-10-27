import React from 'react';
import styles from './ParadigmComparison.module.css';

export default function ParadigmComparison(): React.ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.comparison}>
        {/* Approach 1: Stochastic */}
        <div className={styles.approach}>
          <div className={styles.approachHeader}>
            <h3 className={styles.approachTitle}>Approach 1: Prompt Optimization</h3>
            <span className={styles.badge}>Stochastic</span>
          </div>
          
          <div className={styles.section}>
            <h4 className={styles.sectionTitle}>Model:</h4>
            <div className={styles.model}>
              <code>Given prompt P, AI produces output O with probability distribution D.</code>
              <code>Goal: Tune P to maximize P(O = correct)</code>
            </div>
          </div>

          <div className={styles.section}>
            <h4 className={styles.sectionTitle}>Method:</h4>
            <ul className={styles.list}>
              <li>Run prompt 100 times</li>
              <li>Measure response variance</li>
              <li>Optimize prompt/temperature/examples</li>
              <li>Target: 95%+ probability of correct output</li>
            </ul>
          </div>

          <div className={styles.section}>
            <h4 className={styles.sectionTitle}>When it makes sense:</h4>
            <ul className={styles.list}>
              <li className={styles.pro}>✅ Single-shot tasks (chat responses, code completion)</li>
              <li className={styles.pro}>✅ Well-defined, narrow problems</li>
              <li className={styles.pro}>✅ Real-time requirements (low latency critical)</li>
            </ul>
          </div>

          <div className={styles.section}>
            <h4 className={styles.sectionTitle}>Limitations:</h4>
            <ul className={styles.list}>
              <li className={styles.con}>❌ Each task needs new tuning</li>
              <li className={styles.con}>❌ Model updates break prompts</li>
              <li className={styles.con}>❌ 95% success = 5% production failures</li>
            </ul>
          </div>
        </div>

        {/* Approach 2: Deterministic */}
        <div className={`${styles.approach} ${styles.approachPreferred}`}>
          <div className={styles.approachHeader}>
            <h3 className={styles.approachTitle}>Approach 2: System Design</h3>
            <span className={`${styles.badge} ${styles.badgePreferred}`}>Deterministic Constraints</span>
          </div>
          
          <div className={styles.section}>
            <h4 className={styles.sectionTitle}>Model:</h4>
            <div className={styles.model}>
              <code>Given framework F and goal G, constrain AI behavior B to achieve G.</code>
              <code>Goal: Design F such that B consistently produces high-quality outcomes</code>
            </div>
          </div>

          <div className={styles.section}>
            <h4 className={styles.sectionTitle}>Method:</h4>
            <ul className={styles.list}>
              <li>Build systematic framework (phase gating, quality gates, evidence requirements)</li>
              <li>Inject framework continuously (RAG, side-loaded context)</li>
              <li>Constrain behavior (automated validation, pre-commit hooks)</li>
              <li>Measure product outcomes (Pylint, MyPy, test pass rates)</li>
            </ul>
          </div>

          <div className={styles.section}>
            <h4 className={styles.sectionTitle}>When it makes sense:</h4>
            <ul className={styles.list}>
              <li className={styles.pro}>✅ Complex, multi-phase workflows</li>
              <li className={styles.pro}>✅ Sustained quality requirements</li>
              <li className={styles.pro}>✅ Enterprise-grade deliverables</li>
              <li className={styles.pro}>✅ Objective quality metrics</li>
            </ul>
          </div>

          <div className={styles.section}>
            <h4 className={styles.sectionTitle}>Advantages:</h4>
            <ul className={styles.list}>
              <li className={styles.pro}>✅ Framework scales across tasks</li>
              <li className={styles.pro}>✅ Model-agnostic (works with any LLM)</li>
              <li className={styles.pro}>✅ Quality guaranteed by gates (not probabilistic)</li>
            </ul>
          </div>
        </div>
      </div>

      <div className={styles.summary}>
        <div className={styles.summaryTitle}>Combined Result: Deterministic Quality</div>
        <div className={styles.summaryComparison}>
          <div className={styles.summaryItem}>
            <span className={styles.summaryLabel}>Traditional:</span>
            <span className={styles.summaryFormula}>Good prompt × Probabilistic AI = Variable quality</span>
          </div>
          <div className={`${styles.summaryItem} ${styles.summaryItemPreferred}`}>
            <span className={styles.summaryLabel}>Agent OS:</span>
            <span className={styles.summaryFormula}>Any prompt × Three-layer system = Consistent quality</span>
          </div>
        </div>
        <div className={styles.summaryTagline}>
          <strong>We don't optimize prompts. We build systems that guarantee outcomes.</strong>
        </div>
      </div>
    </div>
  );
}

