# cr-self-01: the review tool's own CI action (draft key, for the owner's review)

Base `cd22309` (REPO before the action), head `07284ea` (the first action commit, 828 lines).
Each row is a defect the head contains, confirmed by a later fix commit and a test that fails
before it and passes after. Lines are at the head commit.

| id | sev | file:line | defect | fixed in |
|---|---|---|---|---|
| g01 | P1 | src/review_core/ci/github.py:266 | The agent-written change summary is read with read_text, which follows a symlink; a misled agent links it to the seeded Codex login and the summary comment publishes it | 20fa0ab |
| g02 | P2 | src/review_core/ci/github.py:167 | The permalink embeds the model's file path raw, so a crafted path injects Markdown, links or @-mentions into the review body | 20fa0ab |
| g03 | P3 | src/review_core/ci/github.py:246 | find_run globs **/review.json, so an agent-written review.json anywhere under the run folder is picked up or makes the post fail | 20fa0ab |
| g04 | P1 | action/action.yml:36 | Ubuntu 24.04 runners block the unprivileged user namespaces bubblewrap needs, so no reviewer can run a command and every review fails | 7b7111e |
| g05 | P1 | action/run-review.sh:24 | The codex-clean row hands every reviewer the ChatGPT account's connected apps, computer use and browser use; in a live run a reviewer reached for Desktop Commander on the owner's Mac | 7b7111e |
| g06 | P2 | src/review_core/ci/github.py:139 | A failed run, in which no reviewer ran, posts "No issues found." and reads as a clean review | ded8ec2 |
| g07 | P1 | src/review_core/ci/github.py:219 | Nothing checks the posted text for credentials, though the reviewers can read the seeded login; a reviewer can copy the token into a finding and it is published | 09b7a52 |
| g08 | P1 | action/run-review.sh:47 | The findings folder is in RUNNER_TEMP, outside the one folder Codex lets agents write, so the aggregator cannot write and every review fails | 8d4a47b |
| g09 | P1 | action/action.yml:53 | The run folder, holding every command the agents ran and its output, is uploaded as an artifact on every run; anyone who can read the repository can download it | c4d9b14 |
| g10 | P1 | action/run-review.sh:45 | python3 -m puts the working directory, the agent-writable checkout, first on the import path, so a planted review_core/ runs inside the poster that holds the GitHub token | c4d9b14 |
| g11 | P1 | action/run-review.sh:5 | The tool runs from .code-review/ inside the checkout, which agents may write, so a reviewer can rewrite the poster before it runs with the token | 0ce743b |
| g12 | P1 | action/workflow.yml:25 | actions/checkout keeps the job token in .git/config, where the reviewers can read it | 0ce743b |
| g13 | P2 | action/run-review.sh:15 | git diff --name-only quotes non-ASCII and unusual paths, so those files drop out of the review | 0ce743b |
| g14 | P2 | src/review_core/ci/github.py:219 | Every push posts every finding again; nothing checks what the bot already posted | 0ce743b |
| g15 | P2 | action/workflow.yml:21 | Dependabot pull requests get no secrets, so the review check fails red on every one | 0ce743b |
| g16 | P3 | action/workflow.yml:25 | Actions are pinned by tag, not by commit SHA | 0ce743b |
| g17 | P2 | src/review_core/ci/github.py:224 | The summary comment to edit is any comment starting with the marker; anyone can post one and the bot overwrites it or fails | 3c951e4 |
| g18 | P1 | action/run-review.sh:24 | Reviewer commands have network access while the Codex login is readable, so a misled reviewer can send the login out directly | 3c951e4 |

Out of this case (introduced after 07284ea, a candidate second case): the credential check's
symlink-only reader (hardlink), escaped-text and fail-open gaps, and forged inline markers.
