---
id: building-blocks/frontend-logger
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend logger"
description: "Console logger that prefixes messages with [VO:category] and exposes typed helper methods."
domain: architecture
tags:
  - building-block
  - frontend
  - logging
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/logger.ts
relations:
  relates_to:
    - crosscutting/logging
---

# Frontend logger

`src/lib/logger.ts` exports `logger`, a set of functions that write to the browser console.

## Facts

- Internal `log(level, category, message, data?)` prints `%c[VO:<category>]` with a per-level CSS colour and a `HH:MM:SS.mmm` time slice, using `console[level]`.
- Levels: `info`, `warn`, `error`, `debug`.
- Named helpers by area: config (`configLoaded`, `configSaved`), recording (`recordingStart`, `recordingChunk`, `recordingStop`, `recordingCancel`), ElevenLabs (`elevenLabsTest`, `elevenLabsTestResult`, `elevenLabsS2S`, `elevenLabsS2SDone`), pipeline (`pipelineStart`, `pipelineStage`, `pipelineComplete`, `pipelineError`), Drive (`driveConnect`, `driveConnected`, `driveUploadStart`, `driveUploadDone`, `driveError`).
- Generic helpers: `info`, `warn`, `error`, `debug` taking `(category, message, data?)`.
- The file header comment says to filter the console by `[VO:`.

## Used by

`src/lib/state.svelte.ts`, `src/lib/recorder.svelte.ts`, `src/routes/preview/+page.svelte`, `src/routes/settings/+page.svelte`.

## Related

- [crosscutting/logging](../crosscutting/logging.md)
- [building-blocks/frontend-state](./frontend-state.md)
- [building-blocks/frontend-recorder](./frontend-recorder.md)
