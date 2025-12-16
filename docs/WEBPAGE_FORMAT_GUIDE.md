# Sacred Digital Dreamweaver - Webpage Format Guide

**Version:** 1.0
**Purpose:** Canonical design system reference for ALL webpage generation.
**Usage:** This document MUST be consulted every time a webpage, landing page, or web content is generated.

---

## Quick Reference - The Essentials

| Property | Dark Mode (Primary) | Light Mode |
|----------|---------------------|------------|
| **Background** | `#0A0A1A` / `oklch(0.145 0 0)` | `#FFFFFF` / `oklch(1 0 0)` |
| **Text (Primary)** | `#FAFAFA` / `oklch(0.985 0 0)` | `#1A1A1A` / `oklch(0.145 0 0)` |
| **Text (Muted)** | `#A3A3A3` / `oklch(0.708 0 0)` | `#737373` / `oklch(0.556 0 0)` |
| **Card Background** | `#262626` / `oklch(0.205 0 0)` | `#FFFFFF` / `oklch(1 0 0)` |
| **Accent (Gold)** | `#FFD700` | `#B8860B` |
| **Border** | `rgba(255,255,255,0.10)` | `#E5E5E5` |

---

## 1. Color System

### 1.1 Dark Mode (Default for Dreamweaver Content)

Dark mode is the PRIMARY theme for Dreamweaver content - it creates the sacred, mystical atmosphere essential to our brand.

```css
/* Dark Mode - Primary Theme */
--background: oklch(0.145 0 0);        /* #1A1A1A - Near black */
--foreground: oklch(0.985 0 0);        /* #FAFAFA - Off-white text */
--card: oklch(0.205 0 0);              /* #262626 - Dark gray cards */
--card-foreground: oklch(0.985 0 0);   /* Off-white text on cards */
--muted: oklch(0.269 0 0);             /* Medium dark gray */
--muted-foreground: oklch(0.708 0 0);  /* Muted text */
--border: oklch(1 0 0 / 10%);          /* White with 10% opacity */
--input: oklch(1 0 0 / 15%);           /* White with 15% opacity */
```

### 1.2 Light Mode (Alternative)

```css
/* Light Mode - Alternative */
--background: oklch(0.985 0 0);        /* Slightly off-white so cards/popovers separate */
--foreground: oklch(0.145 0 0);        /* Dark charcoal text */
--card: oklch(1 0 0);                  /* White cards */
--card-foreground: oklch(0.145 0 0);   /* Dark text */
--muted: oklch(0.97 0 0);              /* Light gray */
--muted-foreground: oklch(0.556 0 0);  /* Gray text */
--border: oklch(0.9 0 0);              /* Stronger separators on near-white surfaces */
```

### 1.3 Sacred Color Palettes

Choose palette based on session/page theme:

#### Sacred Light (Divine/Spiritual)
```
Primary:    #FFD700 (Gold)
Secondary:  #F4E4BC (Warm cream)
Accent:     #FFFFFF (Pure white glow)
Background: #0A0A1A (Deep cosmic blue-black)
```

#### Cosmic Journey (Space/Astral)
```
Primary:    #9B6DFF (Mystic purple)
Secondary:  #64B5F6 (Celestial blue)
Accent:     #FF6B9D (Ethereal pink)
Background: #0D0221 (Deep space purple)
```

#### Garden Eden (Nature/Paradise)
```
Primary:    #50C878 (Emerald green)
Secondary:  #FFD700 (Sunlight gold)
Accent:     #FFFFFF (Divine light)
Background: #0F2818 (Forest shadow)
```

#### Ancient Temple (Historical/Mystical)
```
Primary:    #D4AF37 (Antique gold)
Secondary:  #8B4513 (Warm bronze)
Accent:     #FFF8DC (Candlelight)
Background: #1A0F0A (Temple shadow)
```

