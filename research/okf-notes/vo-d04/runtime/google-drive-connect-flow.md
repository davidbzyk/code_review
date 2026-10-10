---
id: runtime/google-drive-connect-flow
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Google Drive connect flow"
description: "OAuth 2.0 PKCE with a loopback listener, run from the settings page."
domain: architecture
tags:
  - runtime
  - oauth
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
architecture_layer: runtime
sources:
  - resource: src/routes/settings/+page.svelte
  - resource: src-tauri/src/google_drive.rs
related:
  - building-blocks/route-settings
  - building-blocks/backend-google-drive
  - interfaces/external-http-apis
---

# Google Drive connect flow

`connectDrive()` starts a PKCE flow handled in Rust.

## Steps
1. `connectDrive()` invokes `google_drive_connect` with `clientId` and `clientSecret` (src/routes/settings/+page.svelte).
2. `generate_code_verifier()` makes 32 random bytes in base64url; `code_challenge()` hashes with SHA-256 (src-tauri/src/google_drive.rs).
3. A `TcpListener` binds `127.0.0.1:0`; the port forms `redirect_uri`.
4. The authorization URL (scope `drive.file` and `email`, `access_type=offline`, `prompt=consent`) opens through `open::that`.
5. A non-blocking `accept` loop polls every 200 ms for up to 120 s.
6. The `code` query value is read from the request line; an HTML success page is written back.
7. POST `https://oauth2.googleapis.com/token` exchanges the code with the verifier.
8. `expires_at` is now plus `expires_in` minus 60; `get_user_email` reads `userinfo`.
9. `DriveTokens` return; the page merges them into `config.google_drive` and calls `saveConfig()` (src/routes/settings/+page.svelte).

## Related

- [[building-blocks/route-settings]]
- [[building-blocks/backend-google-drive]]
- [[interfaces/external-http-apis]]
