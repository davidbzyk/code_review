---
id: building-blocks/frontend-logger
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend logger"
description: "logger.ts prints categorised console messages with a [VO:category] prefix and a colour per level."
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
    - building-blocks/frontend-state
---
# Frontend logger

The logger is a plain object of named helpers over `console` (src/lib/logger.ts).

## Facts

- Internal `log(level, category, message, data?)` formats `%c[VO:<category>]` plus a time slice of the ISO timestamp and calls `console[level]`.
- Levels: `info`, `warn`, `error`, `debug`, each with its own CSS colour.
- Named helpers exist for config (`configLoaded`, `configSaved`), recording (`recordingStart`, `recordingChunk`, `recordingStop`, `recordingCancel`), ElevenLabs (`elevenLabsTest`, `elevenLabsTestResult`, `elevenLabsS2S`, `elevenLabsS2SDone`), pipeline (`pipelineStart`, `pipelineStage`, `pipelineComplete`, `pipelineError`) and Drive (`driveConnect`, `driveConnected`, `driveUploadStart`, `driveUploadDone`, `driveError`).
- Generic helpers: `info`, `warn`, `error`, `debug` take a category, message and optional data.

## Used by

src/lib/state.svelte.ts, src/lib/recorder.svelte.ts, src/routes/settings/+page.svelte, src/routes/preview/+page.svelte.

## Related

[[crosscutting/logging]], [[building-blocks/frontend-state]]
