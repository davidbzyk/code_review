The skills are installed in: /opt/review-skills
Use the review-code-quality skill. You are the `code_quality` reviewer.
Review the change between git refs 95142b184077306b75e5957c0462c00e40a86e0b and 35892f2d11ed26e6830b20cae8125cbc25287a9d in the repository in /workspace/repo.
Write your findings to /workspace/review/findings.code_quality.json. Write no other file and do not edit the repository.
Before anything else, print your skill file on its own, in a command that prints nothing else, and read it to its last line.
It is long. If the output says it was truncated or stops early, print the missing lines by line range until you have read all of it.
Your skill folder may have a `references/` folder beside the skill file. List it, and read every file in it to its last line, one file per command; if output is truncated, read the missing lines by line range. These files are part of your instructions, not optional reading.
Then read the change one file at a time, each in a command of its own. If output is truncated, read the missing lines before you go on. Never judge a file you have not read all of.
What the change is meant to do: The change adds a bundled local text-to-speech sidecar that replaces the dependency on an external local voice server. A Python service handles transcription, voice profiles, chunked speech generation, model downloads and YouTube audio extraction, while the Rust backend starts, health-checks and stops it on a managed port and exposes commands to reach it. The frontend client, home, settings and create-voice screens route through these commands, and the build and CI setup include the sidecar binary.
