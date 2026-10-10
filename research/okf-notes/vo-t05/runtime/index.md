# Runtime

Step-by-step flows.

## Documents

* [Flow: Record the Screen](./record-screen.md) - How a recording starts, streams chunks to disk, and stops.
* [Flow: Process a Recording (ElevenLabs)](./process-recording-elevenlabs.md) - The `process_recording` steps when the provider is elevenlabs or voice replacement is off.
* [Flow: Process a Recording (Local TTS)](./process-recording-local.md) - The pipeline branch used when config.provider is local.
* [Flow: Sidecar Startup and Shutdown](./sidecar-startup.md) - How the app launches the TTS child process and how the child exits.
* [Flow: Create a Local Voice Profile](./create-voice-profile.md) - The /create-voice wizard from health check to a saved profile id.
* [Flow: Connect and Upload to Google Drive](./google-drive-connect-upload.md) - The settings connect flow and the preview upload flow.
* [Flow: Browser-Mode Processing](./browser-mode-processing.md) - How /preview processes a recording when the app runs without Tauri.
* [Flow: Load and Save Config](./config-load-save.md) - How configuration moves between Tauri app data, the keychain, a dev static file and localStorage.
