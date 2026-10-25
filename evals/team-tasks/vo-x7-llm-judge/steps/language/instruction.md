The skills are installed in: /opt/review-skills
Use the review-language skill. You are the `language` reviewer.
Review the change between git refs 1c236b38a1908ac0957466bbbb94dcedfed3ce20 and 4e456c8999479b805aaa7bedec6a0a25327bb481 in the repository in /workspace/repo.
Write your findings to /workspace/review/findings.language.json. Write no other file and do not edit the repository.
Before anything else, print your skill file on its own, in a command that prints nothing else, and read it to its last line.
It is long. If the output says it was truncated or stops early, print the missing lines by line range until you have read all of it.
Your skill folder may have a `references/` folder beside the skill file. List it, and read every file in it to its last line, one file per command; if output is truncated, read the missing lines by line range. These files are part of your instructions, not optional reading.
Then read the change one file at a time, each in a command of its own. If output is truncated, read the missing lines before you go on. Never judge a file you have not read all of.
What the change is meant to do: The change simplifies how configuration is synced to the static folder and how Drive tokens are refreshed before upload. The Rust sync writes the full configuration instead of a reduced copy with credentials blanked, and its doc comment notes the file is gitignored. The preview page checks token expiry once before upload, for both desktop and browser modes, and refreshes the token when the expiry is missing or has passed.
