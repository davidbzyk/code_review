---
id: runtime/upload-to-drive
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Flow: upload to Google Drive"
description: "Steps of uploading the saved video and getting a share link."
domain: architecture
tags:
  - runtime
  - google-drive
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/preview/+page.svelte
  - resource: src-tauri/src/google_drive.rs
relations:
  relates_to:
    - building-blocks/backend-google-drive
    - building-blocks/page-preview
---

# Flow: upload to Google Drive

This flow starts at the upload button on `/preview` when `google_drive.connected` is true.

## Steps in the desktop app

1. `uploadToDrive()` in `src/routes/preview/+page.svelte` creates a `Channel` and invokes `upload_to_drive` with `accessToken`, `filePath` (`appState.outputPath`) and `onEvent`.
2. `upload_to_drive` in `src-tauri/src/google_drive.rs` reads the file and sends `Progress` 10.
3. It POSTs a multipart body from `build_multipart_body` to `https://www.googleapis.com/upload/drive/v3/files`; progress 80.
4. On failure it sends `DriveEvent::Error` and returns an error.
5. On success it POSTs a permission of type `anyone`, role `reader`; progress 95.
6. It sends `Complete { url }` and returns `webViewLink`, stored in `driveLink`.

## Steps in the browser

1. `uploadToDrive()` reads `window.__voiceover_blob`.
2. If `expires_at` has passed it calls `refreshDriveToken()`.
3. `driveUploadWithToken(blob, token)` uploads with `fetch` and sets the permission.
4. On HTTP 401 it refreshes the token once and retries.

## Related

- [building-blocks/backend-google-drive](../building-blocks/backend-google-drive.md)
- [building-blocks/page-preview](../building-blocks/page-preview.md)
- [runtime/google-drive-connect](./google-drive-connect.md)
