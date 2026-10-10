# Runtime

Step by step flows as the code performs them.

## Documents

* [Config Load and Save Flow](./config-load-save.md) - How configuration moves between the keychain, config.json, the static dev file and localStorage.
* [Drive OAuth Connect Flow](./drive-oauth-connect.md) - The loopback OAuth2 PKCE sign-in run by google_drive_connect.
* [Drive Upload Flow](./drive-upload.md) - Uploading the finished video to Google Drive from the preview page.
* [Process Recording, Browser](./process-recording-browser.md) - The browser path that calls ElevenLabs directly and splices audio with ffmpeg.wasm.
* [Process Recording, Desktop](./process-recording-tauri.md) - The desktop path from the preview button to an MP4 on disk.
* [Record Screen Flow](./record-screen.md) - From pressing Record to a finished recording path.
* [Application Startup](./startup.md) - What happens from process start to the first rendered screen.
