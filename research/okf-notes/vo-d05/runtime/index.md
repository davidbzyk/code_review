# runtime

Notes in this folder.

* [Browser mode pipeline](./browser-mode-pipeline.md) - Preview-page flow used outside Tauri: ElevenLabs fetch and ffmpeg.wasm splicing.
* [Google Drive connect and upload](./drive-connect-and-upload.md) - OAuth connect from Settings and upload from Preview, in Tauri and browser modes.
* [Process recording with ElevenLabs](./process-recording-elevenlabs.md) - Flow of the process_recording command when voice replacement uses the ElevenLabs provider.
* [Process recording with local TTS](./process-recording-local-tts.md) - Flow of process_recording when provider is local, using transcribe-then-generate or voice conversion.
* [Record a screen session](./record-screen.md) - Flow from pressing Record to a finalized recording file and the navigation to the preview page.
* [Sidecar startup](./sidecar-startup.md) - How the Rust host starts the Python sidecar, waits for health and keeps it alive.
* [Voice generation job in the sidecar](./voice-generation-job.md) - How POST /generate queues a job, builds audio per segment and exposes the WAV for download.
* [Create a local voice profile](./voice-profile-creation.md) - Wizard flow from model download to a profile with a reference sample.
