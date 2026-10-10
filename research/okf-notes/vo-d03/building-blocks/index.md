# building-blocks

## Documents

- [Backend config module](./backend-config.md) - Config structs, JSON file in the app data directory, and the static config sync.
- [Backend ElevenLabs client](./backend-elevenlabs.md) - Speech-to-speech upload and API key test against api.elevenlabs.io.
- [Backend entry and app builder](./backend-entry.md) - Rust binary entry, library run function, plugin setup and command registration.
- [Backend ffmpeg wrapper](./backend-ffmpeg.md) - Async functions that run the ffmpeg program, and the startup availability check.
- [Backend Google Drive client](./backend-google-drive.md) - PKCE OAuth flow over a loopback listener, token refresh and file upload to Drive.
- [Backend processing pipeline](./backend-pipeline.md) - The process_recording command that turns a recording into a final MP4.
- [Backend recording commands](./backend-recording.md) - Commands that store recording chunks in the temp directory and join them into one file.
- [Backend window commands](./backend-window.md) - Commands that open and close the floating widget window.
- [Frontend logger](./frontend-logger.md) - Console logger that prefixes messages with [VO:category] and exposes typed helper methods.
- [Frontend recorder module](./frontend-recorder.md) - MediaRecorder wrapper that captures the screen and microphone and returns a file path or blob URL.
- [Frontend shell](./frontend-shell.md) - HTML template, global style, root layout and build configuration of the SvelteKit app.
- [Frontend state module](./frontend-state.md) - Runes-based AppState class holding config and recording progress, plus the isTauri check.
- [Preview page](./page-preview.md) - Route /preview that plays the recording, runs processing and uploads the result to Google Drive.
- [Record page](./page-record.md) - Route / that selects a microphone and capture mode, then starts, pauses and stops a recording.
- [Settings page](./page-settings.md) - Route /settings for the ElevenLabs key, voice list and Google Drive connection.
- [Widget page](./page-widget.md) - Route /widget, the small always-on-top recording control window.
