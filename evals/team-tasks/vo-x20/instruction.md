# The review team reviews a change before it is merged

This is a multi-step task. Each agent reads only its own step's `instruction.md`.

The git repository at `/workspace/repo` holds the change: `f3d8d6db39233016be1ef4f0c08b9993bea4f28d` (base) and
`47f76c29d4bbf66d2df8ca04929894bfc698882d` (head). What the change is meant to do:

The change lets recordings be renamed from the video library, renaming every companion file, and reworks text-to-speech timing: audio duration probing, transcription accuracy and the repair of word timestamps. It prevents audio clipping in both text-to-speech and voice conversion modes, adds the CosyVoice3 model to the prerequisites and model downloads, signs the sidecar build, reads the ElevenLabs API key from the environment when it is set, and updates the README.

Steps 1 to 7 are the seven reviewers (security, tests, correctness, architecture, code_quality, compliance, language), each started with the message the
`review-orchestrator` skill sends it. Step 8 is the validator. The final findings are graded
against the change's known issues.
