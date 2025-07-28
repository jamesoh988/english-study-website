# English Study Website - Layout Documentation

## 📐 Overall Layout Structure

### Desktop Layout (1620px+ screens)
```
┌─────────────────────────── 1620px (max-width) ──────────────────────────┐
│                                                                         │
│  ┌─────────┐  ┌─────────────────────────┐  ┌─────────────────────┐     │
│  │ History │  │      Main Content       │  │   Learning Links    │     │
│  │ Sidebar │  │        Area             │  │     Sidebar         │     │
│  │ 300px   │  │     500px~1000px        │  │       280px         │     │
│  │         │  │                         │  │                     │     │
│  └─────────┘  └─────────────────────────┘  └─────────────────────┘     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Mobile Layout (768px and below)
```
┌─────────────────────────────────┐
│          History Sidebar        │
│            (100%)               │
├─────────────────────────────────┤
│        Main Content Area        │
│            (100%)               │
├─────────────────────────────────┤
│       Learning Links Sidebar    │
│            (100%)               │
└─────────────────────────────────┘
```

## 🎨 Component Specifications

### 1. Header Section
- **Position**: Fixed top
- **Height**: 80px
- **Background**: Linear gradient (#4CAF50, #45a049)
- **Components**:
  - Logo: "🗣️ English Study"
  - Welcome Message: Dynamic user greeting (5-second display)
  - User Section: Login/Settings buttons

### 2. Main Container
- **Max Width**: 1620px
- **Margin**: Auto-centered
- **Gap**: 20px between sections
- **Padding**: 20px
- **Display**: Flexbox (horizontal on desktop, vertical on mobile)

### 3. Left Sidebar (Study History)
- **Width**: 300px (fixed, flex-shrink: 0)
- **Background**: White with gradient header
- **Components**:
  - Header: Orange gradient with "📚 Study History"
  - Action buttons: Select All, Delete
  - History list: Checkboxes + content items
  - Max height: calc(100vh - 200px)

### 4. Main Content Area
- **Width Range**: 500px ~ 1000px (responsive)
- **Default Width**: 1000px
- **Background**: White
- **Border Radius**: 15px
- **Components**:
  - Service Status Bar
  - English Text Input (150px height, fixed)
  - Voice Controls (Fast/Normal/Slow buttons)
  - Action Buttons (Translate/Save/Clear)
  - Translation Result Box (100px~300px height, scrollable)

### 5. Right Sidebar (Learning Resources)
- **Width**: 280px (fixed, flex-shrink: 0)
- **Background**: Purple gradient (#667eea → #764ba2)
- **Components**:
  - Header: "🎯 Learning Resources"
  - Categories: Grammar, Vocabulary, Pronunciation, Reading, Testing
  - External links with hover effects

## 🔧 CSS Flexbox Configuration

### Main Container
```css
.main-container {
    display: flex;
    justify-content: flex-start;
    max-width: 1620px;
    gap: 20px;
    width: 100%;
    box-sizing: border-box;
}
```

### Content Area Flexibility
```css
.content {
    flex: 1 1 auto;
    min-width: 500px;
    max-width: 1000px;
    flex-basis: 1000px;
}

.sidebar, .right-sidebar {
    flex-shrink: 0;
}
```

## 📱 Responsive Breakpoints

### Desktop (769px+)
- **Layout**: 3-column horizontal
- **Content Width**: 500px~1000px
- **Sidebars**: Fixed widths (300px, 280px)

### Tablet/Mobile (768px and below)
```css
@media (max-width: 768px) {
    .main-container {
        flex-direction: column;
        padding: 10px;
        gap: 15px;
    }
    
    .sidebar, .right-sidebar, .content {
        width: 100%;
        max-width: none;
        min-width: auto;
    }
    
    .right-sidebar { order: 3; }
    .content { order: 2; }
    .sidebar { order: 1; }
}
```

### Small Mobile (480px and below)
- **Padding**: Reduced to 5px
- **Font sizes**: Smaller
- **Button layouts**: Vertical stacking

## 🎯 Key Layout Features

### Fixed Elements
- ✅ **Text Input Height**: 150px (prevents random resizing)
- ✅ **Sidebar Widths**: 300px (left) + 280px (right)
- ✅ **Header Height**: 80px
- ✅ **Max Container Width**: 1620px

### Flexible Elements
- ✅ **Main Content**: 500px~1000px range
- ✅ **Translation Box**: 100px~300px height with scroll
- ✅ **Left Margin**: Responsive to screen size

### Visual Enhancements
- ✅ **Border Radius**: 15px for main sections
- ✅ **Box Shadows**: 0 5px 20px rgba(0,0,0,0.1)
- ✅ **Gradients**: Custom for each sidebar
- ✅ **Animations**: Welcome message slide-in

## 🖱️ Interactive Elements

### Button Styles
- **Voice Buttons**: 3D hover effects with service status badges
- **Action Buttons**: Gradient backgrounds with icons
- **Learning Links**: Hover animations with lift effect

### Form Elements
- **Text Area**: Fixed height with auto-scroll
- **Checkboxes**: Custom styling for history items
- **Status Indicators**: Dynamic color-coded badges

## 📊 Spacing System

### Gaps and Padding
- **Container Gap**: 20px (desktop), 15px (tablet), 10px (mobile)
- **Section Padding**: 30px (desktop), 20px (tablet), 15px (mobile)
- **Button Gaps**: 15px (desktop), 10px (mobile)

### Margins
- **Top Margin**: 80px (header height)
- **Auto Centering**: Left/right margins auto
- **Component Margins**: 15px between major sections

## 🎨 Color Scheme

### Primary Colors
- **Green Theme**: #4CAF50 (primary), #45a049 (dark)
- **Orange Accent**: #FF9800, #F57C00 (sidebar header)
- **Purple Gradient**: #667eea → #764ba2 (right sidebar)

### Background Colors
- **Main Background**: White
- **Header**: Linear gradient green
- **Cards**: #f8f9fa with colored borders
- **Translation Box**: Light green gradient

## 📈 Performance Considerations

### CSS Optimizations
- **Box-sizing**: border-box for predictable sizing
- **Flex-shrink**: 0 for fixed-width sidebars
- **Max-height**: Prevents content overflow
- **Overflow**: Auto for scrollable areas

### Responsive Strategy
- **Mobile-first**: Base styles optimized for mobile
- **Progressive Enhancement**: Desktop features added via media queries
- **Content Priority**: Important content accessible on all devices

---

**Last Updated**: January 2025  
**Version**: 2.0  
**Responsive**: Desktop + Tablet + Mobile  
**Browser Support**: Modern browsers with Flexbox support