#### Neural Network (Tech/Consciousness)
```
Primary:    #00D4FF (Cyan)
Secondary:  #9B6DFF (Purple)
Accent:     #FF6B9D (Pink glow)
Background: #0A0A1A (Void black)
```

---

## 2. Typography

### 2.1 Font Stack

```css
/* Primary (Body Text) */
font-family: var(--font-geist-sans), system-ui, -apple-system, sans-serif;

/* Monospace (Code/Technical) */
font-family: var(--font-geist-mono), 'Fira Code', monospace;
```

### 2.2 Type Scale

| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| H1 | 2.5rem (40px) | 600 | 1.2 |
| H2 | 2rem (32px) | 600 | 1.3 |
| H3 | 1.5rem (24px) | 600 | 1.4 |
| H4 | 1.25rem (20px) | 600 | 1.5 |
| Body | 1rem (16px) | 400 | 1.6 |
| Small | 0.875rem (14px) | 400 | 1.5 |
| Caption | 0.75rem (12px) | 500 | 1.4 |

### 2.3 Text Styling

```css
/* Primary headings */
.heading-primary {
  color: var(--foreground);
  font-weight: 600;
  letter-spacing: -0.025em;
}

/* Body text */
.body-text {
  color: var(--foreground);
  line-height: 1.6;
}

/* Muted/secondary text */
.text-muted {
  color: var(--muted-foreground);
}

/* Accent labels */
.label-accent {
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #B8860B; /* Dark gold for light mode */
  /* OR #FFD700 for dark mode */
}
```

---

## 3. Layout System

### 3.1 Container Widths

```css
/* Max content width */
max-width: 72rem (1152px);

/* Padding */
padding-x: 1.5rem (24px);      /* Mobile */
padding-x: 2rem (32px);        /* Desktop */

/* Vertical spacing */
padding-y: 3rem (48px);        /* Mobile */
padding-y: 4rem (64px);        /* Desktop */
```

### 3.2 Grid System

```css
/* Standard content grid */
.content-grid {
  display: grid;
  gap: 1.5rem;
}

/* Two-column (desktop) */
@media (min-width: 1024px) {
  .content-grid-2col {
    grid-template-columns: 1.3fr 1fr;
  }
}

/* Card grid */
.card-grid {
  display: grid;
  gap: 1.25rem;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
}
```

### 3.3 Spacing Scale

| Name | Value | Use Case |
|------|-------|----------|
| xs | 0.25rem (4px) | Tight inline spacing |
| sm | 0.5rem (8px) | Compact elements |
| md | 1rem (16px) | Standard spacing |
| lg | 1.5rem (24px) | Section padding |
| xl | 2.5rem (40px) | Major sections |
| 2xl | 4rem (64px) | Page sections |

---

## 4. Component Patterns

### 4.1 Cards

```css
/* Standard card */
.card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 0.75rem (12px);
  padding: 1.5rem;
}

/* Dark mode card (for light backgrounds) */
.card-dark {
  background: #0F172A;
  color: #FFFFFF;
  border: 1px solid rgba(255,255,255,0.1);
}

/* Glass effect card */
.card-glass {
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(0,0,0,0.1);
}
```

### 4.2 Buttons

```css
/* Primary button */
.btn-primary {
  background: var(--primary);
  color: var(--primary-foreground);
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-weight: 500;
}

/* Secondary/outline button */
.btn-outline {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--foreground);
}

/* Ghost button */
.btn-ghost {
  background: transparent;
  color: var(--foreground);
}

/* Accent button (gold) */
.btn-accent {
  background: #FFD700;
  color: #0A0A1A;
  font-weight: 600;
}
```

### 4.3 Badges

```css
/* Standard badge */
.badge {
  display: inline-flex;
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 9999px;
  background: var(--muted);
  color: var(--muted-foreground);
}

/* Outline badge */
.badge-outline {
  background: transparent;
  border: 1px solid var(--border);
}
```

### 4.4 Border Radius Scale

