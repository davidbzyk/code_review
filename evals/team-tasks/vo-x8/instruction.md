# The review team reviews a change before it is merged

This is a multi-step task. Each agent reads only its own step's `instruction.md`.

The git repository at `/workspace/repo` holds the change: `d5d5f00f761c3ba95294d72aae04380d7b91ba80` (base) and
`cdac7cc610b5f82199f8d6773921842f92c674b6` (head). What the change is meant to do:

The change makes the Drive link on the preview page open through a button and adjusts video encoding for odd dimensions. The link opens through the shell plugin in the desktop app and in a new tab in the browser, with matching styles. The two commands that re-encode video now pad width and height up to even numbers, and the notes folder is added to gitignore.

Steps 1 to 7 are the seven reviewers (security, tests, correctness, architecture, code_quality, compliance, language), each started with the message the
`review-orchestrator` skill sends it. Step 8 is the validator. The final findings are graded
against the change's known issues.
