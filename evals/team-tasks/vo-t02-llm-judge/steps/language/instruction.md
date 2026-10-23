The skills are installed in: /opt/review-skills
Use the review-language skill. You are the `language` reviewer.
Review the change between git refs 3f2a14268a65847b7cc5a8961eb7fb8a4bf575b1 and 9afeb65d8f0b0262250a7e8a11f146f4bf0e1eb1 in the repository in /workspace/repo.
Write your findings to /workspace/review/findings.language.json. Write no other file and do not edit the repository.
Before anything else, print your skill file on its own, in a command that prints nothing else, and read it to its last line.
It is long. If the output says it was truncated or stops early, print the missing lines by line range until you have read all of it.
Your skill folder may have a `references/` folder beside the skill file. List it, and read every file in it to its last line, one file per command; if output is truncated, read the missing lines by line range. These files are part of your instructions, not optional reading.
Then read the change one file at a time, each in a command of its own. If output is truncated, read the missing lines before you go on. Never judge a file you have not read all of.
What the change is meant to do: The change adds a bundled local text-to-speech sidecar that replaces the dependency on an external local voice server. A Python service handles transcription, voice profiles, chunked speech generation, model downloads and YouTube audio extraction, while the Rust backend starts, health-checks and stops it on a managed port and exposes commands to reach it. The frontend client, home, settings and create-voice screens route through these commands, and the build and CI setup include the sidecar binary.
