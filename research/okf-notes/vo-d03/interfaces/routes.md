---
id: interfaces/routes
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend routes"
description: "The four SvelteKit routes and how they navigate between each other."
domain: architecture
tags:
  - interface
  - routes
  - frontend
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/+page.svelte
  - resource: src/routes/preview/+page.svelte
  - resource: src/routes/settings/+page.svelte
  - resource: src/routes/widget/+page.svelte
  - resource: src/routes/+layout.svelte
  - resource: src/routes/+layout.ts
  - resource: src/routes/widget/+layout.ts
relations:
  relates_to:
    - building-blocks/frontend-shell
---

# Frontend routes

Routes are files under `src/routes/`; all are prerendered client-side pages.

| Path | File | Reached by |
|---|---|---|
| `/` | `src/routes/+page.svelte` | `goto('/')` from settings and preview |
| `/preview` | `src/routes/preview/+page.svelte` | `goto('/preview')` in `handleStop()` |
| `/settings` | `src/routes/settings/+page.svelte` | Settings button in `src/routes/+page.svelte` |
| `/widget` | `src/routes/widget/+page.svelte` | window URL in `create_widget_window` |

`src/routes/+layout.svelte` wraps `/`, `/preview` and `/settings`, and by SvelteKit nesting also `/widget`. `src/routes/+layout.ts` and `src/routes/widget/+layout.ts` set `ssr = false` and `prerender = true`.

## Related

- [building-blocks/frontend-shell](../building-blocks/frontend-shell.md)
- [building-blocks/page-record](../building-blocks/page-record.md)
- [building-blocks/page-preview](../building-blocks/page-preview.md)
- [building-blocks/page-settings](../building-blocks/page-settings.md)
- [building-blocks/page-widget](../building-blocks/page-widget.md)
