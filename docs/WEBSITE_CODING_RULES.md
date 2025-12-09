# Website Coding Rules (Anti-Vibe-Coded Standard)

Use these rules on every web UI change to keep the experience intentional, premium, and consistent.

## 1) Foundations
- Spacing: Use a strict 4px or 8px scale for margin/padding/gaps. No ad-hoc values.
- Grid & layout: Align to a predictable grid; consistent section widths and gutters. No drifting or misaligned cards.
- Border radius: One scale only (e.g., 8px everywhere unless circular avatars). Do not mix radii.
- Elevation: One shadow style. Avoid glows and neon effects.

## 2) Typography
- Pick one heading face and one body face; define a type ramp with consistent line heights. No random weights.
- Body text: never ultra-light or ultra-bold. Maintain clear hierarchy and rhythm.
- Avoid emoji as UI decoration in headings/buttons; use proper icons when needed.

## 3) Color
- Small, disciplined palette; high contrast for legibility.
- Avoid purple gradients and neon effects unless explicitly part of the brand.
- Accents reinforce hierarchy; no gratuitous color-for-color’s-sake.

## 4) Components & System
- Use shared primitives (shadcn/ui in `web-ui/src/components/ui/`) and wrap them for brand variants. No one-off buttons/cards.
- Keep padding, radius, and alignment consistent across buttons, inputs, cards, modals, nav, badges.
- Loading states are mandatory for async actions (spinners/skeletons, disabled buttons).
- Responsive by default: verify mobile, tablet, desktop. No overflow or collapsed layouts.

## 5) Interaction & Motion
- Subtle hover/focus only; never layout-shifting lifts/rotations/bounces.
- Animation timing should feel natural; no wiggle/bounce gimmicks. Interactions must always function (tabs, accordions, modals, carousels).

## 6) Copy & Content
- Specific, grounded value propositions; avoid generic hero lines (“build your dreams”, “launch faster”).
- Testimonials must be real (name, role, link); no AI/stock avatars or filler quotes.
- Footer/copyright text accurate and professional.
- Remove placeholder text before shipping.

## 7) Media & Icons
- Icons sized proportionally to text; no massive icons with tiny labels.
- Social icons must link to real destinations or be omitted. No dummy “#” links.

## 8) Technical Hygiene
- Every page: title, meta description, OG image, favicon, and correct social preview.
- Alt text on images; accessible labels on form controls; focus states visible.
- No broken interactions; no unused controls; verify loading states.
- Performance: avoid heavy Lotties or assets that don’t match brand; keep interactions snappy.

## 9) Red-Flag Checklist (avoid all)
- Purple gradients without brand reason; sparkle/emoji overload; fake testimonials.
- Hover animations everywhere; misaligned grids; mixed radii; semi-transparent headers that hurt contrast.
- Missing loading states; broken responsiveness; non-functional buttons/toggles/links.
- Generic taglines; malformed copyright; placeholder links/icons.

## 10) Review Before Ship
- Run through spacing/typography/color consistency.
- Confirm loading states on all async flows.
- Test interactivity (tabs, accordions, modals, carousels, nav).
- Check mobile and desktop layouts.
- Verify meta/OG/favicon/social links and remove any placeholders.
