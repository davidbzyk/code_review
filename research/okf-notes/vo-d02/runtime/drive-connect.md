---
id: runtime/drive-connect
schema: okf/schemas/v1/architecture.json
type: Architecture
title: Runtime: connect Google Drive
description: OAuth2 PKCE loopback flow triggered from the settings page.
domain: architecture
tags:
  - runtime
  - arc42-6
  - google-drive
freshness: "2026-10-05T12:00:00Z"
version: 1.0.0
status: stable
sources:
  - resource: src/routes/settings/+page.svelte
  - resource: src-tauri/src/google_drive.rs
related:
  - building-blocks/backend-drive
  - building-blocks/frontend-settings-page
  - interfaces/external-http-apis
---

`google_drive_connect` obtains tokens through a loopback listener.

1. `connectDrive()` in src/routes/settings/+page.svelte invokes `google_drive_connect` with `clientId` and `clientSecret`.
2. `generate_code_verifier` and `code_challenge` create the PKCE pair (src-tauri/src/google_drive.rs).
3. `TcpListener::bind("127.0.0.1:0")` picks a port; the redirect URI is `http://127.0.0.1:<port>`.
4. `open::that` opens the Google consent URL in the default browser.
5. The listener is non-blocking and polled every 200 ms for up to 120 seconds; on timeout it returns "OAuth timed out".
6. The first request line is parsed and the `code` query parameter extracted; an HTML success page is written back.
7. A POST to `https://oauth2.googleapis.com/token` exchanges the code with `code_verifier`.
8. `expires_at` is now plus `expires_in` (default 3600) minus 60 seconds.
9. `get_user_email` calls `https://www.googleapis.com/oauth2/v2/userinfo`.
10. A `DriveTokens` with `connected: true` is returned; the page merges it into `config.google_drive` and calls `appState.saveConfig()`.

## Related
[[building-blocks/backend-drive]], [[building-blocks/frontend-settings-page]], [[interfaces/external-http-apis]]
