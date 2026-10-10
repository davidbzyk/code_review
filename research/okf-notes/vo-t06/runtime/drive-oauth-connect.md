---
id: runtime/drive-oauth-connect
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Drive OAuth Connect Flow"
description: "The loopback OAuth2 PKCE sign-in run by google_drive_connect."
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
    - building-blocks/route-settings
---

The settings page starts the flow and the Rust command completes it.

## Steps

1. `connectDrive()` in `src/routes/settings/+page.svelte` invokes `google_drive_connect` with `clientId` and `clientSecret`.
2. `google_drive_connect` (`src-tauri/src/google_drive.rs`) calls `generate_code_verifier()` and `code_challenge()`, and makes a random `state` value.
3. It binds a `TcpListener` on `127.0.0.1:0` and uses that port in `redirect_uri`.
4. It builds the `https://accounts.google.com/o/oauth2/v2/auth` URL (scope `drive.file` and `email`, `access_type=offline`, `prompt=consent`) and opens it with `open::that`.
5. It waits up to 120 seconds for one connection, reads the request line and parses the URL.
6. It compares the `state` parameter and extracts `code`; a mismatch returns an error.
7. It writes a small HTML success page to the browser.
8. It posts the code and `code_verifier` to `https://oauth2.googleapis.com/token`.
9. It computes `expires_at` (now plus `expires_in` minus 60) and calls `get_user_email`.
10. It returns `DriveTokens`; the page merges them into `appState.config.google_drive` and saves.

## Related

- [Rust Google Drive](../building-blocks/rust-google-drive.md)
- [Settings route](../building-blocks/route-settings.md)
