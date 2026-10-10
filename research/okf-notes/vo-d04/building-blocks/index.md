# Building Blocks

Notes of kind `building-blocks`.

* [Frontend shell and static assets](./frontend-shell.md) - Root layout, HTML template, global CSS and route options of the SvelteKit app.
* [Frontend shared state](./frontend-state.md) - The AppState class, config types and the isTauri helper.
* [Frontend recorder module](./frontend-recorder.md) - Browser media capture with MediaRecorder, in chunked Tauri mode or in-memory browser mode.
* [Frontend logger](./frontend-logger.md) - Console logger that prefixes messages with [VO:category].
* [Route / (record page)](./route-home.md) - The home page: capture options, voice choice and record controls.
* [Route /preview](./route-preview.md) - Preview, process, save and upload of a finished recording.
* [Route /settings](./route-settings.md) - Settings page for the API key, voices, output folder and Google Drive.
* [Route /widget](./route-widget.md) - Small always-on-top recording widget page.
* [Backend shell](./backend-shell.md) - Rust entry point that builds the Tauri app and registers plugins and commands.
* [Backend config store](./backend-config.md) - AppConfig structs and the get_config and save_config commands.
* [Backend recording commands](./backend-recording-commands.md) - Commands that store, join and read recording files in the OS temp directory.
* [Backend window commands](./backend-window-commands.md) - Commands that open and close the widget window.
* [Backend processing pipeline](./backend-pipeline.md) - The process_recording command that turns a recording into a final MP4.
* [Backend ffmpeg wrappers and prerequisites](./backend-ffmpeg.md) - Functions that run the system ffmpeg program and check that it exists.
* [Backend ElevenLabs client](./backend-elevenlabs.md) - Speech-to-speech request and API key test against api.elevenlabs.io.
* [Backend Google Drive client](./backend-google-drive.md) - OAuth PKCE loopback connect, token refresh helper and file upload.
