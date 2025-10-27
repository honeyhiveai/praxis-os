import React from 'react';
import styles from './SessionEvolution.module.css';

interface StageProps {
  title: string;
  icon: string;
  content: string;
  color: string;
}

const Stage: React.FC<StageProps> = ({ title, icon, content, color }) => (
  <div className={styles.stage}>
    <div className={styles.stageIcon} style={{ borderColor: color }}>
      {icon}
    </div>
    <div className={styles.stageContent}>
      <div className={styles.stageTitle}>{title}</div>
      <pre className={styles.stageCode}>{content}</pre>
    </div>
  </div>
);

export default function SessionEvolution(): React.ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.title}>Meso-Praxis: Session Evolution</div>
      <div className={styles.subtitle}>
        Within a session, the AI learns from corrections
      </div>
      
      <div className={styles.timeline}>
        <Stage
          title="Early in Session"
          icon="🌱"
          content={`AI: "Creating file at workspace/feature.md"
Human: "No, use .agent-os/workspace/design/"`}
          color="var(--honeyhive-orange-border)"
        />
        
        <div className={styles.connector}>
          <div className={styles.connectorLine}></div>
          <div className={styles.connectorDot}></div>
        </div>
        
        <Stage
          title="Mid-Session"
          icon="🔍"
          content={`AI notices pattern, queries standards
AI: search_standards("workspace organization")
→ Discovers the standard`}
          color="var(--honeyhive-orange)"
        />
        
        <div className={styles.connector}>
          <div className={styles.connectorLine}></div>
          <div className={styles.connectorDot}></div>
        </div>
        
        <Stage
          title="Late in Session"
          icon="✅"
          content={`AI: "Creating at .agent-os/workspace/design/YYYY-MM-DD-feature.md"
Human: "Correct!"`}
          color="var(--honeyhive-orange)"
        />
        
        <div className={styles.connector}>
          <div className={styles.connectorLine}></div>
          <div className={styles.connectorDot}></div>
        </div>
        
        <Stage
          title="Post-Session"
          icon="🚀"
          content={`Next session: AI queries first, gets it right immediately`}
          color="var(--honeyhive-orange)"
        />
      </div>
      
      <div className={styles.insight}>
        Learning within a session transfers to future sessions through standards
      </div>
    </div>
  );
}

