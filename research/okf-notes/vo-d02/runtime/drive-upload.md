---
id: runtime/drive-upload
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Runtime: upload to Google Drive
description: How the preview page uploads the output, in the desktop and browser variants.
domain: architecture
tags:
  - runtime
  - arc42-6
  - google-drive
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/preview/+page.svelte
  - resource: src-tauri/src/google_drive.rs
related:
  - building-blocks/backend-drive
  - building-blocks/frontend-preview-page
  - interfaces/external-http-apis
---

`uploadToDrive()` in src/routes/preview/+page.svelte returns early unless `google_drive.connected` is true.

## Desktop
1. It creates a `Channel` and invokes `upload_to_drive` with `accessToken`, `filePath` (`appState.outputPath`) and `onEvent`.
2. `upload_to_drive` (src-tauri/src/google_drive.rs) reads the file, sends `Progress` 10, and POSTs a multipart body (`build_multipart_body`, boundary `voiceover_boundary`) to the Drive upload endpoint.
3. A non-success status sends `Error` and returns `Drive upload error`.
4. It reads the file `id`, POSTs a permission `{type: anyone, role: reader}`, sends `Progress` 95.
5. It sends `Complete { url }` with `webViewLink` and returns the link; the page stores it in `driveLink`.

## Browser
1. If `expires_at` has passed, `refreshDriveToken()` posts a `refresh_token` grant to the token endpoint and saves the new token.
2. `driveUploadWithToken(blob, token)` posts `FormData` (metadata and file) and then the permission request.
3. On HTTP 401 it refreshes and retries once.

## Related
[[building-blocks/backend-drive]], [[building-blocks/frontend-preview-page]], [[interfaces/external-http-apis]]
