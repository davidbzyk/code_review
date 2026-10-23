The skills are installed in: /opt/review-skills
Use the review-language skill. You are the `language` reviewer.
Review the change between git refs 02ac4d2949831e10616c378437beaf866f626f26 and 1300764111acc28a5c4b093d6577116392173f88 in the repository in /workspace/repo.
Write your findings to /workspace/review/findings.language.json. Write no other file and do not edit the repository.
Before anything else, print your skill file on its own, in a command that prints nothing else, and read it to its last line.
It is long. If the output says it was truncated or stops early, print the missing lines by line range until you have read all of it.
Your skill folder may have a `references/` folder beside the skill file. List it, and read every file in it to its last line, one file per command; if output is truncated, read the missing lines by line range. These files are part of your instructions, not optional reading.
Then read the change one file at a time, each in a command of its own. If output is truncated, read the missing lines before you go on. Never judge a file you have not read all of.
What the change is meant to do: The change adds a session-id check to the recording commands, an expiry timestamp for Drive tokens, a timeout on the Drive sign-in callback, async video-tool calls and a content security policy in the window config. The frontend shares one environment-detection helper instead of local copies, sends recording chunks as byte arrays, listens for widget stop and cancel events on the home page and refreshes expired Drive tokens before upload. It removes two unused Rust dependencies and blanks credentials in the config file synced to the static folder.
