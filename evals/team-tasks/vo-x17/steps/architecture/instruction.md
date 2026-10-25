The skills are installed in: /opt/review-skills
Use the review-architecture skill. You are the `architecture` reviewer.
Review the change between git refs 21d799db2caf42be15514065780e0faadaae83d9 and bb090a4a9bf3951afa70d85e4bb727948eeba754 in the repository in /workspace/repo.
Write your findings to /workspace/review/findings.architecture.json. Write no other file and do not edit the repository.
Before anything else, print your skill file on its own, in a command that prints nothing else, and read it to its last line.
It is long. If the output says it was truncated or stops early, print the missing lines by line range until you have read all of it.
Your skill folder may have a `references/` folder beside the skill file. List it, and read every file in it to its last line, one file per command; if output is truncated, read the missing lines by line range. These files are part of your instructions, not optional reading.
Then read the change one file at a time, each in a command of its own. If output is truncated, read the missing lines before you go on. Never judge a file you have not read all of.
What the change is meant to do: The change reorganises sidecar HTTP and generation code and routes generated audio through the desktop backend. The Rust side registers one shared HTTP client with per-request timeouts, adds a command that returns generated audio bytes, validates generation ids and waits for sidecar startup by notification instead of polling. The Python server moves generation and voice conversion into separate functions run by the queue, and common page styles move into the global stylesheet. The content security policy no longer allows media from localhost.
