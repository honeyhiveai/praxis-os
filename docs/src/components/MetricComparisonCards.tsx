import React from 'react';
import styles from './MetricComparisonCards.module.css';

interface Metric {
  label: string;
  september: string;
  october: string;
  change: string;
  isPositive: boolean;
}

interface MetricCardProps {
  label: string;
  september: string;
  october: string;
  change: string;
  isPositive: boolean;
}

const MetricCard: React.FC<MetricCardProps> = ({ label, september, october, change, isPositive }) => (
  <div className={styles.metricCard}>
    <div className={styles.metricLabel}>{label}</div>
    <div className={styles.metricValues}>
      <div className={styles.valueColumn}>
        <div className={styles.valueLabel}>Sept 2025</div>
        <div className={styles.valueNumber}>{september}</div>
      </div>
      <div className={styles.arrow}>→</div>
      <div className={styles.valueColumn}>
        <div className={styles.valueLabel}>Oct 2025</div>
        <div className={styles.valueNumber}>{october}</div>
      </div>
    </div>
    <div className={`${styles.change} ${isPositive ? styles.changePositive : styles.changeNegative}`}>
      {change}
    </div>
  </div>
);

interface MetricComparisonCardsProps {
  metrics?: Metric[];
}

export default function MetricComparisonCards({ metrics }: MetricComparisonCardsProps): React.ReactElement {
  // Default to billing data if no metrics provided
  const defaultMetrics: Metric[] = [
    {
      label: "API Calls",
      september: "6,353",
      october: "4,850",
      change: "-23.7%",
      isPositive: true
    },
    {
      label: "Total Tokens",
      september: "9.2B",
      october: "2.6B",
      change: "-72.1%",
      isPositive: true
    },
    {
      label: "Cost",
      september: "$3,954.52",
      october: "$1,824.19",
      change: "-53.9%",
      isPositive: true
    }
  ];

  const data = metrics || defaultMetrics;

  return (
    <div className={styles.container}>
      {data.map((metric) => (
        <MetricCard
          key={metric.label}
          label={metric.label}
          september={metric.september}
          october={metric.october}
          change={metric.change}
          isPositive={metric.isPositive}
        />
      ))}
    </div>
  );
}

