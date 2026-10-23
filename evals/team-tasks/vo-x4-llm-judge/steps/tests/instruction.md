The skills are installed in: /opt/review-skills
Use the review-tests skill. You are the `tests` reviewer.
Review the change between git refs 966a2d8778fe9a9cadf11431478349771365820f and 02b02c9de77c22a11c5e804064acffaf3c326fed in the repository in /workspace/repo.
Write your findings to /workspace/review/findings.tests.json. Write no other file and do not edit the repository.
Before anything else, print your skill file on its own, in a command that prints nothing else, and read it to its last line.
It is long. If the output says it was truncated or stops early, print the missing lines by line range until you have read all of it.
Your skill folder may have a `references/` folder beside the skill file. List it, and read every file in it to its last line, one file per command; if output is truncated, read the missing lines by line range. These files are part of your instructions, not optional reading.
Then read the change one file at a time, each in a command of its own. If output is truncated, read the missing lines before you go on. Never judge a file you have not read all of.
What the change is meant to do: The change lets the app seed its configuration from a project-level static config file when no saved config exists. The Rust config loader reads that file from the project root if present and writes it to app data, and the sync to the static folder is skipped when no API key is set. On the frontend, the loader accepts a config only if it includes an API key, falls back to the static file otherwise, and saves that config back to app data in the desktop app.
