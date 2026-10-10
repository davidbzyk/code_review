# Building blocks (arc42 section 5)

Notes in the `building-blocks` folder.

## Documents

* [App Shell](./app-shell.md) - The HTML template, global CSS, root layout and per-route layout flags that wrap every page.
* [Backend Config and Secrets](./backend-config-and-secrets.md) - The config file model and the keychain vault.
* [Backend Entry and Commands](./backend-entry-and-commands.md) - The Rust entry point, plugin setup, handler registration, recording commands, window commands and the ffmpeg check.
* [Backend Google Drive](./backend-google-drive.md) - OAuth 2.0 PKCE connection and file upload to Google Drive.
* [Backend Pipeline and ffmpeg](./backend-pipeline-and-ffmpeg.md) - The processing pipeline command and the ffmpeg wrapper.
* [Backend TTS Providers](./backend-tts-providers.md) - The ElevenLabs client, the Voicebox client and the provider enum.
* [Frontend Integrations](./frontend-integrations.md) - Client code for the Voicebox server and Google Drive used by the pages.
* [Frontend Recording](./frontend-recording.md) - Browser media capture, canvas compositing and region selection.
* [Frontend Routes](./frontend-routes.md) - The five pages of the SvelteKit app and what each one does.
* [Frontend State](./frontend-state.md) - Shared reactive app state, the Tauri bridge, the in-memory blob store and the logger.
* [Icon Tooling](./icon-tooling.md) - The Python script that draws the app icon and writes icon files.
