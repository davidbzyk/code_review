# Building Blocks

Notes in this folder.

## Documents

* [Frontend shell](./frontend-shell.md) - The shell holds the HTML template, global CSS, the root layout that loads config and checks ffmpeg, and the per-route rendering flags.
* [Frontend state module](./frontend-state.md) - state.svelte.ts defines the AppConfig types, the AppState class and the isTauri check that every page uses.
* [Frontend recorder module](./frontend-recorder.md) - recorder.svelte.ts wraps MediaRecorder and getDisplayMedia and saves chunks to Rust in Tauri or keeps them in memory in a browser.
* [Frontend logger](./frontend-logger.md) - logger.ts prints categorised console messages with a [VO:category] prefix and a colour per level.
* [Frontend pages](./frontend-pages.md) - Four Svelte routes drive the user flow: record, preview and process, settings, and the floating recording widget.
* [Rust app shell](./rust-app-shell.md) - lib.rs builds the Tauri app, registers plugins and every command, and main.rs only calls run().
* [Rust recording commands](./rust-recording-commands.md) - commands/recording.rs writes recording chunks into a temp folder and joins them into one WebM file.
* [Rust config module](./rust-config.md) - config.rs defines AppConfig and reads and writes config.json in the app data folder.
* [Rust media pipeline](./rust-media-pipeline.md) - pipeline.rs, ffmpeg.rs and prerequisites.rs turn a recording into the final MP4 using ffmpeg and ElevenLabs.
* [Rust ElevenLabs client](./rust-elevenlabs.md) - elevenlabs.rs sends audio to the ElevenLabs speech-to-speech endpoint and validates API keys.
* [Rust Google Drive client](./rust-google-drive.md) - google_drive.rs runs the OAuth PKCE loopback flow and uploads a file to Drive with a public reader link.
