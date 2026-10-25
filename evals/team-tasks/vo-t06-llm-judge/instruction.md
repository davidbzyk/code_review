# The review team reviews a change before it is merged

This is a multi-step task. Each agent reads only its own step's `instruction.md`.

The git repository at `/workspace/repo` holds the change: `d47ca8270bc57385662f40f0c12f83f92b572c96` (base) and
`d9677189b6880ce609fd32f9132b8fc965fac999` (head). What the change is meant to do:

The change adds region capture to screen recording. After the user picks a screen, a selection overlay shows a captured frame and lets them draw a rectangle, and the recorder crops the stream to that rectangle. It also maps the capture mode to the picker's surface hint, minimizes and restores the app window around the picker, waits for the first video frame before compositing, and sets a dark background color on the window and page.

Steps 1 to 7 are the seven reviewers (security, tests, correctness, architecture, code_quality, compliance, language), each started with the message the
`review-orchestrator` skill sends it. Step 8 is the validator. The final findings are graded
against the change's known issues.
