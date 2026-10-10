---
id: runtime/drive-upload
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Drive Upload Flow"
description: "Uploading the finished video to Google Drive from the preview page."
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
  - resource: src/lib/drive.ts
  - resource: src-tauri/src/google_drive.rs
relations:
  relates_to:
    - building-blocks/rust-google-drive
    - building-blocks/frontend-drive-logger
---

`uploadToDrive()` in `src/routes/preview/+page.svelte` returns early unless `google_drive.connected` is true.

## Steps

1. Read `access_token` and `expires_at`; when `expires_at` is 0 or in the past, `refreshDriveToken()` (`src/lib/drive.ts`) fetches a new token and saves config.
2. Tauri: create a `Channel`, invoke `upload_to_drive` with `accessToken`, `filePath` (`appState.outputPath`) and `onEvent`.
3. `upload_to_drive` (`src-tauri/src/google_drive.rs`) reads the file, posts a multipart body to the Drive upload endpoint and sends `Progress` at 10, 80 and 95.
4. It returns `webViewLink` and sends `Complete { url }`; the page stores it in `driveLink`.
5. Browser: `blobStore.getVideo()` goes to `driveUploadWithToken`; on a `DriveUploadError` with status 401 the token is refreshed and the upload is retried once.
6. Errors set `processingError` and call `logger.driveError`.
7. The code does not change file sharing; comments in both upload functions say the file stays private.

## Related

- [Rust Google Drive](../building-blocks/rust-google-drive.md)
- [Frontend drive helper and logger](../building-blocks/frontend-drive-logger.md)
