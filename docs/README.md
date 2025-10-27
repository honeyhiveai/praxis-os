# prAxIs OS Documentation

This directory contains the Docusaurus-based documentation site for prAxIs OS.

## 🚀 Local Development

```bash
# Navigate to docs directory
cd docs

# Install dependencies (first time only)
npm install

# Start development server
npm start
```

This will open `http://localhost:3000` in your browser with live reload.

## 📁 Directory Structure

```
docs/
├── content/              # Markdown documentation files
├── blog/                 # Blog posts (case studies, updates)
├── src/
│   ├── components/       # React components for interactive elements
│   ├── pages/            # Custom pages (landing page, etc.)
│   └── css/              # Custom styling
├── static/               # Static assets (images, files)
├── docusaurus.config.ts  # Main configuration
└── sidebars.ts           # Sidebar navigation structure
```

## 📝 Working with Content

### Documentation Pages

Add/edit markdown files in `content/`:

```markdown
---
sidebar_position: 1
title: My Page
---

# My Page Content

Your content here...
```

### Blog Posts

Add markdown files to `blog/` with date prefix:

```
blog/2025-10-08-my-post.md
```

### Custom React Components

Create components in `src/components/` and use them in markdown with MDX:

```mdx
import MyComponent from '@site/src/components/MyComponent';

<MyComponent />
```

## 🏗️ Building for Production

```bash
# Build static site
npm run build

# Preview production build locally
npm run serve
```

## 🚀 Deployment

### Automatic (via GitHub Actions)

Pushes to `main` branch automatically trigger deployment to GitHub Pages:
- **URL**: https://honeyhiveai.github.io/praxis-os/
- **Workflow**: `.github/workflows/deploy-docs.yml`

### Manual Deployment

```bash
# Deploy directly from local machine
npm run deploy
```

## 🔧 Configuration

Main configuration in `docusaurus.config.ts`:
- Site metadata (title, tagline, URL)
- Theme configuration
- Plugin settings
- Navigation structure

## 📚 Resources

- [Docusaurus Documentation](https://docusaurus.io/)
- [MDX Documentation](https://mdxjs.com/)
- [Markdown Guide](https://docusaurus.io/docs/markdown-features)
