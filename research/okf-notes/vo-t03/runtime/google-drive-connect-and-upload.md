---
id: runtime/google-drive-connect-and-upload
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Google Drive connect and upload"
description: "The OAuth loopback flow and the upload steps."
domain: architecture
tags:
  - runtime
  - google-drive
  - oauth
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src-tauri/src/google_drive.rs
  - resource: src/routes/settings/+page.svelte
  - resource: src/routes/preview/+page.svelte
  - resource: src/lib/drive.ts
related:
  - building-blocks/rust-google-drive
  - building-blocks/frontend-clients
  - crosscutting/secrets-handling
---
# Google Drive connect and upload

Connect happens in Settings; upload happens in Preview.

## Connect

1. `connectDrive` (settings page) invokes `google_drive_connect` with `clientId` and `clientSecret`; in a plain browser it shows an error instead.
2. `google_drive_connect` (src-tauri/src/google_drive.rs) builds a PKCE verifier, challenge and `state`, binds `127.0.0.1:0` and builds the Google consent URL.
3. `open::that` opens the browser.
4. It waits up to 120 s for one HTTP request, checks `state`, reads `code`, and answers with a small HTML page.
5. It posts the code to `https://oauth2.googleapis.com/token`, computes `expires_at`, reads the e-mail, and returns `DriveTokens`.
6. The settings page merges the tokens into config and calls `saveConfig`.

## Upload

1. `uploadToDrive` (preview page) refreshes the token with `refreshDriveToken` when `expires_at` has passed.
2. In Tauri it invokes `upload_to_drive` with `accessToken` and `filePath`; Rust posts a multipart body and returns `webViewLink`.
3. In the browser it calls `driveUploadWithToken` (src/lib/drive.ts) and retries once after a 401 with a refreshed token.

## Related

- [[building-blocks/rust-google-drive]]
- [[building-blocks/frontend-clients]]
- [[crosscutting/secrets-handling]]
