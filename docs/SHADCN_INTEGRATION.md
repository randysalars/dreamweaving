# shadcn/ui Integration Plan

Goal: give this repo a ready-to-use UI playground that uses shadcn/ui (Next.js + Tailwind). This is additive and lives alongside the Python audio tooling.

## Quick scaffold (one-time)
```bash
# 1) Create the playground
cd /home/rsalars/Projects/dreamweaving
npx create-next-app@latest web-ui \
  --typescript --tailwind --eslint --app --src-dir false \
  --import-alias @/* --use-npm --yes

# 2) Enter the app
cd web-ui

# 3) Initialize shadcn/ui (ESM, keep defaults)
npx shadcn-ui@latest init

# 4) Add base primitives
npx shadcn-ui@latest add button card input textarea label badge separator dropdown-menu tabs dialog sheet form toast tooltip skeleton

# 5) Run it
npm run dev
```

What this gives you:
- `web-ui/` isolated Next 15 + Tailwind + shadcn components in `components/ui/`.
- Tailwind design tokens wired via CSS variables; easy to theme for your brand.

## Theming & brand alignment
- Edit `web-ui/src/app/globals.css` and the Tailwind config `web-ui/tailwind.config.ts` to set your palette and radius (shadcn uses CSS vars like `--background`, `--primary`, etc.).
- If you want dark mode, keep `next-themes` (shadcn default) and wrap `app/layout.tsx` with the ThemeProvider the init adds.
- Keep components minimal: prefer adding only what you need to avoid bloat.

## VS Code workflow
- Add a script to `web-ui/package.json`:
  ```json
  "scripts": {
    "ui:add": "shadcn-ui add"
  }
  ```
- Then you can run from the command palette/terminal: `npm run ui:add button` to pull a new primitive.
- Optional task (place in `.vscode/tasks.json` inside `web-ui`):
  ```json
  {
    "version": "2.0.0",
    "tasks": [
      {
        "label": "shadcn add component",
        "type": "shell",
        "command": "npm run ui:add ${input:component}",
        "options": { "cwd": "${workspaceFolder}/web-ui" },
        "problemMatcher": []
      }
    ],
    "inputs": [
      { "id": "component", "type": "promptString", "description": "Component name (e.g. button, card)" }
    ]
  }
  ```

## Usage patterns
- Treat `web-ui` as the design system/playground. Build screens there, then export HTML/JSX or CSS tokens to other surfaces (site, docs, marketing pages).
- Wrap primitives before reuse: create `components/huly/button.tsx` (or similar) that applies your default gradient, spacing, motion, and typography, then import that across pages.
- For previews/review, add simple MDX pages in `app/(preview)/` or use Storybook later if needed.

## If you don’t want to scaffold yet
- You can still use shadcn components in an existing Next app by running steps 3–4 in that app’s root.
- For non-Next stacks (pure React), you can adapt the generated components; they’re unstyled JSX + Tailwind classes, so they port cleanly if Tailwind is present.

## Maintenance tips
- Keep the component list lean; delete unused primitives.
- Re-run `npx shadcn-ui@latest add <component>` to pull updates; the generator is idempotent.
- Commit `components.json` (created by the init) so future adds follow the same config.
