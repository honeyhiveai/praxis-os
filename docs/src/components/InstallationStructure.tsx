import React from 'react';
import styles from './InstallationStructure.module.css';

export default function InstallationStructure(): React.ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.structure}>
        <div className={styles.rootDir}>
          <span className={styles.dirIcon}>📁</span>
          <span className={styles.dirName}>your-project/</span>
        </div>
        
        <div className={styles.children}>
          {/* .cursorrules file */}
          <div className={styles.item}>
            <span className={styles.fileIcon}>📄</span>
            <span className={styles.itemName}>.cursorrules</span>
            <span className={styles.itemDesc}># AI behavioral triggers (27 lines)</span>
          </div>

          {/* .agent-os directory */}
          <div className={styles.mainDir}>
            <span className={styles.dirIcon}>📂</span>
            <span className={styles.dirName}>.agent-os/</span>
          </div>
          <div className={styles.subChildren}>
            <div className={styles.subDir}>
              <span className={styles.fileIcon}>📁</span>
              <span className={styles.itemName}>standards/</span>
            </div>
            <div className={styles.subSubChildren}>
              <div className={styles.item}>
                <span className={styles.fileIcon}>📁</span>
                <span className={styles.itemName}>universal/</span>
                <span className={styles.itemDesc}># Timeless CS fundamentals</span>
              </div>
              <div className={styles.item}>
                <span className={styles.fileIcon}>📁</span>
                <span className={styles.itemName}>development/</span>
                <span className={styles.itemDesc}># Language-specific guidance</span>
              </div>
            </div>
            <div className={styles.item}>
              <span className={styles.fileIcon}>📁</span>
              <span className={styles.itemName}>mcp_server/</span>
              <span className={styles.itemDesc}># MCP/RAG server</span>
            </div>
            <div className={styles.item}>
              <span className={styles.fileIcon}>📁</span>
              <span className={styles.itemName}>.cache/vector_index/</span>
              <span className={styles.itemDesc}># Semantic search index</span>
            </div>
          </div>

          {/* .cursor directory */}
          <div className={styles.mainDir}>
            <span className={styles.dirIcon}>📂</span>
            <span className={styles.dirName}>.cursor/</span>
          </div>
          <div className={styles.subChildren}>
            <div className={styles.item}>
              <span className={styles.fileIcon}>📄</span>
              <span className={styles.itemName}>mcp.json</span>
              <span className={styles.itemDesc}># MCP configuration</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

