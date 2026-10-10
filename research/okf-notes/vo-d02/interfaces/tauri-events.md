---
id: interfaces/tauri-events
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Window events
description: Events exchanged between the main window and the widget window.
domain: architecture
tags:
  - interfaces
  - events
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/+page.svelte
  - resource: src/routes/widget/+page.svelte
related:
  - building-blocks/frontend-record-page
  - crosscutting/state-management
---

Events travel with `@tauri-apps/api/event`.

| Event | Payload | Emitted in | Listened in |
|---|---|---|---|
| `recording-stop` | none | src/routes/widget/+page.svelte `handleStop` | src/routes/+page.svelte `handleRecord` |
| `recording-cancel` | none | src/routes/widget/+page.svelte `handleCancel` | src/routes/+page.svelte `handleRecord` |
| `recording-pause`, `recording-resume` | null | src/routes/widget/+page.svelte `handlePause` via `plugin:event\|emit` | no listener in src/ |
| `widget-voice-name` | string | no emitter in src/ | src/routes/widget/+page.svelte `onMount` |

## Related
[[building-blocks/frontend-record-page]], [[crosscutting/state-management]]
