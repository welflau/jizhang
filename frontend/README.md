# Frontend - Responsive Layout System

## Overview

This document describes the responsive layout implementation for the project, including breakpoints, grid system configuration, and responsive design utilities.

## Breakpoints

The application uses three main breakpoints to support different device sizes:

| Breakpoint | Range | Target Devices |
|------------|-------|----------------|
| **Mobile** | < 768px | Smartphones |
| **Tablet** | 768px - 1023px | Tablets, small laptops |
| **Desktop** | >= 1024px | Laptops, desktops, large screens |

### Breakpoint Variables

```scss
// styles/variables.scss
$breakpoint-mobile: 768px;
$breakpoint-tablet: 1024px;

// Media query mixins
@mixin mobile {
  @media (max-width: #{$breakpoint-mobile - 1px}) {
    @content;
  }
}

@mixin tablet {
  @media (min-width: #{$breakpoint-mobile}) and (max-width: #{$breakpoint-tablet - 1px}) {
    @content;
  }
}

@mixin desktop {
  @media (min-width: #{$breakpoint-tablet}) {
    @content;
  }
}

@mixin tablet-and-up {
  @media (min-width: #{$breakpoint-mobile}) {
    @content;
  }
}

@mixin mobile-and-tablet {
  @media (max-width: #{$breakpoint-tablet - 1px}) {
    @content;
  }
}
```

## Ant Design Grid System

The project uses Ant Design's 24-column grid system with custom responsive configurations.

### Grid Configuration

```typescript
// config/grid.config.ts
export const GRID_GUTTER = {
  xs: 8,   // Mobile
  sm: 16,  // Tablet
  md: 24,  // Desktop
  lg: 24,
  xl: 24,
  xxl: 24,
};

export const CONTAINER_MAX_WIDTH = {
  mobile: '100%',
  tablet: '768px',
  desktop: '1200px',
};
```

### Responsive Column Spans

```typescript
// Example column configurations for different layouts
export const LAYOUT_COLUMNS = {
  // Full width on mobile, half on tablet, third on desktop
  card: {
    xs: 24,
    sm: 12,
    md: 8,
  },
  
  // Full width on mobile, full on tablet, half on desktop
  form: {
    xs: 24,
    sm: 24,
    md: 12,
  },
  
  // Sidebar layout
  sidebar: {
    xs: 24,
    sm: 8,
    md: 6,
  },
  content: {
    xs: 24,
    sm: 16,
    md: 18,
  },
};
```

## Global Responsive Styles

### Container Component

```tsx
// components/Layout/Container.tsx
import { FC, ReactNode } from 'react';
import styles from './Container.module.scss';

interface ContainerProps {
  children: ReactNode;
  fluid?: boolean;
}

export const Container: FC<ContainerProps> = ({ children, fluid = false }) => {
  return (
    <div className={fluid ? styles.containerFluid : styles.container}>
      {children}
    </div>
  );
};
```

```scss
// components/Layout/Container.module.scss
.container {
  width: 100%;
  margin: 0 auto;
  padding: 0 16px;

  @include tablet {
    max-width: 768px;
    padding: 0 24px;
  }

  @include desktop {
    max-width: 1200px;
    padding: 0 32px;
  }
}

.containerFluid {
  width: 100%;
  padding: 0 16px;

  @include tablet {
    padding: 0 24px;
  }

  @include desktop {
    padding: 0 32px;
  }
}
```

## Responsive Utilities

### Visibility Classes

```scss
// styles/utilities.scss
.show-mobile {
  @include tablet-and-up {
    display: none !important;
  }
}

.show-tablet {
  @include mobile {
    display: none !important;
  }
  @include desktop {
    display: none !important;
  }
}

.show-desktop {
  @include mobile-and-tablet {
    display: none !important;
  }
}

.hide-mobile {
  @include mobile {
    display: none !important;
  }
}

.hide-tablet {
  @include tablet {
    display: none !important;
  }
}

.hide-desktop {
  @include desktop {
    display: none !important;
  }
}
```

### Spacing Utilities

