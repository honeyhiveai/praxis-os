import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={styles.heroBanner}>
      <div className="container">
        <div className={styles.heroContent}>
          <div className={styles.heroText}>
            <Heading as="h1" className={styles.heroTitle}>
              prAxIs OS
            </Heading>
            <p className={styles.heroSubtitle}>
              The open-source operating system for spec-driven development with AI coding agents
            </p>
            <p className={styles.heroDescription}>
              Transform AI from helpful assistant to velocity-enhancing partner. 
              Built with MCP, RAG, and architectural phase gating for production-ready results.
            </p>
            <div className={styles.heroButtons}>
              <Link
                className="button button--primary button--lg"
                to="/docs/tutorials/intro">
                Get Started →
              </Link>
              <Link
                className="button button--secondary button--lg"
                to="/docs/tutorials/installation">
                View Installation
              </Link>
            </div>
          </div>
          <div className={styles.heroVisual}>
            <div className={styles.codeExample}>
              <div className={styles.codeHeader}>
                <span className={styles.dot}></span>
                <span className={styles.dot}></span>
                <span className={styles.dot}></span>
                <span className={styles.codeTitle}>Install prAxIs OS</span>
              </div>
              <div className={styles.codeBody}>
                <pre>
{`# Open your project in Cursor and say:

"Install prAxIs OS from 
 github.com/honeyhiveai/praxis-os"

# The agent will:
✓ Analyze your project structure
✓ Copy universal standards  
✓ Install MCP server
✓ Configure everything automatically`}
                </pre>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

