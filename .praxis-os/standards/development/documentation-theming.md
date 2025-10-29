# Documentation Theming Standards

**Keywords for search**: Docusaurus theming, CSS variables, light dark mode, theme compatibility, ifm variables, documentation styling, responsive design, fluid typography, clamp font sizes, viewport units vw, theme testing, color variables, spacing variables

---

## 🎯 TL;DR - Documentation Theming Quick Reference

**Critical theming rules:**

1. **Always use Docusaurus CSS variables** (`--ifm-*`) for colors, spacing, typography
2. **Never hardcode colors** - breaks in light/dark mode
3. **Test in both light and dark themes** before committing
4. **Use semantic variables** - `--ifm-color-emphasis-*` for backgrounds, `--ifm-font-color-base` for text
5. **Use relative units** - `rem` for spacing, `%` for layouts

**Keywords for search**: Docusaurus CSS variables ifm, theme variables light dark mode, semantic color variables, responsive spacing, theme compatibility testing

**When to apply**: Creating React components, writing custom CSS modules, styling documentation elements

**Primary variable categories**: colors (emphasis, primary, success, etc.), spacing, typography, borders

---

## Purpose

Ensure all prAxIs OS documentation components respect Docusaurus theming, work in both light and dark modes, and provide a consistent, professional appearance. Using CSS variables makes components theme-aware and maintainable.

---

## The Problem

**Without theming standards:**
- Hardcoded colors break in dark mode (white text on white background)
- Inconsistent spacing and typography across components
- Components don't respect user theme preferences
- Maintenance nightmare when theme changes
- Poor accessibility (insufficient contrast)
- Visual inconsistency degrades professional appearance

**Real-world pain points:**
```css
/* Hardcoded - breaks in dark mode */
.box {
  background: #ffffff;
  color: #000000;
  border: 1px solid #cccccc;
}
```

**User switches to dark mode:** White box with black text on white background = unreadable.

---

## The Standard

### Always Use Docusaurus CSS Variables

**Core principle:** Let Docusaurus handle theming. Reference variables, never hardcode.

✅ **Correct:**
```css
.container {
  background: var(--ifm-background-surface-color);
  color: var(--ifm-font-color-base);
  border: 1px solid var(--ifm-color-emphasis-300);
}
```

❌ **Incorrect:**
```css
.container {
  background: #ffffff;
  color: #000000;
  border: 1px solid #e0e0e0;
}
```

### Color Variables

**Use semantic color variables for theme compatibility:**

#### Background Colors
```css
/* Surface backgrounds (cards, boxes) */
background: var(--ifm-background-surface-color);

/* Main page background */
background: var(--ifm-background-color);

/* Subtle backgrounds (code blocks, quotes) */
background: var(--ifm-code-background);
```

#### Text Colors
```css
/* Primary text */
color: var(--ifm-font-color-base);

/* Secondary/muted text */
color: var(--ifm-color-emphasis-600);

/* Links */
color: var(--ifm-link-color);

/* Hover states */
color: var(--ifm-link-hover-color);
```

#### Emphasis Colors (Neutral Grays)
```css
/* Light emphasis (subtle backgrounds) */
background: var(--ifm-color-emphasis-100);
border: 1px solid var(--ifm-color-emphasis-300);

/* Medium emphasis (borders, dividers) */
border-color: var(--ifm-color-emphasis-400);

/* Strong emphasis (icons, accents) */
color: var(--ifm-color-emphasis-600);
```

**Emphasis scale:** `100` (lightest) → `900` (darkest) in light mode, inverts in dark mode.

#### Brand Colors
```css
/* Primary brand color (blue) */
background: var(--ifm-color-primary);
color: var(--ifm-color-primary-contrast-background);

/* Lighter shades */
background: var(--ifm-color-primary-lighter);
background: var(--ifm-color-primary-lightest);

/* Darker shades */
background: var(--ifm-color-primary-darker);
background: var(--ifm-color-primary-darkest);
```

