# Runtime

Notes of kind `runtime`.

* [Startup flow](./startup-flow.md) - What runs when the desktop app and the root layout start.
* [Config load and save flow](./config-load-save-flow.md) - Order of config sources on load and the targets written on save.
* [Record screen flow](./record-screen-flow.md) - From the record button to the /preview route.
* [Process recording in the desktop app](./process-recording-desktop-flow.md) - The process_recording command from invoke to saved MP4.
* [Process recording in browser mode](./process-recording-browser-flow.md) - processViaBrowser: S2S fetch and ffmpeg.wasm splice.
* [Google Drive connect flow](./google-drive-connect-flow.md) - OAuth 2.0 PKCE with a loopback listener, run from the settings page.
* [Google Drive upload flow](./google-drive-upload-flow.md) - Token check, then upload through Rust or fetch.
* [Widget window flow](./widget-window-flow.md) - Events and commands used by the recording widget page.
