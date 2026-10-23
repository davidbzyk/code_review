# The review team reviews a change before it is merged

This is a multi-step task. Each agent reads only its own step's `instruction.md`.

The git repository at `/workspace/repo` holds the change: `ea652265cd8db98f0a52d601325af6de837357b9` (base) and
`5794f727be0b1a2474ac9659058a5efae840a94c` (head). What the change is meant to do:

The change makes the Drive link on the preview page open through a button and adjusts video encoding for odd dimensions. The link opens through the shell plugin in the desktop app and in a new tab in the browser, with matching styles. The two commands that re-encode video now pad width and height up to even numbers, and the notes folder is added to gitignore.

Steps 1 to 7 are the seven reviewers (security, tests, correctness, architecture, code_quality, compliance, language), each started with the message the
`review-orchestrator` skill sends it. Step 8 is the validator. The final findings are graded
against the change's known issues.
