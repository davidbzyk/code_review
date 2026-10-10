# runtime notes

## Documents

* [Record the screen](./record-screen.md) - Steps from pressing Record to a finished recording file or in-memory blob.
* [Process a recording](./process-recording.md) - Steps the Rust pipeline performs for process_recording, with and without voice replacement.
* [Sidecar startup and restart](./sidecar-startup.md) - How the host launches the TTS sidecar and keeps it healthy.
* [Local voice generation in the sidecar](./local-voice-generation.md) - Steps the sidecar performs between POST /generate and a downloadable WAV file.
* [Create a local voice profile](./create-local-voice.md) - The five-step wizard in the create-voice route.
* [Google Drive connect and upload](./google-drive-connect-and-upload.md) - The OAuth loopback flow and the upload steps.
* [Config load and save](./config-load-and-save.md) - Where config comes from at startup and where it is written.
