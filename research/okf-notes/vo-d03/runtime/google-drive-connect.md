---
id: runtime/google-drive-connect
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Flow: connect Google Drive"
description: "Steps of the OAuth PKCE sign-in started from the settings page."
domain: architecture
tags:
  - runtime
  - oauth
  - google-drive
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/settings/+page.svelte
  - resource: src-tauri/src/google_drive.rs
relations:
  relates_to:
    - building-blocks/backend-google-drive
    - building-blocks/page-settings
---

# Flow: connect Google Drive

This flow starts at the Connect button on `/settings` and ends with tokens saved in config.

## Steps

1. `connectDrive()` in `src/routes/settings/+page.svelte` invokes `google_drive_connect` with `clientId` and `clientSecret` (desktop only; browser mode sets `driveError`).
2. `google_drive_connect` in `src-tauri/src/google_drive.rs` calls `generate_code_verifier()` and `code_challenge()`.
3. It binds a `TcpListener` on `127.0.0.1` port 0 and forms `redirect_uri`.
4. It builds the `accounts.google.com` consent URL (scope `drive.file` and `email`, `access_type=offline`, `prompt=consent`) and opens it with `open::that`.
5. It polls `accept()` every 200 ms for up to 120 seconds, reads the request line, and extracts the `code` query parameter.
6. It writes a small HTML "Connected" reply to the browser.
7. It POSTs the code and verifier to `https://oauth2.googleapis.com/token`.
8. It computes `expires_at` as now plus `expires_in` minus 60, and calls `get_user_email`.
9. It returns `DriveTokens`.
10. `connectDrive()` merges them into `appState.config.google_drive` and calls `appState.saveConfig()`.

## Related

- [building-blocks/backend-google-drive](../building-blocks/backend-google-drive.md)
- [building-blocks/page-settings](../building-blocks/page-settings.md)
- [crosscutting/secrets](../crosscutting/secrets.md)
- [runtime/upload-to-drive](./upload-to-drive.md)
