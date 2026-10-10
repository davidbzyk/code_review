---
id: runtime/drive-upload
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Drive Upload"
description: "Uploading the saved video to Google Drive from the preview page."
domain: architecture
tags:
  - runtime
  - google-drive
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/preview/+page.svelte
  - resource: src/lib/drive.ts
  - resource: src-tauri/src/google_drive.rs
related:
  - runtime/google-drive-connect
  - building-blocks/frontend-integrations
  - building-blocks/backend-google-drive
---
# Drive Upload

`uploadToDrive` checks the token, then uploads through Rust or the browser.

## Steps
1. `uploadToDrive` (src/routes/preview/+page.svelte) returns early unless `google_drive.connected`.
2. If `expires_at` is zero or past, it calls `refreshDriveToken` (src/lib/drive.ts).
3. Under Tauri it creates a `Channel` and invokes `upload_to_drive` with `accessToken` and `filePath`.
4. `upload_to_drive` (src-tauri/src/google_drive.rs) reads the file, sends `DriveEvent::Progress`, posts multipart metadata and bytes to the Drive upload URL, and returns the link.
5. In a browser it calls `driveUploadWithToken` with the blob; on `DriveUploadError` status 401 it refreshes the token and retries once.
6. A non-empty link is stored in `driveLink` and logged with `logger.driveUploadDone`.

## Related
- [Google Drive Connect](./google-drive-connect.md)
- [Frontend Integrations](../building-blocks/frontend-integrations.md)
- [Backend Google Drive](../building-blocks/backend-google-drive.md)
