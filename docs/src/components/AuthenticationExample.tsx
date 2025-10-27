import React from 'react';
import styles from './AuthenticationExample.module.css';

export default function AuthenticationExample(): React.ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.title}>Example: Implementing Authentication API</div>
      
      {/* Layer 1 */}
      <div className={styles.layer}>
        <div className={styles.layerHeader}>
          <span className={styles.layerBadge}>Layer 1</span>
          <span className={styles.layerTitle}>RAG - Response Quality</span>
        </div>
        <div className={styles.layerContent}>
          <div className={styles.flow}>
            <div className={styles.flowItem}>
              <span className={styles.flowLabel}>User:</span>
              <span className={styles.flowText}>"Implement authentication"</span>
            </div>
            <div className={styles.flowArrow}>↓</div>
            <div className={styles.flowItem}>
              <span className={styles.flowLabel}>AI:</span>
              <code className={styles.code}>search_standards("authentication security requirements")</code>
            </div>
            <div className={styles.flowArrow}>↓</div>
            <div className={styles.flowItem}>
              <span className={styles.flowLabel}>Retrieved:</span>
              <span className={styles.flowText}>"Use JWT with 15-min expiry, bcrypt for passwords, rate limiting"</span>
            </div>
            <div className={styles.flowArrow}>↓</div>
            <div className={styles.flowItem}>
              <span className={styles.flowLabel}>AI Response:</span>
              <span className={styles.flowText}>Implementation following project security standards</span>
            </div>
          </div>
        </div>
      </div>

      {/* Layer 2 */}
      <div className={styles.layer}>
        <div className={styles.layerHeader}>
          <span className={styles.layerBadge}>Layer 2</span>
          <span className={styles.layerTitle}>Workflow - Systematic Execution</span>
        </div>
        <div className={styles.layerContent}>
          <div className={styles.phases}>
            <div className={styles.phase}>
              <div className={styles.phaseTitle}>Phase 1: Analysis</div>
              <div className={styles.phaseDetails}>
                <div className={styles.phaseItem}>├── AI queries: <code className={styles.code}>search_standards("authentication patterns")</code></div>
                <div className={styles.phaseItem}>├── Evidence: Security requirements documented</div>
                <div className={styles.phaseItem}>└── Gate: Pass ✓</div>
              </div>
            </div>
            
            <div className={styles.phase}>
              <div className={styles.phaseTitle}>Phase 2: Design</div>
              <div className={styles.phaseDetails}>
                <div className={styles.phaseItem}>├── AI plans: JWT structure, endpoints, error handling</div>
                <div className={styles.phaseItem}>├── Evidence: Architecture diagram, API contracts</div>
                <div className={styles.phaseItem}>└── Gate: Pass ✓</div>
              </div>
            </div>
            
            <div className={styles.phase}>
              <div className={styles.phaseTitle}>Phase 3: Implementation</div>
              <div className={styles.phaseDetails}>
                <div className={styles.phaseItem}>├── AI generates: Code + tests + docs</div>
                <div className={styles.phaseItem}>├── Evidence: Files created, tests written</div>
                <div className={styles.phaseItem}>└── Gate: Pass ✓</div>
              </div>
            </div>
            
            <div className={styles.phase}>
              <div className={styles.phaseTitle}>Phase 4: Validation</div>
              <div className={styles.phaseDetails}>
                <div className={styles.phaseItem}>├── AI runs: Pylint, MyPy, pytest</div>
                <div className={styles.phaseItem}>├── Evidence: 10.0/10 Pylint, 0 errors, tests green</div>
                <div className={styles.phaseItem}>└── Gate: Pass ✓</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Layer 3 */}
      <div className={styles.layer}>
        <div className={styles.layerHeader}>
          <span className={styles.layerBadge}>Layer 3</span>
          <span className={styles.layerTitle}>Pre-commit - Final Validation</span>
        </div>
        <div className={styles.layerContent}>
          <div className={styles.precommit}>
            <div className={styles.command}>
              <code className={styles.code}>$ git commit -m "Implement authentication API"</code>
            </div>
            <div className={styles.flowArrow}>↓</div>
            <div className={styles.precommitTitle}>Pre-commit hook runs:</div>
            <div className={styles.checks}>
              <div className={styles.check}>├── Formatting check: ✓ Pass</div>
              <div className={styles.check}>├── Linting check: ✓ Pass (10.0/10 Pylint)</div>
              <div className={styles.check}>├── Type checking: ✓ Pass (0 MyPy errors)</div>
              <div className={styles.check}>├── Unit tests: ✓ Pass (100%)</div>
              <div className={styles.check}>├── Integration tests: ✓ Pass (real API tested)</div>
              <div className={styles.check}>└── Documentation: ✓ Pass (sync validated)</div>
            </div>
            <div className={styles.flowArrow}>↓</div>
            <div className={styles.result}>
              <strong>Commit succeeds</strong> → Code is production-ready
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