```scss
// styles/spacing.scss
$spacing-mobile: 8px;
$spacing-tablet: 16px;
$spacing-desktop: 24px;

.responsive-spacing {
  padding: $spacing-mobile;

  @include tablet {
    padding: $spacing-tablet;
  }

  @include desktop {
    padding: $spacing-desktop;
  }
}
```

## React Hooks for Responsive Design

### useBreakpoint Hook

```typescript
// hooks/useBreakpoint.ts
import { useState, useEffect } from 'react';

export type Breakpoint = 'mobile' | 'tablet' | 'desktop';

export const useBreakpoint = (): Breakpoint => {
  const [breakpoint, setBreakpoint] = useState<Breakpoint>('desktop');

  useEffect(() => {
    const handleResize = () => {
      const width = window.innerWidth;
      if (width < 768) {
        setBreakpoint('mobile');
      } else if (width < 1024) {
        setBreakpoint('tablet');
      } else {
        setBreakpoint('desktop');
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return breakpoint;
};
```

### useMediaQuery Hook

```typescript
// hooks/useMediaQuery.ts
import { useState, useEffect } from 'react';

export const useMediaQuery = (query: string): boolean => {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const media = window.matchMedia(query);
    if (media.matches !== matches) {
      setMatches(media.matches);
    }

    const listener = () => setMatches(media.matches);
    media.addEventListener('change', listener);
    return () => media.removeEventListener('change', listener);
  }, [matches, query]);

  return matches;
};

// Usage examples
export const useIsMobile = () => useMediaQuery('(max-width: 767px)');
export const useIsTablet = () => useMediaQuery('(min-width: 768px) and (max-width: 1023px)');
export const useIsDesktop = () => useMediaQuery('(min-width: 1024px)');
```

## Usage Examples

### Example 1: Responsive Grid Layout

```tsx
import { Row, Col } from 'antd';
import { LAYOUT_COLUMNS } from '@/config/grid.config';

const ProductGrid = () => {
  return (
    <Row gutter={[16, 16]}>
      {products.map(product => (
        <Col key={product.id} {...LAYOUT_COLUMNS.card}>
          <ProductCard product={product} />
        </Col>
      ))}
    </Row>
  );
};
```

### Example 2: Conditional Rendering Based on Breakpoint

```tsx
import { useBreakpoint } from '@/hooks/useBreakpoint';

const Navigation = () => {
  const breakpoint = useBreakpoint();

  return (
    <>
      {breakpoint === 'mobile' ? (
        <MobileMenu />
      ) : (
        <DesktopMenu />
      )}
    </>
  );
};
```

### Example 3: Responsive Component with Media Query

```tsx
import { useIsMobile } from '@/hooks/useMediaQuery';

const DataTable = () => {
  const isMobile = useIsMobile();

  return (
    <Table
      columns={columns}
      dataSource={data}
      scroll={isMobile ? { x: 800 } : undefined}
      pagination={isMobile ? { pageSize: 5 } : { pageSize: 10 }}
    />
  );
};
```

## Best Practices

1. **Mobile-First Approach**: Design for mobile first, then enhance for larger screens
2. **Use Grid System**: Leverage Ant Design's grid system for consistent layouts
3. **Avoid Fixed Widths**: Use percentages or max-widths instead of fixed pixel widths
4. **Test on Real Devices**: Always test responsive layouts on actual devices
5. **Performance**: Use CSS media queries for styling, React hooks for behavior changes
6. **Accessibility**: Ensure touch targets are at least 44x44px on mobile devices
7. **Content Priority**: Show most important content first on smaller screens

## Testing Responsive Layouts

### Browser DevTools
- Use Chrome/Firefox DevTools device emulation
- Test common device presets (iPhone, iPad, etc.)
- Test both portrait and landscape orientations

### Recommended Test Devices
- Mobile: iPhone 12/13, Samsung Galaxy S21
- Tablet: iPad, iPad Pro, Samsung Galaxy Tab
- Desktop: 1366x768, 1920x1080, 2560x1440

## Resources

- [Ant Design Grid System](https://ant.design/components/grid/)
- [Ant Design Responsive Design](https://ant.design/docs/spec/responsive)
- [CSS Media Queries](https://developer.mozilla.org/en-US/docs/Web/CSS/Media_Queries)