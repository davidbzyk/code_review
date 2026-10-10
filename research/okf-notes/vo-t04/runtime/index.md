# Runtime

Notes in this folder.

## Documents

* [App startup flow](./app-startup.md) - On launch the Rust side builds the Tauri app and the root layout loads config and checks ffmpeg.
* [Config load and save flow](./config-load-and-save.md) - The frontend reads config from Tauri app data, then a synced static file, then localStorage, and writes to localStorage and Tauri.
* [Record screen flow](./record-screen-flow.md) - Recording runs from the Record button through MediaRecorder chunks to a file path or blob URL and the preview route.
* [Process recording in Tauri](./process-recording-tauri.md) - In the desktop app, process_recording either converts to MP4 or replaces the voice through ElevenLabs and ffmpeg.
* [Process recording in a browser](./process-recording-browser.md) - In browser mode the preview page calls ElevenLabs with fetch and splices audio with ffmpeg.wasm, then downloads a WebM.
* [Google Drive connect flow](./drive-connect-flow.md) - google_drive_connect opens the browser for Google consent, waits for a loopback callback and exchanges the code for tokens.
* [Google Drive upload flow](./drive-upload-flow.md) - uploadToDrive refreshes the token when it has expired and uploads through Rust in Tauri or through fetch in a browser.
* [Recording widget flow](./widget-window-flow.md) - The widget route shows a timer and sends pause, stop and cancel events; the Rust side creates and closes its window.