```css
--radius-sm: 0.375rem (6px);   /* Small elements, badges */
--radius-md: 0.5rem (8px);     /* Buttons, inputs */
--radius-lg: 0.625rem (10px);  /* Cards */
--radius-xl: 1rem (16px);      /* Large cards, sections */
--radius-2xl: 1.5rem (24px);   /* Hero sections */
--radius-full: 9999px;         /* Pills, avatars */
```

---

## 5. Page Structure Template

### 5.1 Standard Page Layout

```html
<div class="min-h-screen bg-background text-foreground">
  <!-- Hero Section -->
  <section class="relative">
    <div class="mx-auto max-w-6xl px-6 py-16 lg:px-8">
      <!-- Content -->
    </div>
  </section>

  <!-- Content Sections -->
  <main class="mx-auto max-w-6xl px-6 py-12 lg:px-8">
    <section class="space-y-8">
      <!-- Section content -->
    </section>
  </main>

  <!-- Footer -->
  <footer class="border-t border-border">
    <div class="mx-auto max-w-6xl px-6 py-12 lg:px-8">
      <!-- Footer content -->
    </div>
  </footer>
</div>
```

### 5.2 Dark Mode Page (Dreamweaver Default)

```html
<div class="dark min-h-screen bg-[#0A0A1A] text-white">
  <main class="mx-auto max-w-6xl px-6 py-12 lg:px-8">
    <!-- Content with dark theme -->
  </main>
</div>
```

### 5.3 Gradient Background (Light Mode Alternative)

```html
<div class="min-h-screen bg-gradient-to-b from-slate-50 via-white to-amber-50 text-slate-900">
  <!-- Content -->
</div>
```

---

## 6. Visual Effects

### 6.1 Glow Effects

```css
/* Text glow (for titles on dark backgrounds) */
.text-glow {
  text-shadow:
    0 0 20px rgba(255, 215, 0, 0.5),
    0 0 40px rgba(255, 215, 0, 0.3);
}

/* Box glow (for cards/elements) */
.box-glow {
  box-shadow:
    0 0 30px rgba(255, 215, 0, 0.2),
    0 0 60px rgba(255, 215, 0, 0.1);
}

/* Subtle shadow */
.shadow-subtle {
  box-shadow:
    0 1px 3px rgba(0, 0, 0, 0.1),
    0 1px 2px rgba(0, 0, 0, 0.06);
}
```

### 6.2 Gradients

```css
/* Sacred gradient (dark to cosmic) */
.gradient-sacred {
  background: linear-gradient(180deg, #0A0A1A 0%, #0D0221 100%);
}

/* Gold accent gradient */
.gradient-gold {
  background: linear-gradient(135deg, #FFD700 0%, #B8860B 100%);
}

/* Ethereal gradient */
.gradient-ethereal {
  background: linear-gradient(180deg,
    rgba(155, 109, 255, 0.1) 0%,
    rgba(100, 181, 246, 0.1) 100%
  );
}
```

### 6.3 Animations

```css
/* Subtle fade-in */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Gentle pulse (for CTAs) */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

/* Glow pulse */
@keyframes glowPulse {
  0%, 100% { box-shadow: 0 0 20px rgba(255, 215, 0, 0.3); }
  50% { box-shadow: 0 0 40px rgba(255, 215, 0, 0.5); }
}
```

---

## 7. Responsive Breakpoints

```css
/* Mobile first */
/* Default: 0px+ */

/* Tablet */
@media (min-width: 640px) { /* sm */ }

/* Small desktop */
@media (min-width: 768px) { /* md */ }

/* Desktop */
@media (min-width: 1024px) { /* lg */ }

/* Large desktop */
@media (min-width: 1280px) { /* xl */ }

/* Extra large */
@media (min-width: 1536px) { /* 2xl */ }
```

---

## 8. Accessibility Requirements

### 8.1 Color Contrast

| Context | Minimum Ratio |
|---------|---------------|
| Normal text | 4.5:1 |
| Large text (18px+) | 3:1 |
| UI components | 3:1 |

