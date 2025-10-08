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
            <h3>🏗️ The Starting Point: A Refactor Goal</h3>
            <p>
              It started with a simple goal: refactor the HoneyHive Python SDK with <strong>AI as the code author</strong>, 
              not just an assistant. As someone new to the AI development space, I looked for ways to improve the quality 
              and consistency of AI-generated code.
            </p>

            <h3>💡 Discovery: BuilderMethods Agent OS</h3>
            <p>
              I discovered{' '}
              <a href="https://buildermethods.com/agent-os" target="_blank" rel="noopener noreferrer" className={styles.journeyLink}>
                BuilderMethods Agent OS
              </a>
              —a 3-layer documentation structure (Standards/Product/Specs) that provided a systematic way to organize 
              development context. Using <code>.cursorrules</code> for side-loaded context and discovery flows via READMEs 
              in <code>.agent-os/standards</code>, <strong>quality and velocity dramatically improved</strong>. 
              This enabled the initial workflow/framework methodology to emerge.
            </p>

            <h3>📈 Success... Then New Problems</h3>
            <p>
              The side-loaded context approach worked brilliantly—until it didn't. As we built more sophisticated 
              workflows and richer standards:
            </p>
            <ul className={styles.journeyList}>
              <li><strong>Diminishing Returns</strong>: More context didn't mean better output</li>
              <li><strong>Cost Explosion</strong>: Context windows ballooning to 50KB+ per request</li>
              <li><strong>AI Confusion</strong>: Too much context actually degraded quality (only 4% relevant)</li>
              <li><strong>No Persistence</strong>: Complex workflows lost when conversations restarted</li>
              <li><strong>No Enforcement</strong>: AI still skipping steps despite better documentation</li>
            </ul>

            <h3>🚀 The Infrastructure Evolution</h3>
            <p>
              Out of necessity, we built the infrastructure layer:
            </p>
            <ul className={styles.journeyList}>
              <li><strong>MCP + RAG Server</strong>: Semantic search reducing context from 50KB→2-5KB (90% reduction), solving the cost and confusion problems</li>
              <li><strong>Structured Workflows</strong>: Test generation V3 (65 phase files), production code V2—systematic, repeatable frameworks</li>
              <li><strong>Persistent State</strong>: Session files surviving restarts and conversation breaks</li>
              <li><strong>Architectural Gating</strong>: Code-enforced checkpoints preventing AI shortcuts</li>
              <li><strong>Operating Model</strong>: Formalizing "AI as author" with clear roles (human: direction, AI: 100% implementation)</li>
              <li><strong>Observability</strong>: HoneyHive tracing dogfooded on itself</li>
            </ul>
            <p>
              Research documented:{' '}
              <a href="https://honeyhiveai.github.io/python-sdk/development/agent-os-mcp-server.html" target="_blank" rel="noopener noreferrer" className={styles.journeyLink}>
                LLM Workflow Engineering Methodology
              </a>
            </p>

            <h3>📦 The Extraction: Agent OS Enhanced</h3>
            <p>
              After proving these patterns in production SDK development (<strong>2,777 tests, 10.0/10 Pylint, 
              AI-authored: 2,500+ lines (100%), human-authored: 0 lines (0%)</strong>), we extracted the platform. 
              Agent OS Enhanced transforms BuilderMethods' conceptual foundation into a complete AI development platform 
              with enforcement, state management, and the infrastructure needed for production-grade AI authorship.
            </p>

            <h3>🙏 Standing on Giants</h3>
            <p>
              BuilderMethods provided the <strong>3-layer structure</strong> and philosophical foundation that made 
              the initial breakthrough possible. Everything built on top—MCP+RAG, workflows, state management, enforcement, 
              the operating model—emerged from solving real problems during production SDK development. 
              They showed the path; we built the infrastructure to scale it.
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
        <TheJourney />
        <QuickStart />
        <KeyFeatures />
        <WhyAgentOS />
      </main>
    </Layout>
  );
}
