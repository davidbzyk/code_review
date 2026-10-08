#!/usr/bin/env bash
# Review one pull request with the Codex review team and post the result. Called by action.yml;
# runs the same way on a laptop given the CR_* variables (CR_DRY_RUN=DIR posts nothing).
set -euo pipefail
here=$(cd "$(dirname "$0")" && pwd)
repo=${GITHUB_WORKSPACE:-$PWD}
work=${RUNNER_TEMP:-$HOME/.cache/code-review-ci}/code-review
rm -rf "$work" && mkdir -p "$work"
export PYTHONPATH="$here/src"

# The files this pull request changes, less the review tool itself.
paths=()
while IFS= read -r path; do
  case "$path" in .code-review/*|"") ;; *) paths+=(--path "$path") ;; esac
done < <(git -C "$repo" diff --no-ext-diff --name-only --diff-filter=ACMR "$CR_BASE...$CR_HEAD")
if [ ${#paths[@]} -eq 0 ]; then
  echo "code-review: no changed files outside .code-review/, nothing to review"
  exit 0
fi

# One input picks the login: the ChatGPT subscription (a seeded auth.json) or an API key.
case "${CR_AUTH:-subscription}" in
  subscription)
    runner=codex-clean
    : "${CODEX_AUTH_JSON_B64:?auth is subscription: set the CODEX_AUTH_JSON_B64 secret}"
    export CODEX_HOME="$work/codex-home"
    mkdir -p "$CODEX_HOME"
    printf '%s' "$CODEX_AUTH_JSON_B64" | base64 -d > "$CODEX_HOME/auth.json"
    chmod 600 "$CODEX_HOME/auth.json"
    unset CODEX_AUTH_JSON_B64 OPENAI_API_KEY ;;
  api-key)
    runner=codex-key
    : "${OPENAI_API_KEY:?auth is api-key: set the OPENAI_API_KEY secret}"
    unset CODEX_AUTH_JSON_B64 ;;
  *) echo "code-review: auth must be subscription or api-key, not ${CR_AUTH}" >&2; exit 2 ;;
esac

# CR_RUNNER and CR_REGISTRY swap in another runner row (a test's fake agent, a new provider).
runner=${CR_RUNNER:-$runner}
registry=()
if [ -n "${CR_REGISTRY:-}" ]; then registry=(--registry "$CR_REGISTRY"); fi

# The review never sees the GitHub token; only the post below gets it.
status=0
env -u GITHUB_TOKEN python3 -m review_core.cli review --repo "$repo" --base "$CR_BASE" \
  --head "$CR_HEAD" --runner "$runner" --model "${CR_MODEL:-gpt-6-luna}" \
  --effort "${CR_EFFORT:-high}" --out "$work/out" --runs "$work/runs" "${registry[@]}" \
  "${paths[@]}" || status=$?

# A failed run still has a review.json; post it so the pull request shows the failure.
post=(python3 -m review_core.ci.github --runs "$work/runs" --repo-dir "$repo" --base "$CR_BASE"
      --head "$CR_HEAD" --repo "$CR_REPO" --pr "$CR_PR" --summary "$work/out/pr-summary.md")
if [ -n "${CR_DRY_RUN:-}" ]; then post+=(--dry-run "$CR_DRY_RUN"); fi
"${post[@]}"
exit "$status"
