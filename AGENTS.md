# AI MCP Routing Policy (VS Code Codex + Claude)

This file defines when to use each MCP server while coding. Treat this as the default routing guide for both VS Code extensions.

## Default Rules

- Start with **Serena** for codebase understanding, symbol lookup, or refactors.
- Use MCP servers only when the task benefits from them; otherwise work locally.
- Prefer the smallest tool that answers the question; avoid chaining multiple tools unless needed.

## Server Routing Matrix

**serena**
- Use for: symbol search, references, refactors, code structure.
- Trigger: "find where used", "rename", "refactor", "overview", "search for pattern".

**context7**
- Use for: framework/library documentation (React/Next.js/Tailwind/TypeScript).
- Trigger: "how do I", "API syntax", "best practice", "docs".
- Avoid: project-specific questions; use Serena or local docs instead.

**shadcn**
- Use for: UI component scaffolding in `web-ui/`.
- Trigger: "add shadcn component", "generate UI component", "create dialog/card/form".

**playwright**
- Use for: end-to-end browser tests and reproducible UI flows.
- Trigger: "e2e test", "write a test", "simulate user flow".

**chrome-devtools**
- Use for: runtime truth (network, console, performance, CLS/LCP).
- Trigger: "what actually happens in the browser", "perf audit", "network errors".

**postgres**
- Use for: database schema changes and queries.
- Trigger: "add column/table", "run query", "migration".
- Guardrail: confirm target DB and keep changes minimal.

**notion**
- Use for: read/write Notion content and databases.
- Trigger: "update Notion", "create Notion page", "sync to Notion".

**dreamweaving-rag**
- Use for: semantic search across Dreamweaving knowledge base.
- Trigger: "search knowledge", "find prior guidance", "what does the canon say".

**coin-rag**
- Use for: rare coin knowledge only.
- Trigger: numismatics-specific research or pricing.

## Path-Based Defaults

- `web-ui/`: prefer **shadcn**, **context7**, **playwright**, **chrome-devtools**.
- `scripts/` or `.py`: prefer **serena** first; use **dreamweaving-rag** for knowledge lookups.
- `sessions/` or `knowledge/`: use **dreamweaving-rag** (and **notion** if editing canon).

## Safety

- If a tool call would write data externally (DB/Notion), ask for confirmation first.
