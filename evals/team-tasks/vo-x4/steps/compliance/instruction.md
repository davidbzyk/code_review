The skills are installed in: /opt/review-skills
Use the review-compliance skill. You are the `compliance` reviewer.
Review the change between git refs b957febf3680dbc91ad08b67333b1ff649f997d5 and 3a0594941a1ae4200d6d532be5ae1a99b58f0201 in the repository in /workspace/repo.
Write your findings to /workspace/review/findings.compliance.json. Write no other file and do not edit the repository.
Before anything else, print your skill file on its own, in a command that prints nothing else, and read it to its last line.
It is long. If the output says it was truncated or stops early, print the missing lines by line range until you have read all of it.
Your skill folder may have a `references/` folder beside the skill file. List it, and read every file in it to its last line, one file per command; if output is truncated, read the missing lines by line range. These files are part of your instructions, not optional reading.
Then read the change one file at a time, each in a command of its own. If output is truncated, read the missing lines before you go on. Never judge a file you have not read all of.
What the change is meant to do: The change lets the app seed its configuration from a project-level static config file when no saved config exists. The Rust config loader reads that file from the project root if present and writes it to app data, and the sync to the static folder is skipped when no API key is set. On the frontend, the loader accepts a config only if it includes an API key, falls back to the static file otherwise, and saves that config back to app data in the desktop app.
