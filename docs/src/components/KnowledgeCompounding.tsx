import React from 'react';
import styles from './KnowledgeCompounding.module.css';

interface MilestoneProps {
  month: number;
  features: number;
  standards: number;
  description: string;
  color: string;
}

const Milestone: React.FC<MilestoneProps> = ({ month, features, standards, description, color }) => (
  <div className={styles.milestone}>
    <div className={styles.milestoneHeader} style={{ borderColor: color }}>
      <div className={styles.monthLabel}>Month {month}</div>
    </div>
    <div className={styles.milestoneContent}>
      <div className={styles.stats}>
        <div className={styles.stat}>
          <div className={styles.statValue}>{features}</div>
          <div className={styles.statLabel}>features</div>
        </div>
        <div className={styles.statArrow}>→</div>
        <div className={styles.stat}>
          <div className={styles.statValue}>{standards}</div>
          <div className={styles.statLabel}>standards</div>
        </div>
      </div>
      <div className={styles.description}>{description}</div>
    </div>
  </div>
);

export default function KnowledgeCompounding(): React.ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.title}>Macro-Praxis: Knowledge Compounding</div>
      <div className={styles.subtitle}>
        Across sessions, the system becomes a domain expert
      </div>
      
      <div className={styles.timeline}>
        <Milestone
          month={1}
          features={5}
          standards={5}
          description="Initial patterns captured"
          color="var(--honeyhive-orange-border)"
        />
        
        <div className={styles.arrow}>↓</div>
        
        <Milestone
          month={3}
          features={20}
          standards={35}
          description="Patterns refined and expanded"
          color="var(--honeyhive-orange)"
        />
        
        <div className={styles.arrow}>↓</div>
        
        <Milestone
          month={6}
          features={50}
          standards={95}
          description="Comprehensive domain expertise"
          color="var(--honeyhive-orange)"
        />
      </div>
      
      <div className={styles.insight}>
        <div className={styles.insightTitle}>Result:</div>
        <div className={styles.insightText}>
          AI that knows <strong>YOUR</strong> codebase, <strong>YOUR</strong> conventions, <strong>YOUR</strong> patterns.
        </div>
        <div className={styles.insightSubtext}>
          Not generic "best practices" but <strong>accumulated domain expertise</strong>.
        </div>
      </div>
      
      <div className={styles.progression}>
        <div className={styles.progressionBar}>
          <div className={styles.progressionFill} style={{ width: '100%' }}></div>
        </div>
        <div className={styles.progressionLabels}>
          <span>Generic AI</span>
          <span>→</span>
          <span>Project Expert</span>
        </div>
      </div>
    </div>
  );
}

