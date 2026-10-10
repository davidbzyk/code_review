---
id: runtime/upload-to-drive
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Upload to Drive"
description: "How the preview route uploads the result and returns a share link."
domain: architecture
tags:
  - runtime
  - google-drive
  - upload
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/preview/+page.svelte
  - resource: src-tauri/src/google_drive.rs
---
# Upload to Drive

`uploadToDrive` runs only when `config.google_drive.connected` is true.

## Desktop steps
1. `uploadToDrive` (src/routes/preview/+page.svelte) invokes `upload_to_drive` with `accessToken`, `filePath` (`outputPath`) and a `Channel`.
2. `upload_to_drive` (src-tauri/src/google_drive.rs) reads the file, posts a multipart body to the Drive upload endpoint, and sends Progress 10, 80 and 95.
3. It posts an `anyone`/`reader` permission and returns `webViewLink`, also sent as `Complete`.

## Browser steps
1. `driveUploadWithToken` posts `FormData` with `metadata` and `file`, then the permission call.
2. On HTTP status 401 the page calls `refreshDriveToken`, which posts a `refresh_token` grant, stores the new access token with `saveConfig`, and retries once.

## Related
- [[building-blocks/google-drive-backend]]
- [[building-blocks/preview-screen]]
- [[interfaces/pipeline-channel-events]]
