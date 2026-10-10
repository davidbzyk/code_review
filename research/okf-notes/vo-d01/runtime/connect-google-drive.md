---
id: runtime/connect-google-drive
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Connect Google Drive"
description: "The OAuth loopback flow started from Settings."
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
---
# Connect Google Drive

`connectDrive` hands the client id and secret to Rust, which completes the OAuth code flow.

## Steps
1. `connectDrive` (src/routes/settings/+page.svelte) invokes `google_drive_connect` in Tauri.
2. `google_drive_connect` (src-tauri/src/google_drive.rs) makes a PKCE verifier and challenge.
3. It binds a TCP listener on `127.0.0.1:0` and forms `redirect_uri` with that port.
4. It opens the consent URL with scope `drive.file email` through `open::that`.
5. It accepts one request, parses `code` from the request line, and writes a success page.
6. It posts the code and verifier to `https://oauth2.googleapis.com/token`.
7. `get_user_email` reads `userinfo`; the command returns `DriveTokens`.
8. The page merges tokens into `config.google_drive` and calls `saveConfig`.

## Related
- [[building-blocks/google-drive-backend]]
- [[building-blocks/settings-screen]]
- [[runtime/upload-to-drive]]
