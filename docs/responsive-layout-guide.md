# Responsive Layout System Documentation

## Overview

This document describes the responsive layout system implemented for the project, including breakpoints, grid system, and utility classes.

## Breakpoints

The system defines three primary breakpoints:

| Breakpoint | Range | CSS Media Query | Container Max-Width |
|------------|-------|-----------------|---------------------|
| **Mobile** | < 768px | Default (mobile-first) | 100% |
| **Tablet** | 768px - 1023px | `@media (min-width: 768px) and (max-width: 1023px)` | 720px |
| **Desktop** | ≥ 1024px | `@media (min-width: 1024px)` | 1200px |

### Why These Breakpoints?

- **768px**: Standard tablet portrait width, separates mobile phones from tablets
- **1024px**: Standard tablet landscape / small laptop width, separates tablets from desktop
- Aligns with common device sizes and Ant Design's default breakpoints

## CSS Variables

All responsive values are defined as CSS custom properties (variables) for easy theming:

```css
:root {
  /* Breakpoint values */
  --breakpoint-mobile: 768px;
  --breakpoint-tablet: 1024px;
  
  /* Spacing scale (auto-adjusts per breakpoint) */
  --spacing-xs: 4px;    /* 4px → 4px → 4px */
  --spacing-sm: 8px;    /* 8px → 8px → 8px */
  --spacing-md: 16px;   /* 16px → 20px → 24px */
  --spacing-lg: 24px;   /* 24px → 28px → 32px */
  --spacing-xl: 32px;   /* 32px → 40px → 48px */
  --spacing-xxl: 48px;  /* 48px → 56px → 64px */
  
  /* Typography scale */
  --font-size-base: 14px;  /* 14px → 15px → 16px */
  --font-size-lg: 16px;    /* 16px → 18px → 20px */
  --font-size-xl: 20px;
  --font-size-xxl: 24px;
  
  /* Grid gutter */
  --grid-gutter: 16px;  /* 16px → 20px → 24px */
}
```

## Container System

### `.container`

Responsive container with max-width constraints:

```html
<div class="container">
  <!-- Content auto-centers and constrains width -->
</div>
```

- **Mobile**: 100% width with 16px horizontal padding
- **Tablet**: Max 720px, centered
- **Desktop**: Max 1200px, centered

### `.container-fluid`

Full-width container (no max-width):

```html
<div class="container-fluid">
  <!-- Always 100% width -->
</div>
```

## Grid System

### Basic Usage

12-column flexbox grid compatible with Ant Design:

```html
<div class="row">
  <div class="col-12 col-md-6 col-lg-4">
    <!-- Mobile: 100%, Tablet: 50%, Desktop: 33.33% -->
  </div>
  <div class="col-12 col-md-6 col-lg-4">
    <!-- Same responsive behavior -->
  </div>
  <div class="col-12 col-md-6 col-lg-4">
    <!-- Same responsive behavior -->
  </div>
</div>
```

### Column Classes

| Class Pattern | Breakpoint | Example |
|---------------|------------|----------|
| `.col-{1-12}` | Mobile (default) | `.col-6` = 50% on all screens |
| `.col-md-{1-12}` | Tablet (≥768px) | `.col-md-4` = 33.33% on tablet+ |
| `.col-lg-{1-12}` | Desktop (≥1024px) | `.col-lg-3` = 25% on desktop |

### Gutter System

Grid gutter automatically adjusts:
- **Mobile**: 16px
- **Tablet**: 20px
- **Desktop**: 24px

Implemented via negative margins on `.row` and padding on columns.

## Responsive Utility Classes

### Display Utilities

```html
<!-- Show/hide based on breakpoint -->
<div class="d-mobile-block d-tablet-none d-desktop-none">
  Mobile only content
</div>

<div class="d-mobile-none d-tablet-block d-desktop-none">
  Tablet only content
</div>

<div class="d-mobile-none d-tablet-none d-desktop-block">
  Desktop only content
</div>
```

| Class | Effect |
|-------|--------|
| `.d-none` | `display: none` on all screens |
| `.d-block` | `display: block` on all screens |
| `.d-flex` | `display: flex` on all screens |
| `.d-mobile-none` | Hide on mobile only |
| `.d-tablet-none` | Hide on tablet only |
| `.d-desktop-none` | Hide on desktop only |

### Spacing Utilities

Margin and padding classes using the responsive spacing scale:

```html
<div class="mt-3 mb-4 p-2">
  <!-- margin-top: var(--spacing-md) -->
  <!-- margin-bottom: var(--spacing-lg) -->
  <!-- padding: var(--spacing-sm) -->
</div>
```

| Class | Property | Value |
|-------|----------|-------|
| `.m-{0-5}` | `margin` | 0 / xs / sm / md / lg / xl |
| `.mt-{0-5}` | `margin-top` | Same scale |
| `.mb-{0-5}` | `margin-bottom` | Same scale |
| `.p-{0-5}` | `padding` | Same scale |

