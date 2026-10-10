# Runtime view (arc42 section 6)

Notes in the `runtime` folder.

## Documents

* [Config Load and Save](./config-load-and-save.md) - How configuration moves between the webview, localStorage, config.json and the keychain.
* [Drive Upload](./drive-upload.md) - Uploading the saved video to Google Drive from the preview page.
* [Google Drive Connect](./google-drive-connect.md) - The OAuth 2.0 loopback flow with PKCE.
* [Process Recording in the Browser](./process-recording-browser.md) - The browser-mode path that calls ElevenLabs directly and splices audio with ffmpeg.wasm.
* [Process Recording on Desktop](./process-recording-desktop.md) - The Rust pipeline from a recorded file to a final MP4.
* [Record Flow](./record-flow.md) - From the Record button to a finalized WebM file and the preview page.
* [Voice Profile Wizard](./voice-profile-wizard.md) - The five-step flow that creates a local Voicebox voice profile.
