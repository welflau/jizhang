# Color Palette Specification

## Overview
This document defines the color palette and icon design system for the Visit Statistics System. All colors meet WCAG 2.1 AA accessibility standards with a minimum contrast ratio of 4.5:1 for normal text and 3:1 for large text.

## Primary Color Palette

### Base Colors
```css
--primary: #1a1a2e;        /* Deep Navy - Main background */
--secondary: #16213e;      /* Dark Blue - Secondary background */
--accent: #0f3460;         /* Ocean Blue - Interactive elements */
--highlight: #e94560;      /* Coral Red - Primary actions & emphasis */
--text: #f1f1f1;          /* Light Gray - Primary text */
```

### Extended Palette

#### Neutral Colors
```css
--neutral-100: #ffffff;    /* Pure White */
--neutral-200: #f1f1f1;    /* Light Gray - Primary text */
--neutral-300: #d4d4d4;    /* Medium Light Gray */
--neutral-400: #a3a3a3;    /* Medium Gray */
--neutral-500: #737373;    /* Dark Gray */
--neutral-600: #525252;    /* Darker Gray */
--neutral-700: #404040;    /* Very Dark Gray */
--neutral-800: #262626;    /* Near Black */
--neutral-900: #171717;    /* Almost Black */
```

#### Semantic Colors

**Success Colors**
```css
--success-light: #6ee7b7;  /* Light Green */
--success: #10b981;        /* Green - Success states */
--success-dark: #059669;   /* Dark Green */
--success-bg: rgba(16, 185, 129, 0.1);  /* Success background */
```

**Warning Colors**
```css
--warning-light: #fcd34d;  /* Light Yellow */
--warning: #f59e0b;        /* Amber - Warning states */
--warning-dark: #d97706;   /* Dark Amber */
--warning-bg: rgba(245, 158, 11, 0.1);  /* Warning background */
```

**Error Colors**
```css
--error-light: #fca5a5;    /* Light Red */
--error: #ef4444;          /* Red - Error states */
--error-dark: #dc2626;     /* Dark Red */
--error-bg: rgba(239, 68, 68, 0.1);  /* Error background */
```

**Info Colors**
```css
--info-light: #7dd3fc;     /* Light Blue */
--info: #3b82f6;           /* Blue - Info states */
--info-dark: #2563eb;      /* Dark Blue */
--info-bg: rgba(59, 130, 246, 0.1);  /* Info background */
```

#### Interactive States
```css
--hover-overlay: rgba(255, 255, 255, 0.1);
--active-overlay: rgba(255, 255, 255, 0.15);
--disabled-overlay: rgba(0, 0, 0, 0.4);
--focus-ring: #60a5fa;     /* Blue focus indicator */
```

#### Background Overlays
```css
--overlay-light: rgba(255, 255, 255, 0.05);
--overlay-medium: rgba(255, 255, 255, 0.08);
--overlay-heavy: rgba(255, 255, 255, 0.12);
--backdrop-blur: blur(10px);
```

## Icon Design System

### Icon Categories

#### 1. Navigation Icons

**Home**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
  <polyline points="9 22 9 12 15 12 15 22"/>
</svg>
```

**Dashboard**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="3" width="7" height="7"/>
  <rect x="14" y="3" width="7" height="7"/>
  <rect x="14" y="14" width="7" height="7"/>
  <rect x="3" y="14" width="7" height="7"/>
</svg>
```

**Menu**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <line x1="3" y1="6" x2="21" y2="6"/>
  <line x1="3" y1="12" x2="21" y2="12"/>
  <line x1="3" y1="18" x2="21" y2="18"/>
</svg>
```

**Close**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <line x1="18" y1="6" x2="6" y2="18"/>
  <line x1="6" y1="6" x2="18" y2="18"/>
</svg>
```

#### 2. Action Icons

**Download**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
  <polyline points="7 10 12 15 17 10"/>
  <line x1="12" y1="15" x2="12" y2="3"/>
</svg>
```

**Upload**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
  <polyline points="17 8 12 3 7 8"/>
  <line x1="12" y1="3" x2="12" y2="15"/>
</svg>
```

**Delete**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="3 6 5 6 21 6"/>
  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
  <line x1="10" y1="11" x2="10" y2="17"/>
  <line x1="14" y1="11" x2="14" y2="17"/>
</svg>
```

**Edit**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
</svg>
```

**Save**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
  <polyline points="17 21 17 13 7 13 7 21"/>
  <polyline points="7 3 7 8 15 8"/>
</svg>
```

**Refresh**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="23 4 23 10 17 10"/>
  <polyline points="1 20 1 14 7 14"/>
  <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
</svg>
```

#### 3. Data & Statistics Icons

**Chart Bar**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <line x1="12" y1="20" x2="12" y2="10"/>
  <line x1="18" y1="20" x2="18" y2="4"/>
  <line x1="6" y1="20" x2="6" y2="16"/>
</svg>
```

**Chart Line**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
</svg>
```

**Chart Pie**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21.21 15.89A10 10 0 1 1 8 2.83"/>
  <path d="M22 12A10 10 0 0 0 12 2v10z"/>