### 8.2 Focus States

```css
/* Focus ring */
:focus-visible {
  outline: 2px solid var(--ring);
  outline-offset: 2px;
}

/* Skip to content link */
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
  z-index: 100;
}
.skip-link:focus {
  top: 0;
}
```

### 8.3 Required Attributes

- All images: `alt` text
- All links: descriptive text (not "click here")
- Form inputs: associated `<label>`
- Interactive elements: visible focus state
- Color alone never conveys meaning

---

## 9. SEO & Metadata

### 9.1 Required Meta Tags

```html
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{Page Title} | Sacred Digital Dreamweaver</title>
  <meta name="description" content="{155 char description}">

  <!-- Open Graph -->
  <meta property="og:title" content="{Title}">
  <meta property="og:description" content="{Description}">
  <meta property="og:image" content="{Thumbnail URL}">
  <meta property="og:type" content="website">

  <!-- Twitter -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{Title}">
  <meta name="twitter:description" content="{Description}">
</head>
```

### 9.2 Structured Data

Always include JSON-LD for:
- WebSite schema
- FAQPage (if applicable)
- Article (for blog posts)
- Product (for session pages)

---

## 10. Brand Elements

### 10.1 Logo Usage

- Minimum clear space: 1x logo height on all sides
- Minimum size: 24px height
- Dark backgrounds: White or gold logo
- Light backgrounds: Dark or gold logo

### 10.2 Icon System

Use Lucide React icons consistently:
```tsx
import { Sparkles, MoonStar, Compass, Shield } from "lucide-react";

// Standard size
<Sparkles className="h-5 w-5" />

// With accent color
<Sparkles className="h-5 w-5 text-amber-600" />
```

### 10.3 Sacred Imagery Guidelines

- Luminous center with dark vignette edges
- Sacred geometry elements
- Ethereal, volumetric lighting
- Color temperature: warm (gold) focal points on cool backgrounds

---

## 11. Code Examples

### 11.1 Dark Mode Section

```tsx
<section className="bg-slate-900 text-white rounded-2xl p-6">
  <div className="flex items-center gap-2 mb-4">
    <Sparkles className="h-5 w-5 text-amber-400" />
    <p className="text-sm font-semibold uppercase tracking-wide text-amber-400">
      Section Label
    </p>
  </div>
  <h3 className="text-xl font-semibold mb-3">Section Title</h3>
  <p className="text-slate-200 mb-4">Description text here.</p>
  <Button variant="secondary" className="bg-white text-slate-900">
    Call to Action
  </Button>
</section>
```

### 11.2 Card Component

```tsx
<Card className="bg-white/80 border-slate-200 ring-1 ring-slate-200">
  <CardHeader>
    <CardTitle className="flex items-center gap-2">
      <Shield className="h-5 w-5 text-amber-600" />
      Card Title
    </CardTitle>
    <CardDescription>Card description text.</CardDescription>
  </CardHeader>
  <CardContent>
    <p className="text-slate-700">Content here.</p>
  </CardContent>
  <CardFooter className="justify-end">
    <Button variant="ghost" className="gap-2">
      Action
      <ArrowRight className="h-4 w-4" />
    </Button>
  </CardFooter>
</Card>
```

### 11.3 Hero Section

```tsx
<section className="relative overflow-hidden">
  <div className="absolute inset-0 bg-gradient-to-b from-slate-50 via-white to-amber-50" />
  <div className="relative mx-auto max-w-6xl px-6 py-16 lg:px-8">
    <div className="space-y-6 max-w-3xl">
      <div className="inline-flex items-center gap-2 rounded-full bg-white/70 px-3 py-1 text-sm font-medium shadow-sm ring-1 ring-slate-200">
        <Sparkles className="h-4 w-4 text-amber-600" />
        Badge Text
      </div>
      <h1 className="text-4xl font-semibold leading-tight tracking-tight sm:text-5xl">
        Page Title Here
      </h1>
      <p className="text-lg text-slate-700">
        Subtitle or description text.
      </p>
    </div>
  </div>
</section>
```

