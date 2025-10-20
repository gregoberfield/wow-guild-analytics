# Dark Theme Implementation

## Overview
The WoW Guild Analytics application has been updated with a dark theme featuring:
- **Black background** (#000000) for all pages
- **Blue navbar/banner** (#0d6efd) for navigation
- **Adjusted text and chart colors** for optimal visibility

## Changes Made

### 1. CSS Styles (`app/static/css/style.css`)

#### Background Colors
- **Body**: Black (#000000)
- **Cards**: Dark gray (#1a1a1a) with subtle border (#333)
- **Card headers**: Slightly lighter gray (#2a2a2a)
- **Footer**: Dark gray (#1a1a1a)

#### Text Colors
- **Primary text**: Light gray (#e0e0e0)
- **Headings**: White (#ffffff)
- **Muted text**: Medium gray (#b0b0b0)
- **Links**: Light blue (#69b4ff)
- **Link hover**: Lighter blue (#9fcdff)

#### Navigation
- **Navbar background**: Blue (#0d6efd)
- **Navbar text**: White (#ffffff)
- **Navbar hover**: Light blue (#cfe2ff)
- **Added icons**: Trophy, house, sync icons

#### Tables
- **Background**: Dark gray (#1a1a1a)
- **Headers**: Darker gray (#2a2a2a) with white text
- **Borders**: Dark borders (#333, #444)
- **Striped rows**: Slightly lighter (#1f1f1f)
- **Hover**: Highlights row (#2a2a2a)

#### Forms
- **Inputs**: Dark gray (#2a2a2a) with light text
- **Focus**: Blue border with subtle glow
- **Labels**: Light gray text
- **Help text**: Medium gray

#### Buttons
- **Primary**: Blue (#0d6efd)
- **Success**: Green (#198754)
- **Hover effects**: Darker shades

#### Alerts
- **Success**: Dark green background (#0f5132)
- **Danger**: Dark red background (#842029)
- **Info**: Dark cyan background (#055160)
- **Close button**: Inverted colors for visibility

#### Additional Elements
- **Cards**: Enhanced shadows using white (not black)
- **Code blocks**: Dark background with light blue text
- **Badges**: Blue background
- **List groups**: Dark styling with borders

### 2. Chart.js Configuration (`app/templates/guild_detail.html`)

#### Global Defaults
```javascript
Chart.defaults.color = '#e0e0e0';  // Text color
Chart.defaults.borderColor = '#444';  // Borders
Chart.defaults.backgroundColor = '#1a1a1a';  // Background
```

#### Scale Colors
- **Grid lines**: Dark gray (#333)
- **Tick labels**: Light gray (#e0e0e0)
- **Axis titles**: White (#ffffff)

#### Plugin Colors
- **Legend labels**: Light gray (#e0e0e0)
- **Tooltip background**: Semi-transparent black with blue border
- **Tooltip text**: White and light gray

#### Chart-Specific Updates
- **Race distribution**: Changed from dark blue (#0070DE) to light blue (#69b4ff)
- **Spec labels**: Changed text color from dark (#333) to light (#e0e0e0)

### 3. Template Updates

#### Base Template (`app/templates/base.html`)
- Removed `bg-dark` class from navbar (now styled via CSS)
- Removed `bg-light` and `text-muted` from footer
- Added Bootstrap icons to navigation:
  - Trophy icon for brand
  - House icon for Home
  - Sync icon for Sync Guild
  - Gear icon for footer

#### Guild Detail Template
- Chart defaults configured at the top of script block
- Spec label plugin updated for light text

## Color Palette

### Primary Colors
| Element | Color | Hex Code |
|---------|-------|----------|
| Background | Black | #000000 |
| Navbar | Blue | #0d6efd |
| Cards | Dark Gray | #1a1a1a |
| Card Headers | Medium Gray | #2a2a2a |

### Text Colors
| Element | Color | Hex Code |
|---------|-------|----------|
| Primary Text | Light Gray | #e0e0e0 |
| Headings | White | #ffffff |
| Muted Text | Medium Gray | #b0b0b0 |
| Links | Light Blue | #69b4ff |

### Border/Accent Colors
| Element | Color | Hex Code |
|---------|-------|----------|
| Light Borders | Medium Gray | #444 |
| Dark Borders | Dark Gray | #333 |
| Chart Grid | Dark Gray | #333 |

### WoW Class Colors (Unchanged)
The official WoW class colors remain the same as they're designed to be vibrant and visible on any background:
- Warrior: #C41F3B (Dark Red)
- Paladin: #F58CBA (Pink)
- Hunter: #ABD473 (Green)
- Rogue: #FFF569 (Yellow)
- Priest: #FFFFFF (White)
- Shaman: #0070DE (Blue)
- Mage: #69CCF0 (Cyan)
- Warlock: #9482C9 (Purple)
- Druid: #FF7D0A (Orange)
- Death Knight: #C41E3A (Red)
- Monk: #00FF96 (Jade)
- Demon Hunter: #A330C9 (Purple)

## Accessibility

### Contrast Ratios
All text colors meet WCAG AA standards for contrast:
- White text (#ffffff) on black background: 21:1
- Light gray text (#e0e0e0) on black background: 16.5:1
- Medium gray (#b0b0b0) on dark backgrounds: 8:1+

### Visual Hierarchy
- **Headings**: Brightest (white)
- **Body text**: Medium brightness (light gray)
- **Secondary text**: Lower brightness (medium gray)
- **Accents**: Blue tones for interactive elements

## User Experience Benefits

### Reduced Eye Strain
- Dark backgrounds reduce screen brightness
- Better for extended viewing sessions
- Particularly helpful in low-light environments

### Visual Focus
- Blue navbar draws attention to navigation
- Class colors pop against dark background
- Charts are more visually striking

### Professional Appearance
- Modern, sleek aesthetic
- Matches gaming application conventions
- Consistent with WoW's dark UI themes

## Browser Compatibility

The dark theme works in all modern browsers:
- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- Mobile browsers: Full support

## Future Enhancements

Potential improvements:
- Theme toggle (light/dark mode switch)
- Custom theme colors per guild faction (Horde red vs Alliance blue)
- Adjustable contrast levels
- High contrast mode for accessibility
- Dark mode respecting OS preferences

## Testing Checklist

- [x] All pages render with black background
- [x] Navbar displays in blue
- [x] All text is readable (sufficient contrast)
- [x] Forms are usable with visible inputs
- [x] Tables display correctly with alternating rows
- [x] Charts render with appropriate colors
- [x] Tooltips are visible
- [x] Links are distinguishable
- [x] Buttons have proper styling
- [x] Alerts are readable
- [x] Icons are visible
- [x] No white flashes on page load
