---
id: runtime/google-drive-connect
schema: okf/schemas/v1/architecture.json
type: Architecture
title: "Google Drive Connect"
description: "The OAuth 2.0 loopback flow with PKCE."
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
related:
  - building-blocks/backend-google-drive
  - runtime/drive-upload
  - interfaces/external-http-apis
---
# Google Drive Connect

`google_drive_connect` obtains tokens through the user's browser and a local TCP listener.

## Steps
1. `connectDrive` (src/routes/settings/+page.svelte) invokes `google_drive_connect` with `clientId` and `clientSecret`; in a browser it shows a message that the desktop app is required.
2. `generate_code_verifier` and `code_challenge` create the PKCE pair; a random `state` is generated.
3. It binds `127.0.0.1:0` and builds the redirect URI `http://127.0.0.1:<port>`.
4. It opens the Google consent URL with `open::that`; scope is `drive.file` and `email`.
5. It waits up to 120 seconds for the callback with `timeout`.
6. It compares the returned `state` and reads `code`; a mismatch returns an error.
7. It writes an HTML success page to the socket.
8. It posts to `https://oauth2.googleapis.com/token` with the verifier, then `get_user_email` fetches the address.
9. It returns `DriveTokens`; `connectDrive` merges them into config and calls `saveConfig`.

## Related
- [Backend Google Drive](../building-blocks/backend-google-drive.md)
- [Drive Upload](./drive-upload.md)
- [External HTTP APIs](../interfaces/external-http-apis.md)
