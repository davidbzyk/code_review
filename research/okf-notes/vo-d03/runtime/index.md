# runtime

## Documents

- [Flow: connect Google Drive](./google-drive-connect.md) - Steps of the OAuth PKCE sign-in started from the settings page.
- [Flow: load configuration at startup](./load-config.md) - Order of config sources tried by appState.loadConfig and the Rust get_config.
- [Flow: process a recording in the browser](./process-recording-browser.md) - Steps of processViaBrowser: S2S request and ffmpeg.wasm splice.
- [Flow: process a recording in the desktop app](./process-recording-desktop.md) - Steps from Save on the preview page to the final MP4 and progress events.
- [Flow: record the screen](./record-screen.md) - Steps from the Record button to a finished recording file or blob.
- [Flow: upload to Google Drive](./upload-to-drive.md) - Steps of uploading the saved video and getting a share link.
