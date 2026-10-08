# code-review

A team of review agents for pull requests: seven reviewers (security, tests, correctness,
architecture, code quality, compliance, language) and a validator, run by one main agent, merged
into one deduplicated set of findings. Around it: evals that regenerate whenever anything in the
pipeline changes, and trials across agents and models.

Status: staging. Built from the `agentic-tooling/code-review` experiment; not public yet.

## Install

    uv tool install git+<repo-url>          # or: pipx install git+<repo-url>
    uv tool install ./                      # from a checkout

This puts `code-review` on your PATH. The vector context provider needs the `context` extra:
`uv tool install "code-review[context] @ git+<repo-url>"`.

## Add the review to a repository's CI

    sh action/install.sh /path/to/your/repo

Then sign Codex in with a ChatGPT subscription or an OpenAI API key; both are described in
[`action/README.md`](action/README.md), which the installer also copies into the repository.

## Layout

- `src/review_core/`: the launcher, runner registry (`launcher/runners.toml`), the reviewers'
  aggregator, contracts, context providers and scoring.
- `src/context_engine/`: the vector index used by the `vector` context provider.
- `src/plugin/`: the review skills and the orchestrator that runs them.
- `src/review_core/pipeline.toml`: every file whose change makes evals and trials stale.
- `trials/results/`: trial job folders (on disk, never tracked: they quote private case material).

## Develop

    uv sync
    uv run pytest
