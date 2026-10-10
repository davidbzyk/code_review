---
id: runtime/drive-connect-flow
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Google Drive connect flow"
description: "google_drive_connect opens the browser for Google consent, waits for a loopback callback and exchanges the code for tokens."
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
relations:
  relates_to:
    - building-blocks/rust-google-drive
    - runtime/drive-upload-flow
    - crosscutting/secrets-handling
---
# Google Drive connect flow

The Settings page starts the OAuth flow, and the Rust command completes it.

## Steps

1. `connectDrive()` in src/routes/settings/+page.svelte invokes `google_drive_connect` with `clientId` and `clientSecret` when in Tauri; in a browser it sets an error message and stops.
2. `google_drive_connect` creates a verifier and S256 challenge (src-tauri/src/google_drive.rs).
3. It binds `TcpListener` on `127.0.0.1:0` and builds `redirect_uri` from the chosen port.
4. It builds the `accounts.google.com/o/oauth2/v2/auth` URL with scope `drive.file` and `email`, `access_type=offline` and `prompt=consent`, then calls `open::that`.
5. It polls the non-blocking listener every 200 ms for up to 120 seconds.
6. It reads the request line, extracts the `code` query value and answers with a small HTML page.
7. It POSTs the code, verifier and redirect URI to `https://oauth2.googleapis.com/token`.
8. It reads `access_token`, `refresh_token`, `expires_in` (default 3600, minus 60 s) and fetches the email from the userinfo endpoint.
9. It returns `DriveTokens`; the page merges them into `appState.config.google_drive` and calls `saveConfig()`.

## Related

[[building-blocks/rust-google-drive]], [[runtime/drive-upload-flow]], [[crosscutting/secrets-handling]]
