import React from 'react';
import styles from './MCPSubstrateStack.module.css';

export default function MCPSubstrateStack(): React.ReactElement {
  return (
    <div className={styles.container}>
      {/* Agent Layer */}
      <div className={styles.layer}>
        <div className={styles.layerTitle}>
          <span className={styles.icon}>🤖</span>
          Your Coding Agent
        </div>
        <div className={styles.layerSubtitle}>
          (Cursor, Claude, Cline, etc.)
        </div>
      </div>

      {/* Connector */}
      <div className={styles.connector}>
        <div className={styles.connectorLabel}>MCP Protocol</div>
        <span className={styles.arrow}>↓</span>
      </div>

      {/* MCP Server Layer */}
      <div className={styles.layer}>
        <div className={styles.layerTitle}>
          <span className={styles.icon}>⚙️</span>
          prAxIs OS MCP Server
        </div>
        <div className={styles.layerFeatures}>
          <div className={styles.feature}>├─ pos_search_project</div>
          <div className={styles.feature}>│  ├─ Multi-repo semantic</div>
          <div className={styles.feature}>│  ├─ Call graph traversal</div>
          <div className={styles.feature}>│  └─ AST pattern search</div>
          <div className={styles.feature}>├─ pos_workflow</div>
          <div className={styles.feature}>│  ├─ Phase-gated execution</div>
          <div className={styles.feature}>│  └─ Evidence validation</div>
          <div className={styles.feature}>└─ Standards (RAG indexed)</div>
        </div>
      </div>

      {/* Connector */}
      <div className={styles.connector}>
        <span className={styles.arrow}>↓</span>
      </div>

      {/* Project Layer */}
      <div className={styles.layer}>
        <div className={styles.layerTitle}>
          <span className={styles.icon}>📁</span>
          Your Project
        </div>
        <div className={styles.layerFeatures}>
          <div className={styles.feature}>└─ .praxis-os/</div>
          <div className={styles.feature}>   ├─ standards/ (searchable)</div>
          <div className={styles.feature}>   ├─ workflows/ (enforced)</div>
          <div className={styles.feature}>   └─ .cache/ (indexes)</div>
        </div>
      </div>
    </div>
  );
}

