---
id: building-blocks/frontend-logger
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend logger"
description: "Console logger that prefixes messages with [VO:category]."
domain: architecture
tags:
  - frontend
  - logging
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: building-blocks
sources:
  - resource: src/lib/logger.ts
related:
  - crosscutting/logging
  - building-blocks/frontend-state
---

# Frontend logger

`src/lib/logger.ts` exports `logger`, a set of named helpers over `console`.

## Facts (src/lib/logger.ts)
- Internal `log(level, category, message, data?)` writes `%c[VO:<category>]` with a per-level colour and a `HH:MM:SS.mmm` timestamp.
- Levels: `debug`, `info`, `warn`, `error`.
- Named helpers cover config (`configLoaded`, `configSaved`), recording, ElevenLabs, pipeline and Drive events.
- Generic helpers: `info`, `warn`, `error`, `debug` taking a category.

## Used by
src/lib/state.svelte.ts, src/lib/recorder.svelte.ts, src/routes/preview/+page.svelte, src/routes/settings/+page.svelte.

## Related

- [[crosscutting/logging]]
- [[building-blocks/frontend-state]]
