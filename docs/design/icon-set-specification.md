# Icon Set Specification

## Overview

This document defines the icon set and color palette for the Visit Statistics System. All icons are designed in SVG format to ensure scalability and accessibility compliance.

## Color Palette

### Primary Colors

| Color Name | Hex Code | RGB | Usage | WCAG AA Compliance |
|------------|----------|-----|-------|-------------------|
| Primary Dark | `#1a1a2e` | rgb(26, 26, 46) | Main background | ✓ (with white text) |
| Secondary Dark | `#16213e` | rgb(22, 33, 62) | Secondary background | ✓ (with white text) |
| Accent Blue | `#0f3460` | rgb(15, 52, 96) | Accent elements | ✓ (with white text) |
| Highlight Red | `#e94560` | rgb(233, 69, 96) | Primary actions, highlights | ✓ (with white text) |
| Text Light | `#f1f1f1` | rgb(241, 241, 241) | Primary text | ✓ (on dark backgrounds) |

### Semantic Colors

| Color Name | Hex Code | RGB | Usage | WCAG AA Compliance |
|------------|----------|-----|-------|-------------------|
| Success Green | `#2ecc71` | rgb(46, 204, 113) | Success messages | ✓ (with dark text) |
| Error Red | `#e74c3c` | rgb(231, 76, 60) | Error messages | ✓ (with white text) |
| Warning Orange | `#f39c12` | rgb(243, 156, 18) | Warning messages | ✓ (with dark text) |
| Info Blue | `#3498db` | rgb(52, 152, 219) | Information messages | ✓ (with white text) |

### Neutral Colors

| Color Name | Hex Code | RGB | Usage |
|------------|----------|-----|-------|
| White | `#ffffff` | rgb(255, 255, 255) | Icons on dark backgrounds |
| Light Gray | `#ecf0f1` | rgb(236, 240, 241) | Secondary icons |
| Medium Gray | `#95a5a6` | rgb(149, 165, 166) | Disabled states |
| Dark Gray | `#34495e` | rgb(52, 73, 94) | Borders, dividers |

## Icon Set (24 Icons)

### Navigation & Actions

#### 1. Home
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
  <polyline points="9 22 9 12 15 12 15 22"/>
</svg>
```

#### 2. Menu
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <line x1="3" y1="6" x2="21" y2="6"/>
  <line x1="3" y1="12" x2="21" y2="12"/>
  <line x1="3" y1="18" x2="21" y2="18"/>
</svg>
```

#### 3. Close
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <line x1="18" y1="6" x2="6" y2="18"/>
  <line x1="6" y1="6" x2="18" y2="18"/>
</svg>
```

#### 4. Search
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="11" cy="11" r="8"/>
  <path d="m21 21-4.35-4.35"/>
</svg>
```

#### 5. Settings
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="3"/>
  <path d="M12 1v6m0 6v6m5.2-13.2l-4.2 4.2m-2 2l-4.2 4.2M23 12h-6m-6 0H1m18.2 5.2l-4.2-4.2m-2-2l-4.2-4.2"/>
</svg>
```

### Data & Statistics

#### 6. Chart Bar
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <line x1="12" y1="20" x2="12" y2="10"/>
  <line x1="18" y1="20" x2="18" y2="4"/>
  <line x1="6" y1="20" x2="6" y2="16"/>
</svg>
```

#### 7. Chart Line
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
</svg>
```

#### 8. Chart Pie
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21.21 15.89A10 10 0 1 1 8 2.83"/>
  <path d="M22 12A10 10 0 0 0 12 2v10z"/>
</svg>
```

#### 9. Trending Up
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/>
  <polyline points="17 6 23 6 23 12"/>
</svg>
```

#### 10. Trending Down
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"/>
  <polyline points="17 18 23 18 23 12"/>
</svg>
```

### File Operations

#### 11. Download
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
  <polyline points="7 10 12 15 17 10"/>
  <line x1="12" y1="15" x2="12" y2="3"/>
</svg>
```

#### 12. Upload
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
  <polyline points="17 8 12 3 7 8"/>
  <line x1="12" y1="3" x2="12" y2="15"/>
</svg>
```

#### 13. File
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
  <polyline points="13 2 13 9 20 9"/>
</svg>
```

#### 14. Folder
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
</svg>
```

#### 15. Save
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
  <polyline points="17 21 17 13 7 13 7 21"/>
  <polyline points="7 3 7 8 15 8"/>
</svg>
```

### User & System

#### 16. User
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
  <circle cx="12" cy="7" r="4"/>
</svg>
```

