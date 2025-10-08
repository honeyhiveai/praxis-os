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
              Agent OS Enhanced
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
                to="/docs/intro">
                Get Started →
              </Link>
              <Link
                className="button button--secondary button--lg"
                to="/docs/installation">
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
                <span className={styles.codeTitle}>Install Agent OS</span>
              </div>
              <div className={styles.codeBody}>
                <pre>
{`# Open your project in Cursor and say:

"Install Agent OS from 
 github.com/honeyhiveai/agent-os-enhanced"

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
      link: '/docs/intro',
    },
    {
      icon: '📚',
      title: 'Core Concepts',
      description: 'Understand MCP, RAG, and phase gating',
      link: '/docs/how-it-works',
    },
    {
      icon: '⚙️',
      title: 'Installation',
      description: 'Detailed setup and configuration guide',
      link: '/docs/installation',
    },
    {
      icon: '🔧',
      title: 'Workflows',
      description: 'Learn about spec creation and execution',
      link: '/docs/workflows',
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
      link: '/docs/architecture',
    },
    {
      icon: '📖',
      title: 'Universal Standards',
      description: 'Timeless CS fundamentals that work across any language with smart generation.',
      link: '/docs/standards',
    },
    {
      icon: '🔒',
      title: 'Architectural Phase Gating',
      description: 'Workflows enforced in code. AI cannot skip phases or bypass quality gates.',
      link: '/docs/workflows',
    },
    {
      icon: '🤖',
      title: 'Specialized Sub-Agents',
      description: 'Design validation, concurrency analysis, test generation - focused tools.',
      link: '/docs/architecture',
    },
    {
      icon: '📦',
      title: 'Portable & Isolated',
      description: 'Each project owns its Agent OS installation, standards, and version.',
      link: '/docs/installation',
    },
    {
      icon: '🛠️',
      title: 'Meta-Framework System',
      description: 'Build your own AI-assisted workflows with proven patterns.',
      link: '/docs/workflows',
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
  return (
    <section className={styles.journeySection}>
      <div className="container">
        <div className={styles.sectionHeader}>
          <Heading as="h2">The Journey</Heading>
          <p>Built on the shoulders of giants</p>
        </div>
        <div className={styles.journeyContent}>
          <div className={styles.journeyStory}>
            <h3>🏗️ Built Upon Agent OS</h3>
            <p>
              Agent OS Enhanced is a fork of{' '}
              <a href="https://buildermethods.com/agent-os" target="_blank" rel="noopener noreferrer" className={styles.journeyLink}>
                BuilderMethods Agent OS
              </a>
              , the groundbreaking framework that pioneered structured AI development workflows.
            </p>
            
            <h3>🚀 Why Enhanced?</h3>
            <p>
              While building production systems at HoneyHive, we discovered patterns that pushed beyond the original vision:
            </p>
            <ul className={styles.journeyList}>
              <li><strong>MCP + RAG</strong>: Context reduction from 50KB→2-5KB (90% reduction)</li>
              <li><strong>Persistent State</strong>: Workflows survive MCP server restarts</li>
              <li><strong>Dynamic Loading</strong>: Zero-config workflow discovery</li>
              <li><strong>Architectural Gating</strong>: Code-enforced phase compliance</li>
              <li><strong>Production Observability</strong>: Full tracing and monitoring</li>
            </ul>

            <h3>🙏 Standing on Strong Foundations</h3>
            <p>
              The core principles—universal standards, spec-driven development, meta-framework patterns—
              all originate from BuilderMethods. Agent OS Enhanced extends these ideas for enterprise scale.
            </p>

            <div className={styles.journeyLinks}>
              <Link
                className="button button--secondary button--md"
                to="https://buildermethods.com/agent-os"
                target="_blank">
                Visit Original Agent OS →
              </Link>
              <Link
                className="button button--primary button--md"
                to="/docs/intro">
                Explore Enhanced Version →
              </Link>
            </div>
          </div>
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
          <Heading as="h2">Why Agent OS Enhanced?</Heading>
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
            to="/docs/how-it-works">
            Learn How It Works →
          </Link>
        </div>
      </div>
    </section>
  );
}

export default function Home(): JSX.Element {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title="Agent OS Enhanced"
      description="The open-source operating system for spec-driven development with AI coding agents">
      <HomepageHeader />
      <main>
        <QuickStart />
        <KeyFeatures />
        <TheJourney />
        <WhyAgentOS />
      </main>
    </Layout>
  );
}
