---
id: runtime/google-drive-connect-upload
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Flow: Connect and Upload to Google Drive
description: The settings connect flow and the preview upload flow.
domain: architecture
tags:
  - runtime
  - google-drive
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/settings/+page.svelte
  - resource: src/routes/preview/+page.svelte
  - resource: src-tauri/src/google_drive.rs
  - resource: src/lib/drive.ts
related:
  - building-blocks/rust-google-drive
  - building-blocks/frontend-integrations
  - crosscutting/secrets
---

# Flow: Connect and Upload to Google Drive

Connect trigger: `connectDrive` in src/routes/settings/+page.svelte.

1. Under Tauri it invokes `google_drive_connect` with `clientId` and `clientSecret`; in a browser it sets an error message instead.
2. Rust builds the PKCE challenge and `state`, binds a loopback listener, and opens the consent URL with `open::that`.
3. It reads the callback request line, checks `state`, extracts `code`.
4. It posts the code to `https://oauth2.googleapis.com/token`, calls `get_user_email`, and returns `DriveTokens`.
5. `connectDrive` merges the tokens into `appState.config.google_drive` and calls `saveConfig`.

Upload trigger: `uploadToDrive` in src/routes/preview/+page.svelte.

1. If `expires_at` is unset or past, it calls `refreshDriveToken` (src/lib/drive.ts).
2. Under Tauri it invokes `upload_to_drive` with `accessToken`, `filePath = appState.outputPath` and a `Channel`; the command posts to the Drive multipart upload URL and returns the link.
3. In a browser it calls `driveUploadWithToken`; on a 401 `DriveUploadError` it refreshes the token and retries once.
4. The link is stored in `driveLink`.

## Related

- [Rust Google Drive](../building-blocks/rust-google-drive.md)
- [Frontend Integrations](../building-blocks/frontend-integrations.md)
- [Secrets](../crosscutting/secrets.md)
