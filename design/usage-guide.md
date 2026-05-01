# Design System Usage Guide

## Color Application

### Text Colors

#### On White/Light Backgrounds
Use these colors for optimal readability (all meet WCAG AA 4.5:1 ratio):

```css
.text-primary { color: #1d4ed8; }    /* primary-700 */
.text-secondary { color: #334155; }  /* secondary-700 */
.text-accent { color: #a21caf; }     /* accent-700 */
.text-body { color: #404040; }       /* neutral-700 */
.text-muted { color: #737373; }      /* neutral-500 */
```

#### On Dark Backgrounds
```css
.text-on-dark { color: #ffffff; }    /* neutral-white */
.text-on-dark-muted { color: #f1f5f9; } /* secondary-100 */
```

### Background Colors

#### Page Backgrounds
```css
.bg-page { background: #fafafa; }    /* neutral-50 */
.bg-card { background: #ffffff; }    /* white */
.bg-subtle { background: #f5f5f5; }  /* neutral-100 */
```

#### Semantic Backgrounds
```css
.bg-success-light { background: #d1fae5; }
.bg-warning-light { background: #fef3c7; }
.bg-error-light { background: #fee2e2; }
.bg-info-light { background: #dbeafe; }
```

### Interactive Elements

#### Buttons
```css
/* Primary Button */
.btn-primary {
  background: #2563eb;  /* primary-600 */
  color: #ffffff;
}
.btn-primary:hover {
  background: #1d4ed8;  /* primary-700 */
}
.btn-primary:active {
  background: #1e40af;  /* primary-800 */
}

/* Secondary Button */
.btn-secondary {
  background: #f1f5f9;  /* secondary-100 */
  color: #334155;       /* secondary-700 */
}
.btn-secondary:hover {
  background: #e2e8f0;  /* secondary-200 */
}
```

#### Links
```css
.link {
  color: #2563eb;       /* primary-600 */
  text-decoration: none;
}
.link:hover {
  color: #1d4ed8;       /* primary-700 */
  text-decoration: underline;
}
```

### Borders

```css
.border-light { border-color: #e5e5e5; }  /* neutral-200 */
.border-medium { border-color: #d4d4d4; } /* neutral-300 */
.border-dark { border-color: #a3a3a3; }   /* neutral-400 */
```

## Icon Usage

### Basic Implementation

#### Inline SVG
```html
<svg class="icon" width="24" height="24" stroke="currentColor">
  <use href="design/icons/category-food.svg#icon"></use>
</svg>
```

#### With Color
```html
<div style="color: #ef4444;">
  <svg class="icon" width="24" height="24">
    <!-- Icon inherits red color -->
  </svg>
</div>
```

### Size Variants

```css
.icon-sm { width: 16px; height: 16px; }
.icon-md { width: 24px; height: 24px; }  /* default */
.icon-lg { width: 32px; height: 32px; }
.icon-xl { width: 48px; height: 48px; }
```

### Category Icon Colors

Apply category-specific colors for visual distinction:

```html
<!-- Food category -->
<div style="color: #ef4444;">
  <svg class="icon"><!-- food icon --></svg>
</div>

<!-- Transport category -->
<div style="color: #3b82f6;">
  <svg class="icon"><!-- transport icon --></svg>
</div>
```

### Icon + Text Combinations

```html
<div class="flex items-center gap-2">
  <svg class="icon" width="20" height="20" style="color: #10b981;">
    <!-- health icon -->
  </svg>
  <span>Health & Fitness</span>
</div>
```

### Accessibility

#### Meaningful Icons
```html
<button>
  <svg role="img" aria-label="Delete transaction">
    <title>Delete</title>
    <!-- icon paths -->
  </svg>
</button>
```

#### Decorative Icons
```html
<div>
  <svg aria-hidden="true" focusable="false">
    <!-- icon paths -->
  </svg>
  <span>Visible label text</span>
</div>
```

## Category Color Mapping

| Category | Color | Hex | Usage |
|----------|-------|-----|-------|
| Food | Red | `#ef4444` | Dining, groceries |
| Transport | Blue | `#3b82f6` | Vehicles, fuel |
| Shopping | Purple | `#8b5cf6` | Retail purchases |
| Entertainment | Pink | `#ec4899` | Movies, games |
| Health | Green | `#10b981` | Medical, fitness |
| Education | Amber | `#f59e0b` | Books, courses |
| Housing | Indigo | `#6366f1` | Rent, mortgage |
| Utilities | Teal | `#14b8a6` | Electric, water |
| Income | Green | `#22c55e` | Salary, revenue |
| Savings | Blue | `#3b82f6` | Savings transfers |
| Debt | Red | `#ef4444` | Loan payments |

