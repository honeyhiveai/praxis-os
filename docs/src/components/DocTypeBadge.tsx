import React from 'react';
import styles from './DocTypeBadge.module.css';

export type DocType = 'tutorial' | 'how-to' | 'reference' | 'explanation';

interface DocTypeBadgeProps {
  type: DocType;
}

const DOC_TYPE_CONFIG = {
  tutorial: {
    icon: '🎓',
    label: 'Tutorial',
    description: 'Learning-oriented: Takes you through a series of steps to complete a project',
    color: '#00b894',
  },
  'how-to': {
    icon: '📋',
    label: 'How-To Guide',
    description: 'Task-oriented: Guides you through steps to solve a specific problem',
    color: '#0984e3',
  },
  reference: {
    icon: '📚',
    label: 'Reference',
    description: 'Information-oriented: Technical descriptions of tools, APIs, and components',
    color: '#6c5ce7',
  },
  explanation: {
    icon: '💡',
    label: 'Explanation',
    description: 'Understanding-oriented: Clarifies and illuminates topics with background and context',
    color: '#fdcb6e',
  },
};

export default function DocTypeBadge({ type }: DocTypeBadgeProps): JSX.Element {
  const config = DOC_TYPE_CONFIG[type];

  if (!config) {
    return null;
  }

  return (
    <div className={styles.docTypeBadge} title={config.description}>
      <span className={styles.icon}>{config.icon}</span>
      <span className={styles.label}>{config.label}</span>
    </div>
  );
}

