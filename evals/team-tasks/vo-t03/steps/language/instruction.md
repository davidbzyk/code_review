The skills are installed in: /opt/review-skills
Use the review-language skill. You are the `language` reviewer.
Review the change between git refs 0b3d1346cb747cee4647c144d91c955f9522cf34 and 3a944f6c5bd372b00769eeecd950eb180cbc656b in the repository in /workspace/repo.
Write your findings to /workspace/review/findings.language.json. Write no other file and do not edit the repository.
Before anything else, print your skill file on its own, in a command that prints nothing else, and read it to its last line.
It is long. If the output says it was truncated or stops early, print the missing lines by line range until you have read all of it.
Your skill folder may have a `references/` folder beside the skill file. List it, and read every file in it to its last line, one file per command; if output is truncated, read the missing lines by line range. These files are part of your instructions, not optional reading.
Then read the change one file at a time, each in a command of its own. If output is truncated, read the missing lines before you go on. Never judge a file you have not read all of.
What the change is meant to do: The change extends the local voice sidecar with a voice-conversion mode alongside text-to-speech, and makes generated audio follow the original recording's timing. The sidecar gains a conversion endpoint, timestamp-aligned segment generation, transcript filtering and path validation; the Rust backend probes video duration, picks the mode from config, saves a transcript next to the output and cleans up stale temporary recordings. It also adds sidecar test suites, a build script and an expanded README.
