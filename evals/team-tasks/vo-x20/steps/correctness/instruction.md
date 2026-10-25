The skills are installed in: /opt/review-skills
Use the review-correctness skill. You are the `correctness` reviewer.
Review the change between git refs 1bba865ce5572776ba281dcefae126d4b74ed0fd and b3b3207e612681e8a48c0ba284ac2a048fc56572 in the repository in /workspace/repo.
Write your findings to /workspace/review/findings.correctness.json. Write no other file and do not edit the repository.
Before anything else, print your skill file on its own, in a command that prints nothing else, and read it to its last line.
It is long. If the output says it was truncated or stops early, print the missing lines by line range until you have read all of it.
Your skill folder may have a `references/` folder beside the skill file. List it, and read every file in it to its last line, one file per command; if output is truncated, read the missing lines by line range. These files are part of your instructions, not optional reading.
Then read the change one file at a time, each in a command of its own. If output is truncated, read the missing lines before you go on. Never judge a file you have not read all of.
What the change is meant to do: The change lets recordings be renamed from the video library, renaming every companion file, and reworks text-to-speech timing: audio duration probing, transcription accuracy and the repair of word timestamps. It prevents audio clipping in both text-to-speech and voice conversion modes, adds the CosyVoice3 model to the prerequisites and model downloads, signs the sidecar build, reads the ElevenLabs API key from the environment when it is set, and updates the README.
