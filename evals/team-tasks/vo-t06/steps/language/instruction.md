The skills are installed in: /opt/review-skills
Use the review-language skill. You are the `language` reviewer.
Review the change between git refs 12998e404b8d505056221802db4756d39adbd5a0 and b27e76080c69c9fe7eb127e1db7f1f9ae692088a in the repository in /workspace/repo.
Write your findings to /workspace/review/findings.language.json. Write no other file and do not edit the repository.
Before anything else, print your skill file on its own, in a command that prints nothing else, and read it to its last line.
It is long. If the output says it was truncated or stops early, print the missing lines by line range until you have read all of it.
Your skill folder may have a `references/` folder beside the skill file. List it, and read every file in it to its last line, one file per command; if output is truncated, read the missing lines by line range. These files are part of your instructions, not optional reading.
Then read the change one file at a time, each in a command of its own. If output is truncated, read the missing lines before you go on. Never judge a file you have not read all of.
What the change is meant to do: The change adds region capture to screen recording. After the user picks a screen, a selection overlay shows a captured frame and lets them draw a rectangle, and the recorder crops the stream to that rectangle. It also maps the capture mode to the picker's surface hint, minimizes and restores the app window around the picker, waits for the first video frame before compositing, and sets a dark background color on the window and page.