#### Semantic Status Colors
```css
/* Success (green) */
background: var(--ifm-color-success);
border-color: var(--ifm-color-success-dark);

/* Info (blue) */
background: var(--ifm-color-info);

/* Warning (orange) */
background: var(--ifm-color-warning);

/* Danger (red) */
background: var(--ifm-color-danger);
```

### Spacing Variables

**Use consistent spacing scale:**

```css
/* Padding/margin scale */
padding: var(--ifm-spacing-vertical) var(--ifm-spacing-horizontal);

/* Individual units */
margin: var(--ifm-global-spacing); /* Usually 1rem */

/* Custom spacing (use rem for consistency) */
padding: 0.5rem;   /* Small */
padding: 1rem;     /* Medium */
padding: 1.5rem;   /* Large */
padding: 2rem;     /* Extra large */
```

**Prefer `rem` over `px`** for accessibility (respects user font size settings).

### Typography Variables

**Use typography variables for text:**

```css
/* Font families */
font-family: var(--ifm-font-family-base);
font-family: var(--ifm-font-family-monospace);

/* Font sizes */
font-size: var(--ifm-font-size-base);
font-size: var(--ifm-h1-font-size);
font-size: var(--ifm-h2-font-size);
/* ... h3, h4, h5, h6 */

/* Line height */
line-height: var(--ifm-line-height-base);

/* Font weights */
font-weight: var(--ifm-font-weight-normal);
font-weight: var(--ifm-font-weight-semibold);
font-weight: var(--ifm-font-weight-bold);
```

### Border and Border Radius

**Use consistent border styling:**

```css
/* Border width */
border-width: var(--ifm-global-border-width); /* Usually 1px */

/* Border color */
border-color: var(--ifm-color-emphasis-300);

/* Border radius */
border-radius: var(--ifm-global-radius);       /* Usually 0.25rem */
border-radius: var(--ifm-code-border-radius);   /* For code blocks */

/* Custom radius (maintain consistency) */
border-radius: 4px;   /* Small */
border-radius: 6px;   /* Medium */
border-radius: 8px;   /* Large */
border-radius: 12px;  /* Extra large */
```

### Responsive Design

**Use relative units and flexible layouts:**

```css
/* Flexbox for responsive layouts */
.container {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

/* Grid for structured layouts */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

/* Media queries for mobile */
@media (max-width: 768px) {
  .flowBox {
    flex-direction: column;
  }
}
```

**Key breakpoints:**
- `996px` - Docusaurus desktop/mobile breakpoint
- `768px` - Tablet
- `480px` - Mobile

### Fluid Typography (Modern Responsive Pattern)

**Critical principle:** Use `clamp()` for font sizes to scale smoothly with viewport width. This provides better responsive behavior than fixed sizes or media queries.

**Pattern:**
```css
font-size: clamp(min, preferred, max);
```

- **`min`**: Minimum size (small viewports) - use `rem`
- **`preferred`**: Fluid size that scales - use `vw` units
- **`max`**: Maximum size (large viewports) - use `rem`

✅ **Correct - fluid typography:**
```css
.heading {
  font-size: clamp(1.5rem, 4vw, 2.5rem);
  /* Scales from 1.5rem (mobile) to 2.5rem (desktop) at 4% of viewport width */
}

.bodyText {
  font-size: clamp(0.875rem, 2vw, 1.125rem);
  /* Scales from 0.875rem (small) to 1.125rem (large) */
}

.label {
  font-size: clamp(0.75rem, 1.5vw, 0.875rem);
  /* Small text that scales proportionally */
}
```

❌ **Incorrect - fixed px font sizes:**
```css
.heading {
  font-size: 24px; /* Doesn't scale with viewport */
}

.bodyText {
  font-size: 16px; /* Fixed size, poor mobile UX */
}
```

**Spacing can also be fluid:**
```css
.container {
  gap: clamp(0.5rem, 2vw, 1rem);
  padding: clamp(1rem, 3vw, 2rem);
}
```

**Flex item sizing tip:**
```css
.flexItem {
  flex: 1;
  min-width: 0; /* CRITICAL: Allows flex items to shrink below content size */
}
```

