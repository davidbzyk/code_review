The skills are installed in: /opt/review-skills
Use the review-security skill. You are the `security` reviewer.
Review the change between git refs 15fc88055ae2fb059db8e5b001b5807a14fdbcbd and 152365b8573f1f24309de7ab6366a5c75b56ed81 in the repository in /workspace/repo.
Write your findings to /workspace/review/findings.security.json. Write no other file and do not edit the repository.
Before anything else, print your skill file on its own, in a command that prints nothing else, and read it to its last line.
It is long. If the output says it was truncated or stops early, print the missing lines by line range until you have read all of it.
Your skill folder may have a `references/` folder beside the skill file. List it, and read every file in it to its last line, one file per command; if output is truncated, read the missing lines by line range. These files are part of your instructions, not optional reading.
Then read the change one file at a time, each in a command of its own. If output is truncated, read the missing lines before you go on. Never judge a file you have not read all of.
What the change is meant to do: The change adds a webcam overlay to recordings and moves stored credentials into the operating system keychain. The recorder composites the webcam bubble into the recorded video, with a preview bubble that can switch between two corner positions saved in preferences. Config handling saves secrets to the keychain, removes them from the config file and local storage, and limits file reads to allowed folders; the Drive sign-in now carries a state value. It also adds a CI workflow, an icon generator script and an in-memory blob store.
