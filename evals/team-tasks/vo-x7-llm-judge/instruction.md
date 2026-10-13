# The review team reviews a change before it is merged

This is a multi-step task. Each agent reads only its own step's `instruction.md`.

The git repository at `/workspace/repo` holds the change: `748d85a9a8cd04b0d38039ddd2489363d3971528` (base) and
`a66bd3b1e89d8e4d07d8991caa9f41f00a952f28` (head). What the change is meant to do:

The change simplifies how configuration is synced to the static folder and how Drive tokens are refreshed before upload. The Rust sync writes the full configuration instead of a reduced copy with credentials blanked, and its doc comment notes the file is gitignored. The preview page checks token expiry once before upload, for both desktop and browser modes, and refreshes the token when the expiry is missing or has passed.

Steps 1 to 7 are the seven reviewers (security, tests, correctness, architecture, code_quality, compliance, language), each started with the message the
`review-orchestrator` skill sends it. Step 8 is the validator. The final findings are graded
against the change's known issues.
