# Provenance: `validator` skill

Every part of `src/plugin/skills/review-validator/SKILL.md` that came from a source plugin, one row per part, as the text reads after the machinery pass. Source paths are relative to `third_party/`. "Adapted" means the idea was taken and rewritten in this project's own words to fit its contract. "Cited" means the source was read and is acknowledged, but the text follows a different source or none. No sentence in the skill is copied from any source.

## Parts

| Part | Source path | Lines | Licence | Treatment | What changed |
|---|---|---|---|---|---|
| A separate validator that tries to reject claims, independent of the reviewers and the orchestrator | `ce-code-review/references/validator-batch-template.md` | 3, 6 | no licence file | adapted | One sub-agent that reads the repository itself, given no diff and no other agent's output. It is asked to disprove, not to confirm. |
| Judge each finding on its own; invent no findings | `ce-code-review/references/validator-batch-template.md` | 8 | no licence file | adapted | Also forbids rewording a finding and changing its severity in either direction. |
| Never raise severity or confidence to keep a finding alive | `ce-code-review/references/validator-batch-template.md` | 47 | no licence file | adapted | Extended to lowering and rewording: the validator can only uphold or decline. |
| A verdict never creates a finding, and a failure never becomes a confirmation | `ce-code-review/references/finish-review.md` | 71 | no licence file | adapted | The first half is the rule that a real problem the reviewers missed is ignored here; the second half is the rule that a finding the validator could not check gets no verdict. |
| Inspect the cited file, its callers, its guards, the contracts and tests, with read-only tools | `ce-code-review/references/validator-batch-template.md` | 50 | no licence file | adapted | A reading list in step 2. The source also allows targeted history and read-only reproduction; here nothing is run. |
| A finding stands only if inspected evidence shows the code permits it, the change exposes it and nothing around it prevents it | `ce-code-review/references/validator-batch-template.md` | 35 | no licence file | adapted | Used as what to read (guards, callers, types) and not as a standard for upholding: the default is to uphold unless disproved (see overlaps). |
| Name the precondition the defect needs, and say when its occurrence was not checked | `ce-code-review/references/validator-batch-template.md` | 37 | no licence file | adapted | Step 3 asks for the input or state, and an unknown state is upheld with that said in `reason`. The source also asks the validator to look for evidence of occurrence; this one cannot run code. |
| Read title and body together; judge the failure alleged, not keywords | `ce-code-review/references/validator-batch-template.md` | 39 | no licence file | adapted | One sentence in step 3. The source's eight protected subjects are not used. |
| Reject only on cited evidence; an assumed guarantee is not evidence | `ce-code-review/references/validator-batch-template.md` | 41 | no licence file | adapted | One evidence form is kept: the file and line that disproves the claim. The others (documentation for the version in force, a hash for pre-existing code, a discriminating test run) need a lookup or a run. |
| Without evidence either way a finding stays unresolved, never rejected | `ce-code-review/references/validator-batch-template.md` | 43, 45 | no licence file | adapted | Here: no verdict row. The script keeps the finding and marks the run as only partly checked. |
| Grounds for rejecting: the cited code does not prove it, or surrounding code handles it | `ce-code-review/references/validator-batch-template.md` | 6 | no licence file | adapted | Kept as two of the four grounds for a decline. The source's other grounds (it predates the change, it is only a preference) are not taken. |
| If the cited file cannot be reached, do not guess | `ce-code-review/references/validator-batch-template.md` | 45 | no licence file | adapted | Step 5: no verdict for that finding, counted in the last line. |
| Inspect in the order given; when out of budget, stop and never guess a verdict | `ce-code-review/references/validator-batch-template.md` | 52 | no licence file | adapted | Leave the rest without a verdict. No time or tool-call numbers. |
| One verdict per finding, identifiers copied unchanged, one permitted write | `ce-code-review/references/validator-batch-template.md` | 54, 66 | no licence file | adapted | Rows of `id`, `verdict` and `reason`; two verdict words; a verdict with an unknown id is ignored. No protected-subject field. |
| Read-only: no edits, commits or pushes | `ce-code-review/references/validator-batch-template.md` | 66 | no licence file | adapted | The only file written is `validation.json`; no project code is run and no package installed. |
| A rejected finding is dropped and the reason is recorded | `ce-code-review/references/finish-review.md` | 68 | no licence file | adapted | A decline names the guard, line or fact; the aggregator writes it to `declined.json`. |
| Read old-side code from the base commit with git, not from the checkout | `ce-code-review/references/dispatch-reviewers.md` | 78 | no licence file | adapted | Step on `old` findings: `git show <base>:<file>`. |
| Fresh eyes: the validator is not shown what the reviewers wrote beyond its own input | `ce-code-review/references/dispatch-reviewers.md` | 16 | no licence file | adapted | Rule that the validator does not read the reviewers' files or the candidates file. |
| No sub-agents of its own | `thermos/agents/thermo-nuclear-review-subagent.md` | 24 | `LICENSE` (MIT, Copyright (c) 2026 Cursor) | adapted | One sentence in the opening. |
| Select every remaining P0 and P1 finding for the validator | `ce-code-review/references/finish-review.md` | 62 | no licence file | adapted | The script chooses the findings; the skill only states that severity is P0 or P1. |
| Cross-agent verification as a named step | `multi-agent-review/SKILL.md` | 146-157 | no licence file | cited | The file names the step and gives no method. The method here follows `ce-code-review`. |

