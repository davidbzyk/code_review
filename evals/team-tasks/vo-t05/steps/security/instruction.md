The skills are installed in: /opt/review-skills
Use the review-security skill. You are the `security` reviewer.
Review the change between git refs 097979928cd0a5376e81f2129cf81d50d425a70d and 471de15e63ce9030beee4560c38a9fc45c7d9837 in the repository in /workspace/repo.
Write your findings to /workspace/review/findings.security.json. Write no other file and do not edit the repository.
Before anything else, print your skill file on its own, in a command that prints nothing else, and read it to its last line.
It is long. If the output says it was truncated or stops early, print the missing lines by line range until you have read all of it.
Your skill folder may have a `references/` folder beside the skill file. List it, and read every file in it to its last line, one file per command; if output is truncated, read the missing lines by line range. These files are part of your instructions, not optional reading.
Then read the change one file at a time, each in a command of its own. If output is truncated, read the missing lines before you go on. Never judge a file you have not read all of.
What the change is meant to do: The change adds a Library screen and a sidebar layout for browsing past recordings. The Rust backend lists recordings with sizes, dates, thumbnails and metadata, and offers commands to generate thumbnails, delete, open and reveal files; the pipeline and Drive upload write a companion metadata file with voice and share-link details. Existing pages move under a shared layout with a sidebar and status bar, and the main window is made wider.