**Why fluid typography matters:**
- ✅ Smooth scaling across all viewport sizes (no jumps)
- ✅ Fewer media queries needed
- ✅ Better UX on tablets and intermediate sizes
- ✅ Text always fits cards/containers
- ✅ Modern, professional responsive behavior

**Common fluid patterns for components:**
```css
/* Card title */
.cardTitle {
  font-size: clamp(0.875rem, 2vw, 1.125rem);
}

/* Icon size */
.icon {
  font-size: clamp(1rem, 2vw, 1.5rem);
}

/* Badge/pill text */
.badge {
  font-size: clamp(0.75rem, 1.5vw, 0.875rem);
}

/* Responsive gap */
.grid {
  gap: clamp(1rem, 3vw, 2rem);
}
```

---

## Checklist

**Before writing CSS for documentation components:**

- [ ] Identified which CSS variables to use (colors, spacing, typography)
- [ ] No hardcoded colors in CSS
- [ ] No hardcoded pixel values for spacing (use `rem`)
- [ ] Using semantic variables (`--ifm-color-emphasis-*` not random colors)
- [ ] Responsive design considered (flexbox/grid, media queries)
- [ ] **Font sizes use `clamp()` for fluid typography** (not fixed `px` or `rem`)
- [ ] Spacing uses fluid units where appropriate (`clamp()` for gaps/padding)
- [ ] Flex items have `min-width: 0` to allow proper shrinking

**After writing CSS:**

- [ ] Tested in light mode - looks good
- [ ] Tested in dark mode - looks good
- [ ] Tested on mobile (narrow viewport)
- [ ] Text has sufficient contrast (readable in both themes)
- [ ] No theme-breaking hardcoded values
- [ ] Spacing consistent with other components

**When in doubt:**
- [ ] Checked existing components for patterns (`StandardsFlowDiagram.module.css`, `CompactDiagram.module.css`)
- [ ] Verified variable usage in Docusaurus docs

---

## Examples

### Example 1: Card Component (Theme-Aware)

✅ **Good - uses CSS variables:**

```css
.card {
  background: var(--ifm-background-surface-color);
  border: 1px solid var(--ifm-color-emphasis-300);
  border-radius: 8px;
  padding: 1.5rem;
  color: var(--ifm-font-color-base);
}

.cardTitle {
  font-weight: var(--ifm-font-weight-semibold);
  color: var(--ifm-font-color-base);
  margin-bottom: 0.5rem;
}

.cardIcon {
  font-size: 1.5rem;
  color: var(--ifm-color-emphasis-600);
}
```

**Why it works:**
- Light mode: White background, dark text
- Dark mode: Dark background, light text
- All colors adjust automatically

❌ **Bad - hardcoded colors:**

```css
.card {
  background: #ffffff;
  border: 1px solid #e0e0e0;
  color: #333333;
}
```

**Problem:** Dark mode shows white card with dark text on dark background = invisible.

### Example 2: Flow Diagram (Compact Pattern)

```css
.compactFlow {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: var(--ifm-background-surface-color);
  border-radius: 8px;
  overflow-x: auto; /* Mobile scroll */
}

.flowBox {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: var(--ifm-color-emphasis-100);
  border: 1px solid var(--ifm-color-emphasis-300);
  border-radius: 6px;
  white-space: nowrap;
}

.flowIcon {
  font-size: 1.5rem;
}

.flowLabel {
  font-weight: 500;
  color: var(--ifm-font-color-base);
}

.flowArrow {
  margin: 0 1rem;
  font-size: 1.5rem;
  color: var(--ifm-color-emphasis-600);
}

/* Mobile responsive */
@media (max-width: 768px) {
  .compactFlow {
    overflow-x: auto;
    padding: 1rem;
  }
  
  .flowArrow {
    margin: 0 0.5rem;
  }
}
```

**Key features:**
- All colors use CSS variables
- Responsive (horizontal scroll on mobile)
- Consistent spacing with `rem`
- Theme-aware emphasis colors

