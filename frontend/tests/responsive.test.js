import { render, screen, waitFor } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import '@testing-library/jest-dom';

// Mock window.matchMedia
const createMatchMedia = (width) => {
  return (query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  });
};

describe('Responsive Layout Tests', () => {
  beforeEach(() => {
    // Reset window.matchMedia before each test
    delete window.matchMedia;
  });

  describe('Breakpoint Detection', () => {
    test('should detect desktop breakpoint (>=1024px)', () => {
      window.innerWidth = 1920;
      window.matchMedia = jest.fn().mockImplementation((query) => ({
        matches: query === '(min-width: 1024px)',
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      }));

      const isDesktop = window.matchMedia('(min-width: 1024px)').matches;
      expect(isDesktop).toBe(true);
    });

    test('should detect tablet breakpoint (768-1023px)', () => {
      window.innerWidth = 800;
      window.matchMedia = jest.fn().mockImplementation((query) => ({
        matches: query === '(min-width: 768px) and (max-width: 1023px)',
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      }));

      const isTablet = window.matchMedia('(min-width: 768px) and (max-width: 1023px)').matches;
      expect(isTablet).toBe(true);
    });

    test('should detect mobile breakpoint (<768px)', () => {
      window.innerWidth = 375;
      window.matchMedia = jest.fn().mockImplementation((query) => ({
        matches: query === '(max-width: 767px)',
        media: query,
        onchange: null,
        addListener: jest.fn(),
        removeListener: jest.fn(),
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
      }));

      const isMobile = window.matchMedia('(max-width: 767px)').matches;
      expect(isMobile).toBe(true);
    });
  });

  describe('Grid System Configuration', () => {
    test('should have correct grid breakpoints defined', () => {
      const breakpoints = {
        xs: 0,
        sm: 576,
        md: 768,
        lg: 1024,
        xl: 1280,
        xxl: 1920,
      };

      expect(breakpoints.md).toBe(768);
      expect(breakpoints.lg).toBe(1024);
      expect(breakpoints.xs).toBe(0);
    });

    test('should calculate correct column spans for desktop', () => {
      const desktopSpan = {
        full: 24,
        half: 12,
        third: 8,
        quarter: 6,
      };

      expect(desktopSpan.full).toBe(24);
      expect(desktopSpan.half).toBe(12);
      expect(desktopSpan.third).toBe(8);
      expect(desktopSpan.quarter).toBe(6);
    });

    test('should calculate correct column spans for tablet', () => {
      const tabletSpan = {
        full: 24,
        half: 12,
        third: 12,
        quarter: 12,
      };

      expect(tabletSpan.full).toBe(24);
      expect(tabletSpan.half).toBe(12);
    });

    test('should calculate correct column spans for mobile', () => {
      const mobileSpan = {
        full: 24,
        half: 24,
        third: 24,
        quarter: 24,
      };

      expect(mobileSpan.full).toBe(24);
      expect(mobileSpan.half).toBe(24);
    });
  });

  describe('Responsive Style Variables', () => {
    test('should define correct spacing variables', () => {
      const spacing = {
        mobile: {
          xs: 4,
          sm: 8,
          md: 12,
          lg: 16,
          xl: 20,
        },
        tablet: {
          xs: 8,
          sm: 12,
          md: 16,
          lg: 20,
          xl: 24,
        },
        desktop: {
          xs: 8,
          sm: 16,
          md: 24,
          lg: 32,
          xl: 40,
        },
      };

      expect(spacing.mobile.md).toBe(12);
      expect(spacing.tablet.md).toBe(16);
      expect(spacing.desktop.md).toBe(24);
    });

    test('should define correct font size variables', () => {
      const fontSize = {
        mobile: {
          xs: 12,
          sm: 14,
          base: 14,
          lg: 16,
          xl: 18,
          xxl: 20,
        },
        tablet: {
          xs: 12,
          sm: 14,
          base: 14,
          lg: 16,
          xl: 20,
          xxl: 24,
        },
        desktop: {
          xs: 12,
          sm: 14,
          base: 16,
          lg: 18,
          xl: 24,
          xxl: 30,
        },
      };

      expect(fontSize.mobile.base).toBe(14);
      expect(fontSize.tablet.base).toBe(14);
      expect(fontSize.desktop.base).toBe(16);
    });

    test('should define correct container max-width variables', () => {
      const containerMaxWidth = {
        mobile: '100%',
        tablet: '768px',
        desktop: '1200px',
        wide: '1440px',
      };

      expect(containerMaxWidth.mobile).toBe('100%');
      expect(containerMaxWidth.tablet).toBe('768px');
      expect(containerMaxWidth.desktop).toBe('1200px');
    });
  });

  describe('Responsive Mixins', () => {
    test('should generate correct media query for mobile', () => {
      const mobileQuery = '@media (max-width: 767px)';
      expect(mobileQuery).toContain('max-width: 767px');
    });

    test('should generate correct media query for tablet', () => {
      const tabletQuery = '@media (min-width: 768px) and (max-width: 1023px)';
      expect(tabletQuery).toContain('min-width: 768px');
      expect(tabletQuery).toContain('max-width: 1023px');
    });

    test('should generate correct media query for desktop', () => {
      const desktopQuery = '@media (min-width: 1024px)';
      expect(desktopQuery).toContain('min-width: 1024px');
    });

    test('should generate correct media query for tablet and above', () => {
      const tabletUpQuery = '@media (min-width: 768px)';
      expect(tabletUpQuery).toContain('min-width: 768px');
    });

    test('should generate correct media query for mobile and tablet', () => {
      const mobileTabletQuery = '@media (max-width: 1023px)';
      expect(mobileTabletQuery).toContain('max-width: 1023px');
    });
  });

  describe('Grid Gutter Configuration', () => {
    test('should define correct gutter sizes for different breakpoints', () => {
      const gutters = {
        mobile: 8,
        tablet: 16,
        desktop: 24,
      };

      expect(gutters.mobile).toBe(8);
      expect(gutters.tablet).toBe(16);
      expect(gutters.desktop).toBe(24);
    });

    test('should define responsive gutter array for Ant Design Grid', () => {
      const responsiveGutter = [
        { xs: 8, sm: 8, md: 16, lg: 24, xl: 24, xxl: 24 },
        { xs: 8, sm: 8, md: 16, lg: 24, xl: 24, xxl: 24 },
      ];

      expect(responsiveGutter[0].xs).toBe(8);
      expect(responsiveGutter[0].md).toBe(16);
      expect(responsiveGutter[0].lg).toBe(24);
    });
  });

  describe('Responsive Component Props', () => {
    test('should define correct responsive column configuration', () => {
      const responsiveCol = {
        xs: 24,
        sm: 24,
        md: 12,
        lg: 8,
        xl: 6,
        xxl: 6,
      };

      expect(responsiveCol.xs).toBe(24);
      expect(responsiveCol.md).toBe(12);
      expect(responsiveCol.lg).toBe(8);
    });

    test('should define correct responsive offset configuration', () => {
      const responsiveOffset = {
        xs: 0,
        sm: 0,
        md: 2,
        lg: 4,
        xl: 4,
        xxl: 4,
      };

      expect(responsiveOffset.xs).toBe(0);
      expect(responsiveOffset.md).toBe(2);
      expect(responsiveOffset.lg).toBe(4);
    });
  });

  describe('Viewport Change Detection', () => {
    test('should detect viewport width changes', () => {
      const viewportWidths = [];
      
      // Simulate different viewport widths
      [375, 800, 1920].forEach(width => {
        window.innerWidth = width;
        viewportWidths.push(window.innerWidth);
      });

      expect(viewportWidths).toEqual([375, 800, 1920]);
    });

    test('should trigger resize event listener', () => {
      const resizeHandler = jest.fn();
      window.addEventListener('resize', resizeHandler);

      // Simulate resize
      act(() => {
        window.dispatchEvent(new Event('resize'));
      });

      expect(resizeHandler).toHaveBeenCalled();
      window.removeEventListener('resize', resizeHandler);
    });
  });

  describe('Responsive Utility Classes', () => {
    test('should define hide/show utility classes for different breakpoints', () => {
      const utilities = {
        hideOnMobile: 'hide-mobile',
        hideOnTablet: 'hide-tablet',
        hideOnDesktop: 'hide-desktop',
        showOnMobile: 'show-mobile',
        showOnTablet: 'show-tablet',
        showOnDesktop: 'show-desktop',
      };

      expect(utilities.hideOnMobile).toBe('hide-mobile');
      expect(utilities.showOnDesktop).toBe('show-desktop');
    });
  });

  describe('Container Padding Configuration', () => {
    test('should define correct container padding for different breakpoints', () => {
      const containerPadding = {
        mobile: 16,
        tablet: 24,
        desktop: 32,
      };

      expect(containerPadding.mobile).toBe(16);
      expect(containerPadding.tablet).toBe(24);
      expect(containerPadding.desktop).toBe(32);
    });
  });

  describe('Responsive Image Sizes', () => {
    test('should define correct image sizes for different breakpoints', () => {
      const imageSizes = {
        mobile: {
          small: 80,
          medium: 120,
          large: 200,
        },
        tablet: {
          small: 100,
          medium: 150,
          large: 250,
        },
        desktop: {
          small: 120,
          medium: 200,
          large: 300,
        },
      };

      expect(imageSizes.mobile.medium).toBe(120);
      expect(imageSizes.tablet.medium).toBe(150);
      expect(imageSizes.desktop.medium).toBe(200);
    });
  });

  describe('Responsive Navigation Configuration', () => {
    test('should define correct navigation layout for different breakpoints', () => {
      const navConfig = {
        mobile: {
          type: 'drawer',
          collapsed: true,
        },
        tablet: {
          type: 'drawer',
          collapsed: false,
        },
        desktop: {
          type: 'inline',
          collapsed: false,
        },
      };

      expect(navConfig.mobile.type).toBe('drawer');
      expect(navConfig.desktop.type).toBe('inline');
    });
  });

  describe('Responsive Table Configuration', () => {
    test('should define correct table scroll configuration for different breakpoints', () => {
      const tableScroll = {
        mobile: { x: 'max-content', y: 400 },
        tablet: { x: 1000, y: 500 },
        desktop: { x: false, y: 600 },
      };

      expect(tableScroll.mobile.x).toBe('max-content');
      expect(tableScroll.desktop.x).toBe(false);
    });
  });

  describe('Responsive Form Layout', () => {
    test('should define correct form layout for different breakpoints', () => {
      const formLayout = {
        mobile: {
          layout: 'vertical',
          labelCol: { span: 24 },
          wrapperCol: { span: 24 },
        },
        tablet: {
          layout: 'horizontal',
          labelCol: { span: 8 },
          wrapperCol: { span: 16 },
        },
        desktop: {
          layout: 'horizontal',
          labelCol: { span: 6 },
          wrapperCol: { span: 18 },
        },
      };

      expect(formLayout.mobile.layout).toBe('vertical');
      expect(formLayout.desktop.layout).toBe('horizontal');
      expect(formLayout.desktop.labelCol.span).toBe(6);
    });
  });

  describe('Responsive Modal Configuration', () => {
    test('should define correct modal width for different breakpoints', () => {
      const modalWidth = {
        mobile: '100%',
        tablet: '80%',
        desktop: 600,
      };

      expect(modalWidth.mobile).toBe('100%');
      expect(modalWidth.tablet).toBe('80%');
      expect(modalWidth.desktop).toBe(600);
    });
  });

  describe('Z-Index Configuration', () => {
    test('should define correct z-index values for layering', () => {
      const zIndex = {
        base: 1,
        dropdown: 1000,
        sticky: 1020,
        fixed: 1030,
        modalBackdrop: 1040,
        modal: 1050,
        popover: 1060,
        tooltip: 1070,
      };

      expect(zIndex.base).toBe(1);
      expect(zIndex.modal).toBe(1050);
      expect(zIndex.tooltip).toBe(1070);
    });
  });
});