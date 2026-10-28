# Ledger format v2

This is an external evidence ledger, not hidden reasoning. Scripts validate structure and recorded status, not whether claims are true. Use UTF-8 JSON (BOM accepted), at most 2 MiB and 500 steps. Unknown fields are rejected to catch misspellings. Do not put secrets in evidence strings.

Use this format only when a persistent ledger adds value; Quick/Explore tasks can use brief prose. Version 1 remains accepted without `profiles` or `not_run`; new ledgers use version 2. Existing requirements can be referenced in `expected`, `check`, and `evidence` rather than duplicated.

Required top-level fields:

| Field | Meaning |
| --- | --- |
| `schema_version` | integer `2` (legacy `1` supported) |
| `profiles` | v2 only: unique selected names from `code`, `debug`, `performance`, `concurrency`, `visual`, `content`; empty is allowed for general tasks |
| `goal` | nonempty user-facing outcome |
| `scope` | nonempty string array of allowed work areas |
| `premises` | objects: `id`, `claim`, `basis` (`given/inferred/assumed`), `verification` (`unverified/verified/refuted`), `evidence` (string array) |
| `steps` | ordered objects: `id`, `premises` (IDs), `depends_on` (earlier IDs), `expected`, `check`, `status` (`pending/running/passed/failed/blocked`), `output`, `evidence` |
| `code_changed` | boolean |
| `review` | dimension maps to `{status: pending/pass/fail/not_applicable, evidence: [...]}`; v2 also allows `{status: not_run, evidence: [...], condition: premise ID}` |
| `recoveries` | objects: `step`, `action`, `attempt` (positive integer), `evidence` |
| `conclusion` | `{status: in_progress/complete/conditional/blocked, summary, conditions: [premise IDs]}` |

IDs match `[A-Za-z][A-Za-z0-9_-]{0,63}` and are globally unique. Every input premise must be declared. Step dependencies must refer backward and be acyclic. An active/passed step must have passed predecessors; it cannot use a refuted premise. Failed/blocked steps cannot have active/passed downstream results. Passing requires a recorded output and evidence; matching the output to `expected` is still a human/model judgment.

Verified or refuted premises need evidence. A final `complete`/`conditional` conclusion requires all steps passed; unverified premises used anywhere in those steps must appear in `conditions` and require `conditional`. Conditions must name unresolved used premises. Changed code requires the four base dimensions regardless of selected profiles. Selected profiles add their dimensions from [review-profiles.md](review-profiles.md): `debug` → `semantic_validity`, `performance` → `performance`, `concurrency` → `concurrency`, `visual` → `visual_quality` + `interaction_accessibility`, `content` → `factual_integrity`. The `code` profile requires all four base dimensions even when `code_changed` is false.

`not_applicable` needs a reason; intent alignment cannot be not applicable. For v2 `not_run`, `condition` must identify an unverified premise used by a step. Finalization is allowed only as `conditional`, with that premise included in the conclusion conditions and the missing check explained in evidence. A failed or pending check prevents finalization even if its profile was not selected. Structural validation does not verify the evidence or prove that the correct profiles were selected.

Each failed/blocked step needs a recovery entry. Repeated local repair (>2 by default) for one step is flagged; switch to a new design/step contract or stop. The CLI accepts `--max-repairs N` (0–20) for an explicitly chosen task budget. Within a step, attempts start at 1 and increase by 1. Historical recoveries can remain after a step passes. The validator checks a snapshot, not a tamper-proof history; it cannot detect a premise changed between snapshots.

## Small example

See `../assets/state.example.json`: an initial ledger to start from. To finish, replace its pending statuses with actual outputs/check evidence; do not copy example results as your own.

## Diff scope format

`review_diff.py` accepts a standard unified text diff and `{"allowed_paths":["src/*.py","tests/*"]}`. Patterns use Python `fnmatchcase` on slash-separated repository paths (`*` may span `/`). Use explicit paths for strict scope. Both old and new paths are checked for renames; paths are treated as data and never opened. Quoted Git paths are decoded. Binary, combined, malformed, or unsupported diffs fail closed with exit 2. Empty diff is valid and says zero changed files. Path scope cannot express semantic intent; manually check changes within an allowed file.
