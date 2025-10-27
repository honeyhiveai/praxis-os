import React from 'react';
import styles from './ThreeLayerSystem.module.css';

export default function ThreeLayerSystem(): React.ReactElement {
  return (
    <div className={styles.container}>
      {/* Layer 1: RAG */}
      <div className={styles.layer}>
        <div className={styles.layerHeader}>
          <span className={styles.layerBadge}>Layer 1</span>
          <span className={styles.layerTitle}>RAG Behavioral Reinforcement</span>
        </div>
        <div className={styles.layerContent}>
          <div className={styles.flow}>
            <div className={styles.flowStep}>User prompt: "Implement authentication"</div>
            <div className={styles.flowArrow}>↓</div>
            <div className={styles.flowStep}>AI queries: <code>search_standards("authentication API design")</code></div>
            <div className={styles.flowArrow}>↓</div>
            <div className={styles.flowStep}>Retrieved: Project standards, security requirements, examples</div>
            <div className={styles.flowArrow}>↓</div>
            <div className={styles.flowStep}>AI response: Informed by project-specific context</div>
          </div>
        </div>
      </div>

      {/* Layer 2: Workflow */}
      <div className={styles.layer}>
        <div className={styles.layerHeader}>
          <span className={styles.layerBadge}>Layer 2</span>
          <span className={styles.layerTitle}>Workflow Execution with Phase Gating</span>
        </div>
        <div className={styles.layerContent}>
          <div className={styles.phases}>
            <div className={styles.phase}>
              <div className={styles.phaseTitle}>Phase 1: Requirements Analysis</div>
              <div className={styles.phaseGate}>└── Gate: Must query standards, document understanding</div>
            </div>
            <div className={styles.phase}>
              <div className={styles.phaseTitle}>Phase 2: Design Planning</div>
              <div className={styles.phaseGate}>└── Gate: Must show architecture, identify dependencies</div>
            </div>
            <div className={styles.phase}>
              <div className={styles.phaseTitle}>Phase 3: Implementation</div>
              <div className={styles.phaseGate}>└── Gate: Must provide code, tests, documentation</div>
            </div>
            <div className={styles.phase}>
              <div className={styles.phaseTitle}>Phase 4: Validation</div>
              <div className={styles.phaseGate}>└── Gate: Must show Pylint 10.0, MyPy 0 errors, tests passing</div>
            </div>
          </div>
        </div>
      </div>

      {/* Layer 3: Pre-commit */}
      <div className={styles.layer}>
        <div className={styles.layerHeader}>
          <span className={styles.layerBadge}>Layer 3</span>
          <span className={styles.layerTitle}>Pre-commit Validation</span>
        </div>
        <div className={styles.layerContent}>
          <div className={styles.gates}>
            <div className={styles.gatesTitle}>Pre-commit runs automatically on <code>git commit</code>:</div>
            <div className={styles.gatesList}>
              <div className={styles.gateItem}>1. YAML validation</div>
              <div className={styles.gateItem}>2. No mocks in integration tests</div>
              <div className={styles.gateItem}>3. Code formatting (Black + isort)</div>
              <div className={styles.gateItem}>4. Code quality (Pylint + MyPy)</div>
              <div className={styles.gateItem}>5. Unit tests (100% pass required)</div>
              <div className={styles.gateItem}>6. Integration tests (real APIs)</div>
              <div className={styles.gateItem}>7. Documentation build</div>
              <div className={styles.gateItem}>8. Documentation navigation</div>
              <div className={styles.gateItem}>9. Feature documentation sync</div>
              <div className={styles.gateItem}>10. Documentation compliance</div>
              <div className={styles.gateItem}>11. Invalid pattern prevention</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

