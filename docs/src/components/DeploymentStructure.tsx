import React from 'react';
import styles from './DeploymentStructure.module.css';

export default function DeploymentStructure(): React.ReactElement {
  return (
    <div className={styles.container}>
      <div className={styles.structure}>
        <div className={styles.rootDir}>
          <span className={styles.dirIcon}>📁</span>
          <span className={styles.dirName}>my-project/</span>
        </div>
        
        <div className={styles.children}>
          {/* .agent-os directory */}
          <div className={styles.mainDir}>
            <span className={styles.dirIcon}>📂</span>
            <span className={styles.dirName}>.agent-os/</span>
          </div>
          <div className={styles.subChildren}>
            <div className={styles.item}>
              <span className={styles.fileIcon}>📁</span>
              <span className={styles.itemName}>mcp_server/</span>
              <span className={styles.itemDesc}># Complete server copy</span>
            </div>
            <div className={styles.item}>
              <span className={styles.fileIcon}>📁</span>
              <span className={styles.itemName}>universal/</span>
              <span className={styles.itemDesc}># Standard library</span>
            </div>
            <div className={styles.item}>
              <span className={styles.fileIcon}>📁</span>
              <span className={styles.itemName}>standards/</span>
              <span className={styles.itemDesc}># Generated for this project</span>
            </div>
            <div className={styles.item}>
              <span className={styles.fileIcon}>📁</span>
              <span className={styles.itemName}>workflows/</span>
              <span className={styles.itemDesc}># Available workflows</span>
            </div>
            <div className={styles.item}>
              <span className={styles.fileIcon}>📁</span>
              <span className={styles.itemName}>specs/</span>
              <span className={styles.itemDesc}># Project-specific specs</span>
            </div>
            <div className={styles.item}>
              <span className={styles.fileIcon}>📁</span>
              <span className={styles.itemName}>state/</span>
              <span className={styles.itemDesc}># Workflow state</span>
            </div>
            <div className={styles.item}>
              <span className={styles.fileIcon}>📁</span>
              <span className={styles.itemName}>.cache/</span>
              <span className={styles.itemDesc}># Vector index</span>
            </div>
          </div>

          {/* Other project files */}
          <div className={styles.item}>
            <span className={styles.fileIcon}>📄</span>
            <span className={styles.itemName}>pyproject.toml</span>
            <span className={styles.itemDesc}># Project dependencies</span>
          </div>
          <div className={styles.item}>
            <span className={styles.fileIcon}>📁</span>
            <span className={styles.itemName}>src/</span>
            <span className={styles.itemDesc}># Project code</span>
          </div>
        </div>
      </div>
    </div>
  );
}

