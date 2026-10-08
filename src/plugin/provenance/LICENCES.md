# Licences of the sources

One row per source the reviewer skills drew on. "Licence as found" records what the copy of
the source under `third_party/` itself contains: the name of its licence file, or that it has
none, plus any licence statement inside its files. The skills take ideas, checklists and rules
from these sources and state them in this project's own words; no sentence is copied, and no
attack string or exploit recipe from the security sources appears in any skill. The row-level
record is in the seven provenance files beside this one.

| Source | Licence as found | Contribution |
|---|---|---|
| `agent-skills` | `LICENSE` (MIT) | Parts used by: security, tests, correctness, architecture, code_quality, compliance, language. |
| `brooks-lint-marketplace` | no licence file | Parts used by: security, tests, correctness, architecture, code_quality, compliance, language. |
| `ce-code-review` | no licence file | Parts used by: security, tests, correctness, architecture, code_quality, compliance, language. |
| `ce-simplify-code` | `LICENSE` (MIT) | Parts used by: tests, correctness, architecture, code_quality, language. |
| `claude-code-workflows` | `LICENSE` (MIT) | Parts used by: security, tests, correctness, architecture, code_quality, compliance, language. |
| `claude-plugins-official/code-review` | `LICENSE` (Apache 2.0) | Parts used by: security, tests, architecture, code_quality, compliance, language. |
| `claude-plugins-official/code-simplifier` | `LICENSE` (Apache 2.0) | Parts used by: code_quality, language. |
| `claude-plugins-official/feature-dev-code-reviewer` | `LICENSE` (Apache 2.0) | Parts used by: security, tests, correctness, architecture, code_quality, language. |
| `claude-plugins-official/mattpocock-code-review` | `LICENSE` (MIT) | Parts used by: tests, architecture, code_quality, compliance, language. |
| `claude-plugins-official/security-guidance` | `LICENSE` (Apache 2.0) | Parts used by: security, compliance, language. |
| `claude-plugins-official/superpowers` | `LICENSE` (MIT) | Parts used by: security, tests, architecture, code_quality, compliance, language. |
| `codebase-audit-suite` | `LICENSE` (MIT) | Parts used by: security, tests, correctness, architecture, code_quality, compliance, language. |
| `multi-agent-review` | no licence file | Parts used by: security, tests, correctness, architecture, code_quality, compliance, language. |
| `pr-review-toolkit` | no licence file; `README.md` says MIT | Parts used by: security, tests, correctness, architecture, code_quality, compliance, language. |
| `secrets-management` | no licence file | Parts used by: security, tests, compliance. |
| `security/007` | no licence file | Parts used by: security, tests, correctness, architecture, code_quality, language. |
| `security/security-and-hardening` | no licence file; frontmatter `license: MIT` | Parts used by: security, compliance. |
| `security/security-arsenal` | no licence file; frontmatter `license: MIT` | Parts used by: security, tests. |
| `security/security-audit` | no licence file | Parts used by: security. |
| `security/security-lens-reviewer` | no licence file | Parts used by: security. |
| `security/security-reviewer` | no licence file | Parts used by: security. |
| `security/security-scanning-security-hardening` | no licence file | Parts used by: security. |
| `thermos` | `LICENSE` (MIT, Copyright (c) 2026 Cursor) | Parts used by: security, tests, correctness, architecture, code_quality, compliance, language. |

## Attribution facts found in the copies

- `agent-skills`: Installed plugin `agent-skills` 0.6.7 from the `addy-agent-skills` marketplace; `LICENSE` is MIT.
- `brooks-lint-marketplace`: Upstream `https://github.com/hyhmrright/brooks-lint` (from `.git/config`). The inventory reports an MIT `LICENSE` upstream; it is not in the copy.
- `ce-code-review`: The inventory reports MIT at the plugin root (`EveryInc/compound-engineering-plugin`, authors Kieran Klaassen and Trevin Chow); no licence text is in the copy.
- `ce-simplify-code`: The `ce-simplify-code` skill of `compound-engineering` 3.30.4 (`EveryInc/compound-engineering-plugin`); `LICENSE` is MIT.
- `claude-code-workflows`: Five parts of the `claude-code-workflows` marketplace (comprehensive-review 1.3.1, developer-essentials 1.0.4, agent-teams 1.0.3, backend-development 1.3.2, data-validation-suite 1.2.1); the marketplace `LICENSE` is MIT, Copyright (c) 2024 Seth Hobson.
- `claude-plugins-official/code-review`: Installed from the `claude-plugins-official` marketplace; `LICENSE` is Apache 2.0.
- `claude-plugins-official/code-simplifier`: Installed from the `claude-plugins-official` marketplace, version 1.0.0; `LICENSE` is Apache 2.0.
- `claude-plugins-official/feature-dev-code-reviewer`: The code-reviewer agent of `feature-dev` from the `claude-plugins-official` marketplace; `LICENSE` is Apache 2.0.
- `claude-plugins-official/mattpocock-code-review`: The engineering code-review skill of `mattpocock-skills` 1.2.3; `LICENSE` is MIT.
- `claude-plugins-official/security-guidance`: Installed from the `claude-plugins-official` marketplace, version 2.0.10; `LICENSE` is Apache 2.0.
- `claude-plugins-official/superpowers`: The requesting and receiving code review skills of `superpowers` 6.4.1; `LICENSE` is MIT.
- `codebase-audit-suite`: The 36 auditor skills of `codebase-audit-suite` from the `levnikolaevich-skills-marketplace`; `LICENSE` is MIT.
- `multi-agent-review`: Frontmatter says only "Converted from Claude command multi-agent-review"; no author or upstream.
- `pr-review-toolkit`: `README.md` 303-309: licence MIT, author Daisy (daisy@anthropic.com); no upstream address.
- `secrets-management`: Frontmatter `source: community`; no author.
- `security/007`: Frontmatter `source: community`, `author: renat`.
- `security/security-and-hardening`: Frontmatter `license_source: https://github.com/addyosmani/agent-skills/blob/main/LICENSE`, `source_repo: addyosmani/agent-skills`.
- `security/security-arsenal`: Frontmatter `license_source: https://github.com/elementalsouls/Claude-BugHunter/blob/main/LICENSE`, `source_repo: elementalsouls/Claude-BugHunter`.
- `security/security-audit`: Frontmatter `source: personal`; no author.
- `security/security-lens-reviewer`: Frontmatter has only a name and a description.
- `security/security-reviewer`: Frontmatter has only a name and a description.
- `security/security-scanning-security-hardening`: Frontmatter `source: community`; no author.
- `thermos`: `.cursor-plugin/plugin.json`: author Cursor, repository `https://github.com/cursor/plugins`, `"license": "MIT"`.

## Open points for the owner

- Nine of the first thirteen sources carry no licence statement at all in the copy. Their ideas are
  restated here, not their text, but whether to name them in a public release is the owner's call.
- `pr-review-toolkit` states MIT in its README and names an internal repository as its home.
- `security/security-arsenal` is an offensive catalogue. Only its class names, its list of
  always-rejected findings and its chain table were used.