### Text Alignment

```html
<div class="text-center text-mobile-center">
  <!-- Center on all screens, force center on mobile -->
</div>
```

| Class | Effect |
|-------|--------|
| `.text-left` | Left align |
| `.text-center` | Center align |
| `.text-right` | Right align |
| `.text-mobile-center` | Center on mobile only |

## Integration with Ant Design

This system is designed to work alongside Ant Design components:

```html
<!-- Ant Design Grid (recommended for complex layouts) -->
<div class="ant-row">
  <div class="ant-col ant-col-xs-24 ant-col-md-12 ant-col-lg-8">
    <a-card>Ant Design Card</a-card>
  </div>
</div>

<!-- Custom Grid (for simple layouts without React) -->
<div class="row">
  <div class="col-12 col-md-6 col-lg-4">
    <div class="demo-box">Custom Box</div>
  </div>
</div>
```

### Ant Design Breakpoints Mapping

| Ant Design | Our System | Width |
|------------|------------|-------|
| `xs` | Mobile | < 768px |
| `sm` | Mobile | ≥ 576px |
| `md` | Tablet | ≥ 768px |
| `lg` | Desktop | ≥ 1024px |
| `xl` | Desktop | ≥ 1200px |

## Best Practices

### 1. Mobile-First Approach

Always define mobile styles first, then override for larger screens:

```html
<!-- Good: Mobile-first -->
<div class="col-12 col-md-6 col-lg-4">
  <!-- 100% → 50% → 33.33% -->
</div>

<!-- Bad: Desktop-first -->
<div class="col-lg-4 col-md-6 col-12">
  <!-- Harder to reason about -->
</div>
```

### 2. Use CSS Variables for Consistency

```css
/* Good: Uses responsive variables */
.my-component {
  padding: var(--spacing-md);
  font-size: var(--font-size-base);
}

/* Bad: Hard-coded values */
.my-component {
  padding: 16px;
  font-size: 14px;
}
```

### 3. Test All Breakpoints

Always test your layout at:
- 375px (iPhone SE)
- 768px (iPad portrait)
- 1024px (iPad landscape)
- 1440px (Desktop)

### 4. Avoid Breakpoint-Specific Logic in JS

Use CSS media queries instead of `window.innerWidth` checks:

```javascript
// Good: CSS handles responsiveness
const element = document.querySelector('.responsive-element');

// Bad: JS breakpoint detection
if (window.innerWidth < 768) {
  element.classList.add('mobile-style');
}
```

## Debugging

### Breakpoint Indicator

The demo page includes a fixed indicator showing the current breakpoint:

```html
<div class="breakpoint-indicator"></div>
```

This displays:
- "Mobile (<768px)" in green
- "Tablet (768-1023px)" in orange
- "Desktop (≥1024px)" in blue

### Browser DevTools

1. Open Chrome DevTools (F12)
2. Click "Toggle device toolbar" (Ctrl+Shift+M)
3. Select preset devices or enter custom dimensions
4. Test responsive behavior

## Migration Guide

### From Bootstrap

| Bootstrap | Our System |
|-----------|------------|
| `.container` | `.container` |
| `.container-fluid` | `.container-fluid` |
| `.row` | `.row` |
| `.col-sm-6` | `.col-md-6` |
| `.col-md-4` | `.col-lg-4` |
| `.d-none .d-md-block` | `.d-mobile-none .d-tablet-block` |

### From Tailwind CSS

| Tailwind | Our System |
|----------|------------|
| `container` | `.container` |
| `grid grid-cols-3` | `.row` + `.col-lg-4` |
| `md:w-1/2` | `.col-md-6` |
| `hidden md:block` | `.d-mobile-none .d-tablet-block` |
| `p-4` | `.p-3` |

## Performance Considerations

- **CSS Variables**: Minimal performance impact, excellent browser support (IE11 needs fallbacks)
- **Flexbox Grid**: Better performance than float-based grids
- **Media Queries**: Evaluated once per layout, very efficient
- **No JavaScript**: Layout is pure CSS, no runtime overhead

## Browser Support

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support (iOS 9.3+)
- IE11: ⚠️ Needs CSS variable fallbacks

## Future Enhancements

- [ ] Add `xxl` breakpoint for ultra-wide screens (≥1920px)
- [ ] Implement CSS container queries when widely supported
- [ ] Add print media query styles
- [ ] Create SCSS/LESS mixins for easier customization

## References

- [Ant Design Breakpoints](https://ant.design/components/grid#api)
- [MDN: Using Media Queries](https://developer.mozilla.org/en-US/docs/Web/CSS/Media_Queries/Using_media_queries)
- [CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/--*)