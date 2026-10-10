---
id: runtime/drive-connect-and-upload
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Google Drive connect and upload
description: OAuth connect from Settings and upload from Preview, in Tauri and browser modes.
domain: architecture
tags:
  - runtime
  - drive
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/settings/+page.svelte
  - resource: src/routes/preview/+page.svelte
  - resource: src/lib/drive.ts
  - resource: src-tauri/src/google_drive.rs
related:
  - building-blocks/tauri-google-drive
  - building-blocks/frontend-state
  - crosscutting/secrets
---

# Google Drive connect and upload

Drive access has a connect flow and an upload flow.

## Connect

1. `connectDrive` (src/routes/settings/+page.svelte) invokes `google_drive_connect` with `clientId` and `clientSecret`; in browser mode it shows an error instead.
2. The Rust command opens the consent URL, accepts one loopback request, verifies `state`, exchanges the code and fetches the email (src-tauri/src/google_drive.rs).
3. The page merges the returned tokens into `appState.config.google_drive` and calls `saveConfig`.

## Upload

1. `uploadToDrive` (src/routes/preview/+page.svelte) refreshes the token with `refreshDriveToken` when `expires_at` has passed.
2. In Tauri it invokes `upload_to_drive` with `accessToken` and `filePath`; the command posts a multipart body and returns `webViewLink`.
3. In browser mode it calls `driveUploadWithToken`; on `DriveUploadError` status 401 it refreshes and retries once.
4. The link is stored in `driveLink`.

## Related

- [[building-blocks/tauri-google-drive]] - Rust Google Drive module
- [[building-blocks/frontend-state]] - Frontend state and Drive client
- [[crosscutting/secrets]] - Secret handling
