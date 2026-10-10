---
id: runtime/drive-upload-flow
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Google Drive upload flow"
description: "uploadToDrive refreshes the token when it has expired and uploads through Rust in Tauri or through fetch in a browser."
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
relations:
  relates_to:
    - building-blocks/rust-google-drive
    - runtime/drive-connect-flow
    - interfaces/external-http-apis
---
# Google Drive upload flow

Upload starts from the preview page once a file has been saved.

## Steps

1. `uploadToDrive()` returns if `google_drive.connected` is false (src/routes/preview/+page.svelte).
2. If `expires_at` is zero or in the past, `refreshDriveToken()` posts a `refresh_token` grant to `oauth2.googleapis.com/token`, stores the new token and expiry, and saves config.
3. In Tauri it invokes `upload_to_drive` with `accessToken`, `filePath` and a `Channel`; the page sets `driveLink` from the result.
4. `upload_to_drive` reads the file, sends progress 10, builds a multipart body with `build_multipart_body`, and POSTs to `upload/drive/v3/files?uploadType=multipart&fields=id,webViewLink` (src-tauri/src/google_drive.rs).
5. On a non-success response it sends a `DriveEvent::Error` and returns an error.
6. It POSTs a permission `{type: anyone, role: reader}` for the new file id, sends progress 95, then `Complete` with `webViewLink`.
7. In a browser, `driveUploadWithToken(blob, token)` does the same with `FormData`; on status 401 the page refreshes the token and retries once.
8. A link button opens the URL with `plugin:shell|open` in Tauri or `window.open` otherwise.

## Related

[[building-blocks/rust-google-drive]], [[runtime/drive-connect-flow]], [[interfaces/external-http-apis]]
