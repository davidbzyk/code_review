# runtime

* [Runtime: record a session](./record-a-session.md) - Step by step flow from the Record button to the /preview route.
* [Runtime: process a recording (desktop)](./process-recording-desktop.md) - Flow of process_recording in Rust with progress events to the preview page.
* [Runtime: process a recording (browser)](./process-recording-browser.md) - Flow of processViaBrowser: ElevenLabs by fetch, then ffmpeg.wasm splice and download.
* [Runtime: connect Google Drive](./drive-connect.md) - OAuth2 PKCE loopback flow triggered from the settings page.
* [Runtime: upload to Google Drive](./drive-upload.md) - How the preview page uploads the output, in the desktop and browser variants.
* [Runtime: load and save configuration](./config-load-and-save.md) - Order of config sources on load and the targets written on save.
