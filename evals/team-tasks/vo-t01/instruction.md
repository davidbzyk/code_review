# The review team reviews a change before it is merged

This is a multi-step task. Each agent reads only its own step's `instruction.md`.

The git repository at `/workspace/repo` holds the change: `f280a86d34b0121cfd84e0815d6fdafa61f10337` (base) and
`c06bf86bd436dda60bee4c2b69f88f21b39f1ba6` (head). What the change is meant to do:

The change adds a Models page for managing local speech models and lets users choose which transcription model the voice pipeline uses. The sidecar gains a registry of named models with categories and recommendations, per-model download status, a delete endpoint, and a transcription model selectable per request. The settings and create-voice screens check only the models needed for the current local mode, and a new config field stores the chosen transcription model.

Steps 1 to 7 are the seven reviewers (security, tests, correctness, architecture, code_quality, compliance, language), each started with the message the
`review-orchestrator` skill sends it. Step 8 is the validator. The final findings are graded
against the change's known issues.