### Example 3: Colored Cards (Variants)

```css
/* Base card */
.card {
  background: var(--ifm-color-emphasis-100);
  border: 1px solid var(--ifm-color-emphasis-300);
  border-radius: 8px;
  padding: 1rem;
}

/* Colored variants using semantic colors */
.cardBlue {
  background: var(--ifm-color-info-contrast-background);
  border-color: var(--ifm-color-info);
}

.cardPurple {
  background: rgba(138, 43, 226, 0.1);
  border-color: rgba(138, 43, 226, 0.3);
}

.cardGreen {
  background: var(--ifm-color-success-contrast-background);
  border-color: var(--ifm-color-success);
}

.cardOrange {
  background: var(--ifm-color-warning-contrast-background);
  border-color: var(--ifm-color-warning);
}
```

**Note:** For custom colors (purple), use `rgba()` with low opacity for theme compatibility.

### Example 4: Interactive States

```css
.button {
  background: var(--ifm-color-primary);
  color: var(--ifm-color-primary-contrast-background);
  border: none;
  border-radius: var(--ifm-global-radius);
  padding: 0.5rem 1rem;
  font-weight: var(--ifm-font-weight-semibold);
  cursor: pointer;
  transition: background 0.2s ease;
}

.button:hover {
  background: var(--ifm-color-primary-dark);
}

.button:active {
  background: var(--ifm-color-primary-darker);
}

.button:disabled {
  background: var(--ifm-color-emphasis-300);
  color: var(--ifm-color-emphasis-600);
  cursor: not-allowed;
}
```

**Interactive states use theme variables** for consistent behavior.

---

## Anti-Patterns

### ❌ Hardcoded Colors

```css
.box {
  background: #ffffff;
  color: #000000;
  border: 1px solid #cccccc;
}
```

**Problem:** Breaks in dark mode, not theme-aware.

**Fix:** Use CSS variables.

### ❌ Fixed Font Sizes (Not Responsive)

```css
.cardTitle {
  font-size: 18px;  /* Fixed size, doesn't scale with viewport */
}

.badge {
  font-size: 14px;  /* Same size on all devices */
}
```

**Problem:** 
- Doesn't scale with viewport width
- Poor UX on mobile (too large) or large displays (too small)
- Text may overflow containers on narrow viewports

**Fix:** Use fluid typography with `clamp()`:
```css
.cardTitle {
  font-size: clamp(0.875rem, 2vw, 1.125rem);
  /* Scales smoothly from 0.875rem (mobile) to 1.125rem (desktop) */
}

.badge {
  font-size: clamp(0.75rem, 1.5vw, 0.875rem);
  /* Smaller text scales proportionally */
}
```

### ❌ Pixel-Based Spacing

```css
.container {
  padding: 24px;
  margin: 16px;
}
```

**Problem:** Doesn't respect user font size preferences, not accessible.

**Fix:** Use `rem` units (or `clamp()` for fluid spacing):
```css
.container {
  padding: clamp(1rem, 3vw, 1.5rem);
  margin: 1rem;
}
```

### ❌ No Mobile Responsiveness

```css
.diagram {
  width: 1200px;
  display: flex;
}
```

**Problem:** Horizontal overflow on mobile, poor UX.

**Fix:** Use flexible layouts:
```css
.diagram {
  max-width: 100%;
  display: flex;
  flex-wrap: wrap;
  overflow-x: auto;
}
```

### ❌ Insufficient Contrast

```css
.text {
  color: #888888; /* Light gray */
  background: #ffffff;
}
```

**Problem:** Fails WCAG contrast requirements (4.5:1 for normal text).

**Fix:** Use semantic emphasis variables:
```css
.text {
  color: var(--ifm-color-emphasis-800);
  background: var(--ifm-background-surface-color);
}
```

### ❌ Theme-Specific Hacks

```css
[data-theme='dark'] .box {
  background: #1a1a1a;
}

[data-theme='light'] .box {
  background: #ffffff;
}
```

