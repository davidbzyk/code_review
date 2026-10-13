# Code Review Workflow

This is both a research experiment into the most effective way to build a custom code review, and
an example workflow for my business, [General Environments](https://general-environments.ai/).
General Environments is a community-based benchmarking and agentic evaluation platform. It has
253 open-source benchmarks: you can fork one to create your own, import your own to evaluate it
quickly across harnesses and models, or work with an expert to build the right agentic workflow
and evaluation set for your business.

**The experiment.** A team of review agents on an affordable, capable model (GPT-6 Luna,
`gpt-6-luna`), given one of three kinds of context: a graphed OKF knowledge base, a vector search
index, or nothing but the code itself (plain). In short, letting the model search the codebase on
its own did as well as either context store, with nothing to build or serve. This repository
holds the public voiceover cases and experiments; I also include the results from General
Environments' own codebase, as it is a great example of rapid agentic engineering.

**The first cross-model result.** On the 12 public eval tasks, gpt-6.1-sol (high) found about 1.7
times as many of the known bugs as gpt-6-luna (medium), at about 19 times the cost per task ($4.65
against $0.24, API-equivalent). The numbers are under [Results so far](#results-so-far).

**The comparison.** Several commercial reviewers were turned on here next to the repository's own
review action, but only two of them reviewed its pull requests: CodeRabbit (60 comments across 18
pull requests) and GitHub Copilot (17). Codex, Greptile, Gravity, Devin and Sonar posted nothing, so
the side-by-side on these pull requests is CodeRabbit, Copilot and the review action.

**The design.** I went through all my code and security review plugins and kept what I thought
was valuable from each; every reviewer cites its sources in its own folder (see the last section).

The full write-up will be a Medium article *(link when published)* that compares and evaluates:
this repository's evals are imported into General Environments and run across models and harnesses,
for review quality and for cost. Running every task on every model proved expensive, so part of the
work is finding the most economically viable set of tasks and models. The article also covers a
larger, more complex codebase (General Environments itself). This README is its summary.

## What is in this repository

| Part | What it does | Where |
|---|---|---|
| The review team | Seven reviewers (security, tests, correctness, architecture, code quality, compliance, language) and a validator, run by one orchestrator, merged into one de-duplicated set of findings | `src/review_core/`, `src/plugin/` |
| The CI action | Reviews every pull request on a GitHub runner with Codex and posts the findings like the commercial review bots do | `action/` |
| The evals | Rubric-graded Harbor tasks built from real, confirmed bugs, each run by the whole review team as a multi-step task, for any agent, harness, model and judge | `evals/` |
| The research | The voiceover cases, the frozen answer keys, the OKF notes and every scored review | `research/` |

## The research: does giving review agents more context help?

**Question.** Does a code-review agent team find more real bugs when it can look things up in a
vector index of the repository (**vector**) or in curated knowledge notes (**OKF**), compared
with reading the code alone (**plain**)?

**Setup.**
- Seven reviewers per review, each its own agent, plus a validator for serious findings.
  Model gpt-6-luna, reasoning effort high, Codex CLI.
- Ground truth: 28 real merged pull requests from one private Python monorepo (General
  Environments' own). The "golden" issues are the comments six paid review bots left that the
  owner accepted: 111 in all.
- Judge: an LLM judge following the Martian Code Review Bench method (does a finding state "the
  same underlying issue" as a golden comment).
- 84 reviews: 28 pull requests, three arms, one run each.

**Results.**

| Arm | Recall | Precision | Findings kept per PR | Billed input per run |
|---|---|---|---|---|
| plain | 32/111 (29%) | 15% | 6.5 | 0.87M tokens |
| vector | 29/111 (26%) | 17% | 5.0 | 0.94M tokens |
| OKF | 31/111 (28%) | 14% | 6.8 | 1.03M tokens |

- **Context did not help.** Pull request by pull request, the arms are within chance of each
  other (plain beat vector on 5 and lost on 2, 20 ties; sign test p = 0.45). Plain wins on
  simplicity: same recall, nothing to build or serve.
- **Variance beats context.** Only 17 of 111 issues were found by all three arms, while 46 (41%)
  were found by at least one. Running the same review twice and merging is the next test.
- **Noise sits in a few reviewers.** The compliance reviewer kept 168 findings that matched 4
  golden issues; dropping it lifts precision from 15% to 23% for one golden issue of recall.
- **Billed versus total tokens.** A run reads 27 to 35M tokens, but about 97% is cached
  re-reading of the agents' own conversations. Quoting total tokens overstates cost about
  thirtyfold.
- **Against the bots.** The team finds about a quarter of what six paid bots raised together.
  Not a replacement yet, though it does find good things at times.

**Caveats.** One run per pull request and arm; one repository, one model, one effort level;
golden issues are only what the bots raised and the owner accepted.

### The pre-registered replication on a public repository

The same question, pre-registered before any scored run, on a public repository: **voiceover**.
Five development changes were used for tuning only; six test changes were scored once, one whole
pull request per review, against a frozen answer key (sha256 recorded in the pre-registration).

| Arm (6 test cases) | Recall | Precision | Findings |
|---|---|---|---|
| plain | 22% | 31% | 36 |
| vector | 32% | 25% | 59 |
| OKF | 26% | 24% | 63 |

Vector found the most bugs but wrote the most noise; with six cases, no arm's lead is outside
chance. The same answer as above: context stores do not yet earn their cost.

`research/` holds everything needed to check it: the cases (`cases.csv`, naming each change's
voiceover commits, and each case's manifest and intent), the answer keys and their lock files
(`key/`), the OKF notes (`okf-notes/`), and every scored review with its scores (`results/`). The
exact trees the reviewers read for the six test cases ship inside the eval tasks
(`evals/team-tasks/vo-t0N/environment/repo.tar.gz`). The vector stores (14 GB) are rebuilt from the
scripts rather than committed.

## The CI action: add the review to your project

Every pull request gets reviewed by the seven-reviewer team on a GitHub runner, and the findings are
posted as one review with inline comments plus a summary that updates on each push. A review takes
2 to 6 minutes here (median 3.5 over the last ten runs).

1. **Install it into your repository** (from a checkout of this one):

       git clone https://github.com/davidbzyk/code_review
       sh code_review/action/install.sh /path/to/your/repo

   This writes `.code-review/` (the smallest working copy of the tool) and
   `.github/workflows/code-review.yml` into your repository.

2. **Give Codex a way to sign in**, one of:

   - a ChatGPT subscription (no per-token cost): sign in once with `codex login`, then
     `base64 < ~/.codex/auth.json | gh secret set CODEX_AUTH_JSON_B64 -R OWNER/REPO`
   - an OpenAI API key: `gh secret set OPENAI_API_KEY -R OWNER/REPO`, then
     `gh variable set CODE_REVIEW_AUTH -b api-key -R OWNER/REPO`

3. **Commit both and open a pull request.** Ready (non-draft) pull requests from branches of your
   repository are reviewed; forks and Dependabot get no secrets and are skipped.

**It remembers its earlier review.** Before each review the action reads its own earlier threads
on the pull request. A finding someone resolved, or answered with a reply (fixed or not), is not
raised again unless the lines it names change; one left open keeps counting in the summary. Replies
reach the reviewers only from people who can push to the repository, checked with the workflow's own
`GITHUB_TOKEN`, so there is no extra token or GitHub App to set up; a reply from a read or triage
collaborator is ignored. On a nine-commit pull request in General Environments, six findings it
raised were answered once and never came back across the five reviews that followed.

To update, run the installer again; never edit `.code-review/` by hand. Model, effort, title and
the other options, and the security model, are in [`action/README.md`](action/README.md).

It was built in a day and then reviewed by every reviewer we had: commercial bots, a headless
Claude review, a security plugin and the action itself on its own pull requests. They found about
40 real defects in it (credential leaks through symlinks, hardlinks and escaped text, a sandbox
that would not start on GitHub's runners, account apps reaching the owner's machine, an import
hijack, findings reposted on every push), each fixed with a test that fails before the fix.

## The evals, and the loop they are for

Each eval is a Harbor task: a real change, its confirmed bugs as a rubric, and a judge that
scores how many of them a review finds. The agent, harness, model and judge are all chosen at
run time, so the same tasks compare any of them.

- `evals/team-tasks/vo-t01` to `vo-t06`: the six scored voiceover changes, one task per pull
  request, reviewed by the team as it ships. Each is a multi-step Harbor task: seven reviewer
  steps, each a fresh agent session given the orchestrator's own message, then the validator step,
  whose final findings a rubric judge grades. One trajectory per step, so you can see each
  reviewer come in and out.
- `evals/team-tasks/vo-x1`, `vo-x4`, `vo-x7`, `vo-x8`, `vo-x17` and `vo-x20`: six more voiceover
  changes, run the same way. Each key is the pull request's first bot review (Codex or CodeRabbit),
  keeping only the findings the reviewed commit confirms on reading. Five of them (all but
  vo-x20) were the study's tuning changes, so they are not blind like the six scored ones.
- `evals/team-tasks/<slug>-llm-judge` for vo-x7, vo-x4, vo-t06, vo-t01, vo-t04 and vo-t02: the same
  six changes with another grader. A judge with file tools reads the review, the known issues and
  the code at the reviewed commit, and rates four 1-5 scales whose weights sum to 1: known issues
  (0.30), whether other findings hold up in the code (0.25), severity and fixes (0.15), and
  economic value, the hard engineering work the review saves (0.30).
- `evals/cases/cr-self-01`: this repository's own history, the first commit of the CI action and
  the 18 confirmed bugs it contained. Can the review tool find the bugs in itself?

### Results so far

Two full runs on 2026-10-12, one trial per task: the review team on the Codex CLI with gpt-6-luna
(reasoning medium) and with gpt-6.1-sol (high), each graded by a Codex judge on gpt-6-luna. Cost is
Harbor's API-equivalent figure for the review team (the runs used a ChatGPT subscription); the
judge's cost is not included. Over the 12 public tasks:

| Agent model | Recall | Findings per task | Input tokens per task | Cost per task |
|---|---|---|---|---|
| gpt-6-luna (medium) | 0.31 | 5.6 | 15.5M | $0.24 |
| gpt-6.1-sol (high) | 0.54 | 13.4 | 21.7M | $4.65 |

- **Sol's recall is about 1.7 times Luna's, at about 19 times the cost.** It also writes 2.4 times
  as many findings. It led on 8 tasks, Luna on 1 (vo-x20, 0.80 to 0), and 3 were tied.
- **Single tasks are noisy.** With one trial each, a key of one or two issues swings a whole point
  (vo-x7, vo-x1); read the totals, not one task.
- **One known judge miss.** On vo-x4 under Sol the judge scored six findings 0 without opening
  `findings.json`: the only such miss in all 44 trials of the two full runs (22 tasks each, the
  12 public ones plus 10 private). It stays: every run is graded the same way.
- The `-llm-judge` tasks have not been run yet.

Per trial (recall, findings, tokens, cost): `research/results/team-evals-2026-10-12.csv`.

### Run the evals yourself

In General Environments, import this repository: every task folder under `evals/` becomes part of
one benchmark, and the run picks the agent, model and judge. With Harbor directly:

    export REWARDKIT_JUDGE=codex REWARDKIT_MODEL=gpt-6-luna \
        CODEX_AUTH_JSON="$(cat ~/.codex/auth.json)"
    harbor run -y -p evals/team-tasks/vo-x7 -a codex -m openai/gpt-6-luna \
        --ak reasoning_effort=medium --ae CODEX_AUTH_JSON_PATH=$HOME/.codex/auth.json

A team task runs eight agent sessions, so a full sweep adds up quickly. To start cheaply, take
the six tasks chosen for content and spread of size: vo-x7 and vo-x4 (one clear bug in a small
change), vo-t06 (frontend lifecycle bugs), vo-t01 (blocking calls and unchecked input in a
backend), vo-t04 (a broken path allowlist and a secrets migration) and vo-t02 (the security
showcase: path traversal, unsafe pickle loading, SSRF). Each also has an `-llm-judge` version.
A judge from another model family than the agent is the safer choice; the results above used the
same family for both.

The loop this repository is building toward:

1. A pull request changes the review logic: a skill, a prompt, the launcher, a runner row.
2. CI sees the pipeline digest move (a hash of every file that shapes a review), regenerates the
   eval tasks, checks them with an Oracle and a no-op run, and commits them back to the branch,
   so the evals always match the code they test.
3. Trials run the changed tool across agents and models; the score posts on the pull request.
4. The review team reviews the pull request itself.
5. On merge, the platform runs the evals at that commit and its analysis says what to improve
   next, which becomes the next pull request.

Steps 1, 2 (the digest) and 4 work today; the rest is this version's work.

## Install and develop

    uv tool install git+https://github.com/davidbzyk/code_review   # the code-review command
    uv sync && uv run pytest                                      # from a checkout

## Status

Current version: v0.1 in progress. Model observations so far: gpt-6-luna leans to minor findings
and padded summaries, and two runs on nearly the same change disagreed on the most serious finding.
The first cross-model results are above; the `-llm-judge` tasks and more models are next.

## Sources and citations

Each reviewer skill cites its sources passage by passage (the source, its file and lines, and
whether the text is verbatim or changed) in `CITATIONS.md` in its folder under
[`src/plugin/skills/`](src/plugin/skills/); [`src/plugin/provenance/`](src/plugin/provenance/)
records what each source contributed and what was left out.
