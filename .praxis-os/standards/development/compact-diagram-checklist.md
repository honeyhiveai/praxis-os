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

- [ ] **All cards use orange theme** (no rainbow colors - no warning/info/success)
- [ ] **Use outline style, not solid fills**:
  - Borders: `2px solid var(--honeyhive-orange-border)` or `3px solid` for emphasis
  - Background: `var(--ifm-background-surface-color)` (dark theme background)
  - Text: `var(--ifm-heading-color)` (theme-aware, NOT hardcoded white)
  - ❌ **Don't use**: `backgroundColor: var(--honeyhive-orange)` with white text
  - ✅ **Do use**: `border: 2px solid var(--honeyhive-orange)` with dark background
- [ ] **Use CSS custom properties** (preferred):
  - `var(--honeyhive-orange)` for primary color (#ff8c5d)
  - `var(--honeyhive-orange-border)` for borders (#ff6b35)
  - `var(--honeyhive-orange-bg)` for subtle backgrounds (rgba with transparency)
  - `var(--honeyhive-orange-shadow)` for hover shadows
- [ ] **OR hardcode if needed** (less maintainable):
  - Primary color: `#ff8c5d`
  - Border color: `#ff6b35`
  - Background: `rgba(255, 140, 93, 0.08)`
  - Hover shadow: `rgba(255, 140, 93, 0.2)` or `rgba(255, 107, 53, 0.25)` for dark mode
- [ ] Dark mode styles included
- [ ] Arrow/connector color uses HoneyHive orange

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
4. Use CSS custom properties for HoneyHive colors (see `docs/src/css/custom.css`)
5. Use this checklist to verify

## HoneyHive Color Reference

**CSS Custom Properties (defined in `docs/src/css/custom.css`):**
```css
/* Use these in your CSS modules */
var(--honeyhive-orange)        /* #ff8c5d - primary orange */
var(--honeyhive-orange-border) /* #ff6b35 - darker border */
var(--honeyhive-orange-bg)     /* rgba(255, 140, 93, 0.08) - subtle background */
var(--honeyhive-orange-shadow) /* rgba(255, 107, 53, 0.2/0.25) - hover shadow */
```

**Example usage in CSS module (outline style):**
```css
/* Card with outline border */
.card {
  border: 2px solid var(--honeyhive-orange-border);
  background: var(--ifm-background-surface-color);
  color: var(--ifm-heading-color);
}

.card:hover {
  border-color: var(--honeyhive-orange);
  box-shadow: 0 4px 12px var(--honeyhive-orange-shadow);
}

/* Badge with outline */
.badge {
  border: 2px solid var(--honeyhive-orange);
  background: var(--ifm-background-surface-color);
  color: var(--ifm-heading-color);
}

/* Icon circle with outline */
.icon {
  border: 3px solid var(--honeyhive-orange);
  background: var(--ifm-background-surface-color);
  border-radius: 50%;
}
```

**❌ Anti-pattern (solid fill):**
```css
/* Don't do this - breaks theme consistency */
.badge {
  background: var(--honeyhive-orange);
  color: white; /* Hardcoded white text */
}
```

**Why use outline style?**
- ✅ Consistent with existing components (CompactDiagram.module.css)
- ✅ Works better in both light and dark modes
- ✅ More professional, less "loud"
- ✅ Text color adapts to theme automatically

**Why use CSS custom properties?**
- ✅ Single source of truth (change once, updates everywhere)
- ✅ Consistent branding across all components
- ✅ Easy to update if brand colors change
- ✅ Works in both light and dark modes


