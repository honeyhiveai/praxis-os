/**
 * HoneyHive Brand Colors
 * 
 * Centralized color definitions for consistent branding across all React components.
 * These colors work in both light and dark modes.
 */

export const HONEYHIVE_COLORS = {
  // Primary orange
  primary: '#ff8c5d',
  
  // Border orange (darker)
  border: '#ff6b35',
  
  // Background tint (subtle orange with transparency)
  backgroundTint: 'rgba(255, 140, 93, 0.08)',
  
  // Hover shadow (orange with transparency)
  hoverShadow: 'rgba(255, 107, 53, 0.2)',
} as const;

/**
 * Usage in React components:
 * 
 * import { HONEYHIVE_COLORS } from '@site/src/theme/colors';
 * 
 * <div style={{ borderColor: HONEYHIVE_COLORS.border }}>
 */

/**
 * Usage in CSS modules:
 * 
 * Since CSS modules can't import TypeScript, use CSS custom properties instead.
 * See: docs/src/css/custom.css for global CSS variable definitions.
 */

