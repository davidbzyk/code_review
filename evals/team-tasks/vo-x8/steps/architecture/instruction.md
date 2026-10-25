The skills are installed in: /opt/review-skills
Use the review-architecture skill. You are the `architecture` reviewer.
Review the change between git refs ea652265cd8db98f0a52d601325af6de837357b9 and 5794f727be0b1a2474ac9659058a5efae840a94c in the repository in /workspace/repo.
Write your findings to /workspace/review/findings.architecture.json. Write no other file and do not edit the repository.
Before anything else, print your skill file on its own, in a command that prints nothing else, and read it to its last line.
It is long. If the output says it was truncated or stops early, print the missing lines by line range until you have read all of it.
Your skill folder may have a `references/` folder beside the skill file. List it, and read every file in it to its last line, one file per command; if output is truncated, read the missing lines by line range. These files are part of your instructions, not optional reading.
Then read the change one file at a time, each in a command of its own. If output is truncated, read the missing lines before you go on. Never judge a file you have not read all of.
What the change is meant to do: The change makes the Drive link on the preview page open through a button and adjusts video encoding for odd dimensions. The link opens through the shell plugin in the desktop app and in a new tab in the browser, with matching styles. The two commands that re-encode video now pad width and height up to even numbers, and the notes folder is added to gitignore.