## Semantic Color Usage

### Success States
```html
<div class="alert" style="background: #d1fae5; color: #047857; border-left: 4px solid #10b981;">
  <svg style="color: #10b981;"><!-- checkmark icon --></svg>
  Transaction saved successfully
</div>
```

### Warning States
```html
<div class="alert" style="background: #fef3c7; color: #d97706; border-left: 4px solid #f59e0b;">
  <svg style="color: #f59e0b;"><!-- warning icon --></svg>
  Budget limit approaching
</div>
```

### Error States
```html
<div class="alert" style="background: #fee2e2; color: #dc2626; border-left: 4px solid #ef4444;">
  <svg style="color: #ef4444;"><!-- error icon --></svg>
  Invalid transaction amount
</div>
```

### Info States
```html
<div class="alert" style="background: #dbeafe; color: #1d4ed8; border-left: 4px solid #3b82f6;">
  <svg style="color: #3b82f6;"><!-- info icon --></svg>
  Tip: Use tags to organize transactions
</div>
```

## Dark Mode Considerations

### Color Adjustments
```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #171717;        /* neutral-900 */
    --color-surface: #262626;   /* neutral-800 */
    --color-text: #fafafa;      /* neutral-50 */
    --color-text-muted: #a3a3a3; /* neutral-400 */
    --color-border: #404040;    /* neutral-700 */
  }
}
```

### Icon Colors in Dark Mode
Use lighter shades for better visibility:
```css
@media (prefers-color-scheme: dark) {
  .icon-food { color: #fca5a5; }      /* red-300 */
  .icon-transport { color: #93c5fd; } /* blue-300 */
  .icon-health { color: #6ee7b7; }    /* green-300 */
}
```

## Responsive Design

### Icon Sizes by Breakpoint
```css
/* Mobile */
@media (max-width: 768px) {
  .category-icon { width: 20px; height: 20px; }
}

/* Tablet */
@media (min-width: 769px) and (max-width: 1024px) {
  .category-icon { width: 24px; height: 24px; }
}

/* Desktop */
@media (min-width: 1025px) {
  .category-icon { width: 28px; height: 28px; }
}
```

## Common Patterns

### Category Badge
```html
<span class="badge" style="
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: #eff6ff;
  color: #1d4ed8;
  border-radius: 16px;
  font-size: 14px;
">
  <svg class="icon" width="16" height="16" style="color: #3b82f6;">
    <!-- category icon -->
  </svg>
  Transport
</span>
```

### Transaction List Item
```html
<div class="transaction-item" style="
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #e5e5e5;
">
  <div style="
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #eff6ff;
    border-radius: 8px;
  ">
    <svg class="icon" width="24" height="24" style="color: #3b82f6;">
      <!-- category icon -->
    </svg>
  </div>
  <div style="flex: 1;">
    <div style="font-weight: 500; color: #404040;">Uber Ride</div>
    <div style="font-size: 14px; color: #737373;">Transport</div>
  </div>
  <div style="font-weight: 600; color: #404040;">$24.50</div>
</div>
```

## Contrast Ratio Reference

| Color Pair | Ratio | WCAG Level | Use Case |
|------------|-------|------------|----------|
| primary-700 / white | 7.5:1 | AAA | Body text |
| secondary-700 / white | 12.5:1 | AAA | Headings |
| neutral-700 / white | 10.7:1 | AAA | Body text |
| success-dark / white | 6.4:1 | AA | Success text |
| error-dark / white | 5.9:1 | AA | Error text |
| warning-dark / white | 4.8:1 | AA | Warning text |

## Testing Checklist

- [ ] All text meets 4.5:1 contrast ratio on backgrounds
- [ ] Icons are visible at 16px size
- [ ] Interactive elements have clear hover/focus states
- [ ] Color is not the only means of conveying information
- [ ] Dark mode colors maintain sufficient contrast
- [ ] Icons have appropriate ARIA labels
- [ ] Category colors are distinguishable for colorblind users

## Resources

- **Contrast Checker**: https://webaim.org/resources/contrastchecker/
- **Color Blindness Simulator**: https://www.color-blindness.com/coblis-color-blindness-simulator/
- **WCAG Guidelines**: https://www.w3.org/WAI/WCAG21/quickref/
