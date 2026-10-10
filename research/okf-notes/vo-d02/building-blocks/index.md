# building-blocks

* [Frontend shell](./frontend-shell.md) - Page template, global styles, layout and route options shared by all pages.
* [Frontend state and logging](./frontend-state-and-logging.md) - The shared AppState class, config types, Tauri detection and the console logger.
* [Frontend recorder module](./frontend-recorder.md) - Browser media capture: screen stream, microphone, MediaRecorder and chunk handling.
* [Record page and widget page](./frontend-record-page.md) - The home route that starts a recording and the floating widget route shown during capture.
* [Preview page](./frontend-preview-page.md) - The /preview route: plays the recording, processes it, and uploads the result to Drive.
* [Settings page](./frontend-settings-page.md) - The /settings route: API key, voice list, output folder and Google Drive connection.
* [Rust entry and command registry](./backend-entry.md) - main.rs, lib.rs and the Tauri builder that registers plugins and every command.
* [Rust config module](./backend-config.md) - AppConfig structs and the get_config and save_config commands.
* [Rust recording commands](./backend-recording-commands.md) - Commands that store recording chunks in a temp folder and join them into one file.
* [Rust window commands](./backend-window-commands.md) - Commands that open and close the floating recording widget window.
* [Rust prerequisites check](./backend-prerequisites.md) - Detects whether ffmpeg runs on the system PATH.
* [Rust processing pipeline](./backend-pipeline.md) - process_recording and the ffmpeg helpers that turn a recording into a final MP4.
* [Rust ElevenLabs client](./backend-elevenlabs.md) - Speech-to-speech request and API key check against the ElevenLabs API.
* [Rust Google Drive module](./backend-drive.md) - OAuth2 PKCE loopback sign-in and multipart upload to Google Drive.
