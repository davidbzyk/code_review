The skills are installed in: /opt/review-skills
Use the review-tests skill. You are the `tests` reviewer.
Review the change between git refs d5d5f00f761c3ba95294d72aae04380d7b91ba80 and cdac7cc610b5f82199f8d6773921842f92c674b6 in the repository in /workspace/repo.
Write your findings to /workspace/review/findings.tests.json. Write no other file and do not edit the repository.
Before anything else, print your skill file on its own, in a command that prints nothing else, and read it to its last line.
It is long. If the output says it was truncated or stops early, print the missing lines by line range until you have read all of it.
Your skill folder may have a `references/` folder beside the skill file. List it, and read every file in it to its last line, one file per command; if output is truncated, read the missing lines by line range. These files are part of your instructions, not optional reading.
Then read the change one file at a time, each in a command of its own. If output is truncated, read the missing lines before you go on. Never judge a file you have not read all of.
What the change is meant to do: The change makes the Drive link on the preview page open through a button and adjusts video encoding for odd dimensions. The link opens through the shell plugin in the desktop app and in a new tab in the browser, with matching styles. The two commands that re-encode video now pad width and height up to even numbers, and the notes folder is added to gitignore.
