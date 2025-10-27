import React from 'react';
import styles from './StandardsProgression.module.css';

interface SessionProps {
  number: number;
  query: string;
  result: string;
  outcome: string;
  color: string;
}

const Session: React.FC<SessionProps> = ({ number, query, result, outcome, color }) => (
  <div className={styles.session} style={{ borderLeftColor: color }}>
    <div className={styles.sessionHeader}>
      <div className={styles.sessionNumber} style={{ borderColor: color }}>
        Session {number}
      </div>
    </div>
    <div className={styles.sessionContent}>
      <div className={styles.block}>
        <div className={styles.label}>Query:</div>
        <pre className={styles.code}>
{`AI: search_standards("${query}")`}
        </pre>
      </div>
      <div className={styles.block}>
        <div className={styles.label}>Result:</div>
        <div className={styles.result}>{result}</div>
      </div>
      <div className={styles.block}>
        <div className={styles.label}>Outcome:</div>
        <div className={styles.outcome}>{outcome}</div>
      </div>
    </div>
  </div>
);

export default function StandardsProgression(): React.ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.title}>Just-in-Time Domain Expertise</div>
      <div className={styles.subtitle}>
        Standards are not generic advice. They're accumulated project-specific knowledge.
      </div>
      
      <div className={styles.sessions}>
        <Session
          number={1}
          query="API patterns"
          result="No results - implements ad-hoc"
          outcome='Human: "This works, let&apos;s capture as standard"'
          color="var(--honeyhive-orange-border)"
        />
        
        <div className={styles.arrow}>↓</div>
        
        <Session
          number={10}
          query="API patterns"
          result="Returns: Your project's API conventions"
          outcome="AI implements: Exactly per your standards"
          color="var(--honeyhive-orange)"
        />
        
        <div className={styles.arrow}>↓</div>
        
        <Session
          number={50}
          query="API rate limiting"
          result="Returns: Comprehensive standard with 20+ patterns"
          outcome="AI implements: Expert-level, first-time correct"
          color="var(--honeyhive-orange)"
        />
      </div>
      
      <div className={styles.insight}>
        <strong>The AI doesn't get smarter. The system does.</strong>
      </div>
      
      <div className={styles.features}>
        <div className={styles.feature}>
          <div className={styles.featureIcon}>⏱️</div>
          <div className={styles.featureText}>
            <strong>Queried exactly when needed</strong>
            <div>Just-in-time knowledge delivery</div>
          </div>
        </div>
        <div className={styles.feature}>
          <div className={styles.featureIcon}>🎯</div>
          <div className={styles.featureText}>
            <strong>Project-specific (not generic)</strong>
            <div>YOUR conventions, YOUR patterns</div>
          </div>
        </div>
        <div className={styles.feature}>
          <div className={styles.featureIcon}>📈</div>
          <div className={styles.featureText}>
            <strong>Accumulated over time</strong>
            <div>Every feature teaches the system</div>
          </div>
        </div>
        <div className={styles.feature}>
          <div className={styles.featureIcon}>🔄</div>
          <div className={styles.featureText}>
            <strong>Compounds with every feature</strong>
            <div>Learning builds on learning</div>
          </div>
        </div>
      </div>
    </div>
  );
}

