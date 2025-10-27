import React from 'react';
import styles from './MCPArchitectureDiagram.module.css';

export default function MCPArchitectureDiagram(): React.ReactElement {
  return (
    <div className={styles.container}>
      {/* Cursor AI Agent - Top */}
      <div className={styles.topBox}>
        <div className={styles.boxTitle}>Cursor AI Agent</div>
        <div className={styles.boxSubtitle}>Claude, GPT-4, etc. via MCP client</div>
      </div>

      <div className={styles.connector}>
        <div className={styles.connectorLabel}>MCP Protocol</div>
        <div className={styles.arrow}>↓</div>
      </div>

      {/* MCP Server - Main Container */}
      <div className={styles.serverBox}>
        <div className={styles.serverTitle}>MCP Server (stdio transport)</div>
        
        {/* Tool Registry */}
        <div className={styles.registryBox}>
          <div className={styles.registryTitle}>Tool Registry</div>
          <div className={styles.toolList}>
            <div className={styles.tool}>• search_standards</div>
            <div className={styles.tool}>• start_workflow</div>
            <div className={styles.tool}>• complete_phase</div>
            <div className={styles.tool}>• get_workflow_state</div>
          </div>
        </div>

        {/* Engines Row */}
        <div className={styles.enginesRow}>
          <div className={styles.engineBox}>
            <div className={styles.engineTitle}>RAG Engine</div>
            <div className={styles.featureList}>
              <div className={styles.feature}>• Vector search</div>
              <div className={styles.feature}>• Chunking</div>
              <div className={styles.feature}>• Embeddings</div>
            </div>
          </div>

          <div className={styles.engineBox}>
            <div className={styles.engineTitle}>Workflow Engine</div>
            <div className={styles.featureList}>
              <div className={styles.feature}>• Phase gating</div>
              <div className={styles.feature}>• State mgmt</div>
              <div className={styles.feature}>• Checkpoints</div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Storage Boxes */}
      <div className={styles.storageRow}>
        <div className={styles.storageBox}>
          <div className={styles.storageTitle}>📁 .praxis-os/</div>
          <div className={styles.storagePath}>universal/</div>
          <div className={styles.storagePath}>standards/</div>
          <div className={styles.storagePath}>.cache/vector_index</div>
        </div>

        <div className={styles.storageBox}>
          <div className={styles.storageTitle}>📁 .praxis-os/</div>
          <div className={styles.storagePath}>state/</div>
          <div className={styles.storagePath}>session_*.json</div>
          <div className={styles.storagePath}>.lock</div>
        </div>
      </div>
    </div>
  );
}