#### 17. Users
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
  <circle cx="9" cy="7" r="4"/>
  <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
  <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
</svg>
```

#### 18. Eye
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
  <circle cx="12" cy="12" r="3"/>
</svg>
```

#### 19. Calendar
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
  <line x1="16" y1="2" x2="16" y2="6"/>
  <line x1="8" y1="2" x2="8" y2="6"/>
  <line x1="3" y1="10" x2="21" y2="10"/>
</svg>
```

#### 20. Clock
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"/>
  <polyline points="12 6 12 12 16 14"/>
</svg>
```

### Status & Feedback

#### 21. Check Circle
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
  <polyline points="22 4 12 14.01 9 11.01"/>
</svg>
```

#### 22. Alert Circle
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"/>
  <line x1="12" y1="8" x2="12" y2="12"/>
  <line x1="12" y1="16" x2="12.01" y2="16"/>
</svg>
```

#### 23. Info Circle
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <circle cx="12" cy="12" r="10"/>
  <line x1="12" y1="16" x2="12" y2="12"/>
  <line x1="12" y1="8" x2="12.01" y2="8"/>
</svg>
```

#### 24. Trash
```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polyline points="3 6 5 6 21 6"/>
  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
  <line x1="10" y1="11" x2="10" y2="17"/>
  <line x1="14" y1="11" x2="14" y2="17"/>
</svg>
```

## Icon Usage Guidelines

### Size Standards

| Size | Dimension | Usage |
|------|-----------|-------|
| Small | 16×16px | Inline text, compact UI |
| Medium | 24×24px | Standard buttons, navigation |
| Large | 32×32px | Feature highlights, headers |
| XLarge | 48×48px | Hero sections, empty states |

### Color Application

#### On Dark Backgrounds
- Primary icons: `#f1f1f1` (Text Light)
- Secondary icons: `#ecf0f1` (Light Gray)
- Accent icons: `#e94560` (Highlight Red)
- Disabled icons: `#95a5a6` (Medium Gray)

#### On Light Backgrounds
- Primary icons: `#1a1a2e` (Primary Dark)
- Secondary icons: `#34495e` (Dark Gray)
- Accent icons: `#e94560` (Highlight Red)
- Disabled icons: `#95a5a6` (Medium Gray)

### Accessibility Requirements

1. **Contrast Ratio**: Minimum 4.5:1 for normal text, 3:1 for large text (WCAG AA)
2. **Interactive Elements**: Minimum 24×24px touch target
3. **Alternative Text**: Always provide aria-label or title for screen readers
4. **Focus States**: Visible focus indicator with 2px outline
5. **Color Independence**: Never rely on color alone to convey information

### Implementation Example

```html
<!-- Standard Icon -->
<svg class="icon icon-medium" aria-label="Home" role="img">
  <use href="#icon-home"></use>
</svg>

<!-- Icon with Text -->
<button class="btn">
  <svg class="icon icon-small" aria-hidden="true">
    <use href="#icon-download"></use>
  </svg>
  <span>Download</span>
</button>

<!-- Icon-only Button -->
<button class="btn-icon" aria-label="Settings">
  <svg class="icon icon-medium">
    <use href="#icon-settings"></use>
  </svg>
</button>
```

### CSS Classes

```css
.icon {
  display: inline-block;
  vertical-align: middle;
  stroke: currentColor;
  fill: none;
}

.icon-small { width: 16px; height: 16px; }
.icon-medium { width: 24px; height: 24px; }
.icon-large { width: 32px; height: 32px; }
.icon-xlarge { width: 48px; height: 48px; }

.icon-primary { color: var(--text); }
.icon-accent { color: var(--highlight); }
.icon-success { color: #2ecc71; }
.icon-error { color: #e74c3c; }
.icon-warning { color: #f39c12; }
.icon-info { color: #3498db; }
```

## Icon Sprite Generation

Create a single SVG sprite file for optimal performance:

```xml
<svg xmlns="http://www.w3.org/2000/svg" style="display: none;">
  <symbol id="icon-home" viewBox="0 0 24 24">
    <!-- Icon path here -->
  </symbol>
  <!-- Additional icons -->
</svg>
```

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01-XX | Initial icon set and color palette |

## References

- WCAG 2.1 Guidelines: https://www.w3.org/WAI/WCAG21/quickref/
- SVG Accessibility: https://www.w3.org/TR/svg-aam-1.0/
- Color Contrast Checker: https://webaim.org/resources/contrastchecker/