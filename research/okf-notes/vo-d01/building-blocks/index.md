# Building Blocks

Notes for the building blocks section.

## Documents

* [Tauri Shell](./tauri-shell.md) - The Rust entry module that registers plugins and every command handler.
* [Config Store](./config-store.md) - Backend module that reads and writes the JSON configuration file in the app data directory.
* [Recording Commands](./recording-commands.md) - Backend commands that write recording chunks to a temp folder and join them.
* [Window Commands](./window-commands.md) - Backend commands that create and close the floating recording widget window.
* [Media Pipeline](./media-pipeline.md) - Backend orchestration of ffmpeg and ElevenLabs steps that turn a recording into the final MP4.
* [ElevenLabs Client](./elevenlabs-client.md) - Backend module that calls the ElevenLabs speech-to-speech and user endpoints.
* [Google Drive Backend](./google-drive-backend.md) - Backend module for the Google OAuth PKCE flow and the Drive upload command.
* [Frontend Shell](./frontend-shell.md) - HTML template, global styles, route-level options and the root layout that loads configuration.
* [Frontend State and Logger](./frontend-state.md) - The shared reactive application state and the console logger.
* [Frontend Recorder](./frontend-recorder.md) - Browser-side capture of screen video and microphone audio with MediaRecorder.
* [Home Screen](./home-screen.md) - The root route that picks capture options and starts, pauses and stops a recording.
* [Preview Screen](./preview-screen.md) - The /preview route that processes the recording, shows progress and uploads to Drive.
* [Settings Screen](./settings-screen.md) - The /settings route for the API key, voices, and Google Drive connection.
* [Widget Screen](./widget-screen.md) - The /widget route shown in the floating recording window.