Not from any source: the rule that the validator never reads the reviewers' own files is derived from `dispatch-reviewers.md` 16 but stated for this project's file layout; the reply of three counts; and the exact shape of `validator-input.json` and `validation.json`, which comes from this project's contract.

## Overlaps resolved

- What to do when a claim cannot be disproved. Competing: `ce-code-review` (`validator-batch-template.md` 23: "never use lack of disproof as evidence of confirmation"; three statuses, with unresolved findings kept in the report as gates) and this project's contract (two verdict words; a finding that is not disproved stays). Winner: this contract, with the source's effect kept: a finding that is not disproved is upheld, and one that could not be checked gets no verdict, which leaves it in place and marks the run as only partly checked, the same outcome as the source's unresolved gate.
- How strict a rejection must be. Competing: `ce-code-review` (`validator-batch-template.md` 41: a higher bar for eight protected subjects, with four evidence forms) and this skill (one bar for every decline: a concrete reason naming the file and line). Winner: one bar. It is as strict as the source's protected bar for the evidence a read-only reader can produce, and it needs no subject list to classify.
- What to do when the validator runs short. Competing: `ce-code-review` (`validator-batch-template.md` 52: mark every remaining finding unresolved with a stated reason) and the earlier text of this skill (uphold the rest with the reason "not inspected"). Winner: `ce-code-review`'s effect. An upheld verdict that was never earned makes the run look fully checked; no verdict leaves it honest.
- What counts as a ground to decline. Competing: `ce-code-review` (`validator-batch-template.md` 6: four grounds) and this skill (four concrete reasons). Winner: this skill's list, plus the source's two grounds that a reader can prove from code. "It predates the change" is the reviewer's own scope label, and "it is only a preference" would let the validator rule on taste, so both are left out.

## Available, not used

Every mined part sorted to this piece that the text or the code does not draw on, with the
reason it was left out. A reason that says "needs a code change" names a sound idea that
only code could carry; it is not written into a skill, because a skill must not promise
behaviour the aggregator does not have. Paths are relative to `third_party/`.

| Part | Source path | Lines | Why left out |
|---|---|---|---|
| Three statuses, and a rule that lack of disproof is never confirmation | `ce-code-review/references/validator-batch-template.md` | 23-33 | Lost to the contract's two verdict words, as described under overlaps. The subject keys in 25-33 classify findings for a stricter bar this skill does not use. Add if security findings should get a stricter bar. |
| The diff and scope context placed in the prompt | `ce-code-review/references/validator-batch-template.md` | 10-20 | The validator reads the repository, and the refs come in the main agent's message. |
| Check each rejection's citation yourself before accepting it, and classify each finding before reading its verdict | `ce-code-review/references/finish-review.md` | 65 | The aggregator cannot check a free-text reason. A decline is audited through `declined.json`, which keeps every reason. |
| A confirmed verdict whose reason says occurrence was not measured is carried on the finding as a validation note | `ce-code-review/references/finish-review.md` | 67 | Needs a code change: the aggregator does not copy an upheld reason onto the finding. Change: keep the validator's reason (or an unchecked flag) on each final finding. |

Not listed: the parts that belong to the orchestrator and the aggregator are in their own records, and the sorting of every cross-cutting part is in `orchestrator.md`.
