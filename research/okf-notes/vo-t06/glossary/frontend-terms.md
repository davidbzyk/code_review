---
id: glossary/frontend-terms
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Glossary, Frontend Terms"
description: "Terms used in the TypeScript and Svelte code."
domain: architecture
tags:
  - glossary
  - frontend
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/state.svelte.ts
  - resource: src/lib/recorder.svelte.ts
  - resource: src/lib/blobStore.ts
  - resource: src/lib/tauri.ts
  - resource: src/lib/drive.ts
  - resource: src/lib/WebcamBubble.svelte
  - resource: src/routes/widget/+page.svelte
relations:
  relates_to:
    - glossary/backend-terms
    - building-blocks/frontend-state
---

Each line gives the term and its defining file.

- `AppState` - store class holding config and recording state (`src/lib/state.svelte.ts`).
- `appState` - the single `AppState` instance (`src/lib/state.svelte.ts`).
- `AppConfig` - TypeScript type of the settings (`src/lib/state.svelte.ts`).
- `RecordingState` - union of eight state names (`src/lib/state.svelte.ts`).
- `isTauri` - detects the desktop shell by `__TAURI_INTERNALS__` (`src/lib/state.svelte.ts`).
- `tauriInvoke` - lazy wrapper over Tauri `invoke` (`src/lib/tauri.ts`).
- `blobStore` - module store of video and audio blobs (`src/lib/blobStore.ts`).
- `CaptureMode` - `fullscreen`, `window` or `region` (`src/lib/recorder.svelte.ts`).
- session id - `rec-<time>-<random>` name of one recording (`generateSessionId`, `src/lib/recorder.svelte.ts`).
- compositor - hidden canvas that draws screen plus webcam (`src/lib/recorder.svelte.ts`).
- webcam bubble - circular webcam overlay (`computeWebcamBubbleRect`, `src/lib/recorder.svelte.ts`; preview in `src/lib/WebcamBubble.svelte`).
- `DriveUploadError` - error with HTTP status (`src/lib/drive.ts`).
- widget - small recording window page (`src/routes/widget/+page.svelte`).

## Related

- [Glossary, backend terms](backend-terms.md)
- [Frontend state](../building-blocks/frontend-state.md)
