# Compact Diagram Checklist - Universal Documentation Practice

**Quick reference checklist for creating compact, effective React diagrams in documentation.**

Use this checklist when creating or reviewing React diagram components.

## Size Requirements ✅

**Horizontal Flow (Preferred):**
- [ ] Container max-width: 800px
- [ ] Container centered with `margin: auto`
- [ ] Box padding: 0.6rem 1rem
- [ ] Icon size: 1.25rem
- [ ] Font size: 0.8rem labels, 600 weight
- [ ] Single horizontal line (~60-80px height)
- [ ] Fits in MacBook viewport (1280x800) without scrolling

**Two-Tier Layout (When Needed):**
- [ ] Container max-width: 900px
- [ ] Card padding: 0.75rem 1rem
- [ ] Icon size: 1.5rem
- [ ] Font sizes: 0.9-1.1rem for content

## HoneyHive Branding ✅

- [ ] All cards use orange theme (no rainbow colors)
- [ ] Primary color: `#ff8c5d`
- [ ] Border color: `#ff6b35`
- [ ] Background: `rgba(255, 140, 93, 0.08)` or similar
- [ ] Dark mode styles included
- [ ] Arrow/connector color: `#ff8c5d`

## Layout & Structure ✅

- [ ] Clear visual hierarchy
- [ ] Responsive (works on mobile)
- [ ] Smooth hover transitions (0.2s ease)
- [ ] Hover shadow uses orange tint: `rgba(255, 140, 93, 0.2)`
- [ ] Compact spacing between elements
- [ ] No wasted whitespace

## Content ✅

- [ ] Concise text (not verbose)
- [ ] Clear labels and titles
- [ ] Appropriate emoji icons (if used)
- [ ] Monospace for code examples

## Accessibility ✅

- [ ] Works with keyboard navigation
- [ ] Color contrast meets WCAG standards
- [ ] Semantic HTML structure
- [ ] No reliance on color alone for meaning

## Performance ✅

- [ ] No heavy animations
- [ ] CSS transitions only (no JS animations)
- [ ] Renders quickly
- [ ] No layout shift on load

## Integration ✅

- [ ] Import works correctly in markdown
- [ ] Module CSS scoped properly
- [ ] No conflicts with global styles
- [ ] Works with Docusaurus build

## Examples

**Horizontal Flow (Gold Standard):**
- `RAGQueryFlow.tsx` - 4-box horizontal flow
- `DataFlowDiagram.tsx` - Horizontal with split middle box
- Uses: `CompactDiagram.module.css`

**Two-Tier Layout:**
- `StandardsFlowDiagram.tsx` - Two-tier comparison
- Uses: `StandardsFlowDiagram.module.css`

**Before creating a new diagram:**
1. Choose horizontal flow if possible (preferred)
2. Copy `RAGQueryFlow.tsx` or `DataFlowDiagram.tsx`
3. Adapt with your content
4. Use this checklist to verify


