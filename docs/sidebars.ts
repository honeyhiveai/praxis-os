import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

/**
 * prAxIs OS Documentation Sidebar
 * 
 * Organized by Divio Documentation Framework quadrants.
 */
const sidebars: SidebarsConfig = {
  tutorialSidebar: [
    // Tutorials - Learning-oriented
    {
      type: 'category',
      label: '🎓 Tutorials',
      collapsible: true,
      collapsed: false,
      items: [
        'tutorials/intro',
        'tutorials/installation',
        'tutorials/your-first-praxis-os-project',
        'tutorials/understanding-praxis-os-workflows',
        'tutorials/your-first-project-standard',
      ],
    },

    // How-To Guides - Task-oriented
    {
      type: 'category',
      label: '📋 How-To Guides',
      collapsible: true,
      items: [
        'how-to-guides/creating-project-standards',
        'how-to-guides/using-code-intelligence',
        'how-to-guides/create-custom-workflows',
        'how-to-guides/setup-quality-gates',
        'how-to-guides/debug-workflow-failures',
        'how-to-guides/upgrading',
        {
          type: 'category',
          label: '🤖 Agent Integrations',
          collapsible: true,
          collapsed: false,
          items: [
            'how-to-guides/agent-integrations/README',
            {
              type: 'category',
              label: 'Cursor',
              items: ['how-to-guides/agent-integrations/cursor/index'],
            },
            {
              type: 'category',
              label: 'Cline',
              items: [
                'how-to-guides/agent-integrations/cline/vscode',
                'how-to-guides/agent-integrations/cline/cursor',
              ],
            },
            {
              type: 'category',
              label: 'Claude Code',
              items: [
                'how-to-guides/agent-integrations/claude-code/vscode',
                'how-to-guides/agent-integrations/claude-code/terminal',
                'how-to-guides/agent-integrations/claude-code/cursor',
              ],
            },
            {
              type: 'category',
              label: 'GitHub Copilot',
              items: [
                'how-to-guides/agent-integrations/github-copilot/index',
              ],
            },
          ],
        },
      ],
    },

    // Explanation - Understanding-oriented
    {
      type: 'category',
      label: '💡 Explanation',
      collapsible: true,
      collapsed: true,
      items: [
        'explanation/passive-enhancement-model',
        'explanation/praxis',
        'explanation/how-it-works',
        'explanation/architecture',
        'explanation/code-intelligence',
        'explanation/adversarial-design',
        'explanation/measuring-outcomes-not-prompts',
        'explanation/knowledge-compounding',
        'explanation/standards-knowledge-compounding',
        'explanation/specs-knowledge-compounding',
        'explanation/economics',
      ],
    },
    
    // Reference - Information-oriented
    {
      type: 'category',
      label: '📚 Reference',
      collapsible: true,
      items: [
        'reference/mcp-tools',
        'reference/config-reference',
        'reference/workflows',
        'reference/standards',
      ],
    },
  ],
};

export default sidebars;