---

## 12. Checklist - Before Publishing

Every webpage MUST pass this checklist:

### Visual
- [ ] Dark background (#0A0A1A) OR light gradient (slate-50 to amber-50)
- [ ] White/off-white primary text
- [ ] Gold (#FFD700) or amber accents
- [ ] Consistent spacing (use spacing scale)
- [ ] Proper border radius (use radius scale)
- [ ] Glow effects on key elements (dark mode)

### Typography
- [ ] Geist font family
- [ ] Proper heading hierarchy (H1 → H2 → H3)
- [ ] Body text at 1rem with 1.6 line-height
- [ ] Accent labels uppercase with tracking

### Components
- [ ] Cards have proper padding and borders
- [ ] Buttons use defined variants
- [ ] Badges are consistent
- [ ] Icons from Lucide at standard sizes

### Accessibility
- [ ] Color contrast passes WCAG AA
- [ ] All images have alt text
- [ ] Focus states visible
- [ ] Semantic HTML structure

### SEO
- [ ] Title tag with brand
- [ ] Meta description (155 chars)
- [ ] Open Graph tags
- [ ] Structured data where applicable

---

## 13. Anti-Patterns (NEVER Use)

**CRITICAL:** These patterns break theme switching and cause unreadable text. Never use them at page level.

### 13.1 Forbidden Color Classes

| Pattern | Why It's Wrong | Use Instead |
|---------|----------------|-------------|
| `text-white` | Becomes invisible in light mode | `text-foreground` |
| `bg-white` | Breaks in dark mode | `bg-background` |
| `text-black` | Becomes invisible in dark mode | `text-foreground` |
| `bg-black` | Breaks in light mode | `bg-background` |
| `text-gray-*` | Ignores theme tokens | `text-muted-foreground` |
| `bg-gray-*` | Ignores theme tokens | `bg-muted` or `bg-card` |
| `bg-[#hex]` | Hardcoded color | Use CSS variable |
| `dark:text-white` | Redundant with semantic tokens | `text-foreground` |
| `dark:bg-black` | Redundant with semantic tokens | `bg-background` |

### 13.2 When Hardcoded Colors ARE Acceptable

- **Inside self-contained components** with their own background (e.g., a card that is always dark regardless of theme)
- **Brand colors** that must remain constant (logos)
- **Decorative elements** that don't affect readability
- **Gradient color stops** where CSS variables aren't practical

### 13.3 Semantic Token Quick Reference

| Need | Use This |
|------|----------|
| Page background | `bg-background` |
| Primary text | `text-foreground` |
| Secondary/muted text | `text-muted-foreground` |
| Card background | `bg-card` |
| Card text | `text-card-foreground` |
| Border color | `border-border` |
| Input background | `bg-input` |
| Success state | `text-success` / `bg-success` |
| Warning state | `text-warning` / `bg-warning` |
| Error/destructive | `text-destructive` / `bg-destructive` |
| Primary accent | `text-primary` / `bg-primary` |

### 13.4 Body Default (Already Configured)

The body element in globals.css already applies:
```css
body {
  @apply bg-background text-foreground;
}
```

This means most pages automatically inherit correct theme colors. Only use explicit color classes when you need to override within a section.

### 13.5 Common Migration Examples

**Before (WRONG):**
```tsx
<div className="bg-[#0D0221] text-white">
  <p className="text-gray-300">Muted text</p>
</div>
```

**After (CORRECT):**
```tsx
<div className="bg-background text-foreground">
  <p className="text-muted-foreground">Muted text</p>
</div>
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | 2025-12 | Added Anti-Patterns section (Section 13) |
| 1.0 | 2024-12 | Initial release |

---

*This document is the single source of truth for all Sacred Digital Dreamweaver web design. When generating any webpage, landing page, or web content, reference this guide first.*
