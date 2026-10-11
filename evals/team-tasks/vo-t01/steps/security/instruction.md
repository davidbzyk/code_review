The skills are installed in: /opt/review-skills
Use the review-security skill. You are the `security` reviewer.
Review the change between git refs aa9931fa0eb907c9b622e3faed1a41bed241aa3f and e6c05ff08b755f3e74c9065d036dede7fb5f2158 in the repository in /workspace/repo.
Write your findings to /workspace/review/findings.security.json. Write no other file and do not edit the repository.
Before anything else, print your skill file on its own, in a command that prints nothing else, and read it to its last line.
It is long. If the output says it was truncated or stops early, print the missing lines by line range until you have read all of it.
Your skill folder may have a `references/` folder beside the skill file. List it, and read every file in it to its last line, one file per command; if output is truncated, read the missing lines by line range. These files are part of your instructions, not optional reading.
Then read the change one file at a time, each in a command of its own. If output is truncated, read the missing lines before you go on. Never judge a file you have not read all of.
What the change is meant to do: The change adds a Models page for managing local speech models and lets users choose which transcription model the voice pipeline uses. The sidecar gains a registry of named models with categories and recommendations, per-model download status, a delete endpoint, and a transcription model selectable per request. The settings and create-voice screens check only the models needed for the current local mode, and a new config field stores the chosen transcription model.
