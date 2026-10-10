# Runtime

Notes for the runtime section.

## Documents

* [Application Startup](./startup.md) - Steps from launching the desktop binary to a loaded main window.
* [Config Load and Save](./config-load-and-save.md) - How configuration moves between the Tauri file, the dev server file and localStorage.
* [Record Screen and Voice](./record-screen-and-voice.md) - Flow from pressing Record to the /preview route.
* [Process Recording on Desktop](./process-recording-desktop.md) - The Rust pipeline that produces the final MP4.
* [Process Recording in the Browser](./process-recording-browser.md) - The in-page path that calls ElevenLabs with fetch and splices with ffmpeg.wasm.
* [Connect Google Drive](./connect-google-drive.md) - The OAuth loopback flow started from Settings.
* [Upload to Drive](./upload-to-drive.md) - How the preview route uploads the result and returns a share link.
* [Widget Controls](./widget-controls.md) - Lifecycle of the floating widget window during a recording.