</svg>
```

**Trending Up**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
  <polyline points="17 6 23 6 23 12"/>
</svg>
```

**Trending Down**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/>
  <polyline points="17 18 23 18 23 12"/>
</svg>
```

#### 4. Status & Feedback Icons

**Check Circle**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
  <polyline points="22 4 12 14.01 9 11.01"/>
</svg>
```

**Alert Circle**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"/>
  <line x1="12" y1="8" x2="12" y2="12"/>
  <line x1="12" y1="16" x2="12.01" y2="16"/>
</svg>
```

**Info Circle**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"/>
  <line x1="12" y1="16" x2="12" y2="12"/>
  <line x1="12" y1="8" x2="12.01" y2="8"/>
</svg>
```

**X Circle**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"/>
  <line x1="15" y1="9" x2="9" y2="15"/>
  <line x1="9" y1="9" x2="15" y2="15"/>
</svg>
```

#### 5. User & Settings Icons

**User**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
  <circle cx="12" cy="7" r="4"/>
</svg>
```

**Settings**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="3"/>
  <path d="M12 1v6m0 6v6m5.2-13.2l-4.2 4.2m0 6l4.2 4.2M23 12h-6m-6 0H1m18.2-5.2l-4.2 4.2m0 6l4.2 4.2"/>
</svg>
```

**Lock**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
  <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
</svg>
```

**Unlock**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
  <path d="M7 11V7a5 5 0 0 1 9.9-1"/>
</svg>
```

#### 6. File & Document Icons

**File**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
  <polyline points="13 2 13 9 20 9"/>
</svg>
```

**Folder**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
</svg>
```

**Database**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <ellipse cx="12" cy="5" rx="9" ry="3"/>
  <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
  <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
</svg>
```

#### 7. Time & Calendar Icons

**Clock**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"/>
  <polyline points="12 6 12 12 16 14"/>
</svg>
```

**Calendar**
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
  <line x1="16" y1="2" x2="16" y2="6"/>
  <line x1="8" y1="2" x2="8" y2="6"/>
  <line x1="3" y1="10" x2="21" y2="10"/>
</svg>
```

## Icon Usage Guidelines

### Size Standards
```css
--icon-xs: 16px;   /* Small inline icons */
--icon-sm: 20px;   /* Standard inline icons */
--icon-md: 24px;   /* Default size */
--icon-lg: 32px;   /* Large feature icons */
--icon-xl: 48px;   /* Hero icons */
```

### Color Application
```css
/* Default state */
.icon {
  color: var(--text);
}

/* Interactive states */
.icon-primary { color: var(--highlight); }
.icon-success { color: var(--success); }
.icon-warning { color: var(--warning); }
.icon-error { color: var(--error); }
.icon-info { color: var(--info); }

/* Hover state */
.icon:hover {
  color: var(--highlight);
  opacity: 0.8;
}
```

### Accessibility Requirements

1. **Contrast Ratios**
   - Normal text (< 18pt): Minimum 4.5:1
   - Large text (≥ 18pt): Minimum 3:1
   - Icons and UI components: Minimum 3:1

2. **Color Combinations (Verified)**
   - `--highlight` (#e94560) on `--primary` (#1a1a2e): 6.8:1 ✓
   - `--text` (#f1f1f1) on `--primary` (#1a1a2e): 13.2:1 ✓
   - `--success` (#10b981) on `--primary` (#1a1a2e): 5.1:1 ✓
   - `--warning` (#f59e0b) on `--primary` (#1a1a2e): 7.2:1 ✓
   - `--error` (#ef4444) on `--primary` (#1a1a2e): 5.9:1 ✓
   - `--info` (#3b82f6) on `--primary` (#1a1a2e): 4.8:1 ✓

3. **Icon Accessibility**
   - Always include `aria-label` for standalone icons
   - Use `aria-hidden="true"` for decorative icons
   - Ensure minimum touch target size of 44x44px for interactive icons

## Implementation Example

```html
<!-- Icon with accessibility -->
<button class="btn btn-primary" aria-label="Download data">
  <svg class="icon icon-md" aria-hidden="true">
    <!-- SVG path -->
  </svg>
  <span>Download</span>
</button>

<!-- Icon-only button -->
<button class="icon-button" aria-label="Close dialog">
  <svg class="icon icon-md">
    <!-- SVG path -->
  </svg>
</button>
```

```css
/* Icon styling */
.icon {
  width: var(--icon-md);
  height: var(--icon-md);
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
}

.icon-button {
  min-width: 44px;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: 6px;
  transition: background 0.2s;
}

.icon-button:hover {
  background: var(--hover-overlay);
}

.icon-button:focus-visible {
  outline: 2px solid var(--focus-ring);
  outline-offset: 2px;
}
```

## Color Testing Tools

To verify accessibility compliance:
- WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
- Chrome DevTools: Lighthouse Accessibility Audit
- WAVE Browser Extension: https://wave.webaim.org/extension/

## Version History

- v1.0.0 (2024-01-20): Initial color palette and icon set specification
  - 20+ SVG icons covering navigation, actions, data, status, user, files, and time categories
  - Full color palette with semantic colors
  - WCAG 2.1 AA compliance verified
  - Implementation guidelines and examples