function QuickStart() {
  const steps = [
    {
      icon: '🚀',
      title: 'Quick Start',
      description: 'Install in your project with one command',
      link: '/docs/tutorials/intro',
    },
    {
      icon: '📚',
      title: 'Core Concepts',
      description: 'Understand MCP, RAG, and phase gating',
      link: '/docs/explanation/how-it-works',
    },
    {
      icon: '⚙️',
      title: 'Installation',
      description: 'Detailed setup and configuration guide',
      link: '/docs/tutorials/installation',
    },
    {
      icon: '🔧',
      title: 'Workflows',
      description: 'Learn about spec creation and execution',
      link: '/docs/reference/workflows',
    },
  ];

  return (
    <section className={styles.quickStart}>
      <div className="container">
        <div className={styles.sectionHeader}>
          <Heading as="h2">Get Started</Heading>
          <p>Everything you need to supercharge your AI development workflow</p>
        </div>
        <div className="row">
          {steps.map((step, idx) => (
            <div key={idx} className="col col--6 margin-bottom--lg">
              <Link to={step.link} className={styles.quickStartLink}>
                <div className={styles.quickStartCard}>
                  <div className={styles.quickStartIcon}>{step.icon}</div>
                  <h3>{step.title}</h3>
                  <p>{step.description}</p>
                  <span className={styles.quickStartArrow}>→</span>
                </div>
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function KeyFeatures() {
  const features = [
    {
      icon: '🎯',
      title: 'MCP/RAG Architecture',
      description: '90% context reduction. Semantic search delivers exactly what AI needs, nothing more.',
      link: '/docs/explanation/architecture',
    },
    {
      icon: '📖',
      title: 'Universal Standards',
      description: 'Timeless CS fundamentals that work across any language with smart generation.',
      link: '/docs/reference/standards',
    },
    {
      icon: '🔒',
      title: 'Architectural Phase Gating',
      description: 'Workflows enforced in code. AI cannot skip phases or bypass quality gates.',
      link: '/docs/reference/workflows',
    },
    {
      icon: '🤖',
      title: 'Specialized Sub-Agents',
      description: 'Design validation, concurrency analysis, test generation - focused tools.',
      link: '/docs/explanation/architecture',
    },
    {
      icon: '📦',
      title: 'Portable & Isolated',
      description: 'Each project owns its prAxIs OS installation, standards, and version.',
      link: '/docs/tutorials/installation',
    },
    {
      icon: '🛠️',
      title: 'Meta-Framework System',
      description: 'Build your own AI-assisted workflows with proven patterns.',
      link: '/docs/reference/workflows',
    },
  ];

  return (
    <section className={styles.features}>
      <div className="container">
        <div className={styles.sectionHeader}>
          <Heading as="h2">Core Features</Heading>
          <p>Production-ready AI development infrastructure</p>
        </div>
        <div className="row">
          {features.map((feature, idx) => (
            <div key={idx} className="col col--4">
              <Link to={feature.link} className={styles.featureCardLink}>
                <div className={styles.featureCard}>
                  <div className={styles.featureIcon}>{feature.icon}</div>
                  <h3>{feature.title}</h3>
                  <p>{feature.description}</p>
                </div>
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function TheJourney() {
  const milestones = [
    {
      icon: '🏗️',
      phase: 'Starting Point',
      title: 'Refactoring the HoneyHive Python SDK',
      description: 'Simple goal: AI as code author, not assistant',
      highlight: null,
    },
    {
      icon: '💡',
      phase: 'Discovery',
      title: 'Found BuilderMethods prAxIs OS',
      description: '3-layer doc structure (Standards/Product/Specs)',
      highlight: 'Quality and velocity dramatically improved',
    },
    {
      icon: '📈',
      phase: 'Scale Challenges',
      title: 'Side-loaded context hit limits',
      description: '50KB+ context windows, 4% relevance, no enforcement',
      highlight: 'Cost explosion + AI confusion',
    },
    {
      icon: '🚀',
      phase: 'Infrastructure Built',
      title: 'MCP + RAG + Workflows + State',
      description: '90% context reduction, phase gating, persistent sessions',
      highlight: '50KB → 2-5KB per request',
    },
    {
      icon: '📦',
      phase: 'Production Proven',
      title: 'Extracted prAxIs OS',
      description: '2,777 tests, 10.0/10 Pylint, 100% AI-authored',
      highlight: 'Complete AI development platform',
    },
  ];

  return (
    <section className={styles.journeySection}>
      <div className="container">
        <div className={styles.sectionHeader}>
          <Heading as="h2">The Journey</Heading>
          <p>From refactor goal to production AI platform</p>
        </div>
        
        <div className={styles.journeyTimeline}>
          {milestones.map((milestone, idx) => (
            <div key={idx} className={styles.timelineItem}>
              <div className={styles.timelineIcon}>{milestone.icon}</div>
              <div className={styles.timelineContent}>
                <div className={styles.timelinePhase}>{milestone.phase}</div>
                <h3 className={styles.timelineTitle}>{milestone.title}</h3>
                <p className={styles.timelineDescription}>{milestone.description}</p>
                {milestone.highlight && (
                  <div className={styles.timelineHighlight}>{milestone.highlight}</div>
                )}
              </div>
              {idx < milestones.length - 1 && <div className={styles.timelineConnector}></div>}
            </div>
          ))}
        </div>

        <div className={styles.journeyCredit}>
          <p>
            🙏 <strong>Built on the shoulders of giants:</strong>{' '}
            <a href="https://buildermethods.com/praxis-os" target="_blank" rel="noopener noreferrer" className={styles.journeyLink}>
              BuilderMethods prAxIs OS
            </a>
            {' '}provided the 3-layer structure and philosophical foundation. 
            We built the infrastructure to scale it.
          </p>
        </div>

        <div className={styles.journeyLinks}>
          <Link
            className="button button--secondary button--lg"
            to="https://buildermethods.com/praxis-os"
            target="_blank">
            Visit Original prAxIs OS →
          </Link>
          <Link
            className="button button--primary button--lg"
            to="/docs/tutorials/intro">
            Explore Enhanced Version →
          </Link>
        </div>
      </div>
    </section>
  );
}

function WhyAgentOS() {
  const benefits = [
    {
      stat: '90%',
      label: 'Context Reduction',
      description: 'RAG delivers 2-5KB targeted chunks vs 50KB files',
    },
    {
      stat: '24x',
      label: 'Better Relevance',
      description: 'From 4% to 95% relevant content in AI context',
    },
    {
      stat: '100%',
      label: 'Phase Compliance',
      description: 'Architectural gating prevents workflow bypassing',
    },
  ];

  return (
    <section className={styles.whySection}>
      <div className="container">
        <div className={styles.sectionHeader}>
          <Heading as="h2">Why prAxIs OS?</Heading>
          <p>Built on production lessons from real AI development challenges</p>
        </div>
        <div className="row">
          {benefits.map((benefit, idx) => (
            <div key={idx} className="col col--4">
              <div className={styles.statCard}>
                <div className={styles.statNumber}>{benefit.stat}</div>
                <div className={styles.statLabel}>{benefit.label}</div>
                <p className={styles.statDescription}>{benefit.description}</p>
              </div>
            </div>
          ))}
        </div>
        <div className="text--center margin-top--xl">
          <Link
            className="button button--primary button--lg"
            to="/docs/explanation/how-it-works">
            Learn How It Works →
          </Link>
        </div>
      </div>
    </section>
  );
}

export default function Home(): React.ReactElement {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title="prAxIs OS"
      description="The open-source operating system for spec-driven development with AI coding agents">
      <HomepageHeader />
      <main>
        <TheJourney />
        <QuickStart />
        <KeyFeatures />
        <WhyAgentOS />
      </main>
    </Layout>
  );
}
