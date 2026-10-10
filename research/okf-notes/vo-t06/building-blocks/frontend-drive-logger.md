---
id: building-blocks/frontend-drive-logger
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Frontend Drive Helper and Logger"
description: "Browser-side Google token refresh and upload, plus the console logger."
domain: architecture
tags:
  - building-blocks
  - frontend
  - logging
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/lib/drive.ts
  - resource: src/lib/logger.ts
relations:
  relates_to:
    - crosscutting/logging
    - runtime/drive-upload
    - building-blocks/route-preview
---

`drive.ts` talks to Google over `fetch`; `logger.ts` writes categorized console lines.

## Facts

- `DriveUploadError` extends `Error` and stores the HTTP `status` (`src/lib/drive.ts`).
- `refreshDriveToken()` reads `client_id`, `client_secret`, `refresh_token` from `appState.config.google_drive`, posts a `refresh_token` grant to `https://oauth2.googleapis.com/token`, stores the new `access_token` and `expires_at` (now plus `expires_in` minus 60 seconds), calls `appState.saveConfig()` and returns the token. It throws when no refresh token is stored.
- `driveUploadWithToken(blob, accessToken)` posts a multipart `FormData` (metadata name `voiceover-<time>.webm`, mime `video/webm`) to the Drive upload endpoint and returns `webViewLink`, or throws `DriveUploadError`.
- `log(level, category, message, data)` in `src/lib/logger.ts` prints `[VO:<category>]` with a colour per level through `console[level]`.
- `logger` exposes named helpers (`configLoaded`, `recordingStart`, `pipelineStage`, `driveUploadDone` and others) and generic `info`, `warn`, `error`, `debug`.
- Callers: `src/routes/preview/+page.svelte` uses `drive.ts`; `logger` is used by `state.svelte.ts`, `recorder.svelte.ts`, `drive.ts` and the preview and settings routes.

## Related

- [Logging](../crosscutting/logging.md)
- [Drive upload flow](../runtime/drive-upload.md)
