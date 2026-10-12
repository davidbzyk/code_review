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

**The comparison.** This repository has several commercial reviewers turned on (Codex, Greptile,
CodeRabbit, Gravity, Devin and Sonar) next to its own review action. That seems excessive, but it
means every pull request here compares them side by side.

**The design.** I went through all my code and security review plugins and kept what I thought
was valuable from each; the sources are cited at the bottom of this page.

The full write-up will be a Medium article *(link when published)*, written as a tutorial: import
this repository into General Environments, run its benchmarks across several models and harnesses,
and find which one suits this use case best for cost and speed. The article also shows the results
on a larger, more complex codebase (General Environments itself), and how benchmarking and analysis
turn the review into a self-improving workflow. This README is its summary.

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
posted as one review with inline comments plus a summary that updates on each push.

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
- `evals/cases/cr-self-01`: this repository's own history, the first commit of the CI action and
  the 18 confirmed bugs it contained. Can the review tool find the bugs in itself?

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

Built in the open. Current version: v0.1 in progress. Model observations so far: gpt-6-luna leans
to minor findings and padded summaries, and two runs on nearly the same change disagreed on the
most serious finding; a comparison across models on the evals is next.

## Sources and citations

<details>
<summary>The review plugins and skills the reviewers were built from</summary>

Each reviewer skill records, passage by passage, which source it came from, the source file and
lines, and whether the text is verbatim or changed: see `CITATIONS.md` in each skill folder under
[`src/plugin/skills/`](src/plugin/skills/).

- [agent-skills](https://github.com/addyosmani/agent-skills) (Addy Osmani)
- [brooks-lint](https://github.com/hyhmrright/brooks-lint)
- [compound-engineering](https://github.com/EveryInc/compound-engineering-plugin) (Every): `ce-code-review`, `ce-simplify-code`
- claude-code-workflows (Seth Hobson): comprehensive-review, developer-essentials, agent-teams,
  backend-development, data-validation-suite
- claude-plugins-official (Anthropic): code-review, code-simplifier, feature-dev code-reviewer,
  security-guidance
- pr-review-toolkit (Anthropic)
- mattpocock-skills: code-review
- superpowers: requesting and receiving code review
- codebase-audit-suite (levnikolaevich-skills-marketplace)
- [Claude-BugHunter](https://github.com/elementalsouls/Claude-BugHunter): security-arsenal
- [Cursor plugins](https://github.com/cursor/plugins): thermos
- [antigravity-awesome-skills](https://github.com/sickn33/antigravity-awesome-skills): 007 (renat),
  secrets-management, security-audit, security-scanning-security-hardening
- security-lens-reviewer, security-reviewer, multi-agent-review

</details>