**Problem:** Duplicates theme logic, unmaintainable.

**Fix:** Use variables that handle this automatically:
```css
.box {
  background: var(--ifm-background-surface-color);
}
```

---

## Frequently Asked Questions

**How do I find available CSS variables?**
→ Inspect Docusaurus site in browser DevTools, look for `--ifm-*` variables on `:root`. Or check [Docusaurus theming docs](https://docusaurus.io/docs/styling-layout#styling-your-site-with-infima).

**What if I need a custom color not in the theme?**
→ Use `rgba()` with low opacity for backgrounds, or add to `docusaurus.config.ts` theme colors. Avoid hardcoding hex values.

**How do I test theme compatibility?**
→ Toggle light/dark mode in Docusaurus (moon/sun icon), verify colors/contrast look good in both.

**Can I use Tailwind or other CSS frameworks?**
→ Not recommended. Stick with CSS modules and Docusaurus variables for consistency.

**What about animations and transitions?**
→ Fine to add, but keep colors/spacing theme-aware. Use CSS variables in transitions.

**How do I handle really complex theming needs?**
→ Check if Docusaurus already provides a variable. If not, propose adding to theme config. Last resort: custom CSS with fallbacks.

---

## Testing Checklist

**Manual testing for every component:**

1. **Light Mode Test**
   - [ ] Text is readable (sufficient contrast)
   - [ ] Backgrounds are appropriate
   - [ ] Borders are visible but subtle
   - [ ] No harsh white glare

2. **Dark Mode Test**
   - [ ] Switch to dark mode (moon icon)
   - [ ] Text is readable (not too dim)
   - [ ] Backgrounds contrast properly
   - [ ] No pure white/black (use variables)
   - [ ] Colors look intentional, not broken

3. **Mobile Test**
   - [ ] Resize browser to 480px width
   - [ ] No horizontal overflow (or intentional scroll)
   - [ ] Text remains readable
   - [ ] Touch targets large enough (44px min)
   - [ ] Spacing works on small screens

4. **Accessibility Test**
   - [ ] Contrast ratio ≥ 4.5:1 for text (use browser tools)
   - [ ] Focus indicators visible
   - [ ] No color-only information (use icons too)

---

## Related Standards

- `documentation-diagrams.md` - Apply theming to diagram components
- `documentation-project-naming.md` - Consistent branding in themed components
- `rag-content-authoring.md` - Document theming patterns for discoverability

---

## Quick Reference: Common Variables

**Colors:**
```css
--ifm-background-color           /* Page background */
--ifm-background-surface-color   /* Card/box background */
--ifm-font-color-base           /* Primary text */
--ifm-color-emphasis-100        /* Subtle background */
--ifm-color-emphasis-300        /* Border color */
--ifm-color-emphasis-600        /* Secondary text */
--ifm-color-primary             /* Brand blue */
--ifm-color-success             /* Green */
--ifm-color-warning             /* Orange */
--ifm-color-danger              /* Red */
--ifm-link-color                /* Link blue */
```

**Spacing:**
```css
--ifm-spacing-vertical          /* Vertical spacing */
--ifm-spacing-horizontal        /* Horizontal spacing */
--ifm-global-spacing            /* Base unit (1rem) */
```

**Typography:**
```css
--ifm-font-family-base          /* Body font */
--ifm-font-family-monospace     /* Code font */
--ifm-font-size-base            /* Base font size */
--ifm-font-weight-semibold      /* Semibold weight */
--ifm-font-weight-bold          /* Bold weight */
```

**Borders:**
```css
--ifm-global-border-width       /* Border width (1px) */
--ifm-global-radius             /* Border radius (4px) */
```

---

## Maintenance

**Update this standard when:**
- Docusaurus updates CSS variable system
- New theming patterns emerge from component creation
- Accessibility requirements change
- Theme color palette updates

**Periodic review:**
- Audit components for hardcoded colors
- Test theme compatibility across all components
- Update examples with new patterns

**Last reviewed:** 2025-10-29

---

