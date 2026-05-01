# Icon System Design Specification

## Overview
This icon set provides 20+ category icons for financial tracking applications. All icons follow a consistent design language optimized for clarity at small sizes.

## Design Principles

### Grid System
- **Base size**: 24×24px
- **Safe area**: 20×20px (2px padding on all sides)
- **Alignment**: Icons centered on pixel grid
- **Keylines**: Circular (18px diameter), square (18×18px), rectangular (20×16px)

### Stroke Properties
- **Stroke width**: 2px (consistent across all icons)
- **Stroke cap**: Round (`stroke-linecap="round"`)
- **Stroke join**: Round (`stroke-linejoin="round"`)
- **Fill**: None (outline style only)

### Corner Radius
- **Small elements**: 1px radius
- **Large elements**: 2px radius
- **Circles**: Perfect circles using `<circle>` element

## Technical Specifications

### SVG Structure
```xml
<svg xmlns="http://www.w3.org/2000/svg" 
     viewBox="0 0 24 24" 
     fill="none" 
     stroke="currentColor" 
     stroke-width="2" 
     stroke-linecap="round" 
     stroke-linejoin="round">
  <!-- icon paths -->
</svg>
```

### Key Attributes
- `viewBox="0 0 24 24"`: Enables scaling without quality loss
- `stroke="currentColor"`: Inherits text color from parent element
- `fill="none"`: Maintains outline style

## File Naming Convention

**Pattern**: `category-{name}.svg`

**Examples**:
- `category-food.svg`
- `category-transport.svg`
- `category-shopping.svg`

**Rules**:
- All lowercase
- Hyphen-separated words
- Prefix with `category-`
- Use descriptive, concise names

## Icon Categories

| Icon Name | Use Case | Visual Metaphor |
|-----------|----------|----------------|
| food | Dining, groceries | Cooking pot |
| transport | Vehicles, fuel | Car |
| shopping | Retail purchases | Shopping cart |
| entertainment | Movies, games | Play button |
| health | Medical, fitness | Heart rate |
| education | Books, courses | Book |
| housing | Rent, mortgage | House |
| utilities | Electric, water | Waveform |
| communication | Phone, internet | Chat bubble |
| insurance | All insurance types | Shield |
| travel | Trips, hotels | Luggage |
| personal-care | Beauty, grooming | Tag |
| pets | Pet supplies | Paw prints |
| gifts | Presents | Gift box |
| subscriptions | Recurring services | Layers |
| taxes | Tax payments | Dollar sign |
| investments | Stocks, funds | Bar chart |
| charity | Donations | Heart |
| business | Business expenses | Briefcase |
| fees | Bank fees, charges | Alert circle |
| other | Miscellaneous | Ellipsis |
| income | Salary, revenue | Trending up |
| savings | Savings transfers | Dollar coin |
| debt | Loan payments | Trending down |

## Usage in HTML

### Inline SVG
```html
<svg class="icon" width="24" height="24">
  <use href="#icon-food"></use>
</svg>
```

### CSS Sizing
```css
.icon {
  width: 24px;
  height: 24px;
  color: var(--icon-color);
}

.icon-lg {
  width: 32px;
  height: 32px;
}

.icon-sm {
  width: 16px;
  height: 16px;
}
```

### Color Application
Icons use `currentColor` and inherit from parent:
```html
<div style="color: #3b82f6;">
  <svg><!-- icon inherits blue color --></svg>
</div>
```

## Accessibility

### ARIA Labels
```html
<svg role="img" aria-label="Food category">
  <title>Food</title>
  <!-- paths -->
</svg>
```

### Decorative Icons
```html
<svg aria-hidden="true" focusable="false">
  <!-- paths -->
</svg>
```

## Export Settings

### For Web
- Format: SVG
- Decimal precision: 2
- Remove editor data: Yes
- Minify: Yes (production)
- SVGO optimization recommended

### Optimization
```bash
# Using SVGO
svgo --multipass --pretty category-*.svg
```

## Version History
- **v1.0** (2024): Initial 24-icon set with consistent 2px stroke system

## License
These icons follow the project's overall license. Free for use within this application.