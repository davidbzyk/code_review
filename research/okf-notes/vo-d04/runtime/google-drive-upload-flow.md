---
id: runtime/google-drive-upload-flow
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Google Drive upload flow"
description: "Token check, then upload through Rust or fetch."
domain: architecture
tags:
  - runtime
  - upload
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: runtime
sources:
  - resource: src/routes/preview/+page.svelte
  - resource: src-tauri/src/google_drive.rs
related:
  - building-blocks/route-preview
  - building-blocks/backend-google-drive
  - interfaces/pipeline-events
---

# Google Drive upload flow

`uploadToDrive()` uploads the saved video and shows a share link.

## Steps
1. Returns at once when `google_drive.connected` is false (src/routes/preview/+page.svelte).
2. If `expires_at` is 0 or past, `refreshDriveToken()` posts a refresh_token grant, stores the new token and saves config.
3. Tauri: invokes `upload_to_drive` with `accessToken`, `filePath` (the output path) and a `Channel`.
4. Rust reads the file, posts a multipart/related body to the upload endpoint with `fields=id,webViewLink`, sending Progress 10 and 80 (src-tauri/src/google_drive.rs).
5. It posts a permission `{type: anyone, role: reader}`, sends Progress 95 and Complete, returns `webViewLink`.
6. Browser: `driveUploadWithToken(blob, token)` does the same with `FormData`; on status 401 it refreshes and retries once.
7. The link goes to `driveLink` and is rendered as an anchor.

## Related

- [[building-blocks/route-preview]]
- [[building-blocks/backend-google-drive]]
- [[interfaces/pipeline-events]